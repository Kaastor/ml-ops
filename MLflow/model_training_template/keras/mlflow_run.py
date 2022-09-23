import os
import sys
from time import gmtime, strftime
import mlflow
from MLflow.model_training_template.keras.ModelTemplate import Runner
from MLflow.model_training_template.keras.params import PARAMS, EXPERIMENT_NAME
from MLflow.model_training_template.keras.utils.mlflow import get_experiment_id
from MLflow.model_training_template.keras.utils.model_utils import is_prod, is_test, set_up_gpu, is_local

# TODO better parametrization

strategy = None
if is_prod() or is_test():
    strategy = set_up_gpu()
    mlflow.set_tracking_uri("http://prod-tracking-uri:80")
if is_local():
    mlflow.set_tracking_uri("http://local-tracking-uri:5000")

run_name = str(os.environ["MODEL"]) + '_' + str(os.environ["ENV"]) + '_' + strftime("%Y-%m-%d-%H:%M:%S", gmtime())

(experimentID, runID) = Runner(PARAMS, strategy).mlflow_run(run_name=run_name,
                                                            experiment_id=get_experiment_id(EXPERIMENT_NAME))
print("MLflow Run completed with run_id {} and experiment_id {}".format(runID, experimentID))
sys.exit(0)
