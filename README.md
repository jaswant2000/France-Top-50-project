# France Top 50 Playlist Analysis

## Deliverables
- `France_Top50_Research_Paper.docx` — research paper with data validation, EDA, insights, limitations, and recommendations
- `France_Top50_Executive_Summary.docx` — stakeholder summary
- `app.py` — Streamlit dashboard
- `eda.py` — data quality checks and exploratory charts
- `Atlantic_France.csv` — supplied source data
- `requirements.txt` — dependencies

## Run locally
1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Install dependencies:
   `pip install -r requirements.txt`
4. Run data checks and charts:
   `python eda.py`
5. Start the dashboard:
   `streamlit run app.py`

## Dashboard modules
- Compliance overview and rank-tier profile
- Explicit vs non-explicit comparisons
- Release-format analysis
- Duration buckets and album size vs popularity
- Data-quality checks and filtered CSV export

## Important notes
The CSV has 27,800 records across 555 dates. One date has 100 records instead of 50; 19 exact duplicate rows and one missing cell were found. Investigate anomalies before treating metrics as final. The dataset is observational; explicit flags and popularity scores do not directly measure cultural sensitivity, legal compliance, or causal audience preference.
