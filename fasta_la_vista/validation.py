# fastalavista/validation.py
from collections import Counter
from dataclasses import dataclass
from typing import List, Optional, Dict
import re

from schemas.sequence import SequenceRecord



@dataclass
class ValidationResult:
    valid: bool
    errors: List[str]
    sequence_records: List[SequenceRecord] = None


FASTA_HEADER_RE = re.compile(r"^>.+")
FASTQ_HEADER_RE = re.compile(r"^@.+")


# -----------------------------
# FORMAT DETECTION
# -----------------------------
def detect_format(text: str) -> Optional[str]:
    """Detect whether text is FASTA or FASTQ.
    Returns "fasta", "fastq", or None.
    """
    stripped = text.strip().splitlines()
    if not stripped:
        return None

    first = stripped[0]
    if first.startswith(">"):
        return "fasta"
    if first.startswith("@"):
        return "fastq"
    return None


# -----------------------------
# FASTA VALIDATION
# -----------------------------
def validate_fasta(text: str) -> ValidationResult:
    lines = text.strip().splitlines()

    errors = []
    if not lines:
        return ValidationResult(False, ["Empty FASTA input"])

    i = 0
    sequence_records = []
    while i < len(lines):
        header = lines[i]
        if not FASTA_HEADER_RE.match(header):
            errors.append(f"Invalid FASTA header at line {i + 1}: {header}")
        i += 1

        # collect sequence until next header
        seq = []
        while i < len(lines) and not lines[i].startswith(">"):
            seq.append(lines[i].strip())
            i += 1

        sequence = "".join(seq)

        sequence_records.append(SequenceRecord(
            id=header[1:].split()[0],
            description=" ".join(header[1:].split()[1:]),
            seq=sequence
        ))

        if not sequence:
            errors.append(f"Empty sequence for header: {header}")
        else:
            invalid = re.findall(r"[^ACGTNacgtn]", sequence)
            if invalid:
                errors.append(
                    f"Invalid characters in sequence under {header}: {set(invalid)}"
                )

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        sequence_records=sequence_records
    )


# -----------------------------
# FASTQ VALIDATION
# -----------------------------
def validate_fastq(text: str) -> ValidationResult:
    lines = text.strip().splitlines()
    errors = []

    if len(lines) % 4 != 0:
        errors.append(
            f"FASTQ should have multiples of 4 lines, found {len(lines)} lines"
        )
        return ValidationResult(False, errors)

    for i in range(0, len(lines), 4):
        header = lines[i]
        seq = lines[i + 1]
        plus = lines[i + 2]
        qual = lines[i + 3]

        if not FASTQ_HEADER_RE.match(header):
            errors.append(f"Invalid FASTQ header at line {i + 1}: {header}")

        if not plus.startswith("+"):
            errors.append(f"Missing '+' line at line {i + 3}: {plus}")

        invalid = re.findall(r"[^ACGTNacgtn]", seq)
        if invalid:
            errors.append(
                f"Invalid characters in sequence at line {i + 2}: {set(invalid)}"
            )

        if len(seq) != len(qual):
            errors.append(
                f"Sequence/quality length mismatch at record starting line {i + 1}"
            )

    return ValidationResult(len(errors) == 0, errors)


def validate_sequence(text: str):
    fmt = detect_format(text)
    if fmt == "fasta":
        return validate_fasta(text)
    elif fmt == "fastq":
        return validate_fastq(text)
    else:
        return ValidationResult(False, ["Unknown format"])


def gc_content(seq) -> float:
    """Calculate GC content percentage of a sequence record."""
    if not seq:
        return 0.0
    gc_count = sum(1 for base in seq if base in "GCgc")
    return (gc_count / len(seq)) * 100.0

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