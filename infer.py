import sentencepiece as spm

sp = spm.SentencePieceProcessor()
sp.load("gbm_tokenizer.model")

# text = "machine learning is powerful"
text = "नमस्कार मेरु नाम सुमितेश च"

tokens = sp.encode(text, out_type=str)
ids = sp.encode(text, out_type=int)

print("Original text:", text)
print("Tokens:", tokens)
print("IDs:", ids)
print("Total tokens:", len(tokens))

# Decode back to verify tokenizer is working correctly
decoded_from_tokens = sp.decode(tokens)
decoded_from_ids = sp.decode(ids)

print("\nDecoded from tokens:", decoded_from_tokens)
print("Decoded from IDs:", decoded_from_ids)

# Verify round-trip
if decoded_from_tokens == text and decoded_from_ids == text:
    print("\n✓ Tokenizer verification: SUCCESS - Round-trip encoding/decoding works correctly!")
else:
    print("\n✗ Tokenizer verification: FAILED - Decoded text doesn't match original")
    if decoded_from_tokens != text:
        print(f"  Expected: '{text}'")
        print(f"  Got from tokens: '{decoded_from_tokens}'")
    if decoded_from_ids != text:
        print(f"  Expected: '{text}'")
        print(f"  Got from IDs: '{decoded_from_ids}'")
