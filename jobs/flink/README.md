# How to run

`jobs_flink_client.py` can create/start/stop a Flink job in a Hopsworks project, effectively a Flink cluster, and submit
 Flink programs remotely without having to use the Hopsworks UI. 
 
## Setup
First you will also need to issue an API key from Hopsworks with scope `job, project` and save it under a file
`jobs.token`. Default value can be overriden by setting the `--apikey` argument. More information how to
create an API key is available under the User Guide in https://hopsworks.readthedocs.io/en/latest/ 

## Run a Flink program
You can start a Flink job (which starts a Flink cluster in Hopsworks) with:
 
`python3 jobs_flink_client.py -u <hopsworks_url> -p <project_name> -jar <path_to_your_flink_program> -m <flink_main_class_name> -args "<your_program_input_arguments"`
 
for example to run a Flink `WordCount.jar` program on a Hopsworks instance running at `localhost:443` with project
 `myproject`, you should do the following:
 `python3 jobs_flink_client.py -u localhost:443 -p myproject -jar /home/myuser/WordCount.jar -m org.apache.flink.streaming.examples.wordcount.WordCount -args "--arg1 a1 --arg2 a2"`

A Hopsworks Flink job starts a Flink cluster which typically is a long running job and can run multiple Flink programs. 
If `jobs_flink_client.py` discovers that a Flnk cluster with the same name (default name is `flinkcluster`) then the
Flink program, such as WordCount.jar, will be submitted to the existing cluster.

## Stop a Flink job(cluster)
Similarly to You can also stop the Hopsworsk Flink job which will shutdown the Flink cluster by doing 
`python3 jobs_flink_client.py -u localhost:443 -p myproject stop`

## Help
You can get more information on how to invoke the client by doing `jobs_flink_client.py -h`.
