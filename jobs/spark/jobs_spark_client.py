import os
import json
import argparse
import shutil
import ntpath
from hops import jobs, project, dataset

parser = argparse.ArgumentParser()
parser.add_argument("-w", "--workspace", help="The Python project workspace")
parser.add_argument("-p", "--project", help="The Hopsworks project name")
parser.add_argument("-j", "--job", default='job', help="The Hopsworks job name")
parser.add_argument("-d", "--dataset", default='Resources', help="The Hopsworks dataset to upload the Python program "
                                                                "and workspace")
parser.add_argument("-u", "--hopsworks-url", help="Hopsworks url (domain and port")
parser.add_argument("-m", "--main", help="The entry point to the application, file with main function")
parser.add_argument("-a", "--apikey", default='jobs.token', help="The file containing the API key to be used to "
                                                                 "submit the job")
parser.add_argument("cmd", type=str, nargs=argparse.REMAINDER, help="command to run python program")
args = parser.parse_args()

project_name = args.project
job_name = args.job
dataset_name = args.dataset
app_file = args.main
app_folder = args.workspace
dependency = ntpath.basename(app_folder)

if not os.path.isfile(args.apikey):
    os.environ['API_KEY'] = args.apikey

with open('job_config.json') as json_file:
    data = json_file.read()

data = data.replace("{PROJECT_NAME}", project_name) \
    .replace("{DATASET_NAME}", dataset_name) \
    .replace("{APP_FILE}", ntpath.basename(app_file)) \
    .replace("{JOB_NAME}", job_name) \
    .replace("{DEPENDENCY}", dependency + ".zip")

data = json.loads(data)

print("Jobs configuration:\n")
print(data)
print("===============================\n")

# Zip the folder containing the code
shutil.make_archive(dependency, "zip", app_folder)
hopsworks_url = args.hopsworks_url  .split(":")
project.connect(project_name, hopsworks_url[0], port=hopsworks_url[1], api_key=args.apikey)
print("Connected to project: " + project_name)

dataset.upload(os.path.join(app_folder, app_file), dataset_name)
dataset.upload(dependency + ".zip", dataset_name)
print("===============================\n")
print("Uploaded program to Hopsworks.")
jobs.create_job(job_name, data)
jobs.start_job(job_name, " ".join(args.cmd))
print("===============================\n")
print("Started job: " + job_name)