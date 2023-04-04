import hopsworks
import requests
import argparse
import urllib.parse
import time
import os

from hopsworks.core import execution_api
from hopsworks.client import exceptions

START_CLUSTER_TIMEOUT = 600


def connect(args):
    project = hopsworks.login(
        host=args.host, port=args.port, project=args.project, api_key_value=args.api_key
    )
    return project.get_jobs_api()


def setup_cluster(jobs_api, args):
    try:
        # If the job already exists, retrieve it
        return jobs_api.get_job(args.job)
    except:
        # If the job doesn't exists, create a new job
        flink_cluster_config = {
            "appName": args.job,
            "type": "flinkJobConfiguration",
            "amQueue": "default",
            "amMemory": 2048,
            "amVCores": 1,
            "jobmanager.heap.size": args.job_manager_mbs,
            "taskmanager.numberOfTaskSlots": args.slots,
            "taskmanager.heap.size": args.task_manager_mbs,
            "jobType": "FLINK",
            "appPath": ""
        }

        return jobs_api.create_job(args.job, flink_cluster_config)


def start_cluster(job):
    e_api = execution_api.ExecutionsApi(job._project_id)
    execution = flink_cluster_job.run()

    polling_time = 0
    while polling_time < START_CLUSTER_TIMEOUT:
        execution = e_api._get(job, execution.id)
        if execution.state == "RUNNING":
            print("Cluster is running")
            return execution

        print(
            "Waiting for cluster to be running. Current state: {}".format(
                execution.state
            )
        )

        polling_time += 5
        time.sleep(5)

    raise "Execution {} did not start within the allocated time".format(execution.id)


def submit_jar(cluster_url, args):
    # Upload Jar
    upload_url = "{}/jars/upload".format(cluster_url)
    response = requests.post(
        upload_url,
        verify=False,
        files={
            "jarfile": (
                os.path.basename(args.jar),
                open(args.jar, "rb"),
                "application/x-java-archive",
            )
        },
        headers={"Authorization": "Apikey " + args.api_key},
    )

    if (response.status_code // 100) != 2:
        raise exceptions.RestAPIError(upload_url, response)

    print("Flink Jar uploaded. Starting the job")

    cluster_jar_response = response.json()

    # Submit execution
    jar_id = cluster_jar_response["filename"].split("/")[-1]
    if args.job_arguments:
        job_url = "{}/jars/{}/run?entry-class={}&program-args={}".format(
            cluster_url, jar_id, args.main, urllib.parse.quote(args.job_arguments)
        )
    else:
        job_url = "{}/jars/{}/run?entry-class={}".format(cluster_url, jar_id, args.main)

    response = requests.post(
        job_url,
        verify=False,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Apikey " + args.api_key,
        },
    )

    if (response.status_code // 100) != 2:
        raise exceptions.RestAPIError(upload_url, response)

    job_id = response.json()["jobid"]
    print("Submitted Job Id: {}".format(job_id))

    return job_id


def monitor(cluster_url, job_id, args):
    job_url = "{}/jobs/{}".format(cluster_url, job_id)

    while True:
        response = requests.get(
            job_url,
            verify=False,
            headers={
                "Authorization": "Apikey " + args.api_key,
            },
        )

        job = response.json()

        # Possible states: [ "INITIALIZING", "CREATED", "RUNNING", "FAILING", "FAILED", "CANCELLING", "CANCELED", "FINISHED", "RESTARTING", "SUSPENDED", "RECONCILING" ]
        if job["state"] not in [
            "INITIALIZING",
            "CREATED",
            "RUNNING",
            "RESTARTING",
            "RECONCILING",
        ]:
            raise Exception("Flink job is not healthy: {}".format(job["state"]))
        else:
            print("Flink job is: {}".format(job["state"]))

        time.sleep(5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Hopsworks cluster configuration
    parser.add_argument("--host", help="Hopsworks cluster host")
    parser.add_argument(
        "--port", help="Port on which Hopsworks is listening on", default=443
    )
    parser.add_argument("--api_key", help="API key to authenticate with Hopsworks")
    parser.add_argument("--project", help="Name of the Hopsworks project to connect to")

    # Flink cluster configuration
    parser.add_argument(
        "--job", default="flinkcluster", help="Flink job name in Hopsworks"
    )
    parser.add_argument(
        "--job_manager_mbs",
        default=2048,
        help="Memory of the Flink job manager in MB",
    )
    parser.add_argument(
        "--task_manager_mbs",
        default=2048,
        help="Memory of the Flink task managers in MB",
    )
    parser.add_argument("--slots", default=1, help="Number of slots per TaskManager")

    # User application configuration
    parser.add_argument("--jar", help="The Flink job jar file")
    parser.add_argument(
        "--main",
        help="The entry point to the application, file with main function",
    )
    parser.add_argument("--job_arguments", help="Flink job runtime arguments")

    args = parser.parse_args()

    # Setup connection to Hopsworks
    jobs_api = connect(args)

    # Setup Flink cluster
    flink_cluster_job = setup_cluster(jobs_api, args)
    execution = start_cluster(flink_cluster_job)
    flink_ui_url = "https://{}:{}/hopsworks-api/flinkmaster/{}".format(
        args.host, args.port, execution.app_id
    )
    print("Cluster is running at: {}/#/overview".format(flink_ui_url))

    # Submit user jar
    job_id = submit_jar(flink_ui_url, args)
    monitor(flink_ui_url, job_id, args)
