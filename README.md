# fast-mda-traceroute

[![Coverage][coverage-badge]][coverage-url]
[![Docker Status][docker-workflow-badge]][docker-workflow-url]
[![PyPI Status][pypi-workflow-badge]][pypi-workflow-url]
[![Tests Status][tests-workflow-badge]][tests-workflow-url]
[![PyPI][pypi-badge]][pypi-url]

`fast-mda-traceroute` is an experimental multipath traceroute tool based on [caracal][caracal]
and [diamond-miner][diamond-miner]. It aims to provide a faster alternative to [paris-traceroute][paris-traceroute]
and [scamper][scamper] for running one-off measurements. It runs on Linux and macOS, on x86-64 and ARM64 systems.

🚧 This tool is highly experimental, may not always work, and its interface is subject to change from one commit to
another.

## Quickstart

### Docker

```bash
docker run ghcr.io/dioptra-io/fast-mda-traceroute --help
```

### Python

You can use pip, or [pipx][pipx] to install `fast-mda-traceroute` in a dedicated virtual environment:

```bash
pipx install fast-mda-traceroute
fast-mda-traceroute --help
```

**Apple Silicon:** we do not (yet) provide a macOS ARM64 binary wheel for Caracal and Diamond-Miner. If you use such as
a system you must have a C++ compiler installed and the installation time might be a little longer (~5 minutes on a M1
MacBook Air).

## Usage

```bash
fast-mda-traceroute --help
fast-mda-traceroute example.org
```

`fast-mda-traceroute` outputs log messages to `stderr` and measurement results to `stdout`.

## Development

```bash
poetry install
poetry run fast-mda-traceroute --help
```

```bash
docker build -t fast-mda-traceroute .
docker run fast-mda-traceroute --help
```

[caracal]: https://github.com/dioptra-io/caracal

[diamond-miner]: https://github.com/dioptra-io/diamond-miner

[paris-traceroute]: https://paris-traceroute.net

[pipx]: https://github.com/pypa/pipx/

[scamper]: https://www.caida.org/catalog/software/scamper/

[coverage-badge]: https://img.shields.io/codecov/c/github/dioptra-io/fast-mda-traceroute?logo=codecov&logoColor=white

[coverage-url]: https://codecov.io/gh/dioptra-io/fast-mda-traceroute

[docker-workflow-badge]: https://img.shields.io/github/workflow/status/dioptra-io/fast-mda-traceroute/Docker?logo=github&label=docker

[docker-workflow-url]: https://github.com/dioptra-io/fast-mda-traceroute/actions/workflows/docker.yml

[pypi-workflow-badge]: https://img.shields.io/github/workflow/status/dioptra-io/fast-mda-traceroute/PyPI?logo=github&label=pypi

[pypi-workflow-url]: https://github.com/dioptra-io/fast-mda-traceroute/actions/workflows/pypi.yml

[tests-workflow-badge]: https://img.shields.io/github/workflow/status/dioptra-io/fast-mda-traceroute/Tests?logo=github&label=tests

[tests-workflow-url]: https://github.com/dioptra-io/fast-mda-traceroute/actions/workflows/tests.yml

[pypi-badge]: https://img.shields.io/pypi/v/fast-mda-traceroute?logo=pypi&logoColor=white

[pypi-url]: https://pypi.org/project/fast-mda-traceroute/
