#!/usr/bin/env python3
"""
Upload the GBM SentencePiece tokenizer to Hugging Face Hub.

Creates a public model repo and uploads tokenizer files. Enable gated access
in the repo Settings on the Hub after upload (see README or HUGGINGFACE.md).
"""

import argparse
import io
import os

from dotenv import load_dotenv
from huggingface_hub import HfApi, create_repo, login

load_dotenv()


# Default model card for the Hub (with optional gated metadata in YAML)
MODEL_CARD_TEMPLATE = """---
license: unlicense
language:
  - gbm
  - hi
  - en
tags:
  - tokenizer
  - sentencepiece
  - garhwali
  - devanagari
library_name: sentencepiece
gated: true
extra_gated_heading: "Request access to the GBM tokenizer"
extra_gated_description: "By agreeing you share your Hugging Face username and email with the model authors."
extra_gated_button_content: "Agree and send request"
---

# GBM Tokenizer

A **SentencePiece unigram** tokenizer optimized for **Garhwali (GBM - ISO 639-3)**, a Central Pahari language of Uttarakhand, India. It handles **Devanagari** script and mixed Garhwali–English text, suitable for language modeling, MT, and NLP on Garhwali corpora.

## Key highlights

- **128,000 tokens** — Vocabulary size aligned with modern LLM tokenizers (e.g. Llama 3).
- **Optimized for Garhwali** — Trained on a domain-specific corpus (621K+ lines).
- **Efficient tokenization** — ~2.11 tokens per word (comparable to GPT-4o’s ~1.92).
- **Strong compression** — ~2.66× characters per token.
- **Fast** — ~2.2M tokens/sec encoding on CPU (single-threaded, Apple Silicon).

## Model details

| Property | Value |
|----------|--------|
| Vocab size | 128,000 |
| Model type | Unigram (SentencePiece) |
| Scripts | Devanagari, Latin |
| Special tokens | `pad_id=0`, `unk_id=1`, `bos_id=2`, `eos_id=3` |
| Normalization | NMT NFKC, byte fallback for full coverage |
| Max piece length | 20 |
| License | Unlicense (public domain) |

## Evaluation (comparison)

Benchmarks on 152 test cases (Devanagari, English, mixed, code, math):

| Tokenizer | Vocab size | Compression | Round-trip accuracy | Fertility (tokens/word) | Speed |
|-----------|------------|--------------|----------------------|-------------------------|-------|
| **GBM Tokenizer** | 128,000 | 2.66× | 98.5% | 2.11 | ~2.2M t/s |
| GPT-4o (o200k) | 199,998 | 2.93× | 100% | 1.92 | ~1.2M t/s |
| Gemma 3 | 262,144 | 3.06× | 100% | 1.84 | ~0.5M t/s |
| Llama 3 | 128,000 | 2.51× | 99.5% | 2.24 | ~0.4M t/s |
| GPT-4/Claude | 100,256 | 1.77× | 100% | 3.18 | ~1.6M t/s |
| Sarvam-1 | 68,096 | 2.31× | 100% | 2.44 | ~0.6M t/s |

*Metrics are from the project’s `eval.txt` test set; speed is hardware-dependent (e.g. Apple Silicon).*

## Usage

### With SentencePiece (Python)

```python
import sentencepiece as spm

sp = spm.SentencePieceProcessor()
sp.load("gbm_tokenizer.model")  # or path from hf_hub_download

tokens = sp.encode("गढ़वळि पाठ", out_type=str)
ids = sp.encode("गढ़वळि पाठ", out_type=int)
decoded = sp.decode(ids)
```

### Download from Hub (gated — request access first)

```python
from huggingface_hub import hf_hub_download
import sentencepiece as spm

path = hf_hub_download(repo_id="{repo_id}", filename="gbm_tokenizer.model")
sp = spm.SentencePieceProcessor()
sp.load(path)
```

## Training

- **Algorithm**: SentencePiece unigram with default splitting (Unicode script, whitespace, numbers).
- **Corpus**: Garhwali-focused text; configurable via the [training repo](https://github.com/sumitesh9/gbm-tokenizer) (`train.py`, `corpus.txt`).

## References

- [SentencePiece](https://github.com/google/sentencepiece)
- [ISO 639-3: GBM (Garhwali)](https://iso639-3.sil.org/code/gbm)
- [Project: gbm-tokenizer](https://github.com/sumitesh9/gbm-tokenizer)
"""


