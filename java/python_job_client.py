import hopsworks
import argparse


def connect(args):
    project = hopsworks.login(
        host=args.host, port=args.port, project=args.project, api_key_value=args.api_key
    )
    return project.get_flink_cluster_api()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Hopsworks cluster configuration
    parser.add_argument("--host", help="Hopsworks cluster host")
    parser.add_argument(
        "--port", help="Port on which Hopsworks is listening on", default=443
    )
    parser.add_argument("--api_key", help="API key to authenticate with Hopsworks")
    parser.add_argument("--project", help="Name of the Hopsworks project to connect to")

    args = parser.parse_args()

    # Setup connection to Hopsworks
    project = connect(args)

    dataset_api = project.get_dataset_api()
    uploaded_file_path_1 = dataset_api.upload(
        "./setup/create_fg_fv.py", "Resources", overwrite=True
    )
    uploaded_file_path_2 = dataset_api.upload(
        "./setup/fg_for_java_write.py", "Resources", overwrite=True
    )

    jobs_api = project.get_jobs_api()

    # 1
    JOB_1_NAME = "create_fv_for_java"
    python_config = jobs_api.get_configuration("PYTHON")
    python_config["appPath"] = uploaded_file_path_2

    if not jobs_api.exists(JOB_1_NAME):
        job_1 = jobs_api.create_job(JOB_1_NAME, python_config)
    else:
        job_1 = jobs_api.get_job(JOB_1_NAME)

    job_1.run(await_termination=True)

    # 2
    JOB_2_NAME = "fg_for_java_write"
    python_config = jobs_api.get_configuration("PYTHON")
    python_config["appPath"] = uploaded_file_path_2

    if not jobs_api.exists(JOB_2_NAME):
        job_2 = jobs_api.create_job(JOB_2_NAME, python_config)
    else:
        job_2 = jobs_api.get_job(JOB_2_NAME)

    job_2.run(await_termination=True)
