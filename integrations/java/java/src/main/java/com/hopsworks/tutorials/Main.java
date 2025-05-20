package com.hopsworks.tutorials;

import com.logicalclocks.hsfs.Feature;
import com.logicalclocks.hsfs.FeatureStore;
import com.logicalclocks.hsfs.FeatureView;
import com.logicalclocks.hsfs.HopsworksConnection;
import com.logicalclocks.hsfs.StreamFeatureGroup;
import com.logicalclocks.hsfs.constructor.Query;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;

public class Main {

    public static void main(String[] args) throws Exception {

        String host = args[0];
        String apiKey =args[1];
        String projectName = args[2];

        FeatureStore fs = HopsworksConnection.builder()
                .host(host)
                .port(443)
                .project(projectName)
                .apiKeyValue(apiKey)
                .hostnameVerification(false)
                .build()
                .getFeatureStore();

        // create Feature Group
        List<Feature> features = new ArrayList<Feature>() {{
            add(new Feature("id", "int", true, false));
            add(new Feature("timestamp", "timestamp", false, false));
            add(new Feature("boolean_flag", "boolean", false, false));
            add(new Feature("byte_value", "int", false, false));
            add(new Feature("short_int", "int", false, false));
            add(new Feature("low_cat_int", "int", false, false));
            add(new Feature("high_cat_int", "int", false, false));
            add(new Feature("long_col", "bigint", false, false));
            add(new Feature("float_zero_std", "float", false, false));
            add(new Feature("float_low_std", "float", false, false));
            add(new Feature("float_high_std", "float", false, false));
            add(new Feature("double_value", "double", false, false));
            add(new Feature("decimalValue", "double", false, false));
            add(new Feature("timestamp_col", "timestamp", false, false));
            add(new Feature("date_col", "date", false, false));
            add(new Feature("string_low_cat", "string", false, false));
            add(new Feature("string_high_cat", "string", false, false));
            add(new Feature("array_column", "array<int>", false, false));
        }};

        fs.createStreamFeatureGroup()
                .name("java_test")
                .version(1)
                .primaryKeys(Collections.singletonList("id"))
                .eventTime("timestamp")
                .onlineEnabled(true)
                .features(features)
                .build()
                .save();

        fs.createStreamFeatureGroup()
                .name("java_test")
                .version(2)
                .primaryKeys(Collections.singletonList("id"))
                .eventTime("timestamp")
                .onlineEnabled(true)
                .features(features)
                .build()
                .save();

        StreamFeatureGroup featureGroup1 = fs.getStreamFeatureGroup("java_test", 1);
        StreamFeatureGroup featureGroup2 = fs.getStreamFeatureGroup("java_test", 2);

        // Generate, for example, 100 rows with seed=42
        List<DataRow> data = DataGenerator.generateData(100, 42L);

        // insert data
        featureGroup1.insertStream(data);
        featureGroup2.insertStream(data);

        // Feature View
        // Query with prefix
        Query query = new Query(featureGroup1, features).join( new Query(featureGroup1, features), "left_");

        // create feature view
        fs.getOrCreateFeatureView("java_test", query, 1);

        // get feature view
        FeatureView fv = fs.getFeatureView("java_test", 1);

        // single lookup sering vector
        Integer id = productIdGenerator();
        List<Object> singleVector = fv.getFeatureVector(new HashMap<String, Object>() {{
            put("id", id);
        }});
        DataRow row = findDataRowById(data, id);
        testFeatureVectorOrder(singleVector, features, row);

        // batch lookup sering vector
        fv.initServing(true, true);
        List<List<Object>> batchVector = fv.getFeatureVectors(productIdGenerator(160));

        // print results
        System.out.println("Feature values from batch lookup");
        for (List<Object> vector: batchVector) {
            testFeatureVectorOrder(vector, features, row);
        }
    }

    private static int productIdGenerator() {
        int leftLimit = 0;
        int rightLimit = 1000;
        return leftLimit + (int) (Math.random() * (rightLimit - leftLimit));
    }

