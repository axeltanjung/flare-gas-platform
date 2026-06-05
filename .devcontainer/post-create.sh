#!/bin/bash
set -e

echo "=========================================="
echo "  FlareGas Intelligence Platform Setup"
echo "=========================================="

echo ""
echo "[1/6] Installing backend dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt
echo "✓ Backend dependencies installed"

echo ""
echo "[2/6] Installing frontend dependencies..."
cd frontend
npm install
cd ..
echo "✓ Frontend dependencies installed"

echo ""
echo "[3/6] Generating synthetic flare gas dataset..."
python data/synthetic_flare_gas_generator.py --rows 150000 --output ./data
echo "✓ Dataset generated (150K rows)"

echo ""
echo "[4/6] Training ML models..."
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -m backend.training.pipeline --data ./data/flare_gas_dataset.csv --models ./models
echo "✓ Models trained and saved"

echo ""
echo "[5/6] Verifying API startup..."
python -c "from backend.api.main import app; print('✓ FastAPI app verified')"

echo ""
echo "[6/6] Building frontend production bundle..."
cd frontend
npm run build
cd ..
echo "✓ Frontend build complete"

echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "  Available commands:"
echo "    Backend:   uvicorn backend.api.main:app --reload --port 8000"
echo "    Frontend:  cd frontend && npm run dev"
echo "    Docker:    docker-compose up --build"
echo "    MLflow:    mlflow server --host 0.0.0.0 --port 5000"
echo ""
echo "  Ports:"
echo "    8000 → FastAPI Backend (Swagger: /docs)"
echo "    5173 → Vite Dev Server"
echo "    3000 → Frontend (Nginx, Docker only)"
echo "    5000 → MLflow UI"
echo "=========================================="
