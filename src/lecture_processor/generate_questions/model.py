from typing import List
from pydantic import BaseModel, Field
from src.lecture_processor.models import Option, PageRange


class ConceptualQuestion(BaseModel):
    question: str = Field(..., description="The conceptual question being asked.")
    topics: List[str] = Field(
        ...,
        description="A list of three key topics or concepts that this question addresses.",
    )
    options: List["Option"] = Field(
        ...,
        description="Multiple-choice options corresponding to possible answers for the question.",
    )
    reference: "PageRange" = Field(
        ...,
        description="Page range within the lecture material where the concept or question originates.",
    )
    explanation: str = Field(
        ...,
        description="A concise explanation of the correct answer intended to help students understand the reasoning.",
    )

    def as_string(self) -> str:
        """Return a formatted string representation of the conceptual question."""
        options_formatted = "\n".join(
            [f"- {'✅ ' if opt.is_correct else ''}{opt.text}" for opt in self.options]
        )
        topics_formatted = ", ".join(self.topics)

        return (
            f"### **Conceptual Question**\n"
            f"**Question:** {self.question}\n\n"
            f"**Topics:** {topics_formatted}\n\n"
            f"**Options:**\n{options_formatted}\n\n"
            f"**Explanation:** {self.explanation}\n\n"
            f"**Reference:** {self.reference}\n"
        )
