package com.hopsworks.tutorials;

import com.logicalclocks.hsfs.Feature;
import com.logicalclocks.hsfs.FeatureStore;
import com.logicalclocks.hsfs.FeatureView;
import com.logicalclocks.hsfs.HopsworksConnection;
import com.logicalclocks.hsfs.StreamFeatureGroup;
import com.logicalclocks.hsfs.TimeTravelFormat;

import com.google.common.base.Joiner;

import com.logicalclocks.hsfs.constructor.Query;
import org.apache.avro.generic.GenericRecord;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;

public class Main {

    public static void main(String[] args) throws Exception {

        String host = args[0];
        String apiKey =args[1];
        String projectName = args[2];
        String fgName = args[3];
        Integer fgVersion = Integer.parseInt(args[4]);
        String fvName = args[5];
        Integer fvVersion = Integer.parseInt(args[6]);

        FeatureStore fs = HopsworksConnection.builder()
                .host(host)
                .port(443)
                .project(projectName)
                .apiKeyValue(apiKey)
                .hostnameVerification(false)
                .build()
                .getFeatureStore();

        // Feature Group
        StreamFeatureGroup featureGroup = fs.getStreamFeatureGroup(fgName, fgVersion);
        // Generate, for example, 100 rows with seed=42
        List<DataRow> data = DataGenerator.generateData(100, 42L);
        featureGroup.insertStream(data);


        List<Feature> features = Arrays.asList(
                Feature.builder().name("pk").type("string").build(),
                Feature.builder().name("event_time").type("timestamp").build(),
                Feature.builder().name("feat").type("array<struct<sku:string,ts:timestamp>>")
                        .onlineType("varbinary(150)").build()
        );

        StreamFeatureGroup structFg =fs.getOrCreateStreamFeatureGroup(
                "java_struct",
                1,
                "fg containing struct features",
                true,
                TimeTravelFormat.HUDI,
                Arrays.asList("pk"),
                null,
                "event_time",
                null,
                features,
                null,
                null,
                null,
                null);
        structFg.save();
        List<JavaStructPojo> structPojos = JavaStructGenerator.generateData(100);
        structFg.insertStream(structPojos);

        StreamFeatureGroup structGenericRecordFg =fs.getOrCreateStreamFeatureGroup(
                "java_struct_generic",
                1,
                "fg containing struct features",
                true,
                TimeTravelFormat.HUDI,
                Arrays.asList("pk"),
                null,
                "event_time",
                null,
                features,
                null,
                null,
                null,
                null);
        structGenericRecordFg.save();
        List<GenericRecord> structGenericRecords = JavaStructGenerator.generateGenericRecordData(100);
        structGenericRecordFg.insertStream(structGenericRecords);

        StreamFeatureGroup structAvroRecordFg =fs.getOrCreateStreamFeatureGroup(
                "java_struct_avro",
                1,
                "fg containing struct features",
                true,
                TimeTravelFormat.HUDI,
                Arrays.asList("pk"),
                null,
                "event_time",
                null,
                features,
                null,
                null,
                null,
                null);
        structAvroRecordFg.save();

        List<JavaStructAvro> structAvroRecords = JavaStructGenerator.generateJavaStructAvroData(100);
        structAvroRecordFg.insertStream(structAvroRecords);

        Query structQuery = structAvroRecordFg.selectAll().join(structGenericRecordFg.selectAll());
        FeatureView structFeatureView = fs.getOrCreateFeatureView("java_structs", structQuery, 1);

        for (int i = 0; i < 100; i++) {
            Integer finalI = i;
            structFeatureView.getFeatureVector(new HashMap<String, Object>() {{
                put("pk", finalI.toString());
            }});
        }

        // Feature View
        // get feature view
        FeatureView fv = fs.getFeatureView(fvName, fvVersion);

        // single lookup sering vector
        List<Object> singleVector = fv.getFeatureVector(new HashMap<String, Object>() {{
            put("id", productIdGenerator());
        }});
        System.out.println("Feature values from single vector lookup");
        System.out.println("[" + Joiner.on(", ").useForNull("null").join(singleVector) + "]");

        // batch lookup sering vector
        fv.initServing(true, true);
        List<List<Object>> batchVector = fv.getFeatureVectors(productIdGenerator(160));

        // print results
        System.out.println("Feature values from batch lookup");
        for (List<Object> vector: batchVector) {
            System.out.println("[" + Joiner.on(", ").useForNull("null").join(vector) + "]");
        }
    }

    private static int productIdGenerator() {
        int leftLimit = 0;
        int rightLimit = 1000;
        return leftLimit + (int) (Math.random() * (rightLimit - leftLimit));
    }

    private static java.util.Map<java.lang.String,java.util.List<java.lang.Object>> productIdGenerator(int batch) {
        List<Object> productIds = new ArrayList<>();
        while (productIds.size() <= batch){
            int productId = productIdGenerator();
            if (!productIds.contains(productId)) {
                productIds.add(productId);
            }
        }
        return new HashMap<String, List<Object>>() {{put("id", productIds);}};
    }
}
