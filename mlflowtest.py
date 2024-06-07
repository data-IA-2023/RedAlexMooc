import mlflow

# Set the experiment name
experiment_name = 'testing_mlflow1'

# Create the experiment
experiment_id = mlflow.create_experiment(
    name=experiment_name,
    artifact_location='testing_mlflow1_artifacts',
    tags={"env": "dev", "version": "1.0.0"}
)

print(f"Experiment '{experiment_name}' created with ID: {experiment_id}")
