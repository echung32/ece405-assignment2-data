from fastwarc.warc import ArchiveIterator, WarcRecordType
from tests.adapters import run_extract_text_from_html_bytes, run_identify_language

warc_file = 'data/CC-MAIN-20250417135010-20250417165010-00065.warc.gz'
output_file = "scripts/out_language_identification.txt"

with open(warc_file, 'rb') as f, open(output_file, 'w', encoding='utf-8') as out:
    examples_found = 0
    for record in ArchiveIterator(f, record_types=WarcRecordType.response):
        if examples_found >= 20:
            break
            
        bytes_content = record.reader.read()
        text = run_extract_text_from_html_bytes(bytes_content)
        
        if text:
            try:
                lang, prob = run_identify_language(text)
                out.write(f"--- Example {examples_found+1} ---\n")
                out.write(f"Language: {lang} (Probability: {prob:.4f})\n")
                out.write(f"Text Sample: {text[:200].replace(chr(10), ' ')}...\n\n")
                examples_found += 1
            except NotImplementedError:
                out.write("Language identification not implemented yet.\n")
                break

print(f"Results successfully written to {output_file}")
