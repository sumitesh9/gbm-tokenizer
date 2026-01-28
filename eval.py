import sentencepiece as spm
import os
import json
import time
import platform
import multiprocessing
from collections import Counter
# Try to import optional dependencies
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

try:
    from transformers import AutoTokenizer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class TokenizerWrapper:
    """Wrapper class to provide unified interface for different tokenizers."""

    def __init__(self, name, tokenizer, vocab_size=None, tokenizer_type="sentencepiece"):
        self.name = name
        self.tokenizer = tokenizer
        self._vocab_size = vocab_size
        self.tokenizer_type = tokenizer_type

    def encode(self, text, out_type=str):
        """Encode text to tokens."""
        if self.tokenizer_type == "sentencepiece":
            return self.tokenizer.encode(text, out_type=out_type)
        elif self.tokenizer_type == "tiktoken":
            ids = self.tokenizer.encode(text, allowed_special="all")
            if out_type is str:
                # For tiktoken, return byte string representations
                # Each token is decoded individually to show what it represents
                return [self.tokenizer.decode([id]) for id in ids]
            else:
                return ids
        elif self.tokenizer_type == "transformers":
            if out_type is str:
                return self.tokenizer.tokenize(text)
            else:
                return self.tokenizer.encode(text, add_special_tokens=False)
        elif self.tokenizer_type == "character":
            if out_type is str:
                return list(text)
            else:
                return [ord(c) for c in text]
        else:
            raise ValueError(f"Unknown tokenizer type: {self.tokenizer_type}")

    def decode(self, tokens):
        """Decode tokens back to text."""
        if not tokens:
            return ""

        if self.tokenizer_type == "sentencepiece":
            return self.tokenizer.decode(tokens)
        elif self.tokenizer_type == "tiktoken":
            if isinstance(tokens[0], str):
                # For tiktoken, string tokens are actually byte representations
                # We need to reconstruct from the original encoding
                # This is a limitation - tiktoken works best with IDs
                # Try to encode each token string and get IDs
                ids = []
                for token_str in tokens:
                    try:
                        # Encode the token string to get its ID
                        token_ids = self.tokenizer.encode(
                            token_str, allowed_special="all")
                        if token_ids:
                            ids.extend(token_ids)
                    except Exception:
                        pass
                return self.tokenizer.decode(ids) if ids else ''.join(tokens)
            else:
                return self.tokenizer.decode(tokens)
        elif self.tokenizer_type == "transformers":
            if isinstance(tokens[0], str):
                return self.tokenizer.convert_tokens_to_string(tokens)
            else:
                return self.tokenizer.decode(tokens, skip_special_tokens=True)
        elif self.tokenizer_type == "character":
            if isinstance(tokens[0], str):
                return ''.join(tokens)
            else:
                return ''.join(chr(t) if t < 0x110000 else '?' for t in tokens)
        else:
            raise ValueError(f"Unknown tokenizer type: {self.tokenizer_type}")

    def get_vocab_size(self):
        """Get vocabulary size."""
        if self._vocab_size:
            return self._vocab_size
        if self.tokenizer_type == "sentencepiece":
            return self.tokenizer.get_piece_size()
        elif self.tokenizer_type == "tiktoken":
            return len(self.tokenizer._mergeable_ranks) if hasattr(self.tokenizer, '_mergeable_ranks') else 0
        elif self.tokenizer_type == "transformers":
            return self.tokenizer.vocab_size if hasattr(self.tokenizer, 'vocab_size') else 0
        elif self.tokenizer_type == "character":
            return 0  # Character-level has no fixed vocab
        else:
            return 0


def load_tokenizer(model_path="gbm_tokenizer.model"):
    """Load the trained tokenizer model."""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Tokenizer model not found: {model_path}")

    sp = spm.SentencePieceProcessor()
    sp.load(model_path)
    return TokenizerWrapper("GBM Tokenizer (Custom)", sp, tokenizer_type="sentencepiece")


