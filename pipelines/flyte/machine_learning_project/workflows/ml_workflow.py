import pandas as pd
from sklearn.datasets import load_wine
from sklearn.linear_model import LogisticRegression
from flytekit import task, workflow


@task
def get_data() -> pd.DataFrame:
    """Get the wine dataset."""
    return load_wine(as_frame=True).frame


@task
def process_data(data: pd.DataFrame) -> pd.DataFrame:
    """Simplify the task from a 3-class to a binary classification problem."""
    return data.assign(target=lambda x: x["target"].where(x["target"] == 0, 1))


@task
def train_model(data: pd.DataFrame, hyperparameters: dict) -> LogisticRegression:
    """Train a model on the wine dataset."""
    features = data.drop("target", axis="columns")
    target = data["target"]
    return LogisticRegression(max_iter=3000, **hyperparameters).fit(features, target)


@workflow
def training_workflow(hyperparameters: dict) -> str:
    """Put all of the steps together into a single workflow."""
    data = get_data()
    processed_data = process_data(data=data)
    train_model(
        data=processed_data,
        hyperparameters=hyperparameters,
    )
    return "Model trained"


# pyflyte run <path/to/script.py> <workflow_or_task_function_name>.
# pyflyte run simple_workflow.py training_workflow  --hyperparameters '{"C": 0.1}'

if __name__ == "__main__":
    # Execute the workflow, simply by invoking it like a function and passing in
    # the necessary parameters
    print(f"Running wf() { training_workflow(hyperparameters={'C': 0.1}) }")
