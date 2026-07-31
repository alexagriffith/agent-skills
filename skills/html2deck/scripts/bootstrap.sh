#!/usr/bin/env bash
# Install html2deck runtime deps + Chromium for Playwright.
set -euo pipefail
python3 -m pip install -U pip
python3 -m pip install playwright python-pptx Pillow pytest
python3 -m playwright install chromium
echo "html2deck bootstrap complete. Try: python3 slice.py --help"
