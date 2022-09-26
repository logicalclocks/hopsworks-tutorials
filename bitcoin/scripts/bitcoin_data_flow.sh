set -e

echo "$PWD"

echo "Bitcoin ingestion pipeline starts"
jupyter nbconvert --to notebook --execute 2_feature_pipeline.ipynb