FROM python:3.14-slim
WORKDIR /app
ARG COMMIT
LABEL org.opencontainers.image.revision=$COMMIT
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY app.py build-metadata.json /app/
RUN python -c 'import os; from app import read_json, validate_build; m=validate_build(read_json("/app/build-metadata.json")); assert m["commit"] == os.environ["COMMIT"]'
USER 65532:65532
EXPOSE 8080
ENTRYPOINT ["python", "/app/app.py", "--host", "0.0.0.0"]
