import json
import os

import onnx
import tensorflow as tf
import tf2onnx
from matplotlib import pyplot as plt

from ..params import LOSS_PLOT_FILE, ONNX_MODEL_PATH


def load_json(path):
    with open(path, 'r') as fp:
        file = json.load(fp)
    return file


def save_to_json(data, file_path):
    mode = 'w'
    if not os.path.isfile(file_path):
        mode = 'x'

    with open(file_path, mode) as fp:
        json.dump(data, fp)


def set_up_gpu():
    physical_devices = tf.config.list_physical_devices('GPU')
    try:
        for dev in physical_devices:
            tf.config.experimental.set_memory_growth(dev, True)
    except:
        print("Invalid device or cannot modify virtual devices once initialized.")
    return tf.distribute.MultiWorkerMirroredStrategy()


def plot_losses(history):
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.xlabel("Epochs")
    plt.legend(['loss', 'val_loss'])
    plt.savefig(LOSS_PLOT_FILE)
    plt.show()


def is_prod():
    return os.environ["ENV"] == 'prod'


def is_test():
    return os.environ["ENV"] == 'test'


def is_local():
    return os.environ["ENV"] == 'local'


def convert_to_onnx(model):
    onnx_model, _ = tf2onnx.convert.from_keras(model, [model.input.type_spec], opset=13)
    onnx.save(onnx_model, ONNX_MODEL_PATH)
