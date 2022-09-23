FROM tensorflow/tensorflow:2.8.0-gpu

COPY . /ml
WORKDIR /ml

RUN mkdir -p /ml/saved-model
RUN pip install --upgrade pip && pip install -r /ml/requirements.txt

ENV MODEL=test

ENTRYPOINT ["python", "gpu-test.py"]