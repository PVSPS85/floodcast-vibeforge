import pandas as pd
from src.data_loader import load_data
from src.features import build_features
from src.models import train_catboost, make_predictions

def main():
    print("=== Phase 1: Loading Data ===")
    train_df, test_df = load_data("data")
    
    print("\n=== Phase 2: Feature Engineering ===")
    train_feat = build_features(train_df)
    test_feat = build_features(test_df)
    
    # Define columns to drop for training (identifiers and target)
    drop_cols = ["date", "discharge_cfs"]
    
    # Align features between train and test
    features = [c for c in train_feat.columns if c not in drop_cols]
    
    X_train = train_feat[features]
    y_train = train_feat["discharge_cfs"]
    
    X_test = test_feat[features]
    
    # Dynamically identify all string columns (station_id, station_name, state)
    cat_features = list(X_train.select_dtypes(include=['object', 'category']).columns)

    print("\n=== Phase 3: Model Training ===")
    model = train_catboost(X_train, y_train, categorical_features=cat_features)
    
    print("\n=== Phase 4: Generating Predictions ===")
    test_preds = make_predictions(model, X_test)
    
    # Create the exact 3-column output required by the hackathon
    submission = pd.DataFrame({
        "station_id": test_feat["station_id"],
        "date": test_feat["date"],
        "discharge_cfs": test_preds
    })
    
    # Ensure exact formatting constraints
    submission["date"] = pd.to_datetime(submission["date"]).dt.strftime("%Y-%m-%d")
    
    # Save the final file
    submission.to_csv("predictions.csv", index=False)
    
    print("\nSUCCESS: 'predictions.csv' generated successfully!")
    print(f"Output shape: {submission.shape}")
    print("Columns:", list(submission.columns))

if __name__ == "__main__":
    main()