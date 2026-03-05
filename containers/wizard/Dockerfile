FROM python:3.11-slim
ENV UDOS_ROOT=/app
ENV UDOS_ROOT_REQUIRED=1
WORKDIR /app
COPY . /app
CMD ["python", "-m", "wizard.server", "--host", "0.0.0.0", "--port", "8765"]
