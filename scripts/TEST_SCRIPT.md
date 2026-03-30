# Test Script Guidelines

When creating test scripts in the `scripts/` directory to evaluate the implementations in `cs336_data/`, please follow these structural guidelines to ensure uniformity and ease of testing.

## 1. Naming Convention
The test script name must exactly match the name of the implementation file in the `cs336_data/` directory. 
- For example, if testing `cs336_data/extract_text.py`, the corresponding test script must be named `scripts/extract_text.py`.
- If testing `cs336_data/mask_pii.py`, the test script must be named `scripts/mask_pii.py`.

## 2. Output Destination
All scripts must export their results to a text file in the project's `scripts/` directory. The naming convention for this output file should be `out_<script_name>.txt`. 
- For example, `scripts/extract_text.py` should write its output directly to a file named `scripts/out_extract_text.txt`.
- Do not print long outputs to standard output (the console); print only a short success message.

## 3. Data Source
Scripts should typically read from a standard WARC file provided in the `data/` directory (e.g., `data/CC-MAIN-20250417135010-20250417165010-00065.warc.gz`) using the `fastwarc` library.

## 4. Basic Script Structure
1. Import necessary adapters from `tests.adapters` or directly from `cs336_data`.
2. Set the `warc_file` path and `output_file` path.
3. Open the output file `out_<script_name>.txt` for writing.
4. Iterate through a small sample of records (to avoid excessively long runtimes, typically break after 20-100 examples depending on the test).
5. Write the extracted or processed text directly to the file, separating examples with clear delimiters (like `--- Example N ---`).

### Template

```python
import sys
from fastwarc.warc import ArchiveIterator, WarcRecordType
from tests.adapters import run_extract_text_from_html_bytes

warc_file = 'data/CC-MAIN-20250417135010-20250417165010-00065.warc.gz'
output_file = 'scripts/out_example_script.txt'

with open(warc_file, 'rb') as f, open(output_file, 'w', encoding='utf-8') as out:
    examples_found = 0
    for record in ArchiveIterator(f, record_types=WarcRecordType.response):
        if examples_found >= 20: # Limit examples
            break
        
        # Parse the record...
        bytes_content = record.reader.read()
        text = run_extract_text_from_html_bytes(bytes_content)
        
        if text:
            # Write out results
            out.write(f"--- Example {examples_found+1} ---\n")
            out.write(f"{text[:200]}...\n\n")
            examples_found += 1
            
print(f"Results successfully written to {output_file}")
```
