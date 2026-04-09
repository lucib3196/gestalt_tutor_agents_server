# Question Generator

This module generates complete question packages by classifying prompts and producing the HTML and server code needed to run them.

- `gestalt_graph.py`: Orchestrates the full question-generation workflow.
- `initialization.py`: Initializes the shared model and vector store used by the graphs.
- `question_metadata_graph.py`: Generates question metadata such as title, topics, type, and adaptive status.
- `question_html_graph.py`: Produces the student-facing `question.html`.
- `solution_html_graph.py`: Produces the instructor-facing `solution.html`.
- `server_js_graph.py`: Generates and validates the JavaScript backend implementation.
- `server_py_graph.py`: Generates and validates the Python backend implementation.