def load_comparison_tokenizers():
    """Load popular tokenizers for comparison."""
    tokenizers = []

    # Character-level tokenizer (baseline)
    class CharTokenizer:
        pass
    tokenizers.append(TokenizerWrapper("Character-level (Baseline)",
                      CharTokenizer(), vocab_size=0, tokenizer_type="character"))

    # GPT-2 tokenizer (tiktoken)
    if TIKTOKEN_AVAILABLE:
        try:
            gpt2_tokenizer = tiktoken.get_encoding("gpt2")
            tokenizers.append(TokenizerWrapper(
                "GPT-2 (tiktoken)", gpt2_tokenizer, vocab_size=50257, tokenizer_type="tiktoken"))
        except Exception as e:
            print(f"  Warning: Could not load GPT-2 tokenizer: {e}")

    # GPT-4 tokenizer (cl100k_base)
    if TIKTOKEN_AVAILABLE:
        try:
            gpt4_tokenizer = tiktoken.get_encoding("cl100k_base")
            tokenizers.append(TokenizerWrapper("GPT-4/Claude (cl100k_base)",
                              gpt4_tokenizer, vocab_size=100256, tokenizer_type="tiktoken"))
        except Exception as e:
            print(f"  Warning: Could not load GPT-4 tokenizer: {e}")

    # GPT-4o tokenizer (o200k_base)
    if TIKTOKEN_AVAILABLE:
        try:
            gpt4o_tokenizer = tiktoken.get_encoding("o200k_base")
            tokenizers.append(TokenizerWrapper(
                "GPT-4o (o200k_base)", gpt4o_tokenizer, vocab_size=199998, tokenizer_type="tiktoken"))
        except Exception as e:
            print(f"  Warning: Could not load GPT-4o tokenizer: {e}")

    # HuggingFace tokenizers
    if TRANSFORMERS_AVAILABLE:
        try:
            bert_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
            tokenizers.append(TokenizerWrapper("BERT (bert-base-uncased)",
                              bert_tokenizer, vocab_size=30522, tokenizer_type="transformers"))
        except Exception as e:
            print(f"  Warning: Could not load BERT tokenizer: {e}")

        # Llama 3 Tokenizer
        try:
            # Try loading Llama 3 tokenizer (might require login/token)
            llama_tokenizer = AutoTokenizer.from_pretrained(
                "meta-llama/Meta-Llama-3-8B")
            tokenizers.append(TokenizerWrapper(
                "Llama 3 (Meta-Llama-3-8B)", llama_tokenizer, tokenizer_type="transformers"))
        except Exception as e:
            print(
                f"  Warning: Could not load Llama 3 tokenizer (check HF login/token): {e}")

        # Gemma 3 Tokenizer
        try:
            gemma_tokenizer = AutoTokenizer.from_pretrained(
                "google/gemma-3-1b-it")
            tokenizers.append(TokenizerWrapper(
                "Gemma 3 (google/gemma-3-1b-it)", gemma_tokenizer, tokenizer_type="transformers"))
        except Exception as e:
            print(f"  Warning: Could not load Gemma 3 tokenizer: {e}")

        # Sarvam-1 tokenizer
        sarvam_tokenizer = None
        try:
            sarvam_tokenizer = AutoTokenizer.from_pretrained(
                "sarvamai/sarvam-1")
        except Exception:
            # Some HF tokenizers/models require this for custom code.
            try:
                sarvam_tokenizer = AutoTokenizer.from_pretrained(
                    "sarvamai/sarvam-1", trust_remote_code=True)
            except Exception as e2:
                print(f"  Warning: Could not load Sarvam-1 tokenizer: {e2}")

        if sarvam_tokenizer is not None:
            tokenizers.append(
                TokenizerWrapper(
                    "Sarvam-1 (sarvamai/sarvam-1)",
                    sarvam_tokenizer,
                    tokenizer_type="transformers",
                )
            )

    return tokenizers


