# GBM Tokenizer

A SentencePiece unigram tokenizer optimized for Garhwali (GBM - ISO 639-3), handling Devanagari script with mixed-language support.

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

| Tokenizer | Vocab Size | Compression | Accuracy | Avg Tokens/Text |
|-----------|------------|-------------|----------|-----------------|
| **GBM Tokenizer** ⭐ | 2,450 | 1.63x | 77.0% | 12.0 |
| GPT-4/Claude | 100,256 | 2.63x | 100.0% | 7.4 |
| BERT | 30,522 | 2.82x | 24.3% | 6.9 |
| GPT-2 | 50,257 | 2.10x | 100.0% | 9.3 |
| Character-level | N/A | 1.00x | 100.0% | 19.5 |

*Results from evaluation on 152 test cases covering Devanagari, English, mixed content, numbers, Unicode, and edge cases.*

### Key Highlights

- 📦 **Compact vocabulary** - 2,450 tokens vs 30K+ for general-purpose tokenizers
- 🎯 **Optimized for Garhwali** - Trained on domain-specific corpus (621K+ lines)
- ⚡ **Efficient tokenization** - 12 tokens per text on average
- 🔄 **Good compression** - 1.63x characters per token

## Configuration

Edit `train.py` to customize:
- `vocab_size`: Vocabulary size (default: 130)
- `model_type`: `"unigram"` or `"bpe"` (default: `"unigram"`)
- `character_coverage`: Coverage ratio (default: 1.0)

**Rule of thumb**: `vocab_size ≈ 2 × (unique characters)`

## Project Structure

```
gbm-tokenizer/
├── train.py              # Training script
├── infer.py              # Inference & verification
├── eval.py               # Evaluation & comparison
├── generate_chart.py     # Chart generation
├── corpus.txt            # Training data
├── eval.txt              # Test cases (239 samples)
└── gbm_tokenizer.model   # Trained model (gitignored)
```

## License

Public domain ([Unlicense](LICENSE)) - use freely without attribution.

## Contributing

Open a PR with clear description of changes. Keep it focused and explain your reasoning.

## References

- [SentencePiece](https://github.com/google/sentencepiece)
- [ISO 639-3: GBM](https://iso639-3.sil.org/code/gbm)
