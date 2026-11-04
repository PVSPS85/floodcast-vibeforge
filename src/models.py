from catboost import CatBoostRegressor
import numpy as np

def train_catboost(X_train, y_train, categorical_features=None):
    """
    Trains a CatBoost Regressor on the engineered features.
    """
    print("Training CatBoost model...")
    
    model = CatBoostRegressor(
        iterations=1000,
        learning_rate=0.05,
        depth=6,
        loss_function='RMSE',
        verbose=100,
        random_seed=42
    )
    
    # Train the model
    model.fit(
        X_train, 
        y_train, 
        cat_features=categorical_features
    )
    
    print("Training complete.")
    return model

def make_predictions(model, X_test):
    """
    Generates predictions and applies the strict hackathon constraint:
    No negative river discharge values allowed.
    """
    preds = model.predict(X_test)
    # Clip all negative predictions to exactly 0.0 to prevent scoring errors
    preds_clipped = np.maximum(0.0, preds)
    return preds_clipped

if __name__ == "__main__":
    print("models.py syntax is correct!")
    