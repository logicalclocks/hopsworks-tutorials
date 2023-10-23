import hopsworks
import argparse


def connect(args):
    if args.host is None or args.project is None:
        project = hopsworks.login(api_key_value=args.api_key)
    else:
        project = hopsworks.login(
            host=args.host, port=args.port, project=args.project, api_key_value=args.api_key
        )
    return project.get_jobs_api()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Hopsworks cluster configuration
    parser.add_argument("--host", help="Hopsworks cluster host", default=None)
    parser.add_argument(
        "--port", help="Port on which Hopsworks is listening on", default=443
    )
    parser.add_argument("--api_key", help="API key to authenticate with Hopsworks")
    parser.add_argument("--project", help="Name of the Hopsworks project to connect to", default=None)

    # job name
    parser.add_argument(
        "--jobname", help="Name of feature group backfill job in Hopsworks"
    )

    args = parser.parse_args()

    # Setup connection to Hopsworks
    jobs_api = connect(args)

    backfill_job = jobs_api.get_job(args.jobname)

    # Run the job
    execution = backfill_job.run(await_termination=True)

    # True if job executed successfully
    print(execution.success)

    # Download logs
    out_log_path, err_log_path = execution.download_logs()