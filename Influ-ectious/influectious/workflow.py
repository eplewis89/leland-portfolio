from sklearn.model_selection import train_test_split
from disease import Disease
from ml_model import ArimaModel


def run(disease_model: str):
    disease = Disease(disease_model)
    disease.ingest_data('csv')
    disease.clean_up_data()
    disease.store_data()
    disease.reconcile()
    disease.analyze_data()

    # Split the data into training and test sets
    train_size = int(len(disease.reconciled_data) * 0.75)
    training_data, testing_data = disease.reconciled_data[:train_size], disease.reconciled_data[train_size:]

    rf_model = ArimaModel()
    rf_model.train_model(training_data)
    rf_model.test_model(testing_data)
    prediction = rf_model.predict(12)
    print(f"Prediction: {prediction}")
