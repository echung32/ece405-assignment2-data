from fastwarc.warc import ArchiveIterator, WarcRecordType
from tests.adapters import run_extract_text_from_html_bytes

warc_file = 'data/CC-MAIN-20250417135010-20250417165010-00065.warc.gz'
wet_file = 'data/CC-MAIN-20250417135010-20250417165010-00065.warc.wet.gz'
output_file = "scripts/out_extract_text.txt"

target_uri = None
wet_text = ""
with open(wet_file, 'rb') as f:
    for record in ArchiveIterator(f, record_types=WarcRecordType.conversion):
        target_uri = record.headers.get("WARC-Target-URI")
        wet_text = record.reader.read().decode('utf-8', errors='replace')
        break

warc_text = ""
with open(warc_file, 'rb') as f:
    for record in ArchiveIterator(f, record_types=WarcRecordType.response):
        if record.headers.get("WARC-Target-URI") == target_uri:
            bytes_content = record.reader.read()
            warc_text = run_extract_text_from_html_bytes(bytes_content)
            break

with open(output_file, 'w', encoding='utf-8') as out:
    out.write("=== OUR EXTRACTION ===\n")
    out.write(warc_text[:500] if warc_text else "None")
    out.write("\n\n=== WET EXTRACTION ===\n")
    out.write(wet_text[:500])

print(f"Results successfully written to {output_file}")
