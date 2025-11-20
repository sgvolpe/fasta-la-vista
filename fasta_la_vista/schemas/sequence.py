from pydantic import BaseModel
from typing import Optional


class SequenceRecord(BaseModel):
    id: Optional[str] = None
    description: Optional[str] = None
    seq: Optional[str] = None
    quality: Optional[str] = None
    line_number: Optional[int] = None


if __name__ == "__main__":
    # Example usage
    record = SequenceRecord(
        id="seq1",
        description="Example sequence",
        seq="ACGTACGT",
        quality="IIIIIIII",
        line_number=1
    )
    print(record.model_dump())
