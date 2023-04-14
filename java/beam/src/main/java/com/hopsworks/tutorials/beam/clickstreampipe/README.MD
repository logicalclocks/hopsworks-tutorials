<!--
    Licensed to the Apache Software Foundation (ASF) under one
    or more contributor license agreements.  See the NOTICE file
    distributed with this work for additional information
    regarding copyright ownership.  The ASF licenses this file
    to you under the Apache License, Version 2.0 (the
    "License"); you may not use this file except in compliance
    with the License.  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing,
    software distributed under the License is distributed on an
    "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
    KIND, either express or implied.  See the License for the
    specific language governing permissions and limitations
    under the License.
-->
# Overview

The e-commerce sample application illustrates common use cases and best practices for implementing streaming data analytics and real-time AI. Use it to learn how to dynamically respond to customer actions by analyzing and responding to events in real time, and also how to store, analyze and visualize that event data for longer-term insights.

The application is implemented in Java, and uses the following products:

* Pub/Sub
* Dataflow
* BigQuery
* Cloud Bigtable

This sample retail application, is intended to be used as an exemplar blueprint for similar applications.

For this first version of the application the following items are shown:

Processing and Analysis of:
* Clickstream data being sent by online systems to Cloud PubSub.
* Transaction data being sent by on-premise / SaaS systems to Cloud PubSub.
* Stock data being sent by on-premise / SaaS systems to Cloud PubSub.

> Note: All data is sent as JSON, this is normal for clickstream data but not necessarily the norm for Transaction / Stock data. Different data formats (e.g xml)  will be shown in future versions.

# Goals
The application was designed to address the following requirements:

* Validate incoming data and apply corrections to it where possible.
* Analyze clickstream data to keep a count of the number of views per product in a given time period. Store this information in a low latency store where the application can use it to provide 'number of people who viewed this product' messages to customers on the web site.
* Use transaction data to inform inventory ordering:

    * Analyze transaction data to calculate the total number of sales for each item, both by store and globally, for a given period.
    * Analyze inventory data to calculate the incoming inventory for each item.
    * Pass this data to inventory systems on a continuous basis so it can be used for inventory purchasing decsions decisions.
* Validate incoming data and apply corrections to it where possible. Write any uncorrectable data to a dead letter queue for additional analysis and processing. Make a metric that represents the percentage of incoming data that gets sent to the dead letter queue available for monitoring and alerting.
* Process all incoming data into a standard format and store it in a data warehouse to use for future analysis and visualization.
* Denormalize transaction data for in-store sales so that it can include information like the latitude and longitude of the store location. Provide the the store information through a slowly changing table in BigQuery, using the store ID as a key.

# Data
The application processes the following types of data:

* Clickstream data being sent by Newkick's web interface.
* Transaction data being sent by on-premise or software-as-a-service (SaaS) systems.
* Inventory data being sent by on-premise or SaaS systems.

------
    Note: All data used by the application is sent as JSON. 
    This is a standard format for clickstream data, but real-world formats for transaction and inventory data vary.
------
# To run the pipeline locally you can make use of the smoke test
```
gradlew :data-engineering-dept:pipelines:test --tests RetailDataProcessingPipelineSimpleSmokeTest --info --rerun-tasks
```
# Task patterns
The application contains a number of task patterns that show the best way to accomplish Java programming tasks that are commonly needed to create this type of application.

## Using Apache Beam schemas to work with structured data
### Content
We recommend using Apache Beam schemas to make processing structured data easier.

Converting your objects to Rows lets you produce very clean Java code, which makes your directed acyclic graph (DAG) building exercise easier. You can also reference object properties as fields within the analytics statements that you create, instead of having to call methods.
### Examples
[CountViewsPerProduct](data-engineering-dept/business-logic/src/main/java/com/google/dataflow/sample/retail/businesslogic/core/transforms/clickstream/CountViewsPerProduct.java)
## Using JsonToRow to convert JSON data
### Content
Processing JSON strings in Dataflow is a common need. For example, when processing clickstream information captured from web applications. To process JSON strings, you need to convert them into either Rows or plain old Java objects (POJOs) for the duration of the pipeline processing.

The Apache Beam utility class JsonToRow is a good solution for converting JSON strings to Rows. The 2 considerations to take into account when using JsonToRow are:

Read JSON -> Use JsonToRow to convert to Row -> Use Convert.fromRows() to convert to POJO

If JsonToRow won't work with your data, Gson is a reasonable alternative. Gson is fairly relaxed in its default processing of data, which may require you to build more validation into the data conversion process.

### Examples
[ClickstreamProcessing.java](data-engineering-dept/business-logic/src/main/java/com/google/dataflow/sample/retail/businesslogic/core/transforms/clickstream/ClickstreamProcessing.java)

[JSONUtils.java](data-engineering-dept/business-logic/src/main/java/com/google/dataflow/sample/retail/businesslogic/core/utils/JSONUtils.java)

## Using the AutoValue code generator to generate plain old Java objects (POJOs)
### Content
Apache Beam schemas are overall the best way to represent objects in a pipeline, because of the intuitive way the allow you to work with structured data. Today, however, there are still places where a POJO is needed, for example, when dealing with key-value objects or handling object state. Hand building POJOs requires you to code appropriate overrides for the equals() and hashcode() methods, which can be time-consuming and error-prone. You can end up with inconsistent application behavior or even data loss if you don't get it right.

To avoid this, use the AutoValue class builder to generate POJOs. This ensures that the necessary overrides are covered and lets you avoid the potential errors introduced by hand-coding, though one minor downside is that it does introduce a fair amount of boilerplate code.

AutoValue is also heavily used within the Apache Beam code base, so familiarity with it is useful if you want to develop Apache Beam pipelines on Dataflow using Java.

