import os
import getpass
import torch
import transformers
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer
from langchain.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory


def load_llm(model_dir) -> tuple:
    """
    Load the LLM and its corresponding tokenizer.

    Args:
        model_dir (str): Path to the pre-trained fine-tuned model.

    Returns:
        tuple: A tuple containing the tokenizer and loaded model.
    """
    # Setup the HuggingFace API Key
    os.environ["HF_API_KEY"] = os.getenv("HF_API_KEY") or getpass.getpass('🔑 Enter your HuggingFace API key: ')

    # Load a model from the saved model directory
    model_llm = AutoPeftModelForCausalLM.from_pretrained(
        model_dir,
        device_map="auto",
        torch_dtype=torch.float16,
        token=os.environ["HF_API_KEY"],
    )

    # Load the tokenizer from the saved model directory
    tokenizer = AutoTokenizer.from_pretrained(
        model_dir,
        token=os.environ["HF_API_KEY"],
    )

    # Set the pad token to the end-of-sequence token
    tokenizer.pad_token = tokenizer.eos_token

    # Set the padding side to "right" to remove warnings
    tokenizer.padding_side = "right"

    # Print device
    print(f'⛳️ Device: {model_llm.device}')
    return tokenizer, model_llm


def get_prompt_template():
    # Define a template for generating prompts
    prompt_template = """
    [INST] 
    Instruction: Prioritize brevity and clarity in responses. 
    Avoid unnecessary repetition and keep answers concise, adhering to a maximum of 750 characters. 
    Eliminate redundant phrases and sentences. 
    If details are repeated, provide them only once for better readability. 
    Focus on delivering key information without unnecessary repetition. 
    If a concept is already conveyed, there's no need to restate it. Ensure responses remain clear and to the point.
    Make sure you do not repeat any sentences in your answer.
    [/INST]

    Previous conversation:
    {chat_history}

    ### CONTEXT:

    {context}

    ### QUESTION:
    [INST]{question}[/INST]"""
    return prompt_template


def get_llm_chain(model_dir):
    """
    Initializes and returns a language model chain for text generation using Hugging Face's transformers library.

    Parameters:
    - model_dir (str): Path to the pre-trained fine-tuned model.

    Returns:
    - LLMChain: A configured chain consisting of a Hugging Face pipeline for text generation and prompt handling.
    """
    
    def get_global_history(session_id: str) -> BaseChatMessageHistory:
        return global_chat_history
    
    # Load LLM and its corresponding tokenizer
    tokenizer, model = load_llm(model_dir)
    
    # Create a text generation pipeline using the loaded model and tokenizer
    text_generation_pipeline = transformers.pipeline(
        model=model,                          # The pre-trained language model for text generation
        tokenizer=tokenizer,                  # The tokenizer corresponding to the language model
        task="text-generation",               # Specify the task as text generation
        temperature=0.2,                      # Controls the randomness of the generation (higher values for more randomness)
        repetition_penalty=1.5,               # Controls the penalty for repeating tokens in generated text
        return_full_text=True,                # Return the full generated text instead of just the generated tokens
        max_new_tokens=750,                   # Limit the maximum number of newly generated tokens
        pad_token_id=tokenizer.eos_token_id,  # Use the end-of-sequence token as the padding token
        do_sample=True,                       # Enable sampling during text generation
    )

    # Create a Hugging Face pipeline for Mistral LLM using the text generation pipeline
    mistral_llm = HuggingFacePipeline(
        pipeline=text_generation_pipeline,
    )

    # Create prompt from prompt template 
    prompt = PromptTemplate(
        input_variables=["context", "question", "chat_history"],
        template=get_prompt_template(),
    )

    # Create the runnable sequence
    runnable = prompt | mistral_llm | StrOutputParser()

    # Initialize a global chat history (shared for all invocations)
    global_chat_history = ChatMessageHistory()

    # Create the RunnableWithMessageHistory using the global history
    llm_chain = RunnableWithMessageHistory(
        runnable,
        get_global_history,
        input_messages_key="question",
        history_messages_key="chat_history",
    )

    return llm_chain
