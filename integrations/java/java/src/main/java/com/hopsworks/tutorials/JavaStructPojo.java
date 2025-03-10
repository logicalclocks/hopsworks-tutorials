package com.hopsworks.tutorials;

import org.apache.avro.reflect.Nullable;
import org.apache.avro.reflect.AvroSchema;
import java.util.List;

public class JavaStructPojo {

    @Nullable
    // This field is a union of null and string.
    private String pk;

    @Nullable
    // Avro will treat this as a long with the logical type "timestamp-micros".
    @AvroSchema("{\"type\":\"long\",\"logicalType\":\"timestamp-micros\"}")
    private Long event_time;

    @Nullable
    // This is a union of null and an array of unions (null or S_feat).
    private List<S_feat> feat;

    // Default constructor
    public JavaStructPojo() {}

    // Parameterized constructor
    public JavaStructPojo(String pk, Long event_time, List<S_feat> feat) {
        this.pk = pk;
        this.event_time = event_time;
        this.feat = feat;
    }

    public String getPk() {
        return pk;
    }

    public void setPk(String pk) {
        this.pk = pk;
    }

    public Long getEvent_time() {
        return event_time;
    }

    public void setEvent_time(Long event_time) {
        this.event_time = event_time;
    }

    public List<S_feat> getFeat() {
        return feat;
    }

    public void setFeat(List<S_feat> feat) {
        this.feat = feat;
    }

    @Override
    public String toString() {
        return "JavaStructPojo{" +
                "pk='" + pk + '\'' +
                ", event_time=" + event_time +
                ", feat=" + feat +
                '}';
    }

    // Nested static class corresponding to the S_feat record.
    public static class S_feat {
        @Nullable
        // Union of null and string.
        private String sku;

        @Nullable
        // Avro will treat this as a long with the logical type "timestamp-micros".
        @AvroSchema("{\"type\":\"long\",\"logicalType\":\"timestamp-micros\"}")
        private Long ts;

        // Default constructor
        public S_feat() {}

        // Parameterized constructor
        public S_feat(String sku, Long ts) {
            this.sku = sku;
            this.ts = ts;
        }

        public String getSku() {
            return sku;
        }

        public void setSku(String sku) {
            this.sku = sku;
        }

        public Long getTs() {
            return ts;
        }

        public void setTs(Long ts) {
            this.ts = ts;
        }

        @Override
        public String toString() {
            return "S_feat{" +
                    "sku='" + sku + '\'' +
                    ", ts=" + ts +
                    '}';
        }
    }
}
