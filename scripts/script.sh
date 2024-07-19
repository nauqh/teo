#!/bin/bash

echo "Starting scraping..."
python scrape.py

if [ $? -eq 0 ]; then
  echo "Scraping successful! Filtering data..."
  python filter.py

  if [ $? -eq 0 ]; then
    echo "Filtering successful! Uploading data..."
    python upload.py
  else
    echo "Filtering failed. Upload not run."
  fi
else
  echo "Scraping failed. Filtering and upload not run."
fi
