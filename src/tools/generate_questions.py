from enum import Enum
from typing import Annotated, List

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from src.core.settings import get_settings

settings = get_settings()

model = init_chat_model(
    model=settings.model,
    model_provider="google_genai",
)


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class LearningObjective(str, Enum):
    CONCEPTUAL_UNDERSTANDING = "conceptual_understanding"
    PROBLEM_SOLVING = "problem_solving"
    EQUATION_APPLICATION = "equation_application"
    CRITICAL_THINKING = "critical_thinking"
    DEFINITION_RECALL = "definition_recall"
    MULTI_STEP_REASONING = "multi_step_reasoning"
    REAL_WORLD_APPLICATION = "real_world_application"
    DATA_INTERPRETATION = "data_interpretation"
    DESIGN_ANALYSIS = "design_analysis"


class MCQInput(BaseModel):
    topic: Annotated[
        str,
        Field(
            description=(
                "Main topic or concept the multiple choice question should "
                "focus on. Examples: 'First Law of Thermodynamics', "
                "'PID Control', 'Fluid Statics', 'Python Dictionaries'."
            )
        ),
    ]

    difficulty: Annotated[
        DifficultyLevel,
        Field(
            description=(
                "Difficulty level of the question. "
                "'easy' should test basic recall or direct application, "
                "'medium' should involve moderate reasoning or calculations, "
                "and 'hard' should involve multi-step reasoning, derivations, "
                "or conceptual depth."
            )
        ),
    ] = DifficultyLevel.MEDIUM

    num_questions: Annotated[
        int,
        Field(
            default=4,
            ge=2,
            le=6,
            description=(
                "Number of multiple-choice questions to generate. "
                "Must be between 2 and 6."
            ),
        ),
    ]

    context: Annotated[
        str,
        Field(
            description=(
                "Surrounding contextual information used to ground the question. "
                "This may include lecture notes, textbook excerpts, derivations, "
                "discussion summaries, or previously discussed concepts."
            )
        ),
    ]

    learning_objective: Annotated[
        LearningObjective,
        Field(
            description=(
                "Primary educational objective the question is intended to assess. "
                "Used internally for classification, filtering, analytics, "
                "and adaptive question generation."
            )
        ),
    ]


class Option(BaseModel):
    option: Annotated[
        str,
        Field(
            description="Answer option text shown to the learner for a given question."
        ),
    ]
    correct: Annotated[
        bool,
        Field(
            description=(
                "Whether this option is the correct answer. Exactly one option "
                "should be true per question."
            )
        ),
    ]


class MultipleChoiceQuestionBase(BaseModel):
    question: Annotated[
        str,
        Field(
            description=(
                "The complete multiple-choice question stem presented to the learner."
            )
        ),
    ]
    options: Annotated[
        List[Option],
        Field(
            description=(
                "List of answer options for the question. Should contain plausible "
                "distractors and exactly one correct option."
            )
        ),
    ]


class MultipleChoiceQuestionResponse(BaseModel):
    questions: Annotated[
        List[MultipleChoiceQuestionBase],
        Field(
            description=(
                "Generated set of multiple-choice questions matching the requested "
                "topic, context, and learning objective."
            )
        ),
    ]
    num_options: Annotated[
        int,
        Field(
            description=(
                "Number of options per question used in the generated set "
                "(typically 4)."
            )
        ),
    ]


class MultipleChoiceQuestion(MultipleChoiceQuestionBase):
    topic: Annotated[
        str,
        Field(description="Topic label attached to each generated question."),
    ]
    difficulty: Annotated[
        DifficultyLevel,
        Field(description="Difficulty label attached to each generated question."),
    ]
    learning_objective: Annotated[
        LearningObjective,
        Field(
            description=(
                "Learning objective label describing what skill the question "
                "is designed to assess."
            )
        ),
    ]


