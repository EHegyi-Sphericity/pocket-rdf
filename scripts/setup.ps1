python -m venv .venv
.\.venv\Scripts\activate
python.exe -m pip install --upgrade pip
pip install .[dev]
pre-commit install --hook-type pre-commit --hook-type commit-msg
