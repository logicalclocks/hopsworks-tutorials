package com.hopsworks.tutorials;

import com.logicalclocks.hsfs.FeatureStore;
import com.logicalclocks.hsfs.FeatureView;
import com.logicalclocks.hsfs.HopsworksConnection;
import com.logicalclocks.hsfs.SecretStore;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

public class FeatureVectors {
  
  public static void main(String[] args) throws Exception {
  
    String host = args[0];
    String projectName = args[1];
    String apiKey = args[2];
    String fvName = args[3];
    Integer fvVersion = Integer.parseInt(args[4]);
  
    FeatureStore fs = HopsworksConnection.builder()
      .host(host)
      .project(projectName)
      .apiKeyValue(apiKey)
      .hostnameVerification(false)
      .build()
      .getFeatureStore();
    
    // get feature view
    FeatureView fv = fs.getFeatureView(fvName, fvVersion);
  
    // single lookup sering vector
    List<Object> singleVector = fv.getFeatureVector(new HashMap<String, Object>() {{
      put("product_id", productIdGenerator());
    }});
    System.out.println("Feature values from single vector lookup");
    System.out.println("[" + Joiner.on(", ").join(singleVector) + "]");
  
    // batch lookup sering vector
    fv.initServing(true, true);
    List<List<Object>> batchVector = fv.getFeatureVectors(productIdGenerator(160));
    
    // print results
    System.out.println("Feature values from batch lookup");
    for (List<Object> vector: batchVector) {
      System.out.println("[" + Joiner.on(", ").join(vector) + "]");
    }
  }
  
  private static int productIdGenerator() {
    int leftLimit = 0;
    int rightLimit = 1000;
    return leftLimit + (int) (Math.random() * (rightLimit - leftLimit));
  }
  
  private static java.util.Map<java.lang.String,java.util.List<java.lang.Object>> productIdGenerator(int batch) {
    List<Object> productIds = new ArrayList<>();
    while (productIds.size() <= batch){
      int productId = productIdGenerator();
      if (!productIds.contains(productId)) {
        productIds.add(productId);
      }
    }
    return new HashMap<String, List<Object>>() {{put("product_id", productIds);}};
  }
}
