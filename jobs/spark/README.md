# How to run

`jobs_spark_client.py` creates an archive of your local Python project, for example a PyCharm project, uploads it to
Hopsworks, creates a job and runs it.
 
This project comes with a toy example of a Python project, [`user_program`](https://github.com/logicalclocks/hops-examples/tree/master/jobs-client/user_program). It contains a program called `pi.py` 
which computes the Pi number in PySpark and also makes use of the `user_program/resources/util.py` module to showcase
how to import and use libraries in this example. 
 
You will also need to issue an API key from Hopsworks with scope `job, project, dataset_create` and save it under a file
`jobs.token`. Default value can be overriden by setting the `--apikey` argument. More information how to
create an API key is available under the User Guide in [here](https://hopsworks.readthedocs.io/en/stable/user_guide/hopsworks/apiKeys.html).
  
You can run the spark-client with:
 
`jobs_spark_client.py -w <ABSOLUTE_PATH_TO_user_program_without_trailing_slash> -p demo_spark_admin000 -u localhost:443 -m code/pi.py 1`
 
you can get more information by doing `jobs_spark_client.py -h`.
