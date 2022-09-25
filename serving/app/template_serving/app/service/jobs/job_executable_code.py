import asyncio
import os

from kubernetes import client
from demo_serving.app.jobs.kubernetes_service import Kubernetes


def create_job():
    k8s = Kubernetes()
    container = k8s.create_container(
        "image-name",
        "job-name",
        "Always",  # always get fresh image!
        [],
        ["python3", "-m", "demo_service.app.jobs.job_executable_code"],
        [client.V1EnvVar(
            name='name',
            value='value')]
    )

    _pod_name = "pod-name"
    _pod_spec = k8s.create_pod_template(_pod_name, container)

    _job_name = "job-name"
    _job = k8s.create_job(_job_name, "namespace", _pod_spec)

    batch_api = client.BatchV1Api()
    batch_api.create_namespaced_job("namespace", _job)


async def job_main_method():
    pass


# Run from Kubernetes Job
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    futures = [asyncio.ensure_future(job_main_method())]
    loop.run_until_complete(asyncio.wait(futures))