def evaluate_round_trip(tokenizer, texts):
    """Evaluate round-trip encoding/decoding accuracy."""
    correct = 0
    total = len(texts)

    # Check for normalization if using SentencePiece
    is_sp = tokenizer.tokenizer_type == "sentencepiece"

    for text in texts:
        try:
            # Use IDs for more reliable round-trip checking
            ids = tokenizer.encode(text, out_type=int)
            decoded = tokenizer.decode(ids)

            # For SentencePiece, we might need to normalize the input text
            # to match what the tokenizer does internally
            if is_sp and decoded != text:
                # If strict match fails, check if it's just normalization
                # SentencePiece usually applies NFKC normalization by default
                import unicodedata
                normalized_text = unicodedata.normalize('NFKC', text)
                if decoded == normalized_text:
                    # It's a match after normalization!
                    correct += 1
                    continue

            if decoded == text:
                correct += 1
            else:
                # Debug failures (optional)
                pass

        except Exception:
            pass  # Skip if encoding fails

    accuracy = (correct / total) * 100 if total > 0 else 0
    return accuracy, correct, total


def calculate_compression_ratio(tokenizer, texts):
    """Calculate compression ratio (characters vs tokens)."""
    total_chars = 0
    total_tokens = 0

    for text in texts:
        try:
            total_chars += len(text)
            tokens = tokenizer.encode(text, out_type=str)
            total_tokens += len(tokens)
        except Exception:
            pass  # Skip if encoding fails

    if total_tokens == 0:
        return 0, total_chars, 0

    ratio = total_chars / total_tokens
    return ratio, total_chars, total_tokens


def analyze_vocabulary(tokenizer):
    """Analyze the tokenizer vocabulary."""
    vocab_size = tokenizer.get_vocab_size()
    return vocab_size


def evaluate_on_corpus(corpus_path="eval.txt"):
    """Evaluate tokenizer on the evaluation test cases."""
    if not os.path.exists(corpus_path):
        print(f"Warning: Evaluation file not found: {corpus_path}")
        # Fallback to corpus.txt if eval.txt doesn't exist
        if corpus_path == "eval.txt" and os.path.exists("corpus.txt"):
            print("  Falling back to corpus.txt...")
            corpus_path = "corpus.txt"
        else:
            return None

    with open(corpus_path, 'r', encoding='utf-8') as f:
        # Skip comment lines (starting with #) and empty lines
        lines = [line.strip() for line in f if line.strip()
                 and not line.strip().startswith('#')]

    if not lines:
        print("Warning: Evaluation file is empty or contains only comments")
        return None

    return lines


def evaluate_tokenizer(tokenizer, texts):
    """Evaluate a single tokenizer and return metrics."""
    try:
        vocab_size = analyze_vocabulary(tokenizer)
        accuracy, correct, total = evaluate_round_trip(tokenizer, texts)
        ratio, total_chars, total_tokens = calculate_compression_ratio(
            tokenizer, texts)

        # Calculate tokens per word (Fertility) and Speed
        total_words = 0
        start_time = time.time()
        token_counts = []

        for text in texts:
            # Simple word count (whitespace split)
            total_words += len(text.split())
            try:
                tokens = tokenizer.encode(text, out_type=str)
                token_counts.append(len(tokens))
            except Exception:
                pass

        end_time = time.time()
        duration = end_time - start_time

        # Avoid division by zero
        avg_tokens = sum(token_counts) / \
            len(token_counts) if token_counts else 0
        fertility = total_tokens / total_words if total_words > 0 else 0
        speed = total_tokens / duration if duration > 0 else 0

        return {
            'name': tokenizer.name,
            'vocab_size': vocab_size,
            'accuracy': accuracy,
            'compression_ratio': ratio,
            'fertility': fertility,
            'speed': speed,
            'total_tokens': total_tokens,
            'avg_tokens_per_text': avg_tokens,
            'success': True
        }
    except Exception as e:
        return {
            'name': tokenizer.name,
            'error': str(e),
            'success': False
        }


