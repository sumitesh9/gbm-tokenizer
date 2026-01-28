#!/usr/bin/env python3
"""
API helper script for tokenization.
This script is called from the Next.js API route to perform tokenization server-side.
"""
import sentencepiece as spm
import sys
import json
import os

# Try to get model path from environment variable first
model_path = os.environ.get("GBM_TOKENIZER_MODEL_PATH")

# If not set, try default locations
if not model_path:
    # Get the project root (parent directory of ui/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(project_root, "gbm_tokenizer.model")
    
    # If still not found, try in the ui directory (for deployment scenarios)
    if not os.path.exists(model_path):
        ui_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(ui_dir, "gbm_tokenizer.model")

if not os.path.exists(model_path):
    error_result = {
        "tokens": [],
        "ids": [],
        "count": 0,
        "error": f"Model file not found. Searched: {model_path}. Set GBM_TOKENIZER_MODEL_PATH environment variable to specify the model location."
    }
    print(json.dumps(error_result))
    sys.exit(1)

try:
    sp = spm.SentencePieceProcessor()
    sp.load(model_path)
    
    # Read text from stdin
    text = sys.stdin.read()
    
    if not text:
        error_result = {
            "tokens": [],
            "ids": [],
            "count": 0,
            "error": "No text provided"
        }
        print(json.dumps(error_result))
        sys.exit(1)
    
    # Tokenize
    tokens = sp.encode(text, out_type=str)
    ids = sp.encode(text, out_type=int)
    
    result = {
        "tokens": tokens,
        "ids": ids,
        "count": len(tokens)
    }
    
    print(json.dumps(result))
except Exception as e:
    error_result = {
        "tokens": [],
        "ids": [],
        "count": 0,
        "error": str(e)
    }
    print(json.dumps(error_result))
    sys.exit(1)
