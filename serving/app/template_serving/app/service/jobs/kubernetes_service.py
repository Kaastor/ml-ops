from kubernetes import client
from kubernetes import config

config.load_incluster_config()


class Kubernetes:
    @staticmethod
    def create_container(image, name, pull_policy, args, command, env):
        container = client.V1Container(
            image=image,
            name=name,
            image_pull_policy=pull_policy,
            args=args,
            command=command,
            env=env
        )

        return container

    @staticmethod
    def create_pod_template(pod_name, container):
        pod_template = client.V1PodTemplateSpec(
            spec=client.V1PodSpec(
                restart_policy="Never",
                containers=[container]
            ),
            metadata=client.V1ObjectMeta(
                name=pod_name
            ),
        )

        return pod_template

    @staticmethod
    def create_job(job_name, namespace, pod_template):
        metadata = client.V1ObjectMeta(
            name=job_name,
            namespace=namespace
        )

        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=metadata,
            spec=client.V1JobSpec(
                backoff_limit=0,
                ttl_seconds_after_finished=60,
                template=pod_template
            ),
        )

        return job
