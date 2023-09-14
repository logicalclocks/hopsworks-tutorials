# Set your project and desired zone
PROJECT_ID="{YOUR_PROJECT_ID}"
ZONE="{YOUR_ZONE}"

# Define the instance name and machine type
INSTANCE_NAME="airflow-instance"
MACHINE_TYPE="e2-small"

# Define the boot disk image
IMAGE_FAMILY="debian-11"
IMAGE_PROJECT="debian-cloud"

# Create the instance with the startup script
gcloud compute instances create $INSTANCE_NAME \
    --project=$PROJECT_ID \
    --zone=$ZONE \
    --machine-type=$MACHINE_TYPE \
    --image-family=$IMAGE_FAMILY \
    --image-project=$IMAGE_PROJECT \
    --metadata=startup-script=startup-script.sh
