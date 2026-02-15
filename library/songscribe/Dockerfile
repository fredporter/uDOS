# Songscribe/Groovebox companion container
# Build: docker build -t udos-songscribe ./library/songscribe
# Smoke: docker run --rm udos-songscribe

FROM python:3.11-slim

WORKDIR /app/library/songscribe
COPY . /app/library/songscribe

# Lightweight smoke at build-time: syntax/bytecode validation.
RUN python3 -m compileall -q /app/library/songscribe

CMD ["python3", "-m", "compileall", "-q", "/app/library/songscribe"]
