# TTC-delay-prediction

### Group 4 - CSCI 3052U

## Project Overview

This project uses historical Toronto Transit Commission (TTC) open data to study and predict reported transit delay minutes. The current modelling scope focuses on bus and streetcar delay records.

The project is developed as part of CSCI 3052U - Machine Learning at Ontario Tech University.

## Repository Structure

```text
ttc-delay-prediction/
├── config/          # Project configuration and reproducibility settings
├── data/
│   ├── raw/         # Raw TTC data (not tracked by Git)
│   └── processed/   # Cleaned/processed data (not tracked by Git)
├── docs/            # Project documentation and proposal
├── notebooks/       # Data profiling and exploratory analysis notebooks
├── src/
│   ├── data/        # Data loading and cleaning code
│   └── features/    # Feature engineering code
├── tests/           # Project tests
├── README.md
└── requirements.txt
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/dminhpham/ttc-delay-prediction.git
cd ttc-delay-prediction
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```
