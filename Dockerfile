FROM astral/uv:python3.14-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

# Install dependencies from pyproject.toml / uv.lock
RUN uv sync

# Run FastAPI with uvicorn
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Copy your FastAPI project
COPY . .