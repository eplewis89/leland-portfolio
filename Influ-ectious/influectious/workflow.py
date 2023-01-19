from sklearn.model_selection import train_test_split
from Disease import Disease
from ml_model import Model


def run(disease_model: str):
    disease = Disease(disease_model)
    disease.ingest_data()
    disease.analyze_data()

    # Split the data into training and test sets
    train_data, test_data = train_test_split(disease.reconciled_data, test_size=0.2)

    rf_model = Model(train_data)
    rf_model.train_model()
    prediction = rf_model.predict()
    print(f"Prediction: {prediction}")



