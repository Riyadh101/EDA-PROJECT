# EDA-PROJECT — Russia-Ukraine War Losses: Data Analysis Project

An individual data analysis project covering the full workflow: EDA, data cleaning, visualizations, and a bilingual (English/Arabic) interactive Streamlit dashboard with a live map.

## 📊 About

This project analyzes real, daily-updated data documenting officially reported Russian losses (personnel and military equipment) in the Russia-Ukraine war, from 2022-02-25 through the latest available update.

**Data source:**
[PetroIvaniuk/2022-Ukraine-Russia-War-Dataset](https://github.com/PetroIvaniuk/2022-Ukraine-Russia-War-Dataset) (official data from the General Staff of the Armed Forces of Ukraine, also available on [Kaggle](https://www.kaggle.com/datasets/piterfm/2022-ukraine-russian-war)).

## 📁 Project Structure

```
EDA-PROJECT/
├── EDA python.ipynb          # Full Jupyter notebook (EDA + cleaning + analysis + insights)
├── clean_data.csv            # Cleaned dataset produced by the notebook
├── data_raw/                 # Original raw data (JSON) before cleaning
│   ├── personnel.json
│   └── equipment.json
├── streamlit_app/            # Streamlit dashboard folder (multi-page app)
│   ├── app.py                # Home/Overview page: banner, KPI cards, weekly comparison, annotated timeline
│   ├── common.py             # Shared code: data loading, translations (EN/AR), sidebar filters
│   ├── pages/
│   │   ├── 1_📊_Deep_Analysis.py     # Category comparisons, correlation heatmap, predictive model
│   │   └── 2_🗺️_Interactive_Map.py   # Searchable + animated map of combat directions
│   ├── clean_data.csv        # Cleaned dataset used as an offline fallback
│   └── requirements.txt      # Required libraries to run the app
└── README.md                 # This file
```

## 🚀 How to Run

### 1) Jupyter Notebook

```bash
pip install pandas numpy matplotlib seaborn jupyter
jupyter notebook "EDA python.ipynb"
```

The notebook automatically loads the data directly from GitHub (no manual downloads needed), then runs all EDA, cleaning, analysis and visualization steps (7 charts), finishing by saving `clean_data.csv`.

### 2) Streamlit App

```bash
cd streamlit_app
pip install -r requirements.txt
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`. Use the sidebar to switch pages (**Overview**, **Deep Analysis**, **Interactive Map**) and to change the **Language / اللغة** (English/Arabic) — this choice stays in sync across pages. For Light/Dark mode, use Streamlit's own built-in theme switcher (☰ menu → Settings → Theme).

**Dashboard features:**
- Multi-page layout: Overview, Deep Analysis, Interactive Map
- Sidebar: dataset description, live/offline data status, and filters — Start/End date pickers, a **slider** (minimum daily personnel losses), a **multiselect** (equipment categories, each with its own icon), and a **dropdown** (single category for the trend chart)
- Custom KPI cards with color-coded borders, a gradient banner header, and a "This Week vs. Last Week" comparison
- An annotated cumulative-losses timeline marking major reported battles
- 5+ interactive Plotly charts (multi-category comparison, single-category daily trend, totals bar chart, colorblind-friendly correlation heatmap)
- An **interactive, searchable, animated map** of reported combat directions (month-by-month playback), geocoded from the free-text `greatest_losses_direction` column
- A simple linear-regression **predictive model** with an adjustable forecast horizon
- **Live data**: fetches the latest data directly from GitHub on load (refreshed hourly), with automatic fallback to the local `clean_data.csv` snapshot if offline
- Light/Dark mode: use Streamlit's own built-in theme switcher (☰ menu → Settings → Theme) — no custom toggle needed

### Sidebar filters explained

| Filter | Type | What it does |
|---|---|---|
| **Start Date / End Date** | Date pickers | Restricts every chart, KPI, and the map to only the days within this range. |
| **Equipment Categories to Compare** | Multiselect | Choose which equipment types appear in the multi-line comparison chart and the correlation heatmap on the Deep Analysis page. |
| **Equipment Category for Trend Chart** | Dropdown | Picks a single category to show its own daily-new-losses bar chart. |
| **Minimum Daily Personnel Losses** | Slider | Filters the whole dashboard down to days where at least this many personnel losses were reported *on that single day* (not the running total). Raising it isolates unusually severe days — e.g. major battles — so you can see how the charts and map narrow down to just those days. Set it back to 0 to see all days again. |

All filters apply across every page (Overview, Deep Analysis, Interactive Map) since they live in the shared sidebar.

## 🔎 Main Questions Explored

- How did personnel and equipment losses evolve over time?
- Which equipment categories were hit hardest, and how are they related to each other?
- Which days were "outliers" in terms of loss volume?
- What is the relationship between daily personnel losses and daily equipment losses?
- Where are the most frequently reported combat directions located geographically?

## ⚠️ Limitations

The data relies on a single official source (the Ukrainian side), with no equivalent data from the Russian side for cross-verification. See the "Limitations" section at the end of the notebook for full details.

## 🛠️ Libraries Used

`pandas` · `numpy` · `matplotlib` · `seaborn` · `streamlit` · `plotly`

---
**Repository:** EDA-PROJECT
**GitHub:** [github.com/Riyadh101](https://github.com/Riyadh101)
