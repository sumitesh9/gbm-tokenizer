import sentencepiece as spm

text = open("corpus.txt").read()

print("Number of unique characters: ", len(set(text)))
# Rule of thumb: vocab size = 2 * (number of unique characters)

spm.SentencePieceTrainer.train(
    input="corpus.txt",
    model_prefix="gbm_tokenizer",
    vocab_size=130,              # small vocab
    model_type="unigram",       # IMPORTANT
    character_coverage=1.0,
    bos_id=-1,                  # disable BOS
    eos_id=-1,                  # disable EOS
)
