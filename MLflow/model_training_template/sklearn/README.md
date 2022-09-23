### General information

* Connect to remote machine in GAT network: `ssh -J ssh.generalaudittool.com -L 5001:10.144.0.68:80 airflow-activeid`
* MLflow will be available on `localhost:5001`
* Code requirements: `scikit-learn==1.1.0, google-cloud-storage, mlflow`
* Remember to set `experiment_id` to change experiment destination