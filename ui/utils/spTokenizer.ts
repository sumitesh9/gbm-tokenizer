import { SentencePieceProcessor } from "@sctg/sentencepiece-js";

let sppPromise: Promise<SentencePieceProcessor> | null = null;
let loadedModelPath: string | null = null;

/**
 * Load and cache SentencePieceProcessor for a given model path.
 * Keeps the model server-side only.
 */
export async function getSentencePiece(modelPath: string): Promise<SentencePieceProcessor> {
  if (sppPromise && loadedModelPath === modelPath) return sppPromise;

  loadedModelPath = modelPath;
  sppPromise = (async () => {
    const spp = new SentencePieceProcessor();
    await spp.load(modelPath);
    return spp;
  })();

  return sppPromise;
}

