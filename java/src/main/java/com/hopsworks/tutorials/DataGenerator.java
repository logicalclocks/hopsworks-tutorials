package com.hopsworks.tutorials;

import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import org.joda.time.LocalDate;

public class DataGenerator {
    /**
     * Probability-based helper to randomly turn a value into null.
     */
    private static <T> T maybeNull(T value, double nullProb, Random rand) {
        return rand.nextDouble() < nullProb ? null : value;
    }

    /**
     * Box-Muller transform to generate a random number ~ N(0,1).
     */
    private static double randomNormal(Random rand) {
        double u = rand.nextDouble();
        double v = rand.nextDouble();
        return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
    }

    public static List<DataRow> generateData(int size, long seed) {
        Random random = new Random(seed);

        // Prepare a simple "base" time array so timestamps can vary.
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime[] timeBase = new LocalDateTime[size];
        for (int i = 0; i < size; i++) {
            // Spread them out 1 day apart for demonstration
            timeBase[i] = now.minusDays(size - 1 - i);
        }

        List<DataRow> rows = new ArrayList<>(size);

        for (int i = 0; i < size; i++) {
            DataRow row = new DataRow();

            // 1) ID
            row.setId(i);

            // 2) Timestamp (random offset up to 1500 days, 10% chance to null)
            long offsetDays = random.nextInt(1500);
            LocalDateTime ts = timeBase[i].minusDays(offsetDays);
            Instant instant = ts.toInstant(ZoneOffset.UTC);
            row.setTimestamp(instant.toEpochMilli());

            // 3) Boolean flag (45% true, 45% false, 10% null)
            double pb = random.nextDouble();
            if (pb < 0.45) {
                row.setBooleanFlag(true);
            } else if (pb < 0.90) {
                row.setBooleanFlag(false);
            } else {
                row.setBooleanFlag(null);
            }

            // 4) Byte value (-128..127 range, 10% chance null)
            row.setByteValue(maybeNull((random.nextInt(256) - 128), 0.1, random));

            // 5) Short integer (-32768..32767 range, 10% chance null)
            row.setShortInt(maybeNull((random.nextInt(65536) - 32768), 0.1, random));

            // 6) Low categorical int (1..18, 5% null)
            int lv = 1 + random.nextInt(18);
            row.setLowCatInt(maybeNull(lv, 0.05, random));

            // 7) High categorical int (1..200, 15% null)
            int hv = 1 + random.nextInt(200);
            row.setHighCatInt(maybeNull(hv, 0.15, random));

            // 8) Long column (full 64-bit range, no null probability here)
            long lng = random.nextLong();
            row.setLongCol(lng);

            // 9) Float zero std (always 100.0, 20% null)
            Float fz = 100.0f;
            row.setFloatZeroStd(maybeNull(fz, 0.2, random));

            // 10) Float low std ~ normal(100, 1.5), 10% null
            double normLow = randomNormal(random) * 1.5; // stdev=1.5
            float fl = (float) (100 + normLow);
            row.setFloatLowStd(maybeNull(fl, 0.1, random));

            // 11) Float high std ~ normal(100, 5.6), 15% null
            double normHigh = randomNormal(random) * 5.6;
            float fh = (float) (100 + normHigh);
            row.setFloatHighStd(maybeNull(fh, 0.15, random));

            // 12) Double value ~ uniform(-1000..1000), 10% null
            double dv = -1000 + 2000 * random.nextDouble();
            row.setDoubleValue(maybeNull(dv, 0.1, random));

            // 13) Decimal value (double rounded to 2 decimals), 10% null
            double decRaw = -1000 + 2000 * random.nextDouble();
            double decRounded = Math.round(decRaw * 100.0) / 100.0;
            row.setDecimalvalue(maybeNull(decRounded, 0.1, random));

            // 14) Another timestamp column (again, random offset up to 1500, 10% null)
            long offsetDays2 = random.nextInt(1500);
            LocalDateTime ts2 = timeBase[i].minusDays(offsetDays2);
            row.setTimestampCol(maybeNull(ts2.toInstant(ZoneOffset.UTC).toEpochMilli(), 0.1, random));

            // 15) Date column (from the second timestamp, 100% null)
            LocalDate dt = new LocalDate(ts.getYear(), ts.getMonthValue(), ts.getDayOfMonth());
            row.setDateCol(maybeNull(dt, 1, random));

            // 16) Low categorical string, e.g. "low_category_<1..19>", 5% null
            int catLow = 1 + random.nextInt(19);
            String sl = "low_category_" + catLow;
            row.setStringLowCat(maybeNull(sl, 0.05, random));

            // 17) High categorical string, e.g. "high_category_<1..200>", 15% null
            int catHigh = 1 + random.nextInt(200);
            String sh = "high_category_" + catHigh;
            row.setStringHighCat(maybeNull(sh, 0.15, random));

            // 18) Array column (list of 3 random ints, no null for the list itself)
            // If you want the entire list or some elements to sometimes be null,
            // you could add that logic as well.
            List<Integer> arrayValues = new ArrayList<>();
            arrayValues.add(random.nextInt(10));
            arrayValues.add(random.nextInt(100));
            arrayValues.add(random.nextInt(1000));
            row.setArrayColumn(arrayValues);

            // Add this row to the list
            rows.add(row);
        }

        return rows;
    }
}
