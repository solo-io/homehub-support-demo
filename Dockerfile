FROM python:3.12-alpine
LABEL org.opencontainers.image.source="https://github.com/solo-io/homehub-support-demo" \
      org.opencontainers.image.licenses="Apache-2.0"
WORKDIR /app
COPY server.py LICENSE NOTICE ./
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
USER 65532:65532
EXPOSE 8080
HEALTHCHECK --interval=3s --timeout=3s --retries=20 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2)"
CMD ["python", "server.py"]
