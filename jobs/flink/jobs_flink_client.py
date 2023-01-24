import os
import requests
import argparse
import urllib.parse
import time
import json
from json.decoder import JSONDecodeError

from hops import project, jobs, util, constants, hdfs
from hops.exceptions import APIKeyFileNotFound, RestAPIError

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--hopsworks-url", help="Hopsworks url (domain and port")
parser.add_argument("-appid", "--application_id", help="The Flink job application id")
parser.add_argument("-jar", help="The Flink job jar file")
parser.add_argument("-p", "--project", help="The Hopsworks project name")
parser.add_argument("-j", "--job", default='flinkcluster', help="The Hopsworks job name")
parser.add_argument("-m", "--main", help="The entry point to the application, file with main function")
parser.add_argument("-a", "--apikey", default="jobs.token",
                    help="The file containing the API key to be used to connect to the project and submit the job")
parser.add_argument("-tm", "--task-managers", default="1", help="Number of Flink task managers")
parser.add_argument("-yjm", "--yarnjobManagerMemory", default="2048", help="Memory of the Flink job manager in MB")
parser.add_argument("-ytm", "--yarntaskManagerMemory", default="4096", help="Memory of the Flink task managers in MB")
parser.add_argument("-ys", "--yarnslots", default="1", help="Number of slots per TaskManager")
parser.add_argument("-parallelism", "--parallelism", default="1", help="Flink job parallelimsThe file containing the API key to be used to submit the job")
parser.add_argument("-args", "--job-arguments", help="Flink job runtime arguments")
parser.add_argument("action", type=str, nargs=argparse.REMAINDER, help="Job action")

args = parser.parse_args()
hopsworks_url = args.hopsworks_url.split(":")
project.connect(args.project, hopsworks_url[0], port=hopsworks_url[1], api_key=args.apikey)

if 'stop' in args.action:
    print(jobs.stop_job(args.job))
    print("Stopped Flink cluster.")
    exit(0)

# Check if Flink job with this name is already running
execution = jobs.get_executions(args.job,
                                "?filter_by=state:INITIALIZING,RUNNING,ACCEPTED,NEW,NEW_SAVING,SUBMITTED,"
                                "STARTING_APP_MASTER,AGGREGATING_LOGS&sort_by=id:desc")
app_id = args.application_id
if execution is None or execution['count'] == 0:
    # Create Flink Hopsworks job and start it. This effectively creates a Flink cluster to submit jobs to
    type = "flinkJobConfiguration"
    job_config = {"type": type,
                  "amQueue": "default",
                  "jobmanager.heap.size": args.yarnjobManagerMemory,
                  "amVCores": "1",
                  "numberOfTaskManagers": args.task_managers,
                  "taskmanager.heap.size": args.yarntaskManagerMemory,
                  "taskmanager.numberOfTaskSlots": args.yarnslots}
    jobs.create_job(args.job, job_config)

    print("Waiting for flink cluster to start...")
    jobs.start_job(args.job)
    # Wait 90 seconds until runner is in status "RUNNING",
    wait = 90
    wait_count = 0
    execution = jobs.get_executions(args.job, "?offset=0&limit=1&sort_by=id:desc")['items'][0]
    state = execution['state']
    while wait_count < wait and state != "RUNNING":
        time.sleep(5)
        wait_count += 5
        execution = jobs.get_executions(args.job, "?offset=0&limit=1&sort_by=id:desc")['items'][0]
        state = execution['state']

    if state != "RUNNING":
        print("Flink cluster did not start, check job logs for details")
        exit(1)
    else:
        app_id = execution['appId']
        print("app_id: " + execution['appId'])
        print("Flink cluster started successfully. Will now proceed to submit the job.")
else:
    app_id = execution['items'][0]['appId']
    print("Found Flink cluster with this name already running, will use it to submit the Flink job")

base_url = "https://" + args.hopsworks_url + "/hopsworks-api/flinkmaster/" + app_id

try:
    with open(args.apikey) as f:
        args.apikey = f.readline().strip()
except:
    raise APIKeyFileNotFound('API Key file could not be read or was not found')

# Upload Flink job jar to job manager
response = requests.post(
    base_url + "/jars/upload",
    verify=False,
    files={
        "jarfile": (
            os.path.basename(args.jar),
            open(args.jar, "rb"),
            "application/x-java-archive"
        )
    },
    headers={"Authorization": "Apikey " + args.apikey}
)

# Run job
jar_id = response.json()["filename"].split("/")[-1]
job_args = urllib.parse.quote(args.job_arguments)
base_url += "/jars/" + jar_id + "/run?entry-class=" + args.main + "&program-args=" + job_args
print("Submitting job to: " + base_url)

response = requests.post(
    base_url,
    verify=False,
    headers={"Content-Type" : "application/json", "Authorization": "Apikey " + args.apikey}
)

try:
    response_object = response.json()
except JSONDecodeError:
    response_object = None

if (response.status_code // 100) != 2:
    if response_object:
        error_code, error_msg, user_msg = util._parse_rest_error(response_object)
    else:
        error_code, error_msg, user_msg = "", "", ""

    raise RestAPIError("Could not execute HTTP request (url: {}), server response: \n "
                       "HTTP code: {}, HTTP reason: {}, error code: {}, error msg: {}, user msg: {}".format(
        base_url, response.status_code, response.reason, error_code, error_msg, user_msg))
else:
    print("Flink job was submitted successfully, please check Hopsworks UI for progress.")