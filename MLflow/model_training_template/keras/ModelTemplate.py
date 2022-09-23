import os
import shutil

import mlflow
import tensorflow as tf
from keras import Sequential
from keras.callbacks import Callback
from keras.losses import MeanSquaredError
from keras.models import Model
from mlflow.tracking import MlflowClient
from sklearn.model_selection import train_test_split
from tensorflow.python.saved_model import signature_constants

from MLflow.model_training_template.keras.params import LOSS_PLOT_FILE, MODEL_DIR
from MLflow.model_training_template.keras.utils.model_utils import plot_losses, is_local, convert_to_onnx

LOSS_EPSILON = 0.001
client = MlflowClient("http://prod-tracking-uri:80")


class LossNearZero(Callback):
    def on_epoch_end(self, epoch, logs=None):
        if logs.get('loss') < LOSS_EPSILON:
            self.model.stop_training = True


class ModelTemplate(Model):
    def __init__(self, params=None, strategy=None):
        super(ModelTemplate, self).__init__()

        if params is None:
            params = {}
        self._params = params

        if strategy:
            with strategy.scope():
                self.model = self.get_definition()
        else:
            self.model = self.get_definition()

    def get_definition(self):
        return Sequential([])


class Runner:
    def __init__(self, params=None, strategy=None):
        if params is None:
            params = {}
        self._params = params
        self.options = tf.data.Options()
        self.options.experimental_distribute.auto_shard_policy = tf.data.experimental.AutoShardPolicy.FILE
        self.model = ModelTemplate(params, strategy)

    @property
    def params(self):
        return self._params

    def mlflow_run(self, data, run_name="Model", experiment_id=None):
        with mlflow.start_run(run_name=run_name) as run:
            # Data preparation
            X_train, X_test = train_test_split(data, test_size=0.3, shuffle=True)
            history = self.run_training(X_train, X_test, True)

            # Log MLflow experiment
            mlflow.set_experiment(experiment_id=experiment_id)
            run_id = run.info.run_uuid
            experiment_id = run.info.experiment_id
            # Log metrics
            mlflow.log_metric("Real Epochs", len(history.history['loss']))
            mlflow.log_metric("Loss", history.history['loss'][-1])
            mlflow.log_metric("Val Loss", history.history['val_loss'][-1])
            mlflow.set_tag("env", os.environ["ENV"])
            mlflow.set_tag("model_type", os.environ["MODEL"])
            # Log params
            mlflow.log_params(self._params)
            mlflow.tensorflow.autolog()
            plot_losses(history)
            mlflow.log_artifact(LOSS_PLOT_FILE)
            if not is_local():
                # Register model
                tag = [tf.compat.v1.saved_model.tag_constants.SERVING]
                key = signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY
                mlflow.tensorflow.log_model(tf_saved_model_dir=MODEL_DIR,
                                            tf_meta_graph_tags=tag,
                                            tf_signature_def_key=key,
                                            artifact_path=os.environ["MODEL"],
                                            registered_model_name=os.environ["MODEL"])
            return experiment_id, run_id

    def run_training(self, train_data, val_data, save=False):
        boundaries = [3000, 6000]
        values = [0.0005, 0.00005, 0.000005]
        learning_rate_fn = tf.keras.optimizers.schedules.PiecewiseConstantDecay(boundaries, values)

        self.model.compile(loss=MeanSquaredError(),
                           optimizer=tf.keras.optimizers.Adam(learning_rate_fn))

        history = self.model.fit(train_data, train_data,
                                 shuffle=True,
                                 batch_size=self.params["batch_size"],
                                 callbacks=[LossNearZero()],
                                 epochs=self.params["epochs"],
                                 validation_data=(val_data, val_data))
        if save:
            self.save_model()
        print(self.model.model.summary())
        return history

    def save_model(self):
        if os.path.isdir(MODEL_DIR):
            shutil.rmtree(MODEL_DIR)
        self.model.model.save(MODEL_DIR)
        convert_to_onnx(self.model.model)
