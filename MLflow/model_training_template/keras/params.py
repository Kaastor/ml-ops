import os
from pathlib import Path

EXPERIMENT_NAME = 'MLflow experiment name'
DIR = str(Path(os.path.realpath(__file__)).parent)
LOSS_PLOT_FILE = os.path.join(DIR, 'plots', 'losses.png')
MODEL_DIR = os.path.join(DIR, 'saved-model')
ONNX_MODEL_PATH = os.path.join(DIR, 'saved-model', 'model.onnx')
MODEL_FILE = 'model.onnx'

PARAMS = {
    "batch_size": 128,
    "epochs": 15
}
