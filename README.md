# UHM ECE 405 Spring 2026 Assignment 2: Data

This asignment is created from Assignment 4 of [CS336 at Stanford taught in Spring 2025](https://stanford-cs336.github.io/spring2025/). 
For the full description of the original assignment, see the assignment handout at
[cs336_spring2025_assignment4_data.pdf](./cs336_spring2025_assignment4_data.pdf)
Check out the [glossary of terms](./glossary.md) for this assignment.

Check out useful [lectures from CS336 at Stanford](https://github.com/stanford-cs336/spring2025-lectures).

If you see any issues with the assignment handout or code, please feel free to
raise a GitHub issue or open a pull request with a fix. Any improvements of the existing codebase
(including adaptations from Stanford to UHM workflows, modifications of PDF, etc) will be rewarded with extra points.

## Test Results

```bash
===================================================================== test session starts ======================================================================
platform linux -- Python 3.13.7, pytest-8.3.5, pluggy-1.5.0 -- /ece405-assignment2-data/.venv/bin/python
cachedir: .pytest_cache
rootdir: /ece405-assignment2-data
configfile: pytest.ini
plugins: jaxtyping-0.3.2, hydra-core-1.3.2
collected 21 items                                                                                                                                             

tests/test_deduplication.py::test_exact_line_deduplication PASSED                                                                                        [  4%]
tests/test_deduplication.py::test_minhash_deduplication_exact_duplicates PASSED                                                                          [  9%]
tests/test_deduplication.py::test_minhash_deduplication_fuzzy_duplicates PASSED                                                                          [ 14%]
tests/test_extract.py::test_extract_text_from_html_bytes PASSED                                                                                          [ 19%]
tests/test_langid.py::test_identify_language_english PASSED                                                                                              [ 23%]
tests/test_langid.py::test_identify_language_chinese_simplified PASSED                                                                                   [ 28%]
tests/test_pii.py::test_mask_emails_single PASSED                                                                                                        [ 33%]
tests/test_pii.py::test_mask_emails_multiple PASSED                                                                                                      [ 38%]
tests/test_pii.py::test_mask_emails_existing_string PASSED                                                                                               [ 42%]
tests/test_pii.py::test_mask_phones_single PASSED                                                                                                        [ 47%]
tests/test_pii.py::test_mask_ips PASSED                                                                                                                  [ 52%]
tests/test_quality.py::test_classify_quality PASSED                                                                                                      [ 57%]
tests/test_quality.py::test_gopher_valid_input PASSED                                                                                                    [ 61%]
tests/test_quality.py::test_gopher_less_than_50_non_symbol_words PASSED                                                                                  [ 66%]
tests/test_quality.py::test_gopher_more_than_100000_non_symbol_words PASSED                                                                              [ 71%]
tests/test_quality.py::test_gopher_average_word_length_less_than_3 PASSED                                                                                [ 76%]
tests/test_quality.py::test_gopher_average_word_length_greater_than_10 PASSED                                                                            [ 80%]
tests/test_quality.py::test_gopher_more_than_30_percent_lines_ending_with_ellipsis PASSED                                                                [ 85%]
tests/test_quality.py::test_gopher_less_than_80_percent_words_with_alphabetic_character PASSED                                                           [ 90%]
tests/test_toxicity.py::test_classify_nsfw PASSED                                                                                                        [ 95%]
tests/test_toxicity.py::test_classify_toxic_speech PASSED                                                                                                [100%]

----------------------------------------- generated xml file: /ece405-assignment2-data/test_results.xml ------------------------------------------
====================================================================== 21 passed in 9.61s ======================================================================
```

## Setup

This directory is organized as follows:

- [`./cs336-basics`](./cs336-basics): directory containing a module
  `cs336_basics` and its associated `pyproject.toml`. This module contains the staff 
  implementation of the language model from assignment 1. You will use this training code
  to train an LM on your filtered data. You should not modify the training logic, since
  your leaderboard submission must use it exactly.
- [`./cs336_data`](./cs336_data): This folder is basically empty! This is the
  module where you will implement code to filter and process the data.

Visually, it should look something like:

``` sh
.
├── cs336_basics  # A python module named cs336_basics
│   └── ... an optimized training implementation ...
├── cs336_data  # TODO(you): code that you'll write for assignment 4
│   ├── __init__.py
│   └── ... TODO(you): any other files or folders you need for assignment 4 ...
├── README.md
├── pyproject.toml
└── ... TODO(you): other files or folders you need for assignment 4 ...
```

As in previous assignments, we use `uv` to manage dependencies.

## Submitting

To submit, run `./test_and_make_submission.sh` . This script will install your
code's dependencies, run tests, and create a gzipped tarball with the output. We
should be able to unzip your submitted tarball and run
`./test_and_make_submission.sh` to verify your test results.


## ECE405 Assignment instructions

Follow along the [CS336@Stanford handout](./cs336_spring2025_assignment4_data.pdf) with small deviations:
1. What the code looks like: clone https://github.com/igormolybog/ece405-assignment2-data.git
2. How to submit: You will submit the report on the assignment to [Assignment Submission Form](https://docs.google.com/forms/d/e/1FAIpQLScJg_QkwjKux3xKeM-EOmZyvA6zlbVIrf_lxN_qoCFoxdqTrg/viewform?usp=sharing&ouid=111841773839267096112). The code does not have to be attached as long as you include links to the main GitHub branch where your code lives and links to all of the Colab notebooks if applicable.
    - You don't need to submit to leaderboard.
3. None of the data or tools are pre-downloaded or pre-installed for you. The handout describes the steps to get them (e.g. download specific WARC files or fastText library). You should follow the steps yourself.
4. You can use warcio library (ArchiveIterator) to iterate through WARC.
5. For Section 2.7, quality_classifier (a), you can also download the Wikipidea URLs from [here](https://drive.google.com/file/d/1hjlgyWSuMRDf-G0AXgGBWZmvjPJdDWc7/view?usp=sharing). To train a classifier, you can prepare a training file (e.g., "quality_train.txt") where each line is formatted as follows:
  ``` 
    __label__high This document is from Wikipedia and is high-quality.
    __label__low This document is from a random crawl and might be low-quality.
  ```
  - This file can be used as the input to the fasttext.train_supervised
6. Problems listed in Section 4 are not required and can be skipped. This is primarily due to the absence of the filtered WARC data. However, the problems can be implemented using data from any other WARC file collections and submitted for extra credit even after the deadline for Assignment 2 (and before the last day of the class) 
    - You may leverage CPUs located on Koa cluster to solve the problems listed in Section 4
