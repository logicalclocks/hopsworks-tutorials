package com.hopsworks.tutorials.beam.clickstreampipe.services;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.hopsworks.tutorials.beam.clickstreampipe.schemas.Item;
import org.apache.beam.sdk.annotations.Experimental;
import org.apache.beam.sdk.schemas.Schema;

/**
 * This class represents a mock client to a microservice implemented by the Demo Retail company.
 *
 * <p>The class emulates communication between the Dataflow pipeline, and a hypothetical internal
 * microservice.
 *
 * <p>Real services will often take 10-100's of ms to respond, which cause back pressure within a
 * pipeline. This version of this mock does not cause push back.
 *
 * <p>TODO convert to a service which requires a few hundred ms to respond.
 */
@Experimental
public class RetailCompanyServices {
  
  public Map<String, Item> convertItemIdsToFullText(List<String> itemIds, Schema itemSchema) {
    
    Map<String, Item> map = new HashMap<>();
    
    Item item =
      Item.builder()
        .setItemBrand("item_brand")
        .setItemCat01("foo_category")
        .setItemName("foo_name")
        .build();
    
    itemIds.forEach(x -> map.put(x, item));
    return map;
  }
}
