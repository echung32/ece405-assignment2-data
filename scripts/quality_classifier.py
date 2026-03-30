import hashlib
import random

from fastwarc.warc import ArchiveIterator, WarcRecordType
from tests.adapters import (
    run_classify_quality,
    run_extract_text_from_html_bytes,
    run_gopher_quality_filter,
    run_identify_language,
)

CC_WARC = "data/CC-MAIN-20250417135010-20250417165010-00065.warc.gz"
WIKI_WARC = "data/subsampled_positive_urls.warc.gz"
TRAIN_FILE = "data/quality_train.txt"
OUTPUT_FILE = "scripts/out_quality_classifier.txt"
NUM_SAMPLES_PER_SOURCE = 10
SEED = 42
MAX_RECORDS_PER_SOURCE = 800
MAX_HTML_BYTES = 2_000_000
MIN_WORDS = 20
MAX_WORDS = 5000


def preprocess_text(text: str) -> str:
    return text.replace("\n", " ").replace("\r", " ").replace("\t", " ").strip()


def text_hash(text: str) -> bytes:
    return hashlib.blake2b(text.encode("utf-8"), digest_size=16).digest()


def load_training_hashes(train_file: str) -> set[bytes]:
    hashes: set[bytes] = set()
    with open(train_file, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or " " not in line:
                continue
            _, text = line.split(" ", 1)
            hashes.add(text_hash(preprocess_text(text)))
    return hashes


def reservoir_sample(
    warc_file: str,
    num_samples: int,
    training_hashes: set[bytes],
    rng: random.Random,
    source: str,
) -> tuple[list[str], int]:
    reservoir: list[str] = []
    candidate_count = 0
    local_hashes: set[bytes] = set()
    records_seen = 0

    with open(warc_file, "rb") as f:
        for record in ArchiveIterator(f, record_types=WarcRecordType.response):
            records_seen += 1
            if records_seen > MAX_RECORDS_PER_SOURCE:
                break

            bytes_content = record.reader.read()
            if len(bytes_content) > MAX_HTML_BYTES:
                continue

            text = run_extract_text_from_html_bytes(bytes_content)
            if not text:
                continue

            clean_text = preprocess_text(text)
            word_count = len(clean_text.split())
            if word_count < MIN_WORDS or word_count > MAX_WORDS:
                continue

            h = text_hash(clean_text)
            if h in training_hashes or h in local_hashes:
                continue

            if source == "wiki":
                lang, prob = run_identify_language(clean_text[:20000])
                if lang != "en" or prob < 0.5:
                    continue
                # sample wiki pages that were filtered out by gopher.
                # this is to not overlap with the training data
                if run_gopher_quality_filter(clean_text):
                    continue

            local_hashes.add(h)
            candidate_count += 1

            if len(reservoir) < num_samples:
                reservoir.append(clean_text)
                continue

            j = rng.randint(1, candidate_count)
            if j <= num_samples:
                reservoir[j - 1] = clean_text

    return reservoir, candidate_count


def main() -> None:
    rng = random.Random(SEED)
    training_hashes = load_training_hashes(TRAIN_FILE)

    cc_samples, cc_candidates = reservoir_sample(
        warc_file=CC_WARC,
        num_samples=NUM_SAMPLES_PER_SOURCE,
        training_hashes=training_hashes,
        rng=rng,
        source="cc",
    )
    wiki_samples, wiki_candidates = reservoir_sample(
        warc_file=WIKI_WARC,
        num_samples=NUM_SAMPLES_PER_SOURCE,
        training_hashes=training_hashes,
        rng=rng,
        source="wiki",
    )

    labeled_samples: list[tuple[str, str]] = [("cc", t) for t in cc_samples] + [("wiki", t) for t in wiki_samples]
    rng.shuffle(labeled_samples)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("Quality classifier evaluation samples\n")
        out.write(f"CC candidates (not in train): {cc_candidates}\n")
        out.write(f"Wiki candidates (EN + filtered out by gopher, not in train): {wiki_candidates}\n")
        out.write(f"Selected: {len(cc_samples)} CC + {len(wiki_samples)} Wiki\n\n")

        for i, (source, text) in enumerate(labeled_samples, start=1):
            label, score = run_classify_quality(text)
            out.write(f"--- Example {i} ---\n")
            out.write(f"Source: {source}\n")
            out.write(f"Quality Prediction: {label} ({score:.4f})\n")
            out.write(f"Text:\n{text[:500]}...\n\n")

    print(f"Results successfully written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
