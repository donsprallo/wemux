<div align="center">

# Wemux

A message bus for event driven web apps.

[![Tests](https://github.com/donsprallo/wemux/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/donsprallo/wemux/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

In Development...

## Development

Install all dependencies with [pdm](https://pdm-project.org).

```bash
pdm install
```

Run tests with [pytest](https://docs.pytest.org).

```bash
pdm run pytest
```

Run tests with coverage.

```bash
pdm run pytest --cov=wemux
```

Create coverage report. Replace `TYPE` with `term`, `html`, `xml`, `json`.

```bash
pdm run pytest --cov=wemux --cov-report=TYPE
```

Run linter with [ruff](https://docs.astral.sh/ruff).

```bash
pdm run ruff --check
```