### Docker

* Keep in mind to get `requirements.txt` as one of the first layers. Then docker
  can utilize caching [docker-caching-model](https://pythonspeed.com/articles/docker-caching-model/)

### Build

* via `sh build.sh` - pushes new version of image to registry.

### Running

* Run `main.py`
* `uvicorn demo_serving.app.main:app --reload` - development

### Documentation

* [RedisAI doc](https://redisai-py.readthedocs.io/en/latest/api.html)
* `http://[IP]:8000/api/v1/serving/docs` - automatically created endpoint doc

### Loading TF models in RedisAI

* Run `saved_model_cli` to see model graph:
    * python3.8 [path-to-saved_model_cli.py] show --dir [model-dir] --all
    * [path-to-saved_model_cli.py] - `./venv/lib/python3.8/site-packages/tensorflow/python/tools/saved_model_cli.py`
    * [model-dir]- `./demo_serving/app/model/`
* Look at `signature_def['serving_default']` to see inputs and output names (`embedding_input` and `conv1d_4`):

```
signature_def['serving_default']:
  The given SavedModel SignatureDef contains the following input(s):
    inputs['embedding_input'] tensor_info:
        dtype: DT_FLOAT
        shape: (-1, 192)
        name: serving_default_embedding_input:0
  The given SavedModel SignatureDef contains the following output(s):
    outputs['conv1d_4'] tensor_info:
        dtype: DT_FLOAT
        shape: (-1, 192, 1)
        name: StatefulPartitionedCall:0
  Method name is: tensorflow/serving/predict

```

* Load model in ONNX file format. Conversion could be done via `tf2onnx` (@`tf_conversion.py`)
* Conversion should use correct `opset`! @see: https://github.com/onnx/tensorflow-onnx

### Loading models created in MLflow via MLflow Model Registry

* MLflow's models are being stored in MLflow Model Registry which is located on Google Cloud Storage 
  bucket.
* [MLflow Model Registry reference](https://www.mlflow.org/docs/latest/model-registry.html)

### [Fetching an MLflow Model from the Model Registry](https://www.mlflow.org/docs/latest/model-registry.html#fetching-an-mlflow-model-from-the-model-registry)

* Remember to set `mlflow.set_tracking_uri("http://[mlflow-ip]")` to have correct connection.

### Model change

* Right now there is no way to reload model automatically via MLflow label change. To reload model one needs to
  * change the label in MLflow
  * restart deployment to load new model
  * I know, shitty solution... for now.

### Look into RedisAI

```
> kubectl exec -it [serving-pod] -c models-cache /bin/bash
> redis-cli
> keys * (show all keys)
```

* `kubectl exec -it [pod-name] -c serving-app /bin/bash` - log into serving-app 

### Test request

* `http://[serving-loadbalancer-internal-ip(10.144.0.85)]:80/api/v1/serving/docs` - run from activeid-airflow instance

### TODO

* Consider creating a service which will periodically check if current stage of the specific model was not changed.
  If it was, we need to change model version in RedisAI. Crucial feature.
