import hopsworks
import argparse
import time

def connect(args):
    project = hopsworks.login(
        host=args.host, port=args.port, project=args.project, api_key_value=args.api_key
    )
    return project.get_flink_cluster_api()


def setup_cluster(flink_cluster_api, args):
    flink_job_config = {'type': 'flinkJobConfiguration', 'amQueue': 'default', 'amMemory': args.job_manager_mbs,
                        'amVCores': 1, 'jobmanager.heap.size': args.job_manager_mbs, 'taskmanager.numberOfTaskSlots': 1,
                        'taskmanager.heap.size': args.task_manager_mbs, 'jobType': 'FLINK', "appName": args.job}

    # producer job
    return flink_cluster_api.setup_cluster(name=args.job, config=flink_job_config)


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
    flink_cluster = setup_cluster(jobs_api, args)

    if flink_cluster._count_ongoing_executions() > 0:
        flink_cluster_execution = jobs_api.get_cluster(args.job)
    else:
        flink_cluster_execution = flink_cluster.start()

    flink_cluster_execution.upload_jar(args.jar)

    # Submit user jar
    jar_metadatas = flink_cluster_execution.get_jars()
    jar_metadata = jar_metadatas[0]
    jar_id = jar_metadata["id"]
    job_id = flink_cluster_execution.submit_job(jar_id, args.main, job_arguments=args.job_arguments)

    while True:
        flink_cluster_job = flink_cluster_execution.get_job(job_id)
        print("Flink job is: {}".format(flink_cluster_job["plan"]["type"]))
        time.sleep(20)
