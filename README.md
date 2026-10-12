# HomeHub Support Demo

A small, deterministic OpenAI Chat Completions-compatible service for response
caching demos. It returns fictional HomeHub product-support answers without LLM
credentials or external dependencies. It uses Python's standard library.

## Run

```sh
docker run --rm --name homehub -p 127.0.0.1:8080:8080 \
  --read-only ghcr.io/danehans/homehub-support-demo:0.1.0
```

```sh
curl -sS http://127.0.0.1:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"homehub-support","messages":[{"role":"user","content":"How do I factory-reset my HomeHub X2?"}]}'
curl -sS http://127.0.0.1:8080/stats
```

`GET /healthz` returns readiness. `GET /stats` returns the number of backend
invocations since startup; health and statistics requests do not increment it.
Repeated completion requests increment it, making cache bypass visible.
Answers cover factory-reset and outdoor-use questions, with a fixed fallback.
Streaming requests return HTTP 400. This is a demo service with no authentication.

## Develop

```sh
python3 -m unittest -v
python3 server.py
docker build -t homehub-support-demo:local .
```

`PORT` overrides the server's default port, 8080, when running Python directly.

## Publish

GitHub Actions tests the service, builds an image, and tests the running
container. Pushes to `main` publish `latest` and a commit tag to GHCR. Release
tags such as `v0.1.0` publish version tags such as `0.1.0`. Published
images support Linux amd64 and arm64 and link to this repository's package.

```sh
git tag -a v0.1.0 -m 'Release 0.1.0'
git push danehans v0.1.0
```

The workflow uses `GITHUB_TOKEN` with `packages: write`; no additional registry
secret is needed. The package must be public so demos can pull it anonymously.

## License

Apache-2.0. See [NOTICE](NOTICE) for the original example attribution.
