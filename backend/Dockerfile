FROM python:3.12.15-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv==0.13.5 && uv sync --frozen --no-dev --no-install-project
COPY app ./app
RUN uv sync --frozen --no-dev
RUN useradd --create-home --uid 10001 lumen && chown -R lumen:lumen /app
USER lumen
EXPOSE 8000
CMD [".venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
