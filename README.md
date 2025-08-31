# phishi-analyzer
A Python-based project to analyze and visualize phishing URLs collected from OSINT feeds.

# Features
- Cleans and normalizes raw URL data
- Generates bar charts for top root domains and TLDs
- Exports a Markdown report with tables and embedded charts

# Usage
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m src.cli -i data\phishing_urls.csv -o reports -v
