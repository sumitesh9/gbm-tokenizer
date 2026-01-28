import type { NextApiRequest, NextApiResponse } from "next";
import { ensureGbmModelDownloaded } from "../../utils/azureModel";
import { getSentencePiece } from "../../utils/spTokenizer";

type TokenizeErrorCode =
  | "MODEL_NOT_READY"
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

async function tokenizeText(text: string, modelPath: string): Promise<TokenizeResponse> {
  try {
    const spp = await getSentencePiece(modelPath);
    const ids = spp.encodeIds(text);
    const tokens = spp.encodePieces(text);
    return { tokens, ids, count: tokens.length };
  } catch {
    return { tokens: [], ids: [], count: 0, error: { code: "TOKENIZE_FAILED" } };
  }
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

  const result = await tokenizeText(text, ensured.localPath);

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
