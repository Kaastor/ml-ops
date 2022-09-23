from mlflow.tracking import MlflowClient


def get_experiment_id(experiment_name=''):
    client = MlflowClient('http://localhost:5001')
    experiment = client.get_experiment_by_name(experiment_name)
    if experiment is None:
        return 0
    else:
        return client.get_experiment_by_name(experiment_name).experiment_id