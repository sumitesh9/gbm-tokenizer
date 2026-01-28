# UI (Next.js)

Single-page tokenizer UI for the **GBM SentencePiece** model.

## Local development

```bash
cd ui
npm install
npm run dev
```

Open `http://localhost:3000`.

## How tokenization works (security)

- The browser calls `POST /api/tokenize`.
- Tokenization runs **server-side** (Node spawns `tokenize_api.py`).

## Model file (not in git)

The `.model` file is gitignored. In deployment, the server **downloads it from Azure Blob Storage** (and caches it locally on the server).

Set these environment variables:

- `AZURE_STORAGE_CONNECTION_STRING`
- `AZURE_MODELS_CONTAINER`
- `GBM_TOKENIZER_BLOB_NAME` (e.g. `gbm_tokenizer.model`)

Optional:

- `GBM_TOKENIZER_MODEL_PATH` (override the local cache path)

See `.env.example`.

