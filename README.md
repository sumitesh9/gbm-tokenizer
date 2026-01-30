# GBM Tokenizer

A SentencePiece unigram tokenizer optimized for Garhwali (GBM - ISO 639-3), handling Devanagari script with mixed-language support.

**Pre-trained tokenizer (gated access):** [somu9/gbm-tokenizer](https://huggingface.co/somu9/gbm-tokenizer) on Hugging Face.

## Quick Start

```bash
git clone https://github.com/sumitesh9/gbm-tokenizer
cd gbm-tokenizer
python -m venv venv && source venv/bin/activate
make install
make train
make eval
```

## Usage

| Command | Description |
|---------|-------------|
| `make train` | Train tokenizer from `corpus.txt` |
| `make infer` | Test tokenizer on sample text |
| `make eval` | Evaluate and compare with other tokenizers |
| `make chart` | Generate comparison charts |

## Evaluation Results

### Performance Comparison

![Tokenizer Comparison](tokenizer_comparison.png)

### Metrics

| Tokenizer | Vocab Size | Compression | Accuracy | Fertility | Speed |
|-----------|------------|-------------|----------|-----------|-------|
| **GBM Tokenizer** ⭐ | 128,000 | 2.66x | 98.5% | 2.11 | ~2.2M t/s |
| GPT-4o (o200k) | 199,998 | 2.93x | 100.0% | 1.92 | ~1.2M t/s |
| Gemma 3 | 262,144 | 3.06x | 100.0% | 1.84 | ~0.5M t/s |
| Llama 3 | 128,000 | 2.51x | 99.5% | 2.24 | ~0.4M t/s |
| GPT-4/Claude | 100,256 | 1.77x | 100.0% | 3.18 | ~1.6M t/s |
| Sarvam-1 | 68,096 | 2.31x | 100.0% | 2.44 | ~0.6M t/s |
| BERT | 30,522 | 2.27x | 18.2% | 2.48 | ~0.4M t/s |
| GPT-2 | 50,257 | 1.31x | 100.0% | 4.30 | ~1.8M t/s |
| Character-level | N/A | 1.00x | 100.0% | 5.63 | ~53M t/s |

*Results from evaluation on 152 test cases covering Devanagari, English, mixed content, numbers, Unicode, and edge cases.*

> **Note**: These metrics are generated using the specific test set in `eval.txt` (approx. 238 lines of mixed English/Garhwali/Code/Math). Performance characteristics (especially compression and fertility) will vary on different corpora. Speed benchmarks are hardware-dependent.

### Hardware Configuration

Benchmarks were run on the following system:
- **OS**: macOS (Darwin 24.6.0)
- **Environment**: Python 3.11, Single-threaded execution
- **Hardware**: Apple Silicon (M-series)

### Key Highlights

- 📦 **Comprehensive vocabulary** - 128,000 tokens matching modern LLM standards
- 🎯 **Optimized for Garhwali** - Trained on domain-specific corpus (621K+ lines)
- ⚡ **Efficient tokenization** - 2.11 tokens per word (vs 1.92 for GPT-4o)
- 🔄 **Excellent compression** - 2.66x characters per token
- 🏎️ **High Performance** - ~2.2M tokens/sec encoding speed on CPU (~2x faster than GPT-4o)

## Configuration

Edit `train.py` to customize:
- `vocab_size`: Vocabulary size (default: 128000)
- `model_type`: `"unigram"` or `"bpe"` (default: `"unigram"`)
- `character_coverage`: Coverage ratio (default: 1.0)

**Rule of thumb**: `vocab_size ≈ 5× to 10× (unique characters)` for better fertility (lower tokens/word).

## Project Structure

```
gbm-tokenizer/
├── train.py              # Training script
├── infer.py              # Inference & verification
├── eval.py               # Evaluation & comparison
├── generate_chart.py     # Chart generation
├── corpus.txt            # Training data
├── eval.txt              # Test cases (238 samples)
└── gbm_tokenizer.model   # Trained model (gitignored)
```

## UI (Next.js)

There is a single-page Next.js UI in `ui/` that tokenizes text via a server-side API route (the SentencePiece model is **never** sent to the browser).

- **Run locally**

```bash
cd ui
npm install
npm run dev
```

- **Model file in deployment**
  - The `.model` file is gitignored; in production the server downloads it from **Azure Blob Storage** at runtime.
  - Configure `AZURE_STORAGE_CONNECTION_STRING`, `AZURE_MODELS_CONTAINER`, and `GBM_TOKENIZER_BLOB_NAME` (see `ui/.env.example`).

## License

Public domain ([Unlicense](LICENSE)) - use freely without attribution.

## Contributing

Open a PR with clear description of changes. Keep it focused and explain your reasoning.

## References

- [SentencePiece](https://github.com/google/sentencepiece)
- [ISO 639-3: GBM](https://iso639-3.sil.org/code/gbm)
