import type { NextApiRequest, NextApiResponse } from "next";
import { spawn } from "child_process";
import path from "path";
import fs from "fs";
import { ensureGbmModelDownloaded } from "../../lib/azureModel";

type TokenizeErrorCode =
  | "MODEL_NOT_READY"
  | "PYTHON_NOT_AVAILABLE"
  | "TOKENIZE_FAILED"
  | "BAD_REQUEST"
  | "METHOD_NOT_ALLOWED";

type TokenizeResponse = {
  tokens: string[];
  ids: number[];
  count: number;
  error?: {
    code: TokenizeErrorCode;
  };
};

function tokenizeText(text: string): Promise<TokenizeResponse> {
  return new Promise((resolve) => {
    try {
      const scriptPath = path.join(process.cwd(), "tokenize_api.py");

      // Check if Python script exists
      if (!fs.existsSync(scriptPath)) {
        resolve({
          tokens: [],
          ids: [],
          count: 0,
          error: { code: "PYTHON_NOT_AVAILABLE" },
        });
        return;
      }

      // Spawn Python process (ensure env passed through)
      const pythonProcess = spawn("python3", [scriptPath], {
        stdio: ["pipe", "pipe", "pipe"],
        env: {
          ...process.env, // Inherit all environment variables
        },
      });

      let stdout = "";

      pythonProcess.stdout.on("data", (data) => {
        stdout += data.toString();
      });

      // Intentionally ignore stderr to avoid leaking internals to clients/logs.
      // (We return a generic error code instead.)
      pythonProcess.stderr.on("data", () => {});

      pythonProcess.on("close", (code) => {
        if (code !== 0) {
          resolve({
            tokens: [],
            ids: [],
            count: 0,
            error: { code: "TOKENIZE_FAILED" },
          });
          return;
        }

        try {
          let result;
          try {
            result = JSON.parse(stdout.trim());
            if (result && typeof result === "object" && "error" in result) {
              resolve({
                tokens: [],
                ids: [],
                count: 0,
                error: { code: "TOKENIZE_FAILED" },
              });
              return;
            }
            resolve(result as TokenizeResponse);
          } catch {
            resolve({
              tokens: [],
              ids: [],
              count: 0,
              error: { code: "TOKENIZE_FAILED" },
            });
          }
        } catch {
          resolve({
            tokens: [],
            ids: [],
            count: 0,
            error: { code: "TOKENIZE_FAILED" },
          });
        }
      });

      pythonProcess.on("error", () => {
        resolve({
          tokens: [],
          ids: [],
          count: 0,
          error: { code: "PYTHON_NOT_AVAILABLE" },
        });
      });

      // Write text to stdin
      pythonProcess.stdin.write(text, "utf-8");
      pythonProcess.stdin.end();
    } catch {
      resolve({
        tokens: [],
        ids: [],
        count: 0,
        error: { code: "TOKENIZE_FAILED" },
      });
    }
  });
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<TokenizeResponse>
) {
  const requestId =
    (typeof req.headers["x-request-id"] === "string" && req.headers["x-request-id"]) ||
    `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;

  if (req.method !== "POST") {
    console.info("[api/tokenize]", { requestId, status: 405, error: "METHOD_NOT_ALLOWED" });
    return res.status(405).json({
      tokens: [],
      ids: [],
      count: 0,
      error: { code: "METHOD_NOT_ALLOWED" },
    });
  }

  const { text } = req.body;

  if (!text || typeof text !== "string") {
    console.info("[api/tokenize]", { requestId, status: 400, error: "BAD_REQUEST" });
    return res.status(400).json({
      tokens: [],
      ids: [],
      count: 0,
      error: { code: "BAD_REQUEST" },
    });
  }

  // Ensure the model file exists locally (download from Azure if needed).
  const ensured = await ensureGbmModelDownloaded();
  if (!ensured.ok) {
    console.error("[api/tokenize]", {
      requestId,
      status: 500,
      error: "MODEL_NOT_READY",
    });
    return res.status(500).json({
      tokens: [],
      ids: [],
      count: 0,
      error: { code: "MODEL_NOT_READY" },
    });
  }

  // Tell the Python script exactly where the model is on disk.
  process.env.GBM_TOKENIZER_MODEL_PATH = ensured.localPath;

  const result = await tokenizeText(text);

  if (result.error) {
    console.error("[api/tokenize]", {
      requestId,
      status: 500,
      error: result.error.code,
    });
    return res.status(500).json(result);
  }

  console.info("[api/tokenize]", {
    requestId,
    status: 200,
    count: result.count,
  });
  return res.status(200).json(result);
}
