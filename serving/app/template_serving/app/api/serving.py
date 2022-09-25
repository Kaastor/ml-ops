import os
import time
from fastapi import APIRouter

from demo_serving.app.service.model_cache import RedisAIConnector
from demo_serving.app.service.utils import tokenize_url

con = RedisAIConnector()
serving = APIRouter()


@serving.get('/predict')
def predict():
    start = time.time()
    url = '00refund123.com/directing/easyweb.td.com/waw/idp/secquestions.php'
    model_id = os.environ['MODEL']

    url_enc = tokenize_url(url, con.load_model_vocab(model_id))
    print(url_enc)
    result = con.predict(url_enc, model_id=model_id)
    end = time.time()
    return {
        'result': result,
        'time [ms]': (end - start) * 1000
    }
