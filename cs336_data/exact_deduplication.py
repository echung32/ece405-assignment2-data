from __future__ import annotations

import hashlib
import os
from collections import defaultdict
from pathlib import Path


def _line_hash(line: str) -> bytes:
    return hashlib.blake2b(line.encode("utf-8"), digest_size=16).digest()


def exact_line_deduplication(input_files: list[os.PathLike], output_directory: os.PathLike) -> None:
    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)

    line_counts: dict[bytes, int] = defaultdict(int)

    for input_path in input_files:
        with open(input_path, encoding="utf-8") as f:
            for line in f:
                # index lines by their hash (build counter)
                line_counts[_line_hash(line)] += 1

    for input_path in input_files:
        input_path = Path(input_path)
        output_path = output_dir / input_path.name

        with open(input_path, encoding="utf-8") as src, open(output_path, "w", encoding="utf-8") as dst:
            for line in src:
                # only preserve unique lines, so any duplicates are not written
                if line_counts[_line_hash(line)] == 1:
                    dst.write(line)
