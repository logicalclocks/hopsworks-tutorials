# Clickstream Analytics

Two approaches to computing windowed aggregations on clickstream data.

## Examples

### Pre-computed (Stream Processing)
`examples/click_counts/precomputed/` - Feldera computes click counts in real-time
- Windows: 1, 10, 30, 60 minutes
- Storage: Pre-aggregated results
- Latency: ~5ms serving

### On-demand (Batch + Query)
`examples/click_counts/on_demand/` - Spark computes windows, query at serving time
- Windows: Same as above
- Storage: All raw events
- Latency: ~50ms serving

## Setup

1. Generate synthetic data: `examples/click_counts/1_synthetic_data.ipynb`
2. Choose your pattern:
   - Pre-computed: `examples/click_counts/precomputed/`
   - On-demand: `examples/click_counts/on_demand/`

## Trade-offs

**Pre-computed**: Low latency (5ms), higher storage, fixed aggregations
**On-demand**: Flexible queries, higher latency (50ms), efficient storage

## CTR Example

`examples/ctr_calculation/` - Click-through rate calculation with Feldera/Flink