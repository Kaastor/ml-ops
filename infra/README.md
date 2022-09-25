## Environment

Based on Kubernetes cluster. It has three main services: **mlflow, serving and service**. Each of them
is a separate microservice build as Docker image (for now they are located in [private repository](https://hub.docker.com/u/przomys)).

**MLflow** is used to contain information about ML experiments, storing artifacts (model files, etc.) and serving them
to the other services.
**Serving** uses MLflow from which it gathers serialized model files and serves them via RedisAI library. 
**Service** is the main entrypoint for external systems

Redis cluster acts as a main cache for data and models

### Local

Services are build and running on **microk8s cluster**. Their deployment is being managed via **Helm Chart** and `values.local.yaml` config file.
Continuous Development and Debugging is done via **skaffold** and **Cloud Code** IntelliJ plugin.
System is dependent on three external services deployed via `docker-compose':
- MinIO - `http://127.0.0.1:9001/` - object storage used by MLflow, artifact store on bucket `shield-demo-local`
- Elasticsearch - `http://0.0.0.0:9200` - monitoring engine
  - localhost deployment of Elastic APM - `http://localhost:8200` 
- Kibana  - `http://0.0.0.0:5601` - monitoring system ui, selected metrics can be observed on Kibana
  - `demo-service` dashboard - `http://0.0.0.0:5601/app/apm/services/demo-service`
- Redis - `http://0.0.0.0:6379` - blacklists and whitelists cache

### Production

Services are build and running on Google Kubernetes Engine. 
Their deployment is being managed via **Helm Chart** and `values.prod.yaml` config file.

System is dependent on few external services:
- GCS bucket - object storage used by MLflow, artifact store.
- Elasticsearch & Kibana (with local deployment of APM) - monitoring system
- Redis database

## Local environment stack

* [Docker](https://www.docker.com/get-started/)

* [micro8s](https://microk8s.io/) Kubernetes cluster
  * Follow: [getting started](https://microk8s.io/docs/getting-started) 
  * `sudo snap install microk8s --classic` - install
  * `sudo microk8s enable dashboard dns hostpath-storage metrics-server` - enable features needed for development
    * `sudo microk8s enable registry` - enable features needed for development
    * `sudo microk8s enable host-access ingress metallb` - enable features needed for development
    * while enabling `metallb` use IP addresses from the example
  * [Enable `allow-insecure-localhost` in Google Chrome](chrome://flags/#allow-insecure-localhost)
  * `sudo microk8s dashboard-proxy` - run k8s dashboard
  * `sudo microk8s start`, `sudo microk8s stop` - start and stop k8s cluster
  * Configure `kubectl` to use microk8s (**be aware**, commands below will overwrite existing config!):
    ```
    cd $HOME
    mkdir .kube
    cd .kube
    sudo microk8s config > config
    ```
  * From inside the cluster, [localhost is available](https://microk8s.io/docs/addon-host-access) at `10.0.1.1` address.
  * Add the following lines to /etc/docker/daemon.json:
    ```
    {
    "insecure-registries" : ["localhost:32000"]
    }
    ```
    and then restart docker with: sudo systemctl restart docker

* [Helm](https://helm.sh/) - package manager for Kubernetes, helps manage k8s applications
  * Install Helm ([releases](https://github.com/helm/helm/releases))
    ```
    curl -LO https://get.helm.sh/helm-v3.9.0-linux-amd64.tar.gz 
    tar -C /tmp/ -zxvf helm-v3.9.0-linux-amd64.tar.gz
    rm helm-v3.4.0-linux-amd64.tar.gz
    sudo mv /tmp/linux-amd64/helm /usr/local/bin/helm
    sudo chmod +x /usr/local/bin/helm
    ```
  * `cd` to `./demo/helm` directory
  * Check if template is correct: `helm template demo demo`
  * **Knowing that `kubectl` is set to your local k8s cluster**, install Chart via 
    * `helm install demo demo --values ./demo/values.local.yaml`
  * Check installation via `helm list`, you should see `demo` with `STATUS=deployed` and `kubectl get all`
  * Locally helm is being used via `skaffold`, which deploys the system and manages the revisions
  * On production helm is being used manually.

* [Skaffold](https://skaffold.dev/)
  * Handles the workflow for building, pushing and deploying your application, allowing you to focus on what matters most: writing code
  * Wraps building and deploying an app. No more: code a little, build images, upgrade helm, etc. 
  * Skaffold will rebuild docker images on file save and replace code in local cluster.
  * Configuration file: `demo/helm/demo/skaffold.yml`
  * [Skaffold description](https://github.com/Kapernikov/skaffold-helm-tutorial/blob/main/chapters/06-skaffold.md)
  * [Install](https://skaffold.dev/docs/install/)
  * To run `microk8s` with `skaffold` we need to configure local image registry for `microk8s`
    * See [tutorial](https://nevyan.blogspot.com/2020/09/skaffold-on-microk8s-kubernettes.html)
    * Basically: add `localhost:32000` in `skaffold.yml` to indicate that images are on registry.
    * Add alias: `sudo snap alias microk8s.kubectl kubectl`
    * **Do not** add in `skaffold.yml`!
      ```
      build:
        local:
           push: false
      ```

* [minio](https://min.io/)
  * Create folder on your local machine: `mkdir /var/demo/minio`
  * Run docker compose from `demo/docker`
  * To connect to minio from microk8s cluster:
    * `MLFLOW_S3_ENDPOINT_URL`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` need to
      be specified both at each client side (i.e. model building and serving) and server side (`mlflow-deployment`)
    * in `mlflow server` command use option `--serve-artifacts` 
  * Log in to dashboard via `127.0.0.1:9001`

* Elasticsearch & Kibana
  * [Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html) 
  * Run docker compose from `demo/docker`
  * Check if [this condition](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html#_set_vm_max_map_count_to_at_least_262144) 
    is satisfied
  * After start up to access kibana ui, get access token via running `bin/elasticsearch-create-enrollment-token --scope kibana` 
    command in elasticsearch container. Next, get 6-digit code from Kibana container log.
  * To set up password for all systems log in to `elastic` container and run `./bin/elasticsearch-setup-passwords interactive`.
    * u:`elastic` p:`elastic`
  * Set up a [**Fleet**](https://www.elastic.co/guide/en/observability/current/ingest-traces.html#set-up-fleet-traces):
    * Configure host at `https://0.0.0.0:8220`
    * Install Fleet Server to a centralized host and confirm that is working (i.e. go to **Fleet** and check if status is **Healthy**)
      * To reinstall, remove Elastic Agent (`sudo sudo /opt/Elastic/Agent/elastic-agent uninstall`) 
        and install again.
  * Add APM integration (**Observability -> APM -> ** Add APM integration -> Add Elastic APM)
    * Set up a name, for example `demo-apm-1`
    * Default server config: `http://localhost:8200`, but **change it to** `0.0.0.0:8200`! Otherwise, microk8s will not be able
      to reach the APM. [Possible reason](https://discuss.elastic.co/t/elasticsearch-apm-agent-not-pushing-to-server/138547/2)
    * At point **2** choose **Existing hosts** and your **Agent policy**.
  * For more information about configuration see [this](https://www.elastic.co/guide/en/observability/current/ingest-traces.html)
  * Elasticsearch is available at `http://0.0.0.0:9200/`
  * Kibana UI is up at `http://0.0.0.0:5601/`
  * After running cluster service metrics will be available at `http://0.0.0.0:5601/app/apm/services/demo-service`

* **Watch out**:
  * `postgres-claim` PersistentVolumeClaim is re-generated every time you will install
    helm from zero **unless** you use `storageClassName: local-storage` and custom `Persistent Volume` (@see mlflow-volume-claim). 

### Initial set up

* Create `namespaces`
* Create dirs: `sudo mkdir /mnt/local-cluster-data`
  * `/mnt/local-cluster-data/mlflow`
  * `/mnt/local-cluster-data/redisai`
* Each storage Pod needs its own PV (`local-storage.yml`), it is not needed on production.
* Start `./demo/docker/docker-compose.yml` locally (configure elastic if it is first run) and `mongodb` locally.
* Run initial model training job from `local-model-training-job.yml` file with `ENV=test`. This will create entry in mlflow.
* Set chosen model to `production` Stage in `mlflow -> Models`.
* Restart `serving-deployment` (right now this is a way to load new model)
* Check if model prediction works via `curl http://127.0.0.1:4502/api/v1/serving/predict`


### Local startup

* Run local cluster via `sudo microk8s start`
* Make sure `kubectl` is connected to `microk8s` context (IP could change).
  * `cd ~/.kube && sudo microk8s config > config` or
  * `kubectl config set-context microk8s`
* Set default namespace as `demo` via `kubectl config set-context --current --namespace=demo`
* Run `sudo microk8s dashboard-proxy` to watch the cluster (or use IntelliJ tools or `k9s`)
* Run `skaffold dev --default-repo=localhost:32000` (indicating where images are stored for microk8s) for `./skaffold.yml`
* Run `Debug` from IntelliJ for debugging. @See *Local debugging* section.

Port forwards from cluster to localhost (@see `skaffold.yml`):
* MLflow is available at `http://127.0.0.1:4500:80/`
* Service is available at `http://127.0.0.1:4501:80/`
* Serving is available at `http://127.0.0.1:4502:80/`


### Final check

* TODO

### IntelliJ integration

* Docker
* Excildraw integration
* Install [**Kubernetes** plugin](https://www.jetbrains.com/help/idea/kubernetes.html).
* Install [Cloud Code](https://plugins.jetbrains.com/plugin/8079-cloud-code)

### Local debugging

* For debugging to work first you need to have installed **Cloud Code** IntellJ plugin.
* Add **source mappings** in **Dev on K8s -> Edit configuration -> Debug**. Point to root app folders in containers.
* Next, all python apps running inside containers must have a `python ...` ENTRYPOINTS/CMD, so that docker containers 
  are started from `python` command.
* Each `Dockerfile` must have `PYTHONPATH` set up, so that Python knows how to find modules. `PYTHONPATH` should point
  to parent folder of application.
* Set up a [virtual environment](https://docs.python.org/3/tutorial/venv.html) (`python3 -m venv ./venv`) for python 
  which will contain all the dependencies used across the project.
* **Attention**: `debug` only works for images that were built by Skaffold to avoid affecting system- or 
  infrastructure-level containers such as proxy sidecars. That is why `mlflow` was not included in `skaffold.yml` file.
  * Additionally, it not works with *code hot-reload*. I do not know if this is a bug but after trying to reload the code
    cluster stops.

### Used ports

* 9001, 9000

## Production environment 

### Configuration

* Create manually `demo` and `redis` namespaces
  * `kubectl create namespace demo`
  * `kubectl create namespace redis`
* Set up `mlflow-postgres-claim`. `mlflow-volume-claim.yml` contains config file to do that. You must do it once
  at cluster building stage, because all data produced by MLflow will be there. 
* Set up `demo-storage-cred` secret with file containing credentials to use `demo` bucket.
  * `kubectl create secret generic demo-storage-cred --from-file=./project-123.json`
* Redis configuration [1](https://www.containiq.com/post/deploy-redis-cluster-on-kubernetes)
  [2](https://www.youtube.com/watch?v=JmCn7k0PlV4&t=132s)
  * **Remember, ideally, you should map single PV (persistent volume) with one PVC (Persistent Volume Claim)**

### Deployment

#### Installation
* Bump helm Chart version in `./demo/helm/demo/Chart.yaml`
* Run `./demo/prod/build.sh`, package file will be moved to chosen instance.
* From `package` folder on instance in order to install helm Chart on GCP run: 
  * `helm install demo demo --values ./demo/values.prod.yaml`
  * Make sure `kubectl` is connected to `demo` namespace!

### Initial set up

* Run initial model training job from `model-training-job.yml` file with `ENV=test`. This will create entry in mlflow.
* Set chosen model to `production` Stage in `mlflow -> Models`.
* Restart `serving-deployment` (right now this is a way to load new model)
* Check if model prediction works via `curl http://[serving-loadbalancer-internal-ip]/api/v1/serving/predict`

## Naming conventions

* All kubernetes manifest files should have the following naming: `[app-name]-[resource-type].yml`
* Resources labels should be consistent with [app-name] from YML file.

## Diagrams

* `system-diagram.png` diagram shows general view of architecture. Contains all parts of kubernetes 
  resources together with connections with external systems.
* `system-local-diagram.png` diagram shows local environment set up.

## Helpers
* `k delete all --all -n demo` - delete all resources in a namespace
* `k rollout restart deployment serving-deployment` - restart deployment

### Kibana
* `transaction.duration.us > 1000000` - get all transactions longer than 1 second
* Delete all data for `demo-service` in kibana
```
POST /apm-*/_delete_by_query
{
    "query": {
    "bool": {
      "must": [
        {
          "term": {
            "service.name": {
              "value": "demo-service"
            }
          }
        }
      ]
    }
  }
}
```