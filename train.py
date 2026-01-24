import sentencepiece as spm
import os

def train_tokenizer(
    input_file="corpus.txt",
    model_prefix="gbm_tokenizer",
    vocab_size=128000,
    model_type="unigram",
    character_coverage=1.0
):
    """Train a SentencePiece tokenizer."""
    
    # Ensure input file exists
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    # Training arguments
    # Note: byte_fallback=True is important for round-trip of rare characters
    args = (
        f"--input={input_file} "
        f"--model_prefix={model_prefix} "
        f"--vocab_size={vocab_size} "
        f"--model_type={model_type} "
        f"--character_coverage={character_coverage} "
        f"--byte_fallback=true "  # Enable byte fallback for 100% coverage
        f"--normalization_rule_name=nmt_nfkc " # Standard normalization
        f"--remove_extra_whitespaces=false " # Preserve whitespace
        f"--pad_id=0 --unk_id=1 --bos_id=2 --eos_id=3 "
    )
    
    print(f"Training tokenizer with args: {args}")
    spm.SentencePieceTrainer.train(args)
    print(f"Tokenizer trained. Model saved to {model_prefix}.model")

if __name__ == "__main__":
    # Check if corpus.txt exists
    if not os.path.exists("corpus.txt"):
        print("Error: corpus.txt not found. Please provide a training corpus.")
    else:
        # Calculate optimal vocab size based on unique characters
        with open("corpus.txt", "r", encoding="utf-8") as f:
            text = f.read()
            unique_chars = sorted(list(set(text)))
            print(f"Number of unique characters: {len(unique_chars)}")
            # print(f"Unique characters: {''.join(unique_chars)}")
            
        train_tokenizer()
