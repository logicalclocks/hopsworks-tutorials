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
import java.util.stream.Collectors;

public class Main {

    public static void main(String[] args) throws Exception {

        String host = args[0];
        Integer port = Integer.parseInt(args[1]);
        String apiKey = args[2];
        String projectName = args[3];
        String fgName = args[4];
        Integer fgVersion = Integer.parseInt(args[5]);
        String fvName = args[6];
        Integer fvVersion = Integer.parseInt(args[7]);

        FeatureStore fs = HopsworksConnection.builder()
                .host(host)
                .port(port)
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

        // get feature vector
        getSingleFeatureVector(fs, fvName, fvVersion);
        getBatchFeatureVectors(fs, fvName, fvVersion);

        // struct features
        structFeatures(fs);
    }

    private static void getSingleFeatureVector(FeatureStore fs, String fvName, Integer fvVersion) throws Exception {
        FeatureView fv = fs.getFeatureView(fvName, fvVersion);
        fv.initServing(false, true);

        // single lookup serving vector
        List<Object> singleVector = fv.getFeatureVector(new HashMap<String, Object>() {{
            put("id", productIdGenerator());
        }});
        System.out.println("Feature values from single vector lookup");
        System.out.println("[" + Joiner.on(", ").useForNull("null").join(singleVector) + "]");
    }

    private static void getBatchFeatureVectors(FeatureStore fs, String fvName, Integer fvVersion) throws Exception {
        FeatureView fv = fs.getFeatureView(fvName, fvVersion);
        fv.initServing(true, true);

        // batch lookup sering vector
        List<List<Object>> batchVector = fv.getFeatureVectors(productIdGenerator(160));

        // print results
        System.out.println("Feature values from batch lookup");
        for (List<Object> vector: batchVector) {
            System.out.println("[" + Joiner.on(", ").useForNull("null").join(vector) + "]");
        }
    }

    private static void structFeatures(FeatureStore fs) throws Exception {
        int size = 100;
        
        List<Feature> features = Arrays.asList(
                Feature.builder().name("pk").type("string").build(),
                Feature.builder().name("event_time").type("timestamp").build(),
                Feature.builder().name("feat").type("array<struct<sku:string,ts:timestamp>>")
                        .onlineType("varbinary(150)").build()
        );

        // Create a feature group JavaStructPojo
        StreamFeatureGroup structFg = fs.getOrCreateStreamFeatureGroup(
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
        List<JavaStructPojo> structPojos = JavaStructGenerator.generateData(size);
        structFg.insertStream(structPojos);

        // Create a feature group GenericRecord
        StreamFeatureGroup structGenericRecordFg = fs.getOrCreateStreamFeatureGroup(
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
        List<GenericRecord> structGenericRecords = JavaStructGenerator.generateGenericRecordData(size);
        structGenericRecordFg.insertStream(structGenericRecords);

        // Create a feature group avro
        StreamFeatureGroup structAvroRecordFg = fs.getOrCreateStreamFeatureGroup(
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
        List<JavaStructAvro> structAvroRecords = JavaStructGenerator.generateJavaStructAvroData(size);
        structAvroRecordFg.insertStream(structAvroRecords);

        // Create a feature view with the struct features
        Query structQuery = structFg.selectAll()
            .join(structGenericRecordFg.selectAll())
            .join(structAvroRecordFg.selectAll());
        FeatureView structFeatureView = fs.getOrCreateFeatureView("java_structs", structQuery, 1);

        // List of all primary keys
        List<Object> valueList = structPojos.stream()
                .map(record -> record.getPk())
                .collect(Collectors.toList());

        // Test get feature vector
        structFeatureView.initServing(false, true);
        for (Object i: valueList) {
            List<Object> results = structFeatureView.getFeatureVector(new HashMap<String, Object>() {{
                put("pk", i);
            }});

            System.out.println(results);
        }

        // Test batch feature vectors
        structFeatureView.initServing(true, true);
        List<List<Object>> results = structFeatureView.getFeatureVectors(new HashMap<String, List<Object>>() {{
            put("pk", valueList);
        }});
        System.out.println(results);
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
