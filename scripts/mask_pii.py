import random
from fastwarc.warc import ArchiveIterator, WarcRecordType
from tests.adapters import run_extract_text_from_html_bytes
from cs336_data.mask_pii import mask_emails, mask_phone_numbers, mask_ips

warc_file = 'data/CC-MAIN-20250417135010-20250417165010-00065.warc.gz'
output_file = 'scripts/out_mask_pii.txt'

examples = []

with open(warc_file, 'rb') as f:
    for record in ArchiveIterator(f, record_types=WarcRecordType.response):
        bytes_content = record.reader.read()
        text = run_extract_text_from_html_bytes(bytes_content)
        if text:
            # Mask emails
            masked_email, num_email = mask_emails(text)
            if num_email > 0:
                examples.append(("EMAIL", text, masked_email))
            
            # Mask phones
            masked_phone, num_phone = mask_phone_numbers(text)
            if num_phone > 0:
                examples.append(("PHONE", text, masked_phone))
                
            # Mask IPs
            masked_ip, num_ip = mask_ips(text)
            if num_ip > 0:
                examples.append(("IP", text, masked_ip))
                
        if len(examples) > 100:  # Collect a pool to sample from
            break

# Print 20 random examples
sample = random.sample(examples, min(20, len(examples)))
with open(output_file, 'w', encoding='utf-8') as out:
    for i, (pii_type, orig, masked) in enumerate(sample):
        out.write(f"\n--- Example {i+1} ({pii_type}) ---\n")
        
        # Try to find the diff to show context
        import difflib
        s = difflib.SequenceMatcher(None, orig, masked)
        for tag, i1, i2, j1, j2 in s.get_opcodes():
            if tag == 'replace':
                out.write(f"Original: ...{orig[max(0, i1-30):min(len(orig), i2+30)]}...\n")
                out.write(f"Masked:   ...{masked[max(0, j1-30):min(len(masked), j2+30)]}...\n")

print(f"Results successfully written to {output_file}")
