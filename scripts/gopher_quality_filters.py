import sys
from fastwarc.warc import ArchiveIterator, WarcRecordType
from tests.adapters import run_extract_text_from_html_bytes, run_gopher_quality_filter

warc_file = "data/CC-MAIN-20250417135010-20250417165010-00065.warc.gz"
output_file = "scripts/out_gopher_quality_filters.txt"

with open(warc_file, "rb") as f, open(output_file, "w", encoding="utf-8") as out:
    examples_found = 0
    for record in ArchiveIterator(f, record_types=WarcRecordType.response):
        if examples_found >= 20:  # Limit examples
            break

        # Parse the record...
        bytes_content = record.reader.read()
        text = run_extract_text_from_html_bytes(bytes_content)

        if text:
            passed_filter = run_gopher_quality_filter(text)
            out.write(f"--- Example {examples_found + 1} ---\n")
            out.write(f"Passed Gopher Quality Filters: {passed_filter}\n")
            out.write(f"Text:\n{text[:500]}...\n\n")
            examples_found += 1

print(f"Results successfully written to {output_file}")
