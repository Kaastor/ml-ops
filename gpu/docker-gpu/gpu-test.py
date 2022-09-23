import tensorflow as tf
from google.cloud import storage
import os
import time

BUCKET = 'bucket-name'
MODEL_DIR = './saved-model/'
MODEL_FILE = 'model.onnx'
MODEL_BUCKET_PATH = os.path.join(os.environ['MODEL'], str(int(time.time())), MODEL_FILE)


class MyModel(tf.keras.Model):
    def __init__(self):
        super(MyModel, self).__init__()
        self.flatten = tf.keras.layers.Flatten()
        self.d1 = tf.keras.layers.Dense(128, activation='relu')
        self.dropout = tf.keras.layers.Dropout(0.2)
        self.d2 = tf.keras.layers.Dense(10, activation='softmax')

    def call(self, x, **kwargs):
        x = self.flatten(x)
        x = self.d1(x)
        x = self.dropout(x)
        x = self.d2(x)
        return x


def print_tensorflow():
    """
    Output Tensorflow related build
    """
    print("Tensorflow", tf.__version__)
    print("isBuild with CUDA:", tf.test.is_built_with_cuda())


def print_gpu_info():
    """
    Output GPU(s) info that is compatible to CUDA on the machine
    """
    print("Number of GPU(s):", len(tf.config.list_physical_devices('GPU')))
    print("GPU(s):", tf.config.list_physical_devices('GPU'))


if __name__ == "__main__":
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET)

    # Output info about tensorflow and gpu(s)
    print_tensorflow()
    print_gpu_info()

    # Retrieve the dataset
    mnist = tf.keras.datasets.mnist

    # Split dataset into train and test datasets
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    x_train, x_test = x_train / 255.0, x_test / 255.0

    # Create a model by grouping layers into an object
    model = MyModel()

    # Configures the model for training
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    # Train the model
    model.fit(x_train, y_train, epochs=5)

    model.save('/ml/saved-model')
    os.system('python3 -m tf2onnx.convert --saved-model /ml/saved-model --output /ml/saved-model/model.onnx --opset=10')
    # Evaluate the model
    model.evaluate(x_test, y_test)

    # save to gcs
    blob = bucket.blob(MODEL_BUCKET_PATH)
    blob.upload_from_filename(MODEL_DIR + MODEL_FILE)
