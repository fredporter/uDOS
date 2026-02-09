FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir mistral-vibe

HEALTHCHECK --interval=60s --timeout=5s --retries=3 \
    CMD python -c "import importlib; importlib.import_module('mistral_vibe')" || exit 1

CMD ["vibe"]
