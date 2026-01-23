# GBM Tokenizer

A SentencePiece unigram tokenizer trained for Garhwali (GBM - ISO 639-3), a language spoken in the Uttarakhand region of India. This tokenizer is optimized for handling Devanagari script text with support for mixed-language content.

## Features

- **Unigram Model**: Uses SentencePiece's unigram algorithm for subword tokenization
- **Devanagari Script Support**: Optimized for Hindi, Garhwali, and Kumaoni languages
- **Comprehensive Evaluation**: Includes evaluation against popular tokenizers (GPT-2, GPT-4, BERT)
- **Diverse Test Cases**: Extensive evaluation suite covering multiple character sets and edge cases
- **Round-trip Verification**: Validates encoding/decoding accuracy

## Installation

1. Clone the repository:
```bash
git clone https://github.com/sumitesh9/gbm-tokenizer
cd gbm-tokenizer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
make install
```

Or manually:
```bash
pip install -r requirements.txt
```

## Requirements

- Python 3.x
- sentencepiece
- datasets
- tiktoken (for comparison with GPT tokenizers)
- transformers (for comparison with BERT)

## Usage

### Training the Tokenizer

Train a new tokenizer model using your corpus:

```bash
make train
```

This will:
- Read text from `corpus.txt`
- Train a SentencePiece unigram model
- Generate `gbm_tokenizer.model` and `gbm_tokenizer.vocab`

**Training Configuration** (in `train.py`):
- Model type: `unigram`
- Vocabulary size: 130 (configurable)
- Character coverage: 1.0
- BOS/EOS tokens: Disabled

### Running Inference

Test the tokenizer on sample text:

```bash
make infer
```

This will:
- Load the trained model
- Encode sample text to tokens and IDs
- Decode back to verify round-trip accuracy

You can modify `infer.py` to test with your own text.

### Evaluating the Tokenizer

Run comprehensive evaluation:

```bash
make eval
```

This will:
- Evaluate the tokenizer on test cases from `eval.txt`
- Calculate metrics (compression ratio, accuracy, vocabulary stats)
- Compare performance against popular tokenizers:
  - GPT-2 (tiktoken)
  - GPT-4/Claude (cl100k_base)
  - BERT (bert-base-uncased)
  - Character-level baseline

### Other Commands

```bash
make help      # Show all available commands
make clean     # Remove Python cache files
make activate  # Activate virtual environment in interactive shell
```

## Project Structure

```
gbm-tokenizer/
├── train.py           # Training script
├── infer.py           # Inference and verification script
├── eval.py            # Comprehensive evaluation script
├── corpus.txt         # Training corpus (Devanagari text)
├── eval.txt           # Evaluation test cases
├── requirements.txt   # Python dependencies
├── Makefile           # Build automation
├── .gitignore         # Git ignore rules
├── README.md          # This file
└── gbm_tokenizer.model # Trained model (generated, gitignored)
    gbm_tokenizer.vocab # Vocabulary file (generated, gitignored)
```

## Evaluation

The `eval.txt` file contains diverse test cases covering:

- **Devanagari Script**: Hindi, Garhwali, Kumaoni text
- **English Text**: Standard English sentences
- **Mixed Content**: Devanagari + English
- **Numbers**: Various number formats and mathematical notation
- **Punctuation**: Common punctuation marks
- **Unicode**: Special characters, symbols, emojis
- **Code-like Strings**: Programming code snippets
- **URLs and Paths**: Various URL and file path formats
- **Edge Cases**: Whitespace, repeated characters, very short strings
- **Multi-language**: Chinese, Japanese, Korean, Arabic, Cyrillic, Greek

## Metrics

The evaluation script reports:

- **Vocabulary Size**: Number of tokens in the vocabulary
- **Compression Ratio**: Average characters per token (higher is better)
- **Round-trip Accuracy**: Percentage of texts that decode correctly
- **Token Statistics**: Average, min, max token lengths
- **Most Common Tokens**: Top 10 most frequent tokens

## Comparison with Other Tokenizers

The evaluation automatically compares your tokenizer against:

| Tokenizer | Vocab Size | Use Case |
|-----------|------------|----------|
| GBM Tokenizer (Custom) | 130 | Optimized for Garhwali |
| GPT-2 | 50,257 | General purpose English |
| GPT-4/Claude | 100,256 | General purpose multilingual |
| BERT | 30,522 | English NLP tasks |
| Character-level | N/A | Baseline comparison |

## Configuration

### Training Parameters

Edit `train.py` to adjust:

- `vocab_size`: Vocabulary size (default: 130)
- `model_type`: `"unigram"` or `"bpe"` (default: `"unigram"`)
- `character_coverage`: Character coverage ratio (default: 1.0)
- `bos_id`/`eos_id`: Begin/End of sentence tokens (default: -1, disabled)

### Rule of Thumb

For vocabulary size: `vocab_size ≈ 2 × (number of unique characters)`

## License

This project is released into the public domain under the [Unlicense](LICENSE). You are free to use, modify, distribute, and commercialize this software without any restrictions or attribution requirements.

## Contributing

Contributions are welcome! To make changes:

1. Create a pull request with your proposed changes
2. Include a clear description of what you're changing and why
3. Keep PRs focused and semi-elaborative (explain the reasoning behind changes)

That's it! No formal process required.

## References

- [SentencePiece](https://github.com/google/sentencepiece)
- [ISO 639-3: GBM (Garhwali)](https://iso639-3.sil.org/code/gbm)