For more information, see Why AutoValue? and the AutoValue docs.
### Examples
[Clickstream.java](data-engineering-dept/data-objects/src/main/java/com/google/dataflow/sample/retail/dataobjects/ClickStream.java)
## Queuing unprocessable data for further analysis
### Content
In production systems, it is important to handle problematic data. You should validate and if possible correct data in-stream, but where correction isn't possible, we recommend logging the value to a queue (sometimes called a "dead letter" queue) for later analysis. A common place to see issues is when converting data from one format to another, for example when converting JSON strings to Rows.

To address this, we recommend using a multi-output transform to shuttle the elements containing the problematic data into another PCollection for further processing. Since this is a common operation that you might want to use in many places in a pipeline, so you should make the transform generic enough to use in multiple places. To do this, first create an error object to wrap common properties, including the original data, then create a sink transform that has multiple options for the destination, as needed to meet your application requirements.
### Examples
[JSONUtils.java](data-engineering-dept/business-logic/src/main/java/com/google/dataflow/sample/retail/businesslogic/core/utils/JSONUtils.java)

[ErrorMsg.java](data-engineering-dept/business-logic/src/main/java/com/google/dataflow/sample/retail/businesslogic/core/transforms/ErrorMsg.java)

[DeadLetterSink.java](data-engineering-dept/business-logic/src/main/java/com/google/dataflow/sample/retail/businesslogic/core/transforms/DeadLetterSink.java)

## Applying data validation transforms serially
### Content
Data collected from external systems often needs cleaning. You should build your pipeline so that it can correct problematic data in-stream where possible, or send it to a queue for further analysis if it can't be corrected.

Since a single message can suffer from multiple issues that need correction, think carefully about the directed acyclic graph (DAG) you'll need; if an element contains data with multiple defects, you must ensure that the element flows through all of the appropriate transforms.

For example imagine a element with these properties, neither of which should be null:

{"itemA": null,"itemB": null}

You should make sure the element flows through transforms that correct both potential issues:

badElements.apply(fixItemA).apply(fixItemB)

This means that your pipeline might have more serial steps, but fusion should help minimize any processing overhead introduced by this.
### Examples
[ValidateAndCorrectClickStreamEvents.java](data-engineering-dept/business-logic/src/main/java/com/google/dataflow/sample/retail/businesslogic/core/transforms/clickstream/ValidateAndCorrectClickStreamEvents.java)

## Using DoFn.StartBundle to micro-batch calls to external services

### Contents
Invoking external APIs as part of your pipeline is a common need. Because a pipeline distributes work across many compute resources, you can overwhelm an external service endpoint if you make a single call for each element flowing through the system, especially if you haven't applied any reducing functions.

To avoid this, we recommend batching calls to external systems. There are several ways to achieve this, including using a GroupByKey transform or using the Apache Beam Timer API. However, these approaches both require shuffling, which introduces some processing overhead as well as the need for a magic number to determine the key space.

Instead, we recommend that you use the StartBundle and FinishBundle lifecycle elements to batch your data since no shuffling is needed.

One minor downside is that bundle sizes are dynamically determined by the implementation of the runner, based on what's currently happening inside the pipeline and its workers, and in stream mode will often be small in size. Dataflow bundling is influenced by backend factors like sharding usage, how much data is available for a particular key, and the throughput of the pipeline.
### Examples
[ValidateAndCorrectClickStreamEvents.java](data-engineering-dept/business-logic/src/main/java/com/google/dataflow/sample/retail/businesslogic/core/transforms/clickstream/ValidateAndCorrectClickStreamEvents.java)

## Using an appropriate side-input pattern
### Content
In streaming analytics applications, it is common to enrich data with additional information that might be useful for further analysis. For example, if you have the storeId for a transaction, you might want to add information about the store location. You would typically add this additional information by taking an element and "denormalizing" it by bringing in information from a lookup table.

For lookup tables that are both slowly changing and smaller in size, it works well to bring the table into the pipeline as a singleton class that implements the Map<K,V> interface. This lets you avoid having each element do an API call for its lookup. Once you include a copy of a table in the pipeline, you need to update it periodically to keep it fresh.

We recommend using the Apache Beam Side input patterns to handle slow updating side inputs.
### Examples
[SlowMovingStoreLocationDimension.java](data-engineering-dept/business-logic/src/main/java/com/google/dataflow/sample/retail/businesslogic/externalservices/SlowMovingStoreLocationDimension.java)

# Setup required for running the sample application on Dataflow service

Please note this application has many inputs and outputs.
All of these will need to be enabled in your project.
Please consult
*PubSub as both input and output.

### Create PubSub Topics and Subscriptions
#### Create four topics:
* "Clickstream-inbound"
* "Transactions-inbound"
* "Inventory-inbound"
* "Inventory-outbound"

#### Create three subscriptions
* "Clickstream-inbound-sub"
* "Transactions-inbound-sub"
* "Inventory-inbound-sub"

### Create BigQuery objects
#### Create two dataset in BigQuery
* "Retail_Store"
* "Retail_Store_Aggregations"
#### Create a location table
This table is used by the slow update side input pattern.
The test data has only one store with id 1.
```
CREATE TABLE
  Retail_Store.Store_Locations ( d INT64,
    city STRING,
    state STRING,
    zip INT64 );
INSERT INTO
  Retail_Store.Store_Locations
VALUES
  (1, 'a_city', 'a_state',00000); 
```
### Create a Bigtable instance
#### Create an instance
* Create a BigTable instance within your project
#### Create a table
* Create the "PageView5MinAggregates" table with Column family "pageViewAgg"
# Deploy Using Terraform
Please refer to [this document](terraform/README.MD) to deploy resources using terraform
