import os
import logging
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("ml-train")

def train():
    if not os.path.exists("ml/features.csv"):
        logger.error("Features file not found. Run feature_engineering.py first.")
        return

    logger.info("Loading features for training...")
    
    # Select features and target
    X = df[['avg_usage', 'growth_rate', 'variability', 'peak_ratio']]
    y = df['congestion_risk']
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    logger.info(f"Model Training Complete. Accuracy: {acc:.2f}")
    logger.info("\nClassification Report:\n" + classification_report(y_test, y_pred))
    
    # Save
    joblib.dump(model, "ml/model.pkl")
    logger.info("Model saved successfully to ml/model.pkl")

if __name__ == "__main__":
    train()
