## on-demand feature in Hopsworks

This example shows how to implement an on-demand feature in Hopsworks - that is, a feature that is computed at  
request-time using application-supplied inputs for an online model .

We use a house-price estimated dataset/model to demonstrate how to implement an on-demand feature.
The on-demand feature here is the zipcode (or postcode) that is computed using longitude/latitude parameters. In our online application, longitude and latitude are provided as parameters to the application, and the same Python function used to calculate the zipcode in the feature pipeline is used to compute the zipcode in the Online Inference pipeline. This is achieved by implementing the on-demand features as a Python function in a Python module. We then ensure that the same version of the Python module is installed in both the feature and inference pipelines.


![diagram](images/diagram.png)
