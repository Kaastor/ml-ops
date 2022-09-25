import os.path

import redisai as rai
import mlflow
import numpy as np
from mlflow.pyfunc import PyFuncModel
from sklearn.metrics import mean_squared_error
from mlflow.tracking import MlflowClient
from mlflow.exceptions import RESOURCE_DOES_NOT_EXIST, MlflowException

from demo_serving.app.service.utils import MODEL_ONNX_FILE, load_json

mlflow_client = MlflowClient("http://mlflow-loadbalancer-internal")
URI = 'redisai-clusterip.redis.svc'
PORT = 6379


class RedisAIConnector:
    def __init__(self):
        self.con = rai.Client(host=URI, port=PORT)

    def test_connection(self):
        self.con.execute_command('AI.TENSORSET', 'foo', 'FLOAT', 2, 2, 'VALUES', 1, 2, 3, 4)
        print("Tensor: ", self.con.execute_command('AI.TENSORGET', 'foo'))

    def test_connection_ai_cli(self):
        array = np.array([2, 3], dtype=np.float32)
        self.con.tensorset('x', array)
        print(self.con.tensorget('x'))

    def predict(self, input_t, model_id): # fixme what if model is not there
        result = self.con.dag().tensorset('input_tensor', np.array([input_t], dtype=np.float32))\
                .modelrun(model_id, inputs=['input_tensor'], outputs=['prediction'])\
                .tensorget('prediction')\
                .run()[-1]
        return mean_squared_error(input_t, np.array(np.squeeze(result)))

    def store_model_vocab(self, model_id, dictionary):
        self.con.hmset(f"{model_id}_vocab", dictionary)

    def load_model_vocab(self, model_id):  # fixme what if vocab is not there, load for correct model (Stage==prod)
        return self.con.hgetall(f"{model_id}_vocab")

    def store_model(self, model_id, model):
        self.con.modelstore(model_id, 'onnx', 'cpu', model, tag='v1.0')
        print('Model stored.')

    def load_model_by_stage(self, model_id, stage):
        print("Loading model started.")
        try:
            model = mlflow.pyfunc.load_model(model_uri=f"models:/{model_id}/{stage}")
            if not self.con.exists(model_id):
                print(f'Loading model: {model_id}, {stage}, {model.metadata}')
                self._load_model(model_id, model, tag=stage)
                print(f'Model loaded: {model_id}, {stage}, {model.metadata}')
        except MlflowException as e:
            print(f'Exception occur during {model_id} loading: {e}')

    def _load_model(self, model_id, model: PyFuncModel, tag):
        model_path = mlflow_client.download_artifacts(run_id=model.metadata.run_id,
                                                      path=model.metadata.artifact_path)
        vocab_path = mlflow_client.download_artifacts(run_id=model.metadata.run_id,
                                                      path=f'{model.metadata.artifact_path}_vocab.json')
        model_path = os.path.join(model_path, 'tfmodel', MODEL_ONNX_FILE)
        model_vocab = load_json(vocab_path)
        model_file = open(model_path, 'rb').read()
        self.con.modelstore(model_id, 'onnx', 'cpu', model_file, tag=tag)
        self.store_model_vocab(model_id, model_vocab)
