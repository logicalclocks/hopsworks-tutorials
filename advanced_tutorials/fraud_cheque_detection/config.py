### Dataset Configuration
DATASET_NAME = "shivi/cheques_sample_data"

### Donut Configuration
DONUT_BASE_REPO = "naver-clova-ix/donut-base" #"nielsr/donut-base"
DONUT_FT_REPO = "shivi/donut-cheque-parser"
IMAGE_SIZE = [960, 720]  # Input image size
MAX_LENGTH = 768         # Max generated sequence length for text decoder of Donut

### Task Tokens
TASK_START_TOKEN = "<parse-cheque>"
TASK_END_TOKEN = "<parse-cheque>"

### Training Configuration
BATCH_SIZE = 1
NUM_WORKERS = 4
MAX_EPOCHS = 30
VAL_CHECK_INTERVAL = 0.2
CHECK_VAL_EVERY_N_EPOCH = 1
GRADIENT_CLIP_VAL = 1.0
LEARNING_RATE = 3e-5
VERBOSE = True

### Hardware Configuration
ACCELERATOR = "gpu"
DEVICE_NUM = 1
PRECISION = 16
