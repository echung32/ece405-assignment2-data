import fasttext
from fastwarc.warc import ArchiveIterator, WarcRecordType
from cs336_data.extract_text import extract_text_from_html_bytes
from cs336_data.language_identification import identify_language
from cs336_data.gopher_quality_filters import gopher_quality_filter
import random


def preprocess_text(text):
    return text.replace("\n", " ").replace("\r", " ").replace("\t", " ").strip()


def extract_warc_texts(warc_path, label, max_examples=500, is_positive_wiki=False):
    texts = []
    try:
        with open(warc_path, "rb") as f:
            for record in ArchiveIterator(f, record_types=WarcRecordType.response):
                if len(texts) >= max_examples:
                    break
                try:
                    bytes_content = record.reader.read()
                    text = extract_text_from_html_bytes(bytes_content)
                    if not text:
                        continue

                    # always filter for English and some minimum confidence
                    lang, score = identify_language(text)
                    if lang != "en" or score < 0.5:
                        continue

                    # apply gopher quality rules to high-quality wiki data
                    # this is way too aggressive to apply on cc data.
                    if is_positive_wiki:
                        if not gopher_quality_filter(text):
                            continue

                    clean_text = preprocess_text(text)
                    # skip very short ones (is this necessary?)
                    if len(clean_text.split()) < 20:
                        continue

                    texts.append(f"__label__{label} {clean_text}")
                except Exception as e:
                    pass
    except Exception as e:
        print(f"Error reading {warc_path}: {e}")
    return texts


def main():
    # subsample 10,000 urls from wiki as not all are guaranteed to work
    # zcat data/enwiki-20240420-extracted_urls.txt.gz | shuf -n 10000 > data/subsampled_positive_urls.txt

    # run the downloader (have slurm script to run this)
    # wget --timeout=5 --waitretry=0 --tries=1 -i data/subsampled_positive_urls.txt --warc-file=data/subsampled_positive_urls -O /dev/null

    # extract wiki texts from wiki
    print("Extracting Wiki texts...")
    wiki_warc = "data/subsampled_positive_urls.warc.gz"

    wiki_texts = extract_warc_texts(wiki_warc, "wiki", max_examples=10000, is_positive_wiki=True)
    print(f"Got {len(wiki_texts)} wiki examples.")

    # cc texts
    print("Extracting CC texts...")
    cc_warc = "data/CC-MAIN-20250417135010-20250417165010-00065.warc.gz"
    cc_texts = extract_warc_texts(cc_warc, "cc", max_examples=len(wiki_texts), is_positive_wiki=False)
    print(f"Got {len(cc_texts)} CC examples.")

    # training data, shuffle so fastText doesn't see all the positive examples followed by all the negative examples
    # also not sure whether this is necessary but makes sense to do.
    train_file = "data/quality_train.txt"
    all_texts = wiki_texts + cc_texts
    random.shuffle(all_texts)
    with open(train_file, "w", encoding="utf-8") as f:
        for t in all_texts:
            f.write(t + "\n")

    # train fasttext model
    # the parameters are pretty arbitrary but they work.
    print("Training fastText model...")
    model = fasttext.train_supervised(input=train_file, epoch=100, lr=0.1, wordNgrams=1)

    model_path = "data/quality_classifier.bin"
    model.save_model(model_path)
    print(f"Model saved to {model_path}")

    # print out some training details
    with open("scripts/out_train_quality_classifier.txt", "w", encoding="utf-8") as out:
        out.write("Training complete\n")
        out.write(f"Wiki examples: {len(wiki_texts)}\n")
        out.write(f"CC examples: {len(cc_texts)}\n")
        out.write(f"Saved model: {model_path}\n\n")


if __name__ == "__main__":
    main()
