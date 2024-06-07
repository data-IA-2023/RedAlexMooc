from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.metrics import accuracy_score
import pandas as pd
from getDf import *
import mlflow
import mlflow.sklearn
from datetime import datetime
import dotenv, re, os

dotenv.load_dotenv()
# Set the tracking URI
mlflow.set_tracking_uri("http://4.233.185.114:5000")


categorical_columns_classifier = ['level_of_education', 'CSP', 'country', 'gender', 'city', 'cours']
numeric_columns_classifier = ['year_of_birth']



def get_X_Y_for_classifier():
        # Récupérer les données
    df = get_the_df()
    df_classifier = get_df_for_classifier(df)
        # Sélectionner les caractéristiques et la cible
    X = df_classifier.drop(columns=['grade', 'isEmail', 'Certificate Delivered', 'datagiven'])
    y = df_classifier['Certificate Delivered']
    return X, y

X_classifier, y_classifier = get_X_Y_for_classifier()

def train_classifier_model(X_classifier, y_classifier, experiment_name):
    # Définir le nom de l'expérience
    mlflow.set_experiment(experiment_name)
    

    # Générer un nom de run unique basé sur la date et l'heure actuelle
    run_name = f"Certificat_training_model_run {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    # Démarrer une nouvelle exécution MLflow avec un nom spécifique
    with mlflow.start_run(run_name=run_name) as run:

        # Encodez les colonnes catégorielles avec LbelEncoder
        label_encoders_classifier = {}
        for column in categorical_columns_classifier:
            encoder = LabelEncoder()
            X_classifier[column] = encoder.fit_transform(X_classifier[column])
            label_encoders_classifier[column] = encoder

        # Appliquer MinMaxScaler aux colonnes numériques
        scaler_classifier = MinMaxScaler()
        X_classifier[numeric_columns_classifier] = scaler_classifier.fit_transform(X_classifier[numeric_columns_classifier])

        # Diviser les données en ensembles de formation et de test
        X_train_classifier, X_test_classifier, y_train_classifier, y_test_classifier = train_test_split(X_classifier, y_classifier, test_size=0.2, random_state=42)

        # Définir la grille de paramètres pour GridSearchCV
        param_grid = {
            'n_estimators': [100, 200, 300, 500],
            'max_depth': [10, 20, 30, 50, 100, None],
            'min_samples_split': [2, 3, 4, 5, 10],
            'min_samples_leaf': [1],
            'max_features': ['sqrt']
        }

        # Initialiser RandomForestClassifier
        model_classifier = RandomForestClassifier(random_state=42)

        # Effectuer une recherche en grille
        grid_search_classifier = GridSearchCV(estimator=model_classifier, param_grid=param_grid, cv=5, n_jobs=-1, verbose=2, scoring='accuracy')
        grid_search_classifier.fit(X_train_classifier, y_train_classifier)

        # Meilleurs paramètres
        best_params_classifier = grid_search_classifier.best_params_
        print(best_params_classifier)
        mlflow.log_params(best_params_classifier)

        # Meilleur modèle
        best_model_classifier = grid_search_classifier.best_estimator_

        # Prédiction sur les données de test
        y_pred_best_classifier = best_model_classifier.predict(X_test_classifier)

        # Calcul de la précision
        accuracy = accuracy_score(y_test_classifier, y_pred_best_classifier)
        mlflow.log_metric("accuracy", accuracy)

        # Enregistrer l'encodeur et le scaler avec les artefacts
        mlflow.sklearn.log_model(best_model_classifier, "model")
        mlflow.sklearn.log_model(label_encoders_classifier, "label_encoders")
        mlflow.sklearn.log_model(scaler_classifier, "scaler")

        # Récupérer l'run_id de l'exécution active
        run_id = run.info.run_id
    mlflow.end_run()


#train_classifier_model(X_classifier,y_classifier,"Certificat_model_training")

run_id = "83cc3feba07846b6b9f39b92a9825a29"
#print("Run ID:", run_id)

def load_mlflow_data(run_id):
    # Charger le modèle
    model = mlflow.sklearn.load_model("runs:/{}/model".format(run_id))

    # Charger les encodeurs
    label_encoders = mlflow.sklearn.load_model("runs:/{}/label_encoders".format(run_id))

    # Charger le scaler
    scaler = mlflow.sklearn.load_model("runs:/{}/scaler".format(run_id))

    return model, label_encoders, scaler

model_classifier, encoder_classifier, scaler_classifier = load_mlflow_data(run_id)


def predict_user_certif(encoder, scaler, X, model, user_data, experiment_name):
    # Définir le nom de l'expérience
    mlflow.set_experiment(experiment_name)
     # Générer un nom de run unique basé sur la date et l'heure actuelle
    run_name = f"Certificat_prediction_model_run {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    # Démarrer une nouvelle exécution MLflow avec un nom spécifique
    with mlflow.start_run(run_name=run_name) as run:
        # Create a DataFrame for new user data
        user_df = pd.DataFrame([user_data])
        
        # Encode categorical columns
        for column in categorical_columns_classifier:
            encoder_classifier = encoder[column]
            user_df[column] = encoder_classifier.transform(user_df[column])
        
        # Apply scaler on numeric columns
        user_df[numeric_columns_classifier] = scaler.transform(user_df[numeric_columns_classifier])
        
        # Ensure columns are in the same order as those used for training the model
        user_df = user_df[X.columns]
        
        # Make prediction
        prediction = model.predict(user_df)
        
        # Log input data, prediction, and other metrics
        mlflow.log_param("user_data", user_data)
        mlflow.log_param("encoded_user_data", user_df.to_dict())
        mlflow.log_param("prediction", prediction[0])  
        
        #print(prediction)
        return prediction[0]
# Example new user data
new_user_data = {
    'level_of_education': 'hs',  
    'CSP': 'employé',        
    'country': 'fr',          
    'gender': 'f',              
    'city': 'paris',             
    'year_of_birth': 1940,
    'cours': '04017'             
}

"""# Predict if the user will get their diploma
certif = predict_user_certif(encoder_classifier, scaler, X_classifier, model_classifier, new_user_data,'Certificat_prediction_model')
print(certif)
print(f"L'utilisateur obtiendra-t-il son diplôme ? {'Oui' if certif == 'Y' else 'Non'}")"""