#!/bin/bash

echo "Starting scraping..."
python scrape.py

if [ $? -eq 0 ]; then
  echo "Scraping successful! Filtering data..."
  python filter.py
else
  echo "Scraping failed. Filtering not run."
fi
