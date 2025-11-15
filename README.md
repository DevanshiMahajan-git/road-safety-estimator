# Road Safety Estimator

A Streamlit-based tool for estimating the cost of road safety interventions using real-world data and IRC standards.

## 🚧 Problem

Planners and engineers often lack quick, explainable tools to estimate the cost of safety interventions. This tool brings transparency and standardization using CPWD/GeM rates and IRC guidelines.

## ✅ Features

- Upload intervention CSVs
- Itemized cost breakdown with IRC references
- Sensitivity analysis (±10%)
- Bar and pie chart visualizations
- Scenario comparison (Plan A vs Plan B)
- Multi-plan comparison across multiple CSVs
- Downloadable reports

## 🛠️ Tech Stack

- Python + Streamlit
- Pandas + Matplotlib
- CPWD/GeM rates (2025)
- Responsive UI with blue/green theme

## 📂 Folder Structure
road-safety-estimator/
│
├── app.py                  # Your Streamlit app
├── rates.csv               # Official rates used in the estimator
├── README.md               # Overview of the project
│
├── test-data/              # Folder for sample CSVs used for testing
│   ├── planA.csv
│   ├── planB.csv
│   ├── interventions.csv
│
└── .streamlit/             # Streamlit config folder 


## 🚀 How to Run

1. Install dependencies: pip install streamlit pandas matplotlib

2. Run the app: streamlit run app.py

3. Upload a CSV file and explore the dashboard.

## 📊 Sample Data

Sample intervention files are available in the `test-data/` folder.
For multiple scenario , use all 3 csv files.

## 🔭 Future Scope

- Live price scraping from CPWD/GeM
- Expansion to all IRC interventions
- Integration with public health and crash data

## 👤 Author

Devanshi Mahajan — [GitHub Profile](https://github.com/DevanshiMahajan-git)