MCQ_SYSTEM_PROMPT = r"""
You are an expert engineering tutor creating high-quality conceptual multiple-choice questions for engineering and STEM education.

Use ONLY the supplied inputs:
- topic
- context
- difficulty
- num_questions
- learning_objective

Core Objective:
- Generate conceptually focused questions that evaluate understanding, interpretation, physical intuition, governing principles, assumptions, system behavior, conceptual relationships, and engineering reasoning.
- The focus is NOT computational problem solving.
- Questions should resemble conceptual engineering exam questions, oral assessment questions, or theory-focused review questions.

Question Scope Rules:
- Computational or numerically solved problems are STRICTLY FORBIDDEN.
- Do NOT require arithmetic, algebraic manipulation, derivations, solving equations, unit conversions, or multi-step calculations.
- Questions MAY reference governing equations, symbolic relationships, trends, proportionality, physical meaning, limiting behavior, assumptions, or variable relationships conceptually.
- Questions MAY ask students to interpret the meaning or implications of an equation WITHOUT solving it mathematically.
- Questions should prioritize conceptual mastery over procedural computation.

Requirements:
1) Generate exactly num_questions questions.
2) Each question must have exactly 4 options.
3) Exactly one option must be marked correct.
4) Questions must align to the requested difficulty:
   - easy:
     - terminology
     - definitions
     - direct conceptual recall
     - identification of physical principles
   - medium:
     - conceptual interpretation
     - engineering reasoning
     - qualitative relationships
     - conceptual application to scenarios
   - hard:
     - deeper conceptual insight
     - multi-concept reasoning
     - identifying subtle misconceptions
     - interpreting system behavior or governing assumptions
5) Questions must directly target the requested learning_objective.
6) Questions must remain grounded in the provided topic and context.
7) Do NOT invent unrelated engineering facts, equations, systems, or terminology.
8) Keep wording clear, unambiguous, concise, and exam-ready.
9) Avoid trick questions.
10) Avoid “all of the above” and “none of the above.”
11) Distractors should be plausible and reflect common conceptual misunderstandings.
12) Return output matching the required structured schema exactly.

Math Formatting Rules (STRICTLY ENFORCED):
- ALL mathematical expressions MUST use LaTeX formatting.
- Inline mathematics MUST use:
  `$ ... $`

- Block/display mathematics MUST use:
  `$$ ... $$`

- The following delimiters are STRICTLY FORBIDDEN:
  - `\[ ... \]`
  - `\(...\)`
  - any escaped-parenthesis or escaped-bracket math variants

- NEVER write mathematical expressions in plain text.
- NEVER mix inline and block delimiters in the same expression.
- Variables, subscripts, superscripts, Greek letters, vectors, operators, units, and symbolic notation MUST be properly formatted using LaTeX.
- Governing equations, constitutive equations, conservation equations, and symbolic relationships MUST always be enclosed in valid LaTeX delimiters.
- If mathematics is unnecessary, avoid including it entirely.
- If an expression cannot be represented cleanly in LaTeX, rewrite or omit it.

Conceptual Engineering Question Guidelines:
- Prefer questions about:
  - physical interpretation
  - governing principles
  - conservation laws
  - assumptions of models
  - limiting behavior
  - qualitative trends
  - system behavior
  - cause-and-effect relationships
  - interpretation of engineering diagrams/equations
  - conceptual comparison between systems
  - common engineering misconceptions

- Avoid:
  - plugging values into equations
  - solving for unknown variables
  - symbolic derivations
  - lengthy algebra
  - computation-heavy thermodynamics/fluids/statics/dynamics calculations
  - calculator-style questions

Examples of GOOD conceptual prompts:
- "What does the continuity equation physically represent?"
- "How does increasing Reynolds number conceptually affect flow behavior?"
- "What assumption is required for Bernoulli’s equation to remain valid?"
- "What is the physical interpretation of the Fourier law negative sign?"
- "How does damping conceptually influence transient response?"

Examples of BAD questions:
- "Calculate the pressure drop..."
- "Solve for the velocity..."
- "Determine the numerical heat transfer rate..."
- "Find the eigenvalues..."
- "Compute the stress at point A..."
""".strip()


class MultipleChoiceQuestionToolResponse(BaseModel):
    payload: List[MultipleChoiceQuestion]


@tool(args_schema=MCQInput)
def generate_mcq(
    topic: str,
    context: str,
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
    num_questions: int = 3,
    learning_objective: LearningObjective = (
        LearningObjective.CONCEPTUAL_UNDERSTANDING
    ),
):
    """
    Generate context-grounded multiple-choice questions for a given topic.

    Args:
        topic: Topic/concept to assess.
        context: Reference material used to ground question content.
        difficulty: Requested question difficulty (`easy`, `medium`, `hard`).
        num_questions: Number of questions to generate (2 to 6 recommended).
        learning_objective: Primary skill/outcome each question should assess.

    Returns:
        A list of `MultipleChoiceQuestion`, each containing:
        - question stem
        - four options with exactly one correct answer
        - metadata labels (topic, difficulty, learning_objective)
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", MCQ_SYSTEM_PROMPT),
            (
                "human",
                (
                    "Create MCQs with the following inputs:\n"
                    "topic: {topic}\n"
                    "difficulty: {difficulty}\n"
                    "num_questions: {num_questions}\n"
                    "learning_objective: {learning_objective}\n"
                    "context:\n{context}\n"
                ),
            ),
        ]
    )

    llm = model.with_structured_output(MultipleChoiceQuestionResponse)
    response = llm.invoke(
        prompt.invoke(
            {
                "topic": topic,
                "difficulty": difficulty.value,
                "num_questions": num_questions,
                "learning_objective": learning_objective.value,
                "context": context,
            }
        )
    )

    parsed = MultipleChoiceQuestionResponse.model_validate(response)
    final: List[MultipleChoiceQuestion] = []
    for r in parsed.questions:
        f = MultipleChoiceQuestion(
            question=r.question,
            topic=topic,
            difficulty=difficulty,
            learning_objective=learning_objective,
            options=r.options,
        )
        final.append(f)

    return MultipleChoiceQuestionToolResponse(payload=final).model_dump()
