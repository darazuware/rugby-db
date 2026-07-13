#!/bin/bash
set -e

echo "--- 1. Integrating scraped Top 14 data into master CSV ---"
python3 scripts/integrate_top14_data.py

echo "--- 2. Generating player Markdown files (All Leagues) ---"
python3 scripts/generate_players.py

echo "--- 3. Verifying site integrity and links ---"
python3 scripts/verify_site_integrity.py

echo "--- 4. Updating standings (Standings only) ---"
python3 scripts/scrape_standings.py

echo "--- 5. All data updated successfully! ---"
echo "You can now check the dev server: http://localhost:3333"
