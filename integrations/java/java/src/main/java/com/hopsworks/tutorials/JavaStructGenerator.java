package com.hopsworks.tutorials;


import org.apache.avro.Schema;
import org.apache.avro.Schema.Parser;
import org.apache.avro.generic.GenericData;
import org.apache.avro.generic.GenericRecord;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.UUID;

public class JavaStructGenerator {

    private static final Random random = new Random();

    /**
     * Generates a random microsecond timestamp.
     * This value is computed between Jan 1, 2000 and the current time.
     */
    private static Long getRandomMicroTimestamp() {
        // Jan 1, 2000 in milliseconds (946684800000L)
        long startMillis = 946684800000L;
        long nowMillis = System.currentTimeMillis();
        long randomMillis = startMillis + (long) (random.nextDouble() * (nowMillis - startMillis));
        return randomMillis * 1000; // convert milliseconds to microseconds
    }

    /**
     * Generates a random instance of JavaStructPojo.
     */
    public static JavaStructPojo generateJavaStructPojo() {
        // Generate a random primary key
        String pk = UUID.randomUUID().toString();
        // Generate a random event_time (timestamp in microseconds)
        Long eventTime = getRandomMicroTimestamp();

        // Create a random list of S_feat items (between 1 and 5 items)
        int featSize = random.nextInt(5) + 1;
        List<JavaStructPojo.S_feat> featList = new ArrayList<>();
        for (int i = 0; i < featSize; i++) {
            featList.add(generateRandomS_feat());
        }

        return new JavaStructPojo(pk, eventTime, featList);
    }

    public static JavaStructAvro generateJavaStructAvro() {

        JavaStructAvro javaStructAvro = new JavaStructAvro();

        // Set primary key (union of null and string, so non-null value)
        javaStructAvro.setPk(UUID.randomUUID().toString());

        // Set event_time (as a Long for timestamp-micros)
        javaStructAvro.setEventTime(getRandomMicroTimestamp());

        // Create a random list of S_feat items (between 1 and 5 items)
        // Generate a list of S_feat records.
        List<S_feat> featList = new ArrayList<>();
        int count = (int) (Math.random() * 5) + 1; // between 1 and 5 items
        for (int i = 0; i < count; i++) {
            S_feat feat = new S_feat();
            String sku = "SKU-" + UUID.randomUUID().toString().substring(0, 8);
            Long ts = getRandomMicroTimestamp();
            feat.setSku(sku);
            feat.setTs(ts);
            featList.add(feat);
        }
        javaStructAvro.setFeat(featList);

        return javaStructAvro;
    }

    /**
     * Generates a random GenericRecord for the given schema.
     */
    public static GenericRecord generateRandomRecord(Schema schema) {
        // Create the main record for the "java_struct_1" record.
        GenericRecord record = new GenericData.Record(schema);

        // "pk": union [null, string] -> choose a random UUID string.
        record.put("pk", UUID.randomUUID().toString());

        // "event_time": union [null, long] -> generate a random timestamp in microseconds.
        record.put("event_time", getRandomMicroTimestamp());

        // "feat": union [null, array<union[null, S_feat]>]
        // Retrieve the union schema for the "feat" field.
        Schema featFieldSchema = schema.getField("feat").schema();
        // In the union, index 1 is the non-null array schema.
        Schema arraySchema = featFieldSchema.getTypes().get(1); // non-null branch for the array
        // The array’s element is itself a union: [null, S_feat]
        Schema featElementUnionSchema = arraySchema.getElementType();
        // In the union, index 1 is the S_feat record schema.
        Schema sFeatSchema = featElementUnionSchema.getTypes().get(1); // non-null branch for S_feat

        // Create a list of S_feat records (choosing a non-null value).
        int featSize = random.nextInt(5) + 1; // between 1 and 5 items.
        List<GenericRecord> featList = new ArrayList<>();
        for (int i = 0; i < featSize; i++) {
            GenericRecord featRecord = new GenericData.Record(sFeatSchema);
            featRecord.put("sku", "SKU-" + UUID.randomUUID().toString().substring(0, 8));
            featRecord.put("ts", getRandomMicroTimestamp());
            featList.add(featRecord);
        }
        record.put("feat", featList);

        return record;
    }

    /**
     * Generates a random S_feat instance.
     */
    public static JavaStructPojo.S_feat generateRandomS_feat() {
        String sku = "SKU-" + UUID.randomUUID().toString().substring(0, 8);
        Long ts = getRandomMicroTimestamp();
        return new JavaStructPojo.S_feat(sku, ts);
    }

    public static List<JavaStructPojo> generateData(int size) {

        List<JavaStructPojo> rows = new ArrayList<>(size);

        for (int i = 0; i < size; i++) {
            JavaStructPojo data = generateJavaStructPojo();
            rows.add(data);
        }
        return rows;
    }

    public static List<JavaStructAvro> generateJavaStructAvroData(int size) {

        List<JavaStructAvro> rows = new ArrayList<>(size);

        for (int i = 0; i < size; i++) {
            JavaStructAvro data = generateJavaStructAvro();
            rows.add(data);
        }
        return rows;
    }

    /**
     * Test method to generate and print a random Avro record.
     */
    public static List<GenericRecord>  generateGenericRecordData(int size) throws IOException {
        String SCHEMA_JSON = "{\n" +
                "    \"type\": \"record\",\n" +
                "    \"name\": \"JavaStructAvro\",\n" +
                "    \"namespace\": \"com.hopsworks.tutorials\",\n" +
                "    \"fields\": [\n" +
                "        {\n" +
                "            \"name\": \"pk\",\n" +
                "            \"type\": [\"null\", \"string\"]\n" +
                "        },\n" +
                "        {\n" +
                "            \"name\": \"event_time\",\n" +
                "            \"type\": [\"null\", {\"type\": \"long\", \"logicalType\": \"timestamp-micros\"}]\n" +
                "        },\n" +
                "        {\n" +
                "            \"name\": \"feat\",\n" +
                "            \"type\": [\"null\", {\"type\": \"array\", \"items\": [\"null\", {\"type\": \"record\", \"name\": \"S_feat\", \"fields\": [\n" +
                "                {\"name\": \"sku\", \"type\": [\"null\", \"string\"]},\n" +
                "                {\"name\": \"ts\", \"type\": [\"null\", {\"type\": \"long\", \"logicalType\": \"timestamp-micros\"}]}\n" +
                "            ]}]}]\n" +
                "        }\n" +
                "    ]\n" +
                "}";

        Schema.Parser parser = new Parser();
        Schema schema = parser.parse(SCHEMA_JSON);

        List<GenericRecord> rows = new ArrayList<>(size);
        for (int i = 0; i < size; i++) {
            GenericRecord data = generateRandomRecord(schema);
            rows.add(data);
        }
        return rows;
    }
}
