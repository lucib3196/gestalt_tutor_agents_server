from pydantic import BaseModel, Field


class PageRange(BaseModel):
    start_page: int
    end_page: int


class Option(BaseModel):
    text: str = Field(..., description="Text of the answer choice.")
    is_correct: bool = Field(
        ..., description="True if this option is the correct answer, otherwise False."
    )

