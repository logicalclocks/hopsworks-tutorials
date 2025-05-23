package com.hopsworks.tutorials;


import org.apache.avro.Schema;
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
    public static JavaStructPojo generateJavaStructPojo(Integer id) {
        // Generate a random primary key
        String pk = id.toString();
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

            // no createUnion, just add the record
            Object unionWrappedSFeat = GenericData.get().deepCopy(elementUnionSchema, sFeat);
            featList.add(unionWrappedSFeat);
        }

        // no wrapping for union of feat, just set the list (or null)
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
            JavaStructPojo data = generateJavaStructPojo(i);
            rows.add(data);
        }
        return rows;
    }

    /**
     * Test method to generate and print a random Avro record.
     */
    public static List<GenericRecord> generateGenericRecordData(Schema schema, int size) throws IOException {
        List<GenericRecord> rows = new ArrayList<>(size);
        for (int i = 0; i < size; i++) {
            GenericRecord data = generateRandomRecord(schema, i);
            rows.add(data);
        }
        return rows;
    }
}
