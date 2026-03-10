from pathlib import Path
from typing import List
import json
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from src.lecture_processor.lecture_analysis.model import LectureAnalysis 


class LectureDocumentLoaderBase(BaseLoader):
    """BaseClass for Lecture Loading"""

    def __init__(
        self,
        root: str | Path,
        recursive: bool = True,
        metadata: dict[str, str] | None = None,
        lecture_key: str = "lecture_analysis",
    ):
        self.root = Path(root).resolve()
        if not self.root.exists():
            raise ValueError(f"[Document Loader] Failed to resolve path {self.root}.")

        self.recursive = recursive
        self.base_metadata = metadata or {}
        self.cwd = Path().resolve()

        self.lecture_key = lecture_key

    def _relpath(self, path: Path | None) -> str | None:
        """Return path relative to CWD as POSIX string, or None."""
        if path is None:
            return None
        return path.resolve().relative_to(self.cwd).as_posix()


class LectureDocumentLoader(LectureDocumentLoaderBase):
    def load(self) -> List[Document]:
        docs = []
        for lecture_dir in self.root.iterdir():
            if not lecture_dir.is_dir():
                continue
            # -------------------------
            # Markdown content
            # -------------------------
            content = ""
            md_path = next(lecture_dir.glob("*.md"), None)
            if md_path:
                content = md_path.read_text(encoding="utf-8")
            # -------------------------
            # Source PDF
            # -------------------------
            pdf_path = next(lecture_dir.glob("*.pdf"), None)
            if not pdf_path:
                raise ValueError("Source PDF not present")
            # -------------------------
            # Lecture metadata
            # -------------------------
            lecture_metadata: dict = {}
            metadata_path = lecture_dir / "output.json"
            if metadata_path.exists():
                raw = json.loads(metadata_path.read_text(encoding="utf-8"))
                lecture_metadata = raw.get(self.lecture_key, {})
                if not lecture_metadata:
                    raise ValueError(
                        "Failed to load the lecture metadata please fix before embedding"
                    )
            lec_meta = LectureAnalysis.model_validate(lecture_metadata)
            # -------------------------
            # Yield document
            # -------------------------
            docs.append(
                Document(
                    id=f"{lec_meta.lecture_title}_{pdf_path.stem}",
                    page_content=content,
                    metadata={
                        **self.base_metadata,
                        **lec_meta.model_dump(),
                        "source_pdf": self._relpath(pdf_path),
                        "source_markdown": self._relpath(md_path),
                    },
                )
            )
        return docs


if __name__ == "__main__":
    loader = LectureDocumentLoader(
        root=r"assets/ME135Lecture",
        metadata={
            "course": "ME135",
            "professor": "Sundar",
        },
    )
    print(list(loader.load())[0])
