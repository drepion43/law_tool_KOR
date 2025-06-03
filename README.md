# uv init
uv init --python=3.12
uv add -r requirements.txt
uv lock

# uv apply
uv venv --python 3.12
uv sync --frozen
source ./venv/bin/activate

# docker build
docker build -t law_mcp .