# fastalavista

**FASTA/FASTQ Validator · Sequence Stats · Lightweight Annotator**

`fastalavista` is a fast, modern, and developer-friendly toolkit for working with biological sequence files. It validates FASTA and FASTQ formats, computes essential sequence statistics, and performs simple sequence annotations.

It is designed as a:
- **Python library** (import and use in scripts)
- **CLI tool** (validate, analyze, annotate from the terminal)
- *(Optional)* **FastAPI microservice** (for remote sequence validation and processing)

---

## ✨ Features

### 🧪 Validation
- FASTA format validation
- FASTQ 4-line block validation
- Malformed record detection
- Illegal character checks
- Auto-detection of file type

### 📊 Statistics
- GC content (per sequence + global)
- Sequence/read length distribution
- Base composition
- Ambiguous base ("N") counts

### 📝 Annotation
- Motif/regex search
- Low-complexity detection (simple entropy-based)
- Basic ORF scanning *(optional future feature)*

---

## 🚀 Getting Started

### Installation
```bash
pip install fastalavista
```
*(Package will be published to PyPI once the first stable version is ready.)*

### Command-line usage

#### Validate a FASTA or FASTQ file
```bash
fastalavista validate sample.fasta
fastalavista validate sample.fastq
```

#### Compute sequence statistics
```bash
fastalavista stats sample.fasta
```

#### Annotate sequences (e.g., search motifs)
```bash
fastalavista annotate sample.fasta --motif ATG --motif CGT
```

#### Run all analyses together
```bash
fastalavista all sample.fastq --json
```

---

## 📚 Python Library Usage

```python
from validators import validate_fasta
from fastalavista.stats import gc_content

records = validate_fasta("example.fasta")
results = gc_content(records)
print(results)
```

---

## 🗂️ Project Structure
```
fastalavista/
├── src/fastalavista/
│   ├── cli.py
│   ├── validators/
│   ├── stats/
│   ├── annotators/
│   ├── api/
│   └── utils/
├── tests/
├── examples/
├── README.md
├── pyproject.toml
└── LICENSE
```

---

## 🔧 Roadmap
- [ ] FASTA validator
- [ ] FASTQ validator
- [ ] GC content calculation
- [ ] Length distribution
- [ ] Motif search
- [ ] Complexity estimation
- [ ] CLI interface (Click)
- [ ] FastAPI microservice
- [ ] PyPI release

---

## 🤝 Contributing
Pull requests, issues, and suggestions are welcome! This project aims to remain beginner-friendly while offering robust utilities for real-world bioinformatics.

---

## 📄 License
Licensed under the MIT License — see the `LICENSE` file for details.