    public static void testFeatureVectorOrder(List<Object> singleVector, List<Feature> features, DataRow row) {
        // Assert size
        // Assert that the vector size matches the number of features
        assert singleVector.size() == features.size() * 2 : "Vector size doesn't match features size";

        // Assert that each element in the vector corresponds to the expected feature in the right order
        for (int i = 0; i < features.size() * 2; i++) {
            String extepectedFeatureName = features.get(i).getName();
            if (i >= features.size()){
                extepectedFeatureName = "left_" + extepectedFeatureName;
            }
            Object expectedValue = row.get(extepectedFeatureName);
            Object vectorValue = singleVector.get(i);
            assertValuesEqual(expectedValue, vectorValue, extepectedFeatureName, i);
        }
    }

    /**
     * Find a DataRow by its ID using a traditional loop
     * @param data The list of DataRows
     * @param searchId The ID to search for
     * @return The found DataRow or null if not found
     */
    public static DataRow findDataRowById(List<DataRow> data, Integer searchId) {
        for (DataRow row : data) {
            if (row.getId() != null && row.getId().equals(searchId)) {
                return row;
            }
        }
        return null;
    }

    /**
     * Assert that two values are equal, handling different data types
     * @param expectedValue The expected value from the row
     * @param vectorValue The actual value from the vector
     * @param featureName The name of the feature (for error messages)
     * @param index The index in the list (for error messages)
     */
    private static void assertValuesEqual(Object expectedValue, Object vectorValue, String featureName, int index) {
        String errorMsg = "Values don't match at index " + index + " for feature '" + featureName +
                "': expected=" + expectedValue + ", actual=" + vectorValue;

        // If both are null, they're equal
        if (expectedValue == null && vectorValue == null) {
            return;
        }

        // If one is null but the other isn't, they're not equal
        assert (expectedValue != null && vectorValue != null) : errorMsg;

        // Handle different types appropriately
        if (expectedValue instanceof Number && vectorValue instanceof Number) {
            // For numeric types, compare their double values to handle different numeric types
            double expectedDouble = ((Number) expectedValue).doubleValue();
            double actualDouble = ((Number) vectorValue).doubleValue();

            // Use a small delta for floating point comparisons
            double delta = 0.0000001;
            assert Math.abs(expectedDouble - actualDouble) <= delta :
                    "Value mismatch at index " + index + " for feature '" + featureName +
                            "': expected=" + expectedDouble + ", actual=" + actualDouble;
        }
        else if (expectedValue instanceof Boolean && vectorValue instanceof Boolean) {
            assert expectedValue.equals(vectorValue) :
                    "Boolean value mismatch at index " + index + " for feature '" + featureName +
                            "': expected=" + expectedValue + ", actual=" + vectorValue;
        }
        else if (expectedValue instanceof String && vectorValue instanceof String) {
            assert expectedValue.equals(vectorValue) :
                    "String value mismatch at index " + index + " for feature '" + featureName +
                            "': expected=" + expectedValue + ", actual=" + vectorValue;
        }
        else if (expectedValue instanceof java.util.Date && vectorValue instanceof java.util.Date) {
            assert ((java.util.Date) expectedValue).getTime() == ((java.util.Date) vectorValue).getTime() :
                    "Date value mismatch at index " + index + " for feature '" + featureName +
                            "': expected=" + expectedValue + ", actual=" + vectorValue;
        }
        else if (expectedValue instanceof java.util.List && vectorValue instanceof java.util.List) {
            // For array types, compare each element
            java.util.List<?> expectedList = (java.util.List<?>) expectedValue;
            java.util.List<?> actualList = (java.util.List<?>) vectorValue;

            assert expectedList.size() == actualList.size() :
                    "List size mismatch at index " + index + " for feature '" + featureName +
                            "': expected size=" + expectedList.size() + ", actual size=" + actualList.size();

            for (int j = 0; j < expectedList.size(); j++) {
                assertValuesEqual(expectedList.get(j), actualList.get(j),
                        featureName + "[" + j + "]", index);
            }
        }
        else {
            // For any other types, use the equals method
            assert expectedValue.equals(vectorValue) : errorMsg;
        }
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
