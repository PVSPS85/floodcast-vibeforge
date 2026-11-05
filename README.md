# 🌊 Floodcast — Real-Time ML River Discharge & Flood Forecasting
### **Built by Team VibeForge**

[![Next.js](https://img.shields.io/badge/Next.js-15.0-black?logo=next.js)](https://nextjs.org/)
[![CatBoost](https://img.shields.io/badge/Model-CatBoost%20Regressor-yellow)](https://catboost.ai/)
[![USGS NWIS](https://img.shields.io/badge/Data-USGS%20NWIS%20Telemetry-blue)](https://waterdata.usgs.gov/nwis)
[![Validation](https://img.shields.io/badge/Submission-PASS%20(7%2F7)-emerald)](validate_submission.py)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

---

## 👥 Team Information
* **Team Name:** Team VibeForge
* **Team Members:**
  * **Harshith Varanasi** (Lead Developer & Machine Learning Engineer) — [@PVSPS85](https://github.com/PVSPS85)
  * **Team VibeForge Collaborators**

---

## 📌 Approach Summary (Executive Overview)

**Floodcast** is an end-to-end hydrological machine learning and decision-support dashboard designed to anticipate extreme river discharge and flash flood events across the continental United States. Our approach leverages an extreme-weighted **CatBoost Regressor** trained on 12 years of real-time streamflow observations from the **USGS National Water Information System (NWIS)**, antecedent weather signals from the **Open-Meteo Historical Archive** (precipitation pulses, daily temperature swings, and root-zone soil moisture), and static catchment physiographic drivers from **USGS StreamStats**. By applying a custom 2.5× sample weighting scheme on the top 15% highest peak discharge events, our model specifically counters severe-event underprediction in power-law river basins while strictly respecting physical non-negative flow constraints. The interactive Next.js command dashboard visualizes live cause-and-effect hydrographs, National Weather Service flood stage alerts, and geographic gauge telemetry across 50 major US river basins.

---

## 🛠️ Tech Stack

### **Machine Learning & Data Pipeline (Python)**
* **CatBoost Regressor & LightGBM**: Gradient-boosted decision tree architecture with categorical station encoding, sample weighting, and loss function tailored to high-flow extreme tails.
* **scikit-learn & NumPy / Pandas**: Chronological time-series splitting, missing-value station median imputation, rolling lag aggregations, and evaluation scoring.
* **FastAPI & Uvicorn**: High-throughput REST API serving real-time model inference and historical telemetry.
* **USGS NWIS & Open-Meteo REST APIs**: Multi-station telemetry ingestion pipeline (`fetch_batch_data.py`).

### **Interactive Dashboard (Frontend)**
* **Next.js 15 (App Router)**: Hybrid server-side streaming API routes (`/api/stations/[station_id]`) and responsive client application.
* **React 18 & TypeScript**: Strict type safety across all hydrologic domain interfaces.
* **Tailwind CSS**: Modern National Weather Service-inspired dark dashboard with responsive grids.
* **React-Leaflet & Esri World Topo**: Interactive geographic gauge explorer with global pan/zoom and station search autocomplete.
* **Recharts**: Dual-axis Cause-and-Effect Hydrographs with inverted precipitation hyetographs and peak threshold lines.
* **Zustand**: Global state management handling real-time telemetry streaming, time-range slicing (7D / 30D / 90D), and dynamic extreme surge detection.
* **Framer Motion**: Fluid warning animations, emergency flood banners, and status transitions.

---

## 🚀 How to Run the Code

### 1. Prerequisites
* **Python**: 3.10+ (Recommended: Python 3.11)
* **Node.js**: 18.17+ or 20+
* **Package Managers**: `pip` and `npm`

---

### 2. Backend & Machine Learning Pipeline Setup

Clone the repository and install the Python dependencies:

```bash
# Clone the repository
git clone https://github.com/PVSPS85/floodcast-vibeforge.git
cd floodcast-vibeforge

# (Optional) Create and activate a virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install all ML and backend dependencies
pip install -r requirements.txt
```

#### Run Model Training & Generate Predictions:
```bash
# Train CatBoost model and export predictions.csv
python solution.py

# Verify submission compliance and data alignment (all 7 integrity tests)
python validate_submission.py

# Run full hackathon judging criteria audit (all 10/10 compliance rules)
python scripts/test_judging_criteria.py
```

#### (Optional) Run the FastAPI Telemetry Server:
```bash
# Launch FastAPI backend on port 8000
uvicorn src.models:app --reload --port 8000
```

---

### 3. Next.js Frontend Dashboard Setup

Navigate to the `floodcast-frontend/` directory and install the Node packages:

```bash
cd floodcast-frontend

# Install dependencies
npm install

# Start the Next.js development server
npm run dev
```

The Floodcast dashboard will be live at:
👉 **[http://localhost:3000](http://localhost:3000)** (or `http://localhost:3001`)

#### Build for Production:
```bash
npm run build
npm run start
```

---

## 📂 Repository Structure

```
floodcast-vibeforge/
├── README.md                            # Hackathon overview, team, tech stack, and instructions
├── requirements.txt                     # Pinned Python package dependencies
├── solution.py                          # Self-contained end-to-end model training script
├── predictions.csv                      # Output predictions for test.csv (36,500 rows)
├── model_card.md                        # Model card specifications and evaluation report
├── data/                                # Benchmark datasets
│   ├── train.csv                        # 219,150 historical observations (2010-2021)
│   └── test.csv                         # 36,500 test period records (2022-2023)
├── presentations/                       # 5-Slide Presentation Deck
│   ├── floodcast_presentation.pdf       # Formal 5-slide PDF presentation deck
│   └── floodcast_presentation.md        # Slide deck content and speaker notes
├── src/                                 # Core ML & data library
│   ├── data_loader.py                   # Clean multi-station ingestion & time-safe imputations
│   ├── features.py                      # 19 hydrological features (rolling rainfall, lags, proxy volumes)
│   ├── metrics.py                       # Competition evaluation suite (Overall RMSE, Extreme Peak RMSE, MAE, R²)
│   └── models.py                        # Unified CatBoost / LightGBM regressor wrapper
├── floodcast-frontend/                  # Next.js 15 interactive application
│   ├── app/
│   │   ├── api/stations/[station_id]/   # High-speed streaming CSV API route
│   │   │   └── route.ts
│   │   ├── layout.tsx                   # Global layout and dark theme styling
│   │   ├── page.tsx                     # Main dashboard page
│   │   └── globals.css                  # Tailwind styles and Leaflet customizations
│   ├── components/
│   │   ├── charts/CauseEffectChart.tsx  # Dual-axis precipitation & discharge hydrograph
│   │   ├── dashboard/                   # Catchment profiles, model health, extreme alerts
│   │   ├── layout/                      # Topbar and master shell
│   │   └── map/                         # Leaflet gauge map with NWS Esri Topo layer
│   ├── store/useStationStore.ts         # Zustand live client store
│   └── lib/api.ts                       # Typed client API integration
├── notebooks/                           # Exploratory Data Analysis & Hydrographs
│   ├── 01_eda_and_hydrographs.ipynb
│   └── 02_model_benchmarking.ipynb
├── fetch_batch_data.py                  # Multi-station NWIS & Open-Meteo harvester
├── validate_submission.py               # Official submission compliance validator
└── Dockerfile                           # Containerized reproducible execution environment
```

---

## 📊 Model Evaluation & Submission Verification

Run the built-in validator to inspect the submission file:

```bash
python validate_submission.py
```

```
=================================================================
RUNNING SUBMISSION INTEGRITY CHECKS: predictions.csv
=================================================================
1. [ PASS ] File Exists & Non-Empty -> (1,069,301 bytes)
2. [ PASS ] Exact Column Headers    -> ['station_id', 'date', 'discharge_cfs']
3. [ PASS ] Row Count Match         -> 36,500 rows
4. [ PASS ] No Null / NaN / Inf     -> 0 null values
5. [ PASS ] Non-Negative Discharge  -> Min: 0.00 cfs, Max: 870,435.35 cfs
6. [ PASS ] Date Format (YYYY-MM-DD)-> 2022-01-01 to 2023-12-31
7. [ PASS ] Station & Date Alignment-> Row-for-row alignment confirmed
=================================================================
>>> FINAL RESULT: ALL INTEGRITY CHECKS PASSED. READY FOR SUBMISSION. <<<
=================================================================
```
