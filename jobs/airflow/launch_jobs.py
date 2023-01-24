## NOTES:
##
## Example Airflow DAG for launching jobs on Hopsworks
## This example assumes that you have already defined
## four jobs from the Jobs UI.
##
## You can create a Spark tour project and copy the
## demo job.
##
## In this example we will launch one job and wait for
## it to finish successfully. Then launch two more jobs
## in parallel. We will wait only for one of them and
## only on successful completion we will launch the last
## job.

import airflow

from datetime import datetime, timedelta
from airflow import DAG

from hopsworks_plugin.operators.hopsworks_operator import HopsworksLaunchOperator
from hopsworks_plugin.sensors.hopsworks_sensor import HopsworksJobSuccessSensor

###################################################
## These variables should be changed accordingly ##
###################################################

# Username in Hopsworks
# Click on Account from the top right drop-down menu
DAG_OWNER = 'meb10000'

# Project name this DAG belongs to
PROJECT_NAME = 'demo_project'

# Job names as we defined them in Hopsworks Jobs UI
JOB_NAME_0 = "job-0"
JOB_NAME_1 = "job-1"
JOB_NAME_2 = "job-2"
JOB_NAME_3 = "job-3"


####################
## DAG definition ##
####################
delta = timedelta(minutes=-10)
now = datetime.now()

args = {
    'owner': DAG_OWNER,
    'depends_on_past': False,

    # DAG should have run 10 minutes before now
    # It will be automatically scheduled to run
    # when we upload the file in Hopsworks
    'start_date': now + delta,

    # Uncomment the following line if you want Airflow
    # to authenticate to Hopsworks using API key
    # instead of JWT
    #
    # NOTE: Edit only YOUR_API_KEY
    #
    #'params': {'hw_api_key': 'YOUR_API_KEY'}
}

# Our DAG
dag = DAG(
    # Arbitrary identifier/name
    dag_id = "job_launcher_dag",
    default_args = args,

    # Run the DAG only one time
    # It can take Cron like expressions
    # E.x. run every 30 minutes: */30 * * * * 
    schedule_interval = "@once"
)

# First task of DAG
task0 = HopsworksLaunchOperator(dag=dag,
                                project_name=PROJECT_NAME,
                                # Arbitrary task name
                                task_id="run_{0}".format(JOB_NAME_0),
                                #job_arguments="--key val", #runtime arguments to be passed to the job
                                job_name=JOB_NAME_0)

# Second task of DAG
task1 = HopsworksLaunchOperator(dag=dag,
                                project_name=PROJECT_NAME,
                                # Arbitrary task name
                                task_id="run_{0}".format(JOB_NAME_1),
                                #job_arguments="--key val", #runtime arguments to be passed to the job
                                job_name=JOB_NAME_1,

                                # Do not wait for the job to complete
                                wait_for_completion=False)

# Third task of DAG
task2 = HopsworksLaunchOperator(dag=dag,
                                project_name=PROJECT_NAME,
                                # Arbitrary task name
                                task_id="run_{0}".format(JOB_NAME_2),
				#job_arguments="--key val", #runtime arguments to be passed to the job
                                job_name=JOB_NAME_2,

                                # Do not wait for the job to complete
                                wait_for_completion=False)

# Fourth task of DAG
task3 = HopsworksLaunchOperator(dag=dag,
                                project_name=PROJECT_NAME,
                                # Arbitrary task name
                                task_id="run_{0}".format(JOB_NAME_3),
                                #job_arguments="--key val", #runtime arguments to be passed to the job
                                job_name=JOB_NAME_3,

                                # Do not wait for the job to complete
                                wait_for_completion=False)

# Special operator which will wait until job-2 finishes successfully
sensor = HopsworksJobSuccessSensor(dag=dag,
                                   project_name=PROJECT_NAME,
                                   task_id='wait_for_{0}'.format(JOB_NAME_2),
                                   job_name=JOB_NAME_2)


# First run task0, wait for it to finish successfully
# and then launch task1 and task2 in parallel. After that,
# wait for job-2 to finish and launch task3 without waiting
# for completion
task0 >> [task1, task2] >> sensor >> task3
