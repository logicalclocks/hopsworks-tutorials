package com.hopsworks.tutorials;


import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.UUID;

public class TestFGdataGenerator {

    private static final Random random = new Random();

    // Generate a random MyPojo instance
    public static TestFG generateRandomMyPojo() {
        // Create a random primary key using UUID
        String pk = UUID.randomUUID().toString();

        // Generate a random timestamp for eventTime
        Timestamp eventTime = getRandomTimestamp();

        // Generate a random list of Feat objects (array of struct)
        int featSize = random.nextInt(5) + 1; // between 1 and 5 Feat objects
        List<Feat> featList = new ArrayList<>();
        for (int i = 0; i < featSize; i++) {
            featList.add(generateRandomFeat());
        }

        return new TestFG(pk, eventTime, featList);
    }

    // Generate a random Feat instance
    private static Feat generateRandomFeat() {
        // Create a random SKU string, taking a substring for brevity
        String sku = "SKU-" + UUID.randomUUID().toString().substring(0, 8);
        Timestamp ts = getRandomTimestamp();
        return new Feat(sku, ts);
    }

    // Generate a random timestamp between Jan 1, 2000 and now
    private static Timestamp getRandomTimestamp() {
        long startMillis = Timestamp.valueOf("2000-01-01 00:00:00").getTime();
        long nowMillis = System.currentTimeMillis();
        long randomMillis = startMillis + (long)(random.nextDouble() * (nowMillis - startMillis));
        return new Timestamp(randomMillis);
    }

    // Main method to test the generator; renamed to testFG as requested
    public static void testFG(String[] args) {
        TestFG randomPojo = generateRandomMyPojo();
        System.out.println(randomPojo);
    }

    // For ease of running from the command line, you can also have a standard main method.
    public static void main(String[] args) {
        testFG(args);
    }
}

