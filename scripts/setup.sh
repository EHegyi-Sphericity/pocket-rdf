python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install .[dev]
pre-commit install --hook-type pre-commit --hook-type commit-msg
