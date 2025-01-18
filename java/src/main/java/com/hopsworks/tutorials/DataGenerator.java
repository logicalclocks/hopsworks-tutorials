package com.hopsworks.tutorials;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class DataGenerator {

    public static void main(String[] args) {
        // Generate, for example, 100 rows with seed=42
        List<DataRow> data = DataGenerator.generateData(100, 42L);

        // Print the first row’s fields
        DataRow first = data.get(0);
        System.out.println("ID: " + first.getId());
        System.out.println("Timestamp: " + first.getTimestamp());
        System.out.println("BooleanFlag: " + first.getBooleanFlag());
        System.out.println("ByteValue: " + first.getByteValue());
        // etc.
    }

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
            row.setTimestamp(maybeNull(ts, 0.0, random));

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
            byte bv = (byte) (random.nextInt(256) - 128);
            row.setByteValue(maybeNull(bv, 0.1, random));

            // 5) Short integer (-32768..32767 range, 10% chance null)
            short sv = (short) (random.nextInt(65536) - 32768);
            row.setShortInt(maybeNull(sv, 0.1, random));

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
            row.setDecimalValue(maybeNull(decRounded, 0.1, random));

            // 14) Another timestamp column (again, random offset up to 1500, 10% null)
            long offsetDays2 = random.nextInt(1500);
            LocalDateTime ts2 = timeBase[i].minusDays(offsetDays2);
            row.setTimestampCol(maybeNull(ts2, 0.1, random));

            // 15) Date column (from the second timestamp, 10% null)
            LocalDate dt = ts2.toLocalDate();
            row.setDateCol(maybeNull(dt, 0.1, random));

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

    public static class DataRow {
        // 1) ID
        private Integer id;

        // 2) Timestamp
        private LocalDateTime timestamp;

        // 3) Boolean flag
        private Boolean booleanFlag;

        // 4) Byte value
        private Byte byteValue;

        // 5) Short integer
        private Short shortInt;

        // 6) Low categorical int
        private Integer lowCatInt;

        // 7) High categorical int
        private Integer highCatInt;

        // 8) Long column
        private Long longCol;

        // 9) Float zero std
        private Float floatZeroStd;

        // 10) Float low std
        private Float floatLowStd;

        // 11) Float high std
        private Float floatHighStd;

        // 12) Double value
        private Double doubleValue;

        // 13) Decimal value (rounded to 2 decimals)
        private Double decimalValue;

        // 14) Another timestamp column
        private LocalDateTime timestampCol;

        // 15) Date column
        private LocalDate dateCol;

        // 16) Low categorical string
        private String stringLowCat;

        // 17) High categorical string
        private String stringHighCat;

        // 18) Array column (3 random ints)
        private List<Integer> arrayColumn;

        // -------------------------
        // Getters / Setters
        // -------------------------
        public Integer getId() {
            return id;
        }
        public void setId(Integer id) {
            this.id = id;
        }

        public LocalDateTime getTimestamp() {
            return timestamp;
        }
        public void setTimestamp(LocalDateTime timestamp) {
            this.timestamp = timestamp;
        }

        public Boolean getBooleanFlag() {
            return booleanFlag;
        }
        public void setBooleanFlag(Boolean booleanFlag) {
            this.booleanFlag = booleanFlag;
        }

        public Byte getByteValue() {
            return byteValue;
        }
        public void setByteValue(Byte byteValue) {
            this.byteValue = byteValue;
        }

        public Short getShortInt() {
            return shortInt;
        }
        public void setShortInt(Short shortInt) {
            this.shortInt = shortInt;
        }

        public Integer getLowCatInt() {
            return lowCatInt;
        }
        public void setLowCatInt(Integer lowCatInt) {
            this.lowCatInt = lowCatInt;
        }

        public Integer getHighCatInt() {
            return highCatInt;
        }
        public void setHighCatInt(Integer highCatInt) {
            this.highCatInt = highCatInt;
        }

        public Long getLongCol() {
            return longCol;
        }
        public void setLongCol(Long longCol) {
            this.longCol = longCol;
        }

        public Float getFloatZeroStd() {
            return floatZeroStd;
        }
        public void setFloatZeroStd(Float floatZeroStd) {
            this.floatZeroStd = floatZeroStd;
        }

        public Float getFloatLowStd() {
            return floatLowStd;
        }
        public void setFloatLowStd(Float floatLowStd) {
            this.floatLowStd = floatLowStd;
        }

        public Float getFloatHighStd() {
            return floatHighStd;
        }
        public void setFloatHighStd(Float floatHighStd) {
            this.floatHighStd = floatHighStd;
        }

        public Double getDoubleValue() {
            return doubleValue;
        }
        public void setDoubleValue(Double doubleValue) {
            this.doubleValue = doubleValue;
        }

        public Double getDecimalValue() {
            return decimalValue;
        }
        public void setDecimalValue(Double decimalValue) {
            this.decimalValue = decimalValue;
        }

        public LocalDateTime getTimestampCol() {
            return timestampCol;
        }
        public void setTimestampCol(LocalDateTime timestampCol) {
            this.timestampCol = timestampCol;
        }

        public LocalDate getDateCol() {
            return dateCol;
        }
        public void setDateCol(LocalDate dateCol) {
            this.dateCol = dateCol;
        }

        public String getStringLowCat() {
            return stringLowCat;
        }
        public void setStringLowCat(String stringLowCat) {
            this.stringLowCat = stringLowCat;
        }

        public String getStringHighCat() {
            return stringHighCat;
        }
        public void setStringHighCat(String stringHighCat) {
            this.stringHighCat = stringHighCat;
        }

        public List<Integer> getArrayColumn() {
            return arrayColumn;
        }
        public void setArrayColumn(List<Integer> arrayColumn) {
            this.arrayColumn = arrayColumn;
        }
    }
}
