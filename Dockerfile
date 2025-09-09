FROM futureys/claude-code-selenium-python:20250728092000
COPY pyproject.toml uv.lock /workspace/
RUN uv sync
COPY . /workspace/
