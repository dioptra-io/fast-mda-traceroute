#!/usr/bin/env bash
set -xeuo pipefail

fast-mda-traceroute --format=scamper-json $* | jq > fast_mda_traceroute.jsonl
eval "$(fast-mda-traceroute --print-command=scamper $*)" | jq > scamper.jsonl

diff --expand-tabs --minimal --side-by-side scamper.jsonl fast_mda_traceroute.jsonl > diff
