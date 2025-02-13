import os
import torch
from vllm import __version__, AsyncEngineArgs, AsyncLLMEngine


class Predictor:

    def __init__(self):
        print("Using vLLM version: " + str(__version__))
        
        # Load the configuration for the vLLM engine from the configuration file, if any
        if "CONFIG_FILE_PATH" in os.environ and os.path.exists(os.environ["CONFIG_FILE_PATH"]):
            print("Reading engine config from file...")
            
            import yaml
            with open(os.environ["CONFIG_FILE_PATH"], 'r') as f:
                config = yaml.load(f, Loader=yaml.SafeLoader)
                self._disable_log_stats(config)
        else:
            print("Configuration file not found, defaulting to hard-coded engine config...")
            config = {
                # reduce resources need
                "dtype": "half",
                "max_model_len": 2048,
                "gpu_memory_utilization": 0.96,
                # disable logging stats and requests
                "disable_log_stats": True,
                "disable_log_requests": True,
            }

        print("Starting vLLM backend...")
        engine_args = AsyncEngineArgs(
            model=os.environ["MODEL_FILES_PATH"],
            **config
        )
        if torch.cuda.is_available():
            # adjust tensor parallel size
            engine_args.tensor_parallel_size = torch.cuda.device_count()

        # "self.vllm_engine" is required as the local variable with the vllm engine handler
        self.vllm_engine = AsyncLLMEngine.from_engine_args(engine_args)
        
    def _disable_log_stats(self, config):
        config["disable_log_stats"] = True
        config["disable_log_requests"] = True