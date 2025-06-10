import os
from typing import Iterable, Dict, Any, cast, Optional

import torch

from vllm import __version__, AsyncEngineArgs, AsyncLLMEngine
from vllm.transformers_utils.tokenizers import maybe_serialize_tool_calls

from kserve.protocol.rest.openai import (
    ChatPrompt,
    ChatCompletionRequestMessage,
)
from kserve.protocol.rest.openai.types.openapi import ChatCompletionTool

from mistral_common.protocol.instruct.request import ChatCompletionRequest


class Predictor:

    def __init__(self):
        print("Using vLLM version: " + str(__version__))
        
        # Load the configuration for the vLLM engine from the configuration file, if any
        if "CONFIG_FILE_PATH" in os.environ and os.path.exists(os.environ["CONFIG_FILE_PATH"]):
            print("Reading engine config from file...")
            
            import yaml
            with open(os.environ["CONFIG_FILE_PATH"], 'r') as f:
                config = yaml.load(f, Loader=yaml.SafeLoader)
                self._drop_unsupported_engine_args(config)
                self._disable_log_stats(config)
        else:
            print("Configuration file not found, defaulting to hard-coded engine config...")
            config = {
                "tokenizer_mode": "mistral",
                # reduce resources need
                "dtype": "half",
                "max_model_len": 20720,
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
    
    def apply_chat_template(
        self,
        messages: Iterable[ChatCompletionRequestMessage],
        chat_template: Optional[str] = None,
        tools: Optional[list[ChatCompletionTool]] = None,
    ) -> ChatPrompt:
        """Converts a prompt or list of messages into a single templated prompt string"""
        
        tool_dicts=[tool.model_dump() for tool in tools] if tools else None
        parsed_messages = self._parse_messages(messages)
        request = ChatCompletionRequest(messages=parsed_messages,
                                        tools=tool_dicts)

        encoded = self.tokenizer.encode_chat_completion(request)
        
        return ChatPrompt(prompt=encoded.text)
    
    def _parse_messages(self, messages):
        # The Mistral tokenizer expects a slightly different format of messages.
        # https://github.com/mistralai/mistral-common/blob/21ee9f6cee3441e9bb1e6ed2d10173f90bd9b94b/src/mistral_common/protocol/instruct/request.py#L21
        # e.g., we need to remove the 'name' field from the messages.
        parsed_messages = []
        for msg in messages:
            parsed_msg = vars(msg)
            del parsed_msg["name"]  # name field is not accepted by mistral tokenizer
            if "function_call" in parsed_msg:
                del parsed_msg["function_call"]  # function_call field is not accepted by mistral tokenizer
            if "tool_calls" in parsed_msg and parsed_msg["tool_calls"] is None:
                del parsed_msg["tool_calls"]  # vllm mistral tokenizer wrapper doesn't allow None tool_calls
            parsed_messages.append(parsed_msg)
        
        last_message = cast(Dict[str, Any], parsed_messages[-1])
        if last_message["role"] == "assistant":
            last_message["prefix"] = True
            
        # NOTE from vllm:
        # because of issues with pydantic we need to potentially
        # re-serialize the tool_calls field of the request
        # for more info: see comment in `maybe_serialize_tool_calls`
        class MessagesWrapper:
            def __init__(self, messages):
                self.messages = messages
        messages_wrapper = MessagesWrapper(parsed_messages)
        maybe_serialize_tool_calls(messages_wrapper)
        parsed_messages = messages_wrapper.messages
        
        return parsed_messages
    
    def _drop_unsupported_engine_args(self, config):
        # The following arguments are supported by the vllm-openai server, not the vllm engine itself.
        if "enable_auto_tool_choice" in config:
            del config["enable_auto_tool_choice"]
        if "tool_call_parser" in config:
            del config["tool_call_parser"]
        if "chat_template" in config:
            del config["chat_template"]
            
    def _disable_log_stats(self, config):
        config["disable_log_stats"] = True
        config["disable_log_requests"] = True