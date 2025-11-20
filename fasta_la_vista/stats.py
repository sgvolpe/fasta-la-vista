# fastalavista/stats.py
from typing import List, Dict
from collections import Counter
import re

# ---------------------------------------
# Sequence Length Distribution
# ---------------------------------------
def length_distribution(sequences: List[str]) -> Dict[int, int]:
    """
    Compute a length distribution for a list of sequences.

    Returns a dictionary:
        { length: count }
    """
    lengths = [len(seq.strip()) for seq in sequences if seq.strip()]
    return dict(Counter(lengths))


# ---------------------------------------
# GC Content
# ---------------------------------------
def gc_content(sequences: List[str]) -> Dict[str, float]:
    """
    Returns global GC content and per-sequence values.

    sequences: list of DNA strings
    """
    per_seq = []
    total_gc = 0
    total_len = 0

    for seq in sequences:
        seq_clean = re.sub(r"[^ACGTNacgtn]", "", seq)
        if not seq_clean:
            per_seq.append(0)
            continue

        gc = seq_clean.upper().count("G") + seq_clean.upper().count("C")
        length = len(seq_clean)

        per_seq.append(gc / length)
        total_gc += gc
        total_len += length

    global_gc = (total_gc / total_len) if total_len > 0 else 0

    return {
        "global_gc": global_gc,
        "per_sequence_gc": per_seq,
    }


# ---------------------------------------
# Extract sequences from FASTA/FASTQ text
# ---------------------------------------
def extract_sequences_from_fasta(text: str) -> List[str]:
    lines = text.strip().splitlines()
    seqs = []
    curr = []

    for line in lines:
        if line.startswith(">"):
            if curr:
                seqs.append("".join(curr))
                curr = []
        else:
            curr.append(line.strip())

    if curr:
        seqs.append("".join(curr))

    return seqs


def extract_sequences_from_fastq(text: str) -> List[str]:
    lines = text.strip().splitlines()
    seqs = []

    for i in range(0, len(lines), 4):
        if i + 1 < len(lines):
            seqs.append(lines[i + 1].strip())

    return seqs


# ---------------------------------------
# Combined stats for any file
# ---------------------------------------
def compute_stats(text: str, fmt: str) -> Dict:
    if fmt == "fasta":
        seqs = extract_sequences_from_fasta(text)
    elif fmt == "fastq":
        seqs = extract_sequences_from_fastq(text)
    else:
        raise ValueError(f"Unknown format: {fmt}")

    return {
        "count": len(seqs),
        "length_distribution": length_distribution(seqs),
        "gc": gc_content(seqs),
    }
