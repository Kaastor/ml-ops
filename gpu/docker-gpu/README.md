## Tensorflow GPU Docker

* Based on [tensorflow docker container tutorial](https://www.tensorflow.org/install/docker#start_a_tensorflow_docker_container)
* Containerized environment which allows running Tensorflow with GPU support
* Node machine still needs to have:
    * NVIDIA GPU driver installed (@see `../gpu-config/readme.md/Graphics Card Driver`)
    * Docker engine (> 19.03)
    * [NVIDIA Docker support](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
    * Verify installation via `sudo docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi` (should output correct 
      `nvidia-smi`)
* Download a TensorFlow Docker image
  * Check if a GPU is available: `lspci | grep -i nvidia`
  * Choose image with correct TF version and GPU support e.x `docker pull tensorflow/tensorflow:2.8.0-gpu`
    * Verify image run: `docker run --gpus all -it --rm tensorflow/tensorflow:2.8.0-gpu \
    python -c "import tensorflow as tf; print('isBuild with CUDA:', tf.test.is_built_with_cuda())"`
  * It can take a while to set up the GPU-enabled image. If repeatedly running GPU-based scripts, you can 
    use `docker exec` to reuse a container.
* Run `docker run --gpus all --rm przomys/gpu-test` on instance to check if CUDA is working properly

## K8 Nodes Management

* Stop node via `gcloud compute instances stop <instance-id>`
