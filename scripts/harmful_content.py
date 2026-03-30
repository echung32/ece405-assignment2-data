import sys
from fastwarc.warc import ArchiveIterator, WarcRecordType
from tests.adapters import run_extract_text_from_html_bytes, run_classify_nsfw, run_classify_toxic_speech

warc_file = "data/CC-MAIN-20250417135010-20250417165010-00065.warc.gz"
output_file = "scripts/out_toxicity.txt"

with open(warc_file, "rb") as f, open(output_file, "w", encoding="utf-8") as out:
    examples_found = 0
    for record in ArchiveIterator(f, record_types=WarcRecordType.response):
        if examples_found >= 20:  # Limit examples
            break

        # Parse the record...
        bytes_content = record.reader.read()
        text = run_extract_text_from_html_bytes(bytes_content)

        if text and len(text.strip()) > 50:
            nsfw_label, nsfw_score = run_classify_nsfw(text)
            toxic_label, toxic_score = run_classify_toxic_speech(text)

            out.write(f"--- Example {examples_found + 1} ---\n")
            out.write(f"NSFW: {nsfw_label} ({nsfw_score:.4f})\n")
            out.write(f"Toxic: {toxic_label} ({toxic_score:.4f})\n")
            out.write(f"Text:\n{text[:500]}...\n\n")
            examples_found += 1

print(f"Results successfully written to {output_file}")
