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


    # model = ArimaModel()
    # model.train_model(disease.reconciled_data)
    # model.test_model(testing_data)
    # prediction = model.predict(12)
    # print(f"Prediction: {prediction}")
