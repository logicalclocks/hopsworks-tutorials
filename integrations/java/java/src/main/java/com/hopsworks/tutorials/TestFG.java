package com.hopsworks.tutorials;

import lombok.Getter;

import java.sql.Timestamp;
import java.util.List;

@Getter
public class TestFG {
    // Getter and Setter for pk
    private String pk;
    // Getter and Setter for eventTime
    private Timestamp eventTime;
    // Getter and Setter for feat
    private List<Feat> feat;

    // Default constructor
    public TestFG() {}

    // Parameterized constructor
    public TestFG(String pk, Timestamp eventTime, List<Feat> feat) {
        this.pk = pk;
        this.eventTime = eventTime;
        this.feat = feat;
    }

    public void setPk(String pk) {
        this.pk = pk;
    }

    public void setEventTime(Timestamp eventTime) {
        this.eventTime = eventTime;
    }

    public void setFeat(List<Feat> feat) {
        this.feat = feat;
    }

    @Override
    public String toString() {
        return "testFG{" +
                "pk='" + pk + '\'' +
                ", eventTime=" + eventTime +
                ", feat=" + feat +
                '}';
    }
}

// The Feat class representing each element in the feat array.
class Feat {
    private String sku;
    private Timestamp ts;

    // Default constructor
    public Feat() {}

    // Parameterized constructor
    public Feat(String sku, Timestamp ts) {
        this.sku = sku;
        this.ts = ts;
    }

    // Getter and Setter for sku
    public String getSku() {
        return sku;
    }

    public void setSku(String sku) {
        this.sku = sku;
    }

    // Getter and Setter for ts
    public Timestamp getTs() {
        return ts;
    }

    public void setTs(Timestamp ts) {
        this.ts = ts;
    }

    @Override
    public String toString() {
        return "Feat{" +
                "sku='" + sku + '\'' +
                ", ts=" + ts +
                '}';
    }
}