def print_system_info():
    """Print system information for reproducibility."""
    print("=" * 60)
    print("SYSTEM CONFIGURATION")
    print("=" * 60)
    print(f"OS: {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"Python: {platform.python_version()}")
    print(f"CPU Cores: {multiprocessing.cpu_count()}")
    print("=" * 60)
    print()


def print_statistics(tokenizer, texts):
    """Print comprehensive statistics about the tokenizer."""
    print_system_info()
    print("=" * 60)
    print("TOKENIZER EVALUATION REPORT")
    print("=" * 60)

    # Vocabulary analysis
    vocab_size = analyze_vocabulary(tokenizer)
    print("\n📚 Vocabulary Statistics:")
    print(f"  - Vocabulary size: {vocab_size:,}")
    print("  - Model file: gbm_tokenizer.model")

    # Round-trip accuracy
    accuracy, correct, total = evaluate_round_trip(tokenizer, texts)
    print("\n✅ Round-trip Accuracy:")
    print(f"  - Accuracy: {accuracy:.2f}% ({correct}/{total})")

    # Compression analysis
    ratio, total_chars, total_tokens = calculate_compression_ratio(
        tokenizer, texts)

    # Calculate fertility for detailed report
    total_words = sum(len(t.split()) for t in texts)
    fertility = total_tokens / total_words if total_words > 0 else 0

    print("\n📊 Compression & Efficiency Statistics:")
    print(f"  - Total characters: {total_chars:,}")
    print(f"  - Total tokens: {total_tokens:,}")
    print(f"  - Compression ratio: {ratio:.2f}x (higher is better)")
    print(f"  - Fertility: {fertility:.2f} tokens/word (lower is better)")
    print(f"  - Average chars per token: {ratio:.2f}")

    # Token distribution
    all_tokens = []
    token_lengths = []
    for text in texts:
        try:
            tokens = tokenizer.encode(text, out_type=str)
            all_tokens.extend(tokens)
            token_lengths.extend([len(token) for token in tokens])
        except Exception:
            pass

    if token_lengths:
        avg_token_len = sum(token_lengths) / len(token_lengths)
        max_token_len = max(token_lengths)
        min_token_len = min(token_lengths)

        print("\n🔤 Token Length Statistics:")
        print(f"  - Average token length: {avg_token_len:.2f} characters")
        print(f"  - Min token length: {min_token_len}")
        print(f"  - Max token length: {max_token_len}")

    # Most common tokens
    if all_tokens:
        token_counts = Counter(all_tokens)
        print("\n🏆 Top 10 Most Common Tokens:")
        for token, count in token_counts.most_common(10):
            display_token = repr(token) if len(token) > 20 else token
            print(f"  - {display_token}: {count:,} occurrences")

    # Sample encoding
    print("\n📝 Sample Encoding (first 3 lines):")
    for i, text in enumerate(texts[:3], 1):
        try:
            tokens = tokenizer.encode(text, out_type=str)
            ids = tokenizer.encode(text, out_type=int)
            decoded = tokenizer.decode(tokens)

            print(f"\n  Sample {i}:")
            print(
                f"    Original: {text[:80]}{'...' if len(text) > 80 else ''}")
            print(
                f"    Tokens ({len(tokens)}): {tokens[:10]}{'...' if len(tokens) > 10 else ''}")
            print(
                f"    IDs ({len(ids)}): {ids[:10]}{'...' if len(ids) > 10 else ''}")
            print(
                f"    Decoded: {decoded[:80]}{'...' if len(decoded) > 80 else ''}")
            print(f"    Match: {'✓' if decoded == text else '✗'}")
        except Exception as e:
            print(f"  Sample {i}: Error encoding - {e}")

    print("\n" + "=" * 60)


def print_comparison(results):
    """Print comparison table of all tokenizers."""
    print("\n" + "=" * 80)
    print("TOKENIZER COMPARISON")
    print("=" * 80)

    # Filter successful results
    successful = [r for r in results if r.get('success', False)]

    if not successful:
        print("No tokenizers could be evaluated successfully.")
        return

    # Sort by compression ratio (higher is better)
    successful.sort(key=lambda x: x.get('compression_ratio', 0), reverse=True)

    # Print header
    print(f"\n{'Tokenizer':<30} {'Vocab':<8} {'Comp':<7} {'Acc':<7} {'Fertility':<10} {'Speed':<10}")
    print("-" * 80)

    # Print each tokenizer
    for result in successful:
        name = result['name']
        vocab = f"{result['vocab_size']:,}" if result['vocab_size'] > 0 else "N/A"
        comp = f"{result['compression_ratio']:.2f}x"
        acc = f"{result['accuracy']:.1f}%"
        fert = f"{result.get('fertility', 0):.2f}"
        speed = f"{result.get('speed', 0):.0f} t/s"

        # Highlight our tokenizer
        marker = " ⭐" if "GBM" in name else ""
        print(f"{name:<30}{vocab:<8}{comp:<7}{acc:<7}{fert:<10}{speed:<10}{marker}")

    # Print failed tokenizers
    failed = [r for r in results if not r.get('success', False)]
    if failed:
        print("\n⚠️  Failed to evaluate:")
        for result in failed:
            print(
                f"  - {result['name']}: {result.get('error', 'Unknown error')}")

    # Find best performers
    if successful:
        best_compression = max(
            successful, key=lambda x: x.get('compression_ratio', 0))
        best_accuracy = max(successful, key=lambda x: x.get('accuracy', 0))

        print("\n🏆 Best Performance:")
        print(
            f"  - Best Compression: {best_compression['name']} ({best_compression['compression_ratio']:.2f}x)")
        print(
            f"  - Best Accuracy: {best_accuracy['name']} ({best_accuracy['accuracy']:.1f}%)")

    print("\n" + "=" * 80)


def main():
    """Main evaluation function."""
    print("Loading GBM tokenizer...")
    try:
        gbm_tokenizer = load_tokenizer()
        print("✓ GBM Tokenizer loaded successfully")
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        print("Please train the tokenizer first using: make train")
        return

    print("\nLoading evaluation test cases...")
    texts = evaluate_on_corpus()

    if texts is None:
        print("Using sample text for evaluation...")
        texts = ["नमस्कार मेरु नाम सुमितेश च"]

    print(f"✓ Loaded {len(texts)} test cases for evaluation\n")

    # Run evaluation on GBM tokenizer
    print_statistics(gbm_tokenizer, texts)

    # Load and compare with other tokenizers
    print("\n" + "=" * 80)
    print("Loading comparison tokenizers...")
    print("=" * 80)
    comparison_tokenizers = load_comparison_tokenizers()
    print(f"✓ Loaded {len(comparison_tokenizers)} comparison tokenizers")

    # Evaluate all tokenizers
    print("\nEvaluating all tokenizers...")
    results = []

    # Evaluate GBM tokenizer
    gbm_result = evaluate_tokenizer(gbm_tokenizer, texts)
    results.append(gbm_result)

    # Evaluate comparison tokenizers
    for tokenizer in comparison_tokenizers:
        print(f"  Evaluating {tokenizer.name}...")
        result = evaluate_tokenizer(tokenizer, texts)
        results.append(result)

    # Print comparison
    print_comparison(results)

    # Save results to JSON for chart generation
    try:
        with open('eval_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        print("\n💾 Results saved to eval_results.json (use generate_chart.py to create charts)")
    except Exception as e:
        print(f"\n⚠️  Could not save results to JSON: {e}")

    print("\n✓ Evaluation complete!")


if __name__ == "__main__":
    main()
