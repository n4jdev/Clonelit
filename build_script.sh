#!/bin/bash

# Install Playwright and browsers
pip install playwright
playwright install chromium
mkdir -p playwright-browsers
mv /home/vcap/app/.cache/ms-playwright playwright-browsers/
