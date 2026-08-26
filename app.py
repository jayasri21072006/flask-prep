import os

import joblib
import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


app = Flask(__name__)

MODEL_PATH = "model.pkl"
REAL_TIME_PREDICTIONS_PATH = "data/real_time_predictions.csv"
BATCH_PREDICTIONS_PATH = "data/batch_predictions.csv"
ONLINE_DATA_PATH = "data/online_data.csv"

REQUIRED_FEATURES = [
    "Pregnancy",
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI",
    "DiabetesPedigreeFunction",
    "Age",
]


def fetch_save_data():
    """Fetch and save data from the online dataset."""
    url = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv"
    columns = REQUIRED_FEATURES + ["Outcome"]
    os.makedirs("data", exist_ok=True)

    try:
        df = pd.read_csv(url, names=columns)
        df.to_csv(ONLINE_DATA_PATH, index=False)
        return df
    except Exception as exc:
        print(f"Failed to fetch data: {exc}")
        return None


def train_and_save_model():
    """Train and save the model."""
    if os.path.exists(ONLINE_DATA_PATH):
        df = pd.read_csv(ONLINE_DATA_PATH)
    else:
        df = fetch_save_data()

    if df is None:
        raise RuntimeError("Could not load training data.")

    X = df.drop("Outcome", axis=1)
    y = df["Outcome"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {accuracy}")

    joblib.dump(model, MODEL_PATH)
    return model


def load_model():
    """Load model from disk or train a fresh one."""
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)

    print("Model not found. Training a new model.")
    return train_and_save_model()


model = load_model()


def validate_input(data, required_features):
    """Validate request data."""
    if data is None:
        raise ValueError("Request body must be valid JSON.")

    missing_features = [feature for feature in required_features if feature not in data]
    if missing_features:
        raise ValueError(f"Missing required features: {', '.join(missing_features)}")


@app.route("/", methods=["GET"])
def home():
    """Basic landing route so the app does not return 404 at the root URL."""
    return jsonify(
        {
            "message": "Pima Diabetes Prediction API is running.",
            "endpoints": ["/predict", "/batch_predict"],
        }
    )


@app.route("/predict", methods=["GET", "POST"])
def predict():
    """Real-time prediction for a single request."""
    if request.method == "GET":
        return jsonify(
            {
                "message": "Send a POST request with JSON to this endpoint.",
                "required_features": REQUIRED_FEATURES,
            }
        )

    data = request.get_json(silent=True)

    try:
        validate_input(data, REQUIRED_FEATURES)
        input_data = np.array([data[feature] for feature in REQUIRED_FEATURES]).reshape(1, -1)
        prediction = model.predict(input_data)

        record = {**data, "Prediction": int(prediction[0])}
        os.makedirs("data", exist_ok=True)
        file_exists = os.path.exists(REAL_TIME_PREDICTIONS_PATH)
        pd.DataFrame([record]).to_csv(
            REAL_TIME_PREDICTIONS_PATH,
            mode="a",
            header=not file_exists,
            index=False,
        )

        return jsonify({"prediction": int(prediction[0])})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/batch_predict", methods=["GET", "POST"])
def batch_predict():
    """Batch prediction for multiple samples."""
    if request.method == "GET":
        return jsonify(
            {
                "message": "Send a POST request with a CSV file field named 'file'.",
                "required_features": REQUIRED_FEATURES,
            }
        )

    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files["file"]
        batch_data = pd.read_csv(file)
        missing_features = [
            feature for feature in REQUIRED_FEATURES if feature not in batch_data.columns
        ]

        if missing_features:
            return jsonify(
                {"error": f"Missing required features: {', '.join(missing_features)}"}
            ), 400

        X = batch_data[REQUIRED_FEATURES]
        predictions = model.predict(X)

        os.makedirs("data", exist_ok=True)
        batch_data["Prediction"] = predictions
        batch_data.to_csv(BATCH_PREDICTIONS_PATH, index=False)

        return jsonify({"message": "Batch predictions saved successfully"})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.errorhandler(404)
def not_found(_error):
    """Return a helpful JSON message for unknown routes."""
    return (
        jsonify(
            {
                "error": "Route not found",
                "available_endpoints": ["/", "/predict", "/batch_predict"],
            }
        ),
        404,
    )


@app.errorhandler(405)
def method_not_allowed(_error):
    """Return a helpful JSON message when the wrong HTTP method is used."""
    return (
        jsonify(
            {
                "error": "Method not allowed",
                "hint": "Use GET for help pages, POST for inference.",
                "available_endpoints": ["/", "/predict", "/batch_predict"],
            }
        ),
        405,
    )


if __name__ == "__main__":
    app.run(debug=True)
