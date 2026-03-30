from __future__ import annotations

import hashlib
import itertools
import os
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from scipy.cluster.hierarchy import DisjointSet


_WHITESPACE_RE = re.compile(r"\s+")


def _normalize_text(text: str) -> str:
    """
    To improve recall (following Penedo et al., 2023), normalize
    the text before computing minhash signatures and/or comparing Jaccard similarity by lowercasing,
    removing punctuation, normalizing whitespaces, and removing accents, and applying NFD unicode
    normalization.
    """
    text = text.lower()
    # because Unicode can be represented in composed (nfc) and decomposed (nfd)
    # so this is basically normalizing all of it into NFD to remove accents easier
    text = unicodedata.normalize("NFD", text)
    # Mn is the accents (Like é -> e + ´), so remove those.
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    # replace punctuation category (P) with spaces
    text = "".join(" " if unicodedata.category(ch).startswith("P") else ch for ch in text)
    # replace whitespace sequences with a single space and trim leading/trailing whitespace
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text


def _ngrams_from_text(text: str, n: int) -> set[str]:
    normalized = _normalize_text(text)

    words = normalized.split()
    if len(words) < n:
        # fewer words than n, then just return the whole text as one "ngram"
        return {" ".join(words)}

    # otherwise, return all contiguous sequences of n words as ngrams
    return {" ".join(words[i : i + n]) for i in range(len(words) - n + 1)}


def _hash_ngram(ngram: str, seed: int) -> int:
    payload = f"{seed}:{ngram}".encode()
    return int.from_bytes(hashlib.blake2b(payload, digest_size=8).digest(), "big")


def _minhash_signature(ngram_set: set[str], num_hashes: int) -> tuple[int, ...]:
    """
    your function should compute minhash signatures for each
    document in the provided list of paths,
    """
    signature: list[int] = []
    for seed in range(num_hashes):
        min_value = min(_hash_ngram(ngram, seed) for ngram in ngram_set)
        signature.append(min_value)
    return tuple(signature)


def _jaccard_similarity(a: set[str], b: set[str]) -> float:
    # true ngram Jaccard similarity between two documents
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def minhash_deduplication(
    input_files: list[os.PathLike],
    num_hashes: int,
    num_bands: int,
    ngrams: int,
    jaccard_threshold: float,
    output_directory: os.PathLike,
) -> None:
    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)

    docs: list[tuple[Path, str]] = []
    for input_path in input_files:
        path = Path(input_path)
        with open(path, encoding="utf-8") as f:
            docs.append((path, f.read()))

    # convert docs to ngram sets and compute their minhash signatures
    ngram_sets = [_ngrams_from_text(text, ngrams) for _, text in docs]
    signatures = [_minhash_signature(ngram_set, num_hashes) for ngram_set in ngram_sets]

    # need to make sure num hashes and bands are divisible here.
    # it's okay in testing.
    band_size = num_hashes // num_bands
    buckets: dict[tuple[int, tuple[int, ...]], list[int]] = defaultdict(list)

    """
    Finally, we cluster duplicate documents across buckets. For example, suppose that documents A and B
    match in one bucket and have a true Jaccard similarity that's higher than our threshold, and that documents
    B and C match in another bucket and also have a true Jaccard similarity that's higher than our threshold.
    Then, we'd treat documents A, B, and C as a single cluster. We randomly remove all but one of the
    documents in each cluster.
    """

    for doc_idx, signature in enumerate(signatures):
        for band_idx in range(num_bands):
            start = band_idx * band_size
            end = start + band_size
            # lsh key
            band_signature = signature[start:end]
            # lsh bucket
            # if they are very similar, then they will have the same signature for at least one of the bands, 
            # and thus be put in the same bucket for that band.
            buckets[(band_idx, band_signature)].append(doc_idx)

    candidate_pairs: set[tuple[int, int]] = set()
    for bucket_docs in buckets.values():
        if len(bucket_docs) < 2:
            # means the bucket only has one doc
            # so likely means no duplicates, skip it
            continue
        # compare buckets here thjat have more than 1 document, and add candidate pairs to candidate_pairs set
        for i, j in itertools.combinations(sorted(bucket_docs), 2):
            candidate_pairs.add((i, j))

    # use disjoint set for transitive property for merging (a=b b=c, then a=b=c)
    dsu = DisjointSet(range(len(docs)))
    for i, j in candidate_pairs:
        # now check true js to see if they are actually similar enough to be merged
        similarity = _jaccard_similarity(ngram_sets[i], ngram_sets[j])
        if similarity >= jaccard_threshold:
            dsu.merge(i, j)

    clusters: dict[int, list[int]] = defaultdict(list)
    for subset in dsu.subsets():
        members = sorted(subset)
        if not members:
            continue
        clusters[members[0]] = members

    kept_indices: set[int] = set()
    for members in clusters.values():
        # choose min index, discard the rest as duplicates
        kept_indices.add(min(members))

    for idx, (path, text) in enumerate(docs):
        if idx not in kept_indices:
            continue
        output_path = output_dir / path.name
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
