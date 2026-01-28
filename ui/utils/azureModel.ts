import { BlobServiceClient } from "@azure/storage-blob";
import fs from "fs";
import path from "path";
import os from "os";
import { pipeline } from "stream/promises";

type EnsureModelResult =
  | { ok: true; localPath: string }
  | { ok: false; error: string };

let inFlight: Promise<EnsureModelResult> | null = null;

function getEnv(name: string): string | undefined {
  const v = process.env[name];
  return v && v.trim() ? v.trim() : undefined;
}

function defaultLocalModelPath(): string {
  // On serverless (e.g. Vercel), only /tmp is writable.
  const base = process.env.VERCEL ? os.tmpdir() : path.join(process.cwd(), ".cache");
  return path.join(base, "gbm-tokenizer", "gbm_tokenizer.model");
}

async function fileLooksValid(p: string): Promise<boolean> {
  try {
    const st = await fs.promises.stat(p);
    return st.isFile() && st.size > 0;
  } catch {
    return false;
  }
}

/**
 * Ensures `gbm_tokenizer.model` exists locally by downloading it from Azure Blob Storage.
 *
 * Required env vars:
 * - AZURE_STORAGE_CONNECTION_STRING
 * - AZURE_MODELS_CONTAINER
 * - GBM_TOKENIZER_BLOB_NAME
 *
 * Optional:
 * - GBM_TOKENIZER_MODEL_PATH (if you want to force a specific local path)
 */
export async function ensureGbmModelDownloaded(): Promise<EnsureModelResult> {
  if (inFlight) return inFlight;

  inFlight = (async () => {
    const forcedLocalPath = getEnv("GBM_TOKENIZER_MODEL_PATH");
    const localPath = forcedLocalPath || defaultLocalModelPath();

    // If already present, don't re-download.
    if (await fileLooksValid(localPath)) {
      return { ok: true, localPath };
    }

    const connStr = getEnv("AZURE_STORAGE_CONNECTION_STRING");
    const containerName = getEnv("AZURE_MODELS_CONTAINER");
    const blobName = getEnv("GBM_TOKENIZER_BLOB_NAME");

    if (!connStr || !containerName || !blobName) {
      return {
        ok: false,
        error:
          "Model file missing locally and Azure download is not configured. " +
          "Set AZURE_STORAGE_CONNECTION_STRING, AZURE_MODELS_CONTAINER, and GBM_TOKENIZER_BLOB_NAME.",
      };
    }

    await fs.promises.mkdir(path.dirname(localPath), { recursive: true });

    const tmpPath = `${localPath}.download`;
    // Best-effort cleanup of any partial download.
    try {
      await fs.promises.unlink(tmpPath);
    } catch {}

    try {
      const service = BlobServiceClient.fromConnectionString(connStr);
      const container = service.getContainerClient(containerName);

      const containerExists = await container.exists();
      if (!containerExists) {
        return { ok: false, error: `Azure container does not exist: ${containerName}` };
      }

      const blob = container.getBlobClient(blobName);
      const blobExists = await blob.exists();
      if (!blobExists) {
        return {
          ok: false,
          error: `Azure blob does not exist: container=${containerName} blob=${blobName}`,
        };
      }

      const download = await blob.download();
      if (!download.readableStreamBody) {
        return { ok: false, error: "Azure download stream was not readable." };
      }

      const out = fs.createWriteStream(tmpPath, { flags: "wx" });
      await pipeline(download.readableStreamBody, out);

      // Atomic replace.
      await fs.promises.rename(tmpPath, localPath);

      if (!(await fileLooksValid(localPath))) {
        return { ok: false, error: `Downloaded model is empty or invalid: ${localPath}` };
      }

      return { ok: true, localPath };
    } catch (e) {
      // Clean up partial download.
      try {
        await fs.promises.unlink(tmpPath);
      } catch {}
      let errorMsg = "Failed to download model.";
      if (
        e &&
        typeof e === "object" &&
        "message" in e &&
        typeof (e as { message?: unknown }).message === "string"
      ) {
        errorMsg = String((e as { message: string }).message);
      }
      return { ok: false, error: errorMsg };
    }
  })();

  const result = await inFlight;
  // Allow retry on failure.
  if (!result.ok) inFlight = null;
  return result;
}

