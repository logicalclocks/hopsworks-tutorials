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

    public static JavaStructAvro generateJavaStructAvro(Integer id) {

        JavaStructAvro javaStructAvro = new JavaStructAvro();

        // Set primary key (union of null and string, so non-null value)
        javaStructAvro.setPk(id.toString());

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
    public static GenericRecord generateRandomRecord(Schema schema, Integer id) {
        GenericRecord record = new GenericData.Record(schema);

        // Wrap "pk" in union [null, string]
        Schema pkSchema = schema.getField("pk").schema();
        record.put("pk", GenericData.get().deepCopy(pkSchema.getTypes().get(1), id.toString()));

        // Wrap "event_time" in union [null, timestamp-micros]
        Schema eventTimeSchema = schema.getField("event_time").schema();
        record.put("event_time", GenericData.get().deepCopy(eventTimeSchema.getTypes().get(1), getRandomMicroTimestamp()));

        // feat: [null, array<union[null, S_feat]>]
        Schema featUnionSchema = schema.getField("feat").schema();
        Schema arraySchema = featUnionSchema.getTypes().get(1); // array<union[null, S_feat]>
        Schema elementUnionSchema = arraySchema.getElementType(); // union[null, S_feat]
        Schema sFeatSchema = elementUnionSchema.getTypes().get(1); // S_feat

        List<Object> featList = new ArrayList<>();
        for (int i = 0; i < random.nextInt(5) + 1; i++) {
            GenericRecord sFeat = new GenericData.Record(sFeatSchema);
            sFeat.put("sku", GenericData.get().deepCopy(
                sFeatSchema.getField("sku").schema().getTypes().get(1),
                "SKU-" + UUID.randomUUID().toString().substring(0, 8))
            );
            sFeat.put("ts", GenericData.get().deepCopy(
                sFeatSchema.getField("ts").schema().getTypes().get(1),
                getRandomMicroTimestamp())
            );

            // Wrap sFeat in union [null, S_feat]
            Object wrappedSFeat = GenericData.get().deepCopy(elementUnionSchema.getTypes().get(1), sFeat);
            featList.add(wrappedSFeat);
        }

        // ✅ Wrap the entire list in its union
        record.put("feat", GenericData.get().deepCopy(featUnionSchema, featList));

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
            JavaStructAvro data = generateJavaStructAvro(i);
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
            GenericRecord data = generateRandomRecord(schema, i);
            rows.add(data);
        }
        return rows;
    }
}
