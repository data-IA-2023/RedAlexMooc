from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pandas as pd
from getDf import *
import mlflow
import mlflow.sklearn
from datetime import datetime
import dotenv, re, os

dotenv.load_dotenv()
mlflow.set_tracking_uri(os.environ.get('MLFLOW_URL'))


categorical_columns_regressor = ['level_of_education', 'CSP', 'country', 'gender', 'city', 'cours']
numeric_columns_regressor     = ['year_of_birth']


def get_X_Y_for_regressor():
        # Récupérer les données
    df = get_the_df()
    df_regressor = get_df_for_regressor(df)
        # Sélectionner les caractéristiques et la cible
    X = df_regressor.drop(columns=['grade', 'isEmail', 'Certificate Delivered', 'datagiven'])
    y = df_regressor['grade']
    return X, y

X_regressor, y_regressor = get_X_Y_for_regressor()


def train_model_regressor(X_regressor, y_regressor, experiment_name):
    # Définir le nom de l'expérience
    mlflow.set_experiment(experiment_name)
    

    # Générer un nom de run unique basé sur la date et l'heure actuelle
    run_name = f"Grade_model_training_run {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    # Démarrer une nouvelle exécution MLflow avec un nom spécifique
    with mlflow.start_run(run_name=run_name):
        # Encoder les colonnes catégorielles avec LabelEncoder
        label_encoders_regressor = {}
        for column in categorical_columns_regressor:
            encoder = LabelEncoder()
            X_regressor[column] = encoder.fit_transform(X_regressor[column])
            label_encoders_regressor[column] = encoder

        # Appliquer le MinMaxScaler sur les colonnes numériques
        scaler_regressor = MinMaxScaler()
        X_regressor[numeric_columns_regressor] = scaler_regressor.fit_transform(X_regressor[numeric_columns_regressor])

        # Division des données en ensembles de formation et de test
        X_train_regressor, X_test_regressor, y_train_regressor, y_test_regressor = train_test_split(X_regressor, y_regressor, test_size=0.2, random_state=42)

        # Définir les paramètres à tester
        param_grid_regressor = {
            'n_estimators': [100, 200, 300, 500],
            'max_depth': [10, 20, 30, 50, 100, None],
            'min_samples_split': [2, 3, 4, 5, 10],
            'min_samples_leaf': [1],
            'max_features': ['sqrt']
        }

        # Initialiser le modèle
        model_regressor = RandomForestRegressor(random_state=42)

        # Effectuer une recherche en grille
        grid_search_regressor = GridSearchCV(estimator=model_regressor, param_grid=param_grid_regressor, cv=5, n_jobs=-1, verbose=2, scoring='r2')
        grid_search_regressor.fit(X_train_regressor, y_train_regressor)

        # Meilleurs paramètres
        best_params_regressor = grid_search_regressor.best_params_
        mlflow.log_params(best_params_regressor)
        #print("Meilleurs paramètres trouvés :", best_params_regressor)

        # Entraîner le modèle avec les meilleurs paramètres
        best_model_regressor = grid_search_regressor.best_estimator_
        best_model_regressor.fit(X_train_regressor, y_train_regressor)

        # Prédiction sur les données de test
        y_pred_best_regressor = best_model_regressor.predict(X_test_regressor)

        # Évaluation
        mae_best_regressor = mean_absolute_error(y_test_regressor, y_pred_best_regressor)
        mse_best_regressor = mean_squared_error(y_test_regressor, y_pred_best_regressor)
        r2_best_regressor = r2_score(y_test_regressor, y_pred_best_regressor)
        rmse_best_regressor = mse_best_regressor ** 0.5

        # Log metrics
        mlflow.log_metric("MAE", mae_best_regressor)
        mlflow.log_metric("MSE", mse_best_regressor)
        mlflow.log_metric("RMSE", rmse_best_regressor)
        mlflow.log_metric("R²", r2_best_regressor)

        #print(f"MAE: {mae_best_regressor}")
        #print(f"MSE: {mse_best_regressor}")
        #print(f"RMSE: {rmse_best_regressor}")
        #print(f"R^2: {r2_best_regressor}")

        # Enregistrer l'encodeur et le scaler avec les artefacts
        mlflow.sklearn.log_model(best_model_regressor, "model")
        mlflow.sklearn.log_model(label_encoders_regressor, "label_encoders")
        mlflow.sklearn.log_model(scaler_regressor, "scaler")

        # Récupérer l'run_id de l'exécution active
        run_id = mlflow.active_run().info.run_id
    mlflow.end_run()
#train_model_regressor(X_regressor, y_regressor,"Grade_model_training")



run_id = "c296ebdc6d9b465eb75564bc0541dead"
#print("Run ID:", run_id)

def load_mlflow_data(run_id):
    # Charger le modèle
    model = mlflow.sklearn.load_model("runs:/{}/model".format(run_id))

    # Charger les encodeurs
    label_encoders = mlflow.sklearn.load_model("runs:/{}/label_encoders".format(run_id))

    # Charger le scaler
    scaler = mlflow.sklearn.load_model("runs:/{}/scaler".format(run_id))

    return model, label_encoders, scaler

model_regressor, encoder_regressor, scaler_regressor = load_mlflow_data(run_id)






def predict_user_grade(encoder, scaler, X, model, user_data, experiment_name):
    # Définir le nom de l'expérience
    mlflow.set_experiment(experiment_name)
     # Générer un nom de run unique basé sur la date et l'heure actuelle
    run_name = f"Grade_prediction_model_run {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    # Démarrer une nouvelle exécution MLflow avec un nom spécifique
    with mlflow.start_run(run_name=run_name) as run:
        # Create a DataFrame for new user data
        user_df = pd.DataFrame([user_data])
        
        # Encode categorical columns
        for column in categorical_columns_regressor:
            encoder_classifier = encoder[column]
            user_df[column] = encoder_classifier.transform(user_df[column])
        
        # Apply scaler on numeric columns
        user_df[numeric_columns_regressor] = scaler.transform(user_df[numeric_columns_regressor])
        
        # Ensure columns are in the same order as those used for training the model
        user_df = user_df[X.columns]
        
        # Make prediction
        prediction = model.predict(user_df)
        
        # Log input data, prediction, and other metrics
        mlflow.log_param("user_data", user_data)
        mlflow.log_param("encoded_user_data", user_df.to_dict())
        mlflow.log_param("prediction", round(prediction[0],2))  
        #print(prediction)
        return round(prediction[0],2)
# Example new user data
new_user_data = {
    'level_of_education': 'hs',  
    'CSP': 'employé',        
    'country': 'fr',          
    'gender': 'f',              
    'city': 'Paris',             
    'year_of_birth': 1990,
    'cours': '04017'             
}


"""# Predict if the user will get their diploma
grade = predict_user_grade(encoder_regressor, scaler_regressor, X_regressor, model_regressor, new_user_data,'Grade_prediction_model')
print(grade)"""
