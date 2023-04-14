package com.hopsworks.tutorials.beam.clickstreampipe.schemas;


import com.google.auto.value.AutoValue;
import org.apache.beam.sdk.annotations.Experimental;
import org.apache.beam.sdk.schemas.AutoValueSchema;
import org.apache.beam.sdk.schemas.annotations.DefaultSchema;

@Experimental
public class Dimensions {
  
  @AutoValue
  @DefaultSchema(AutoValueSchema.class)
  public abstract static class StoreLocation {
    public abstract Integer getId();
    
    public abstract Integer getZip();
    
    public abstract String getCity();
    
    public abstract String getState();
    
    public abstract Double getLat();
    
    public abstract Double getLng();
    
    public abstract StoreLocation.Builder toBuilder();
    
    public static StoreLocation.Builder builder() {
      
      return new AutoValue_Dimensions_StoreLocation.Builder();
    }
    
    @AutoValue.Builder
    public abstract static class Builder {
      public abstract Builder setId(Integer value);
      
      public abstract Builder setZip(Integer value);
      
      public abstract Builder setCity(String value);
      
      public abstract Builder setState(String value);
      
      public abstract Builder setLat(Double value);
      
      public abstract Builder setLng(Double value);
      
      public abstract StoreLocation build();
    }
    
    //    @Override
    //    public boolean equals(Object obj) {
    //
    //      if (obj == null) return false;
    //      if (getClass() != obj.getClass()) return false;
    //      final StoreLocation other = (StoreLocation) obj;
    //      return Objects.equals(this.id, other.id)
    //          && Objects.equals(this.zip, other.zip)
    //          && Objects.equals(this.city, other.city)
    //          && Objects.equals(this.state, other.state)
    //          && Objects.equals(this.lat, other.lat)
    //          && Objects.equals(this.lng, other.lng);
    //    }
    //
    //    @Override
    //    public int hashCode() {
    //
    //      return Objects.hash(this.id, this.zip, this.city, this.state, this.lat, this.lng);
    //    }
  }
}
