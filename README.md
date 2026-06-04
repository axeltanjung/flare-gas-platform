# 🔥 Oil & Gas Flare Gas Prediction & Emission Intelligence Platform

> AI-powered ESG analytics system for predicting flare gas emissions, assessing compliance risk, and optimizing operational efficiency in Oil & Gas operations.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![React](https://img.shields.io/badge/React-18.2-blue)
![XGBoost](https://img.shields.io/badge/XGBoost-2.0-orange)
![LightGBM](https://img.shields.io/badge/LightGBM-4.2-green)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Table of Contents

- [Project Background](#project-background)
- [Business Value](#business-value)
- [Domain Knowledge](#domain-knowledge)
- [System Architecture](#system-architecture)
- [AI/ML Architecture](#aiml-architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Dashboard Screenshots](#dashboard-screenshots)
- [MLflow Integration](#mlflow-integration)
- [Future Improvements](#future-improvements)

---

## Project Background

### What is Flare Gas?

Gas flaring is the controlled burning of natural gas that cannot be processed or sold during oil and gas production. It occurs at:

- **Production facilities** — during wellhead operations
- **Processing plants** — during gas separation and treatment
- **Refineries** — during operational upsets
- **Offshore platforms** — for safety pressure relief

### Why Does Flaring Happen?

1. **Safety pressure relief** — prevent dangerous overpressure conditions
2. **Equipment failures** — compressor trips, valve malfunctions
3. **Startup/shutdown operations** — transitional gas that can't be captured
4. **Lack of infrastructure** — no pipeline access for gas transportation
5. **Economic decisions** — gas deemed uneconomical to capture

### The Environmental Impact

- Global gas flaring burns approximately **144 billion cubic meters** of natural gas annually
- This releases over **400 million tonnes of CO₂ equivalent** emissions
- Equivalent to the total emissions of **France and Spain combined**
- Incomplete combustion releases methane (28x more potent than CO₂ as a greenhouse gas)

### Regulatory Pressure

- **World Bank Zero Routine Flaring by 2030** initiative
- **EU Emissions Trading System (ETS) Phase IV** — carbon pricing mechanisms
- **EPA 40 CFR 60** — US emission standards for oil and gas
- **OGMP 2.0** — Oil and Gas Methane Partnership reporting framework
- **Paris Agreement NDCs** — National Determined Contributions for emission reduction

---

## Business Value

| Benefit | Impact |
|---------|--------|
| Carbon Reduction | 15-35% emission reduction through operational optimization |
| Regulatory Compliance | Avoid $50K-$500K per violation in fines |
| ESG Score Improvement | Better ESG ratings attract lower-cost capital |
| Operational Efficiency | Identify energy waste worth $2-8M annually |
| Predictive Maintenance | Reduce emergency flaring by 40% with risk prediction |
| Sustainability Reporting | Automated carbon footprint calculation for ESG reports |
| Carbon Credits | Monetize verified emission reductions |

### ROI Analysis

- **Average implementation cost**: $200K-$500K
- **Annual savings from optimization**: $2-8M per major facility
- **Regulatory penalty avoidance**: $1-5M per year
- **Carbon credit revenue potential**: $500K-$2M per year

---

## Domain Knowledge

### Gas Flaring Process

```
Wellhead → Separator → Compressor → Pipeline
                ↓ (excess gas)
            Flare Header → Knock-Out Drum → Flare Stack
                                                ↓
                                         Combustion Zone
                                    (CO₂ + H₂O + heat + NOx)
```

### Emission Factors

| Gas Component | GWP (100-year) | Emission Factor |
|--------------|----------------|-----------------|
| CO₂ | 1 | 2.34 kg/m³ natural gas |
| Methane (CH₄) | 28 | Variable (slip rate) |
| N₂O | 265 | Trace amounts |
| Black Carbon | 900 (20-yr) | Incomplete combustion |

### Key Operational Triggers

1. **Compressor trips** — sudden gas routing to flare
2. **Separator liquid carry-over** — reduced gas processing capacity
3. **Pressure safety valve (PSV) relief** — emergency overpressure
4. **Process upsets** — temperature/pressure excursions
5. **Well testing** — exploration and production testing phases

### Combustion Efficiency

- **Good combustion** (>98%): Complete destruction, minimal methane slip
- **Moderate** (95-98%): Some methane escapes, elevated CO₂
- **Poor** (<95%): Significant methane slip, soot production
- Factors: wind speed, gas composition, pilot flame stability, flare tip design

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ESG       │ │Facility  │ │AI        │ │Compliance│   │
│  │Dashboard │ │Detail    │ │Insights  │ │& Risk    │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
└────────────────────────┬────────────────────────────────┘
                         │ REST API (JSON)
┌────────────────────────┴────────────────────────────────┐
│                   BACKEND (FastAPI)                       │
│  ┌──────────────┐ ┌───────────────┐ ┌───────────────┐  │
│  │Prediction    │ │Emission       │ │Explainability │  │
│  │Service       │ │Engine         │ │Module (SHAP)  │  │
│  └──────┬───────┘ └───────┬───────┘ └───────┬───────┘  │
│         │                  │                  │          │
│  ┌──────┴──────────────────┴──────────────────┴──────┐  │
│  │              ML Model Registry                     │  │
│  │  ┌─────────┐ ┌──────────┐ ┌─────────────────┐    │  │
│  │  │XGBoost  │ │LightGBM  │ │GBClassifier     │    │  │
│  │  │(Volume) │ │(Emission)│ │(Risk)           │    │  │
│  │  └─────────┘ └──────────┘ └─────────────────┘    │  │
│  └───────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │SQLite DB │  │MLflow    │  │CSV Data / Synthetic  │  │
│  │          │  │Tracking  │  │Generator             │  │
│  └──────────┘  └──────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## AI/ML Architecture

### Model 1: XGBoost Regression — Flare Gas Volume Prediction

- **Target**: `flare_gas_volume` (continuous, m³)
- **Features**: 35+ operational, process, and environmental features
- **Metrics**: RMSE, MAE, R², MAPE
- **Explainability**: SHAP feature importance + local explanations

### Model 2: LightGBM Regression — Emission Prediction

- **Target**: `co2_emission_equivalent` (continuous, kg CO₂e)
- **Features**: Same feature set + engineered interactions
- **Calibration**: Uncertainty estimation via staged predictions
- **Feature Interaction**: Correlation analysis of top features

### Model 3: Gradient Boosting Classifier — Risk Prediction

- **Target**: `flare_event_risk` (binary: 0/1)
- **Imbalance handling**: SMOTE oversampling
- **Threshold tuning**: Precision-recall optimization
- **Metrics**: F1, ROC-AUC, Precision, Recall

### Emission Estimation Engine

- Physics-based CO₂ equivalent calculation
- Methane slip estimation (GWP-weighted)
- Emission intensity per production unit
- Energy waste quantification (MJ/MWh)

---

## Features

- **Batch Prediction Pipeline** — Process historical data for emission forecasting
- **5 Target Variables** — Volume, CO₂e, risk, intensity, compliance level
- **SHAP Explainability** — Understand why emissions increase
- **Compliance Monitoring** — EPA, EU ETS, OGMP 2.0, World Bank standards
- **Facility Ranking** — Compare emission performance across sites
- **Optimization Engine** — AI-driven operational recommendations
- **ESG Reporting** — Automated carbon footprint calculations
- **Modern Dashboard** — Dark-mode enterprise analytics UI

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI, Pandas, NumPy |
| ML Models | XGBoost, LightGBM, Scikit-learn, SHAP |
| Experiment Tracking | MLflow 2.9 |
| Frontend | React 18, Vite, TailwindCSS, Recharts |
| Animation | Framer Motion |
| Database | SQLite |
| Deployment | Docker, docker-compose, Nginx |

---

## Project Structure

```
flare-gas-platform/
├── backend/
│   ├── api/
│   │   ├── main.py                    # FastAPI application
│   │   └── routes/
│   │       ├── predict.py             # Prediction endpoints
│   │       ├── emissions.py           # Emission report endpoints
│   │       ├── compliance.py          # Compliance status
│   │       ├── explain.py             # SHAP explanations
│   │       └── facilities.py          # Facility data
│   ├── models/
│   │   └── schemas.py                 # Pydantic request/response models
│   ├── training/
│   │   ├── preprocessor.py            # Data preprocessing pipeline
│   │   ├── trainer_xgboost.py         # XGBoost training
│   │   ├── trainer_lightgbm.py        # LightGBM training
│   │   ├── trainer_classifier.py      # Classification training
│   │   └── pipeline.py                # Full training orchestration
│   ├── emissions/
│   │   ├── calculator.py              # CO₂e calculation engine
│   │   ├── engine.py                  # Emission processing
│   │   └── compliance.py              # Regulatory compliance checker
│   ├── explainability/
│   │   └── shap_explainer.py          # SHAP analysis module
│   ├── services/
│   │   └── prediction_service.py      # Inference service
│   ├── utils/
│   │   ├── config.py                  # Settings management
│   │   └── logger.py                  # Logging setup
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── main.jsx                   # React entry
│   │   ├── App.jsx                    # Router configuration
│   │   ├── index.css                  # Tailwind + custom styles
│   │   ├── components/
│   │   │   └── Layout.jsx             # Sidebar navigation
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx          # ESG overview
│   │   │   ├── FacilityDetail.jsx     # Facility analysis
│   │   │   ├── AIInsights.jsx         # SHAP explainability
│   │   │   ├── Compliance.jsx         # Regulatory monitoring
│   │   │   └── Optimization.jsx       # Reduction recommendations
│   │   └── services/
│   │       └── api.js                 # Axios API client
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── package.json
├── data/
│   └── synthetic_flare_gas_generator.py
├── docker/
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   ├── mlflow.Dockerfile
│   └── nginx.conf
├── models/                            # Trained model artifacts
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 20+ (for frontend development)

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/your-org/flare-gas-platform.git
cd flare-gas-platform

# Copy environment file
cp .env.example .env

# Generate synthetic dataset
cd data
python synthetic_flare_gas_generator.py --rows 150000
cd ..

# Train models
python -m backend.training.pipeline --data ./data/flare_gas_dataset.csv --models ./models

# Launch with Docker
docker-compose up --build
```

### Access Points

| Service | URL |
|---------|-----|
| Dashboard | http://localhost:3000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| MLflow UI | http://localhost:5000 |
| Health Check | http://localhost:8000/health |

### Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn backend.api.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

---

## API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Service health check |
| POST | `/predict/flare-volume` | Predict flare gas volume |
| POST | `/predict/emissions` | Predict CO₂ equivalent emissions |
| POST | `/predict/risk` | Predict flare event risk |
| GET | `/emission/report` | Generate emission report |
| GET | `/facility/{id}` | Get facility details |
| GET | `/compliance/status` | Check compliance status |
| POST | `/explain/emission` | Get SHAP explanation |

### Example Request

```bash
curl -X POST http://localhost:8000/predict/flare-volume \
  -H "Content-Type: application/json" \
  -d '{
    "gas_pressure": 55.2,
    "gas_flow_rate": 320.5,
    "methane_ratio": 0.85,
    "ethane_ratio": 0.08,
    "propane_ratio": 0.04,
    "combustion_temperature": 890.0,
    "ambient_temperature": 28.5,
    "wind_speed": 4.2,
    "humidity": 65.0,
    "upstream_pressure": 78.3,
    "separator_pressure": 42.1,
    "compressor_load": 72.0,
    "valve_opening_percentage": 45.0,
    "production_rate": 1200.0
  }'
```

### Example Response

```json
{
  "predicted_volume_m3": 245.67,
  "confidence_interval_lower": 197.52,
  "confidence_interval_upper": 293.82,
  "model_version": "xgboost-v1.0"
}
```

---

## MLflow Integration

### Experiment Tracking

```bash
# Start MLflow server
mlflow server --host 0.0.0.0 --port 5000

# Run training with MLflow logging
python -m backend.training.pipeline --mlflow-uri http://localhost:5000

# With hyperparameter tuning
python -m backend.training.pipeline --tune --mlflow-uri http://localhost:5000
```

### Tracked Metrics

- **XGBoost**: RMSE, MAE, R², MAPE
- **LightGBM**: RMSE, MAE, R², MAPE, uncertainty estimates
- **Classifier**: Accuracy, F1, ROC-AUC, Precision, Recall
- **Artifacts**: Feature importance CSVs, SHAP values

---

## Future Improvements

| Category | Enhancement |
|----------|-------------|
| Data Sources | Satellite-based emission detection (TROPOMI, GHGSat) |
| IoT Integration | Real-time sensor data from flare stacks |
| Advanced ML | Reinforcement learning for optimal control strategies |
| Digital Twin | Physics-informed neural networks for combustion modeling |
| Carbon Trading | Integration with voluntary carbon credit registries |
| Edge Computing | On-premise inference for low-latency safety systems |
| NLP | Automated regulatory document parsing and compliance mapping |
| Computer Vision | Flame analysis from thermal imaging cameras |
| Federated Learning | Multi-facility model training without data sharing |
| LLM Integration | Natural language querying of emission databases |

---

## License

MIT License — See [LICENSE](LICENSE) for details.

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/emission-optimizer`)
3. Commit changes (`git commit -m 'Add emission reduction algorithm'`)
4. Push to branch (`git push origin feature/emission-optimizer`)
5. Open a Pull Request

---

*Built for ESG analytics professionals, ML engineers, and sustainability teams in the Energy sector.*
