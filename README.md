# Road Safety Estimator

A Streamlit-based tool for estimating the cost of road safety interventions using real-world data and IRC standards.

## 🚧 Problem

Planners and engineers often lack quick, explainable tools to estimate the cost of safety interventions. This tool brings transparency and standardization using CPWD/GeM rates and IRC guidelines.

## ✅ Features

- Upload intervention CSVs
- Itemized cost breakdown with IRC references
- AI flags for anomalies (High Cost, Missing IRC Code, Unusual Quantity, etc.)
- Styled tables with blue/green gradients for readability
- Sensitivity analysis (±10%)
- Bar and pie chart visualizations (NaN-safe)
- Scenario comparison (Plan A vs Plan B)
- Multi-plan comparison across multiple CSVs
- Downloadable reports
- Future scope panel for planned enhancements


## 🛠️ Tech Stack

- Python + Streamlit
- Pandas + Matplotlib
- CPWD/GeM rates (2025)
- Responsive UI with blue/green theme

## 📂 Folder Structure
estimator/
│
├── app.py                  # Final Streamlit app (updated with AI flags, styled tables, NaN-safe charts)
├── rates.csv               # Official rates used in the estimator
├── README.md               # Project overview and instructions
│
├── test-data/              # Folder for sample/test CSVs
│   ├── planA.csv           # Example scenario A
│   ├── planB.csv           # Example scenario B
│   ├── interventions.csv   # Original sample interventions
│   └── test_interventions.csv   # NEW test file for validation of flags
│
└── streamlit/              # Streamlit cache/config folder (auto-generated)


## 🚀 How to Run

1. Install dependencies: pip install streamlit pandas matplotlib

2. Run the app: streamlit run app.py

3. Upload a CSV file and explore the dashboard.

## 📊 Sample Data

Sample intervention files are available in the `test-data/` folder.
For multiple scenario , use all csv files.

## 🔭 Future Scope

- Live price scraping from CPWD/GeM
- Expansion to all IRC interventions
- Integration with public health and crash data
- Predictive AI for cost overruns
- Clustering interventions by ROI or risk

## 👤 Author

Devanshi Mahajan — [GitHub Profile](https://github.com/DevanshiMahajan-git)