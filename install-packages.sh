#!/bin/bash
source .env
pip install -r requirements.txt

# git clone https://github.com/rkern/line_profiler.git && find line_profiler -name '*.pyx' -exec cython {} \; && cd line_profiler && pip install . && cd .. && rm -rf line_profiler
