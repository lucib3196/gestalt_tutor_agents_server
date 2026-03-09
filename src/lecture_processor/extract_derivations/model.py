from pydantic import BaseModel, Field
from typing import List
from lecture_processor.models import PageRange


class Derivation(BaseModel):
    derivation_title: str = Field(
        ...,
        description="A short, concise title describing what the derivation focuses on.",
    )
    derivation_stub: str = Field(
        ...,
        description="A brief statement of the equation, relationship, or expression being derived.",
    )
    steps: List[str] = Field(
        ...,
        description="An ordered list of logical or mathematical steps used to carry out the derivation.",
    )
    reference: PageRange = Field(
        ...,
        description="The range of pages within the lecture material where this derivation appears.",
    )

    def as_string(self) -> str:
        steps_formatted = "\n".join(
            [f"{i+1}. {step}" for i, step in enumerate(self.steps)]
        )
        return (
            f"### **{self.derivation_title}**\n"
            f"**Stub:** {self.derivation_stub}\n\n"
            f"**Steps:**\n{steps_formatted}\n\n"
            f"**Reference:** {self.reference}\n"
        )
