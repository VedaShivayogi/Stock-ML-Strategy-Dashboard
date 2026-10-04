# Stock ML Strategy Dashboard

A modern full-stack application for predicting stock price direction using Machine Learning (Random Forest, XGBoost, LightGBM, Ensemble), with comprehensive Risk Analysis (Monte Carlo) and Explainability (SHAP).

## Tech Stack
- **Backend:** FastAPI, Pandas, scikit-learn, XGBoost, LightGBM, SHAP, yfinance.
- **Frontend:** React, TypeScript, Vite, Tailwind CSS, Recharts, TanStack Query.

## Setup Instructions

### 1. Backend (Python)
1. Ensure Python 3.9+ is installed.
2. Install the requirements:
   ```bash
   pip install -r requirements.txt
   pip install fastapi uvicorn cachetools
   ```

### 2. Frontend (Node.js)
1. Ensure Node.js 18+ is installed.
2. Navigate to the `frontend` directory and install dependencies:
   ```bash
   cd frontend
   npm install
   ```

## Running the Application
You can run both servers with a single command from the root directory:
```bash
npm install
npm run dev
```

Alternatively, you can run them separately:
- **Backend:** `python -m uvicorn backend.main:app --reload --port 8000`
- **Frontend:** `cd frontend && npm run dev`

## Customizing the Theme
The application uses Tailwind CSS with CSS variables for the color theme. To change the theme colors, edit the `:root` and `.dark` variables in `frontend/src/index.css`.
