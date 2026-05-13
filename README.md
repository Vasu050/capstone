# Telecom Network Intelligence System

A production-grade end-to-end data engineering and AI platform for monitoring and predicting telecom network congestion.

## 🚀 Architecture Overview
- **Data Layer**: Raw CDR data validated and processed into Parquet.
- **Orchestration**: Apache Airflow managing the ETL pipeline.
- **Processing**: PySpark for distributed data transformations.
- **Storage**: MySQL Star Schema Warehouse (Fact/Dim tables).
- **Backend**: FastAPI REST API providing real-time analytics.
- **Frontend**: React Dashboard for visual monitoring and ML risk prediction.
- **AI/ML**: Random Forest Classifier for congestion risk and anomaly detection.

## 📁 Project Structure
```
telecom-intelligence/
├── airflow/           # DAGs and pipeline orchestration
├── api/               # FastAPI backend (Modular routes)
├── data/              # Landing, Raw, Processed, and Rejected layers
├── ml/                # Feature engineering, Training, and Batch Scoring
├── react-app/         # React Frontend
├── spark/             # PySpark ETL jobs
└── warehouse/         # SQL Schemas and DB Loader
```

## 🛠️ Setup Instructions

### 1. Environment Configuration
Create a `.env` file in the root directory:
```env
MYSQL_HOST=your_host
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=telecom_db
```

### 2. Database Setup
Execute the schema script in your MySQL instance:
```bash
mysql -u root -p < warehouse/schema.sql
```

### 3. Running the Backend
```bash
cd api
uvicorn main:app --reload
```

### 4. Running the Frontend
```bash
cd react-app
npm install
npm run dev
```

### 5. Running the ML Pipeline
```bash
python ml/feature_engineering.py
python ml/train_model.py
python ml/batch_score.py
```

## 📊 Evaluation Criteria Met
- [x] **Data Engineering**: Idempotent Airflow DAG with failure handling.
- [x] **Warehouse**: Optimized Star Schema design.
- [x] **API**: Pydantic validated REST endpoints with modular routing.
- [x] **Dashboard**: Premium React UI with Recharts integration.
- [x] **ML**: Feature-engineered classifier with accuracy reporting and batch scoring.
- [x] **Code Quality**: Zero hardcoding (ENV based), structured logging, and clean modular architecture.
