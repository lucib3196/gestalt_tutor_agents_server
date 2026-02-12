from pydantic import BaseModel, Field
from typing import List, Optional

class LectureAnalysis(BaseModel):
    lecture_title: str = Field(
        ...,
        description="A concise, descriptive title summarizing the main focus of the lecture.",
    )

    lecture_summary: str = Field(
        ...,
        description=(
            "A concise, high-level summary of the lecture, written in clear "
            "pedagogical language. Should capture the main ideas, not details."
        ),
    )

    core_topics: List[str] = Field(
        ...,
        description=(
            "A list of the primary concepts or topics covered in the lecture. "
            "Each item should be a short noun phrase (e.g., 'Bernoulli equation')."
        ),
    )

    learning_objectives: List[str] = Field(
        ...,
        description=(
            "What a student should understand or be able to do after the lecture. "
            "Each objective should start with an action verb (e.g., 'derive', 'explain')."
        ),
    )

    assumed_prerequisites: Optional[List[str]] = Field(
        default=None,
        description=(
            "Concepts or courses the lecture assumes prior knowledge of "
            "(e.g., 'basic calculus', 'Newtonian mechanics')."
        ),
    )

    lecture_type: Optional[str] = Field(
        default=None,
        description=(
            "The primary nature of the lecture, such as 'conceptual', "
            "'derivation-heavy', 'computational', or 'mixed'."
        ),
    )

    def as_string(self) -> str:
        topics_formatted = "\n".join(f"- {topic}" for topic in self.core_topics)
        objectives_formatted = "\n".join(
            f"{i+1}. {obj}" for i, obj in enumerate(self.learning_objectives)
        )

        prereqs_formatted = (
            "\n".join(f"- {p}" for p in self.assumed_prerequisites)
            if self.assumed_prerequisites
            else "None specified"
        )

        lecture_type_str = self.lecture_type or "Not specified"

        return (
            f"## {self.lecture_title}\n\n"
            f"**Lecture Type:** {lecture_type_str}\n\n"
            f"### Summary\n"
            f"{self.lecture_summary}\n\n"
            f"### Core Topics\n"
            f"{topics_formatted}\n\n"
            f"### Learning Objectives\n"
            f"{objectives_formatted}\n\n"
            f"### Assumed Prerequisites\n"
            f"{prereqs_formatted}\n"
        )
