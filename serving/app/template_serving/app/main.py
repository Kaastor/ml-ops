import os

import mlflow
import uvicorn
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from demo_serving.app.api.models import Stage
from demo_serving.app.api.serving import serving
from demo_serving.app.service.model_cache import RedisAIConnector

mlflow.set_tracking_uri("http://mlflow-loadbalancer-internal")
app = FastAPI(openapi_url='/api/v1/serving/openapi.json', docs_url='/api/v1/serving/docs')
background_tasks = BackgroundTasks()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


def load_model():
    con_ai = RedisAIConnector()
    con_ai.load_model_by_stage(model_id=os.environ['MODEL'], stage=Stage.PRODUCTION)


@app.on_event("startup")
async def startup():
    load_model()

app.include_router(serving, prefix='/api/v1/serving')

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