def get_model_card(repo_id: str) -> str:
    return MODEL_CARD_TEMPLATE.format(repo_id=repo_id)


def upload(
    repo_id: str,
    tokenizer_dir: str = ".",
    private: bool = False,
    token: str | None = None,
    create_repo_if_missing: bool = True,
) -> None:
    """Upload tokenizer files and model card to Hugging Face Hub."""
    api = HfApi(token=token)

    model_file = os.path.join(tokenizer_dir, "gbm_tokenizer.model")
    vocab_file = os.path.join(tokenizer_dir, "gbm_tokenizer.vocab")

    if not os.path.isfile(model_file):
        raise FileNotFoundError(
            f"Tokenizer model not found: {model_file}. Run `make train` first."
        )

    if create_repo_if_missing:
        try:
            create_repo(
                repo_id,
                repo_type="model",
                private=private,
                exist_ok=True,
                token=token,
            )
            print(f"Repo ensured: https://huggingface.co/{repo_id}")
        except Exception as e:
            print(f"Note: {e}")

    # Upload tokenizer files
    for local_path, path_in_repo in [
        (model_file, "gbm_tokenizer.model"),
        (vocab_file, "gbm_tokenizer.vocab"),
    ]:
        if os.path.isfile(local_path):
            api.upload_file(
                path_or_fileobj=local_path,
                path_in_repo=path_in_repo,
                repo_id=repo_id,
                repo_type="model",
                token=token,
            )
            print(f"Uploaded: {path_in_repo}")
        else:
            print(f"Skipped (not found): {local_path}")

    # Upload model card (Hub requires YAML frontmatter; use generated card unless local has it)
    readme_path = os.path.join(tokenizer_dir, "README.md")
    use_local_readme = False
    if os.path.isfile(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            first_line = (f.readline() or "").strip()
        if first_line == "---":
            use_local_readme = True
    if use_local_readme:
        api.upload_file(
            path_or_fileobj=readme_path,
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="model",
            token=token,
        )
        print("Uploaded: README.md (local file with YAML)")
    else:
        api.upload_file(
            path_or_fileobj=io.BytesIO(get_model_card(repo_id).encode("utf-8")),
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="model",
            token=token,
        )
        print("Uploaded: README.md (generated model card with YAML metadata)")

    print(f"\nDone. View at: https://huggingface.co/{repo_id}")
    print(
        "To enable gated access: Repo → Settings → Enable 'Access request' (automatic or manual approval)."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Upload GBM tokenizer to Hugging Face Hub."
    )
    parser.add_argument(
        "repo_id",
        nargs="?",
        default=None,
        help="Hugging Face repo id (e.g. username/gbm-tokenizer). Default: prompt or HF_USERNAME/gbm-tokenizer",
    )
    parser.add_argument(
        "--tokenizer-dir",
        default=".",
        help="Directory containing gbm_tokenizer.model (and optionally .vocab). Default: current dir",
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Create repo as private (gating is separate; enable in Settings for public gated).",
    )
    parser.add_argument(
        "--token",
        default=None,
        help="Hugging Face token (or set HF_TOKEN). Run 'huggingface-cli login' if needed.",
    )
    parser.add_argument(
        "--no-create-repo",
        action="store_true",
        help="Do not create repo if missing; only upload files.",
    )
    args = parser.parse_args()

    repo_id = args.repo_id
    if not repo_id:
        # Try env or prompt
        repo_id = os.environ.get("HF_REPO_ID")
        if not repo_id:
            username = os.environ.get("HF_USERNAME")
            if not username:
                username = input("Enter your Hugging Face username: ").strip()
            repo_id = f"{username}/gbm-tokenizer"
        print(f"Using repo_id: {repo_id}")

    token = args.token or os.environ.get("HF_TOKEN")
    if not token:
        try:
            login()
        except Exception:
            pass
        token = os.environ.get("HF_TOKEN")

    if not token:
        print(
            "No Hugging Face token. Set HF_TOKEN or run: huggingface-cli login"
        )
        raise SystemExit(1)

    upload(
        repo_id=repo_id,
        tokenizer_dir=args.tokenizer_dir,
        private=args.private,
        token=token,
        create_repo_if_missing=not args.no_create_repo,
    )


if __name__ == "__main__":
    main()
