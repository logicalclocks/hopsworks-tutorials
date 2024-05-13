import os
import getpass
from transformers import AutoTokenizer, AutoModelForCausalLM
import transformers
import torch
from langchain.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain

from functions.utils import (
    load_image,
)
from functions.donut import (
    parse_text,
    evaluate_cheque_fraud,
)


def load_llm(model_id: str = "meta-llama/Meta-Llama-3-8B-Instruct") -> tuple:
    """
    Load the LLM and its corresponding tokenizer.

    Args:
        model_id (str, optional): Identifier for the pre-trained model. Defaults to "meta-llama/Meta-Llama-3-8B-Instruct".

    Returns:
        tuple: A tuple containing the loaded model and tokenizer.
    """
    
    # Setup the HuggingFace API Key
    os.environ["HF_API_KEY"] = os.getenv("HF_API_KEY") or getpass.getpass('🔑 Enter your HuggingFace API key: ')

    # Load the Meta-Llama-3-8B-Instruct tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        model_id,
        token=os.environ["HF_API_KEY"],
    )

    # Load the Meta-Llama-3-8B-Instruct model
    model_llm = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="auto",
        token=os.environ["HF_API_KEY"],
    )

    # Print device
    print(f'⛳️ Device: {model_llm.device}')
    return tokenizer, model_llm


def get_prompt_template():
    prompt = """
    <|begin_of_text|>
    <|start_header_id|>system<|end_header_id|>
    You are a professional cheque fraud detection assistant.
    Provide a rich description on why the cheque is fraud or valid.

    ###CONTEXT
    {context}

    ###INSTRUCTIONS
    - Do not say that you are not a professional cheque fraud detection assistant.
    - You are to provide clear, concise, and direct responses.
    - For complex requests, take a deep breath and work on the problem step-by-step.
    - For every response, you will be tipped up to $1000 (depending on the quality of your output).
    - Maintain a casual tone in your communication.
    - Start with the cheque verdict (Fraud, Valid) and then justify your decision.
    - If the "Amount in words" is missing, skip the spelling validation part.
    - Use the provided example as a template.
    - Make sure that you do NOT use enumeration or bullet points in your response.
    - Be sure in your answer.
    
    ###EXAMPLE 1
    - User: Is this cheque fraud or valid?
    - AI Assistant: Valid | The cheque is considered valid because the amount in words <AMOUNT IN WORDS> matches the amount in numbers <AMOUNT IN NUMBERS> and the spelling is correct.
    
    ###EXAMPLE 2
    - User: Is this cheque fraud or valid?
    - AI Assistant: Fraud | The cheque is fraudulent due to a mismatch between the numeric and alphabetic values. <EXPLAIN WHY MISMATCH HERE>.
            
    ###EXAMPLE 3
    - User: Is this cheque fraud or valid?
    - AI Assistant: Fraud | The cheque is considered fraudulent because the amount in words is missing, which is a crucial detail that should be included in a valid cheque.
    <|eot_id|>
    <|start_header_id|>user<|end_header_id|>
    Is this cheque fraud or valid?
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>
    """
    return prompt


def get_llm_chain(model_id: str = "meta-llama/Meta-Llama-3-8B-Instruct"):
    """
    Initializes and returns a language model chain for text generation using Hugging Face's transformers library.

    Parameters:
    - model_id (str): The identifier for the pre-trained language model and tokenizer to load from Hugging Face.

    Returns:
    - LLMChain: A configured chain consisting of a Hugging Face pipeline for text generation and prompt handling.
    """
    # Load LLM and its corresponding tokenizer
    tokenizer, model = load_llm(model_id)
    
    # Define special tokens that signal the end of a sequence
    terminators = [
        tokenizer.eos_token_id,                        # End of string token
        tokenizer.convert_tokens_to_ids("<|eot_id|>")  # Converts an empty string to a token ID if needed
    ]
    
    # Create a text generation pipeline using the loaded model and tokenizer
    text_generation_pipeline = transformers.pipeline(
        "text-generation",                   # Specify the task as text generation
        model=model,                         # The pre-trained language model for text generation
        tokenizer=tokenizer,                 # The tokenizer corresponding to the language model
        use_cache=True,                      # Enable caching to speed up processing
        do_sample=True,                      # Enable sampling to generate diverse text
        temperature=0.7,                     # Control the randomness of the output
        top_p=0.9,                           # Use nucleus sampling with this threshold
        top_k=0,                             # Disable top-k sampling
        max_new_tokens=500,                  # Limit the maximum number of new tokens generated
        eos_token_id=terminators,            # List of tokens to consider as end-of-sequence
    )

    # Create a Hugging Face pipeline for Mistral LLM using the text generation pipeline
    pipeline_llm = HuggingFacePipeline(
        pipeline=text_generation_pipeline,
    )

    # Create prompt from a predefined template 
    prompt = PromptTemplate(
        input_variables=["context"],         # Variables to be replaced in the template
        template=get_prompt_template(),      # Fetch the prompt template
    )

    # Create the LLM chain
    llm_chain = prompt | pipeline_llm

    return llm_chain


def format_context(parsed_text, evaluation):
    """
    Formats the parsed text and evaluation details into a structured context string.

    This function takes parsed cheque details and the results of a fraud evaluation, combining them into a 
    single formatted string that provides a clear, readable summary of the cheque's details and the evaluation 
    outcome.

    Parameters:
    - parsed_text (dict): A dictionary containing parsed text details, specifically amounts in words and figures.
    - evaluation (tuple): A tuple containing the fraud evaluation result and relevant messages.

    Returns:
    - str: A formatted string containing detailed context information.
    """
    # Format the context into a multiline string with clear labels and values
    context_formatted = f"""
Amount in words: {parsed_text['amt_in_words']}
Amount in numbers: {parsed_text['amt_in_figures']}
{evaluation[1]}
{evaluation[2]}
Verdict: {evaluation[0]}
"""
    return context_formatted


def generate_response(
    image_path, 
    processor, 
    model_parser, 
    model_fraud_detection, 
    llm_chain, 
    verbose: bool = False, 
    folder_name='data/images/'
):
    """
    Processes an image to extract text, evaluates it for fraud, and generates a response using a language model chain.

    This function performs a series of operations including loading an image, parsing text from it, detecting
    potential fraud in the text, formatting the context for further processing, and finally invoking a language
    model chain to generate a response based on the context.

    Parameters:
    - image_path (str): Path to the image file.
    - processor: Preconfigured processor for handling image data.
    - model_parser: Model used to parse text from the image.
    - model_fraud_detection: Model used to detect fraud in the parsed text.
    - llm_chain: Configured language model chain for generating text responses.
    - verbose (bool, optional): If True, prints formatted context. Defaults to False.
    - folder_name (str, optional): Folder path where the image is stored. Defaults to 'data/images/'.

    Returns:
    - str: The text response generated by the language model.
    """
    # Load image from the specified folder and path
    image = load_image(
        image_path,
        folder_name,
    )
    
    # Parse text from the loaded image using the specified models
    parsed_text = parse_text(
        image, 
        processor, 
        model_parser,
    )
    
    # Evaluate the parsed text for potential fraud
    evaluation = evaluate_cheque_fraud(
        parsed_text, 
        model_fraud_detection,
    )

    # Format the context from parsed text and its evaluation for the language model
    context_formatted = format_context(
        parsed_text, 
        evaluation,
    )
    if verbose:
        print(f'📖 Context:\n{context_formatted.strip()}\n----------\n')
    
    # Invoke the language model chain with the formatted context and retrieve the output
    model_output = llm_chain.invoke({
        "context": context_formatted, 
    })

    # Process the model output to extract the relevant response part
    return model_output.split(
       '<|start_header_id|>assistant<|end_header_id|>'
    )[-1].strip()
 
    
def format_response(response):
    """
    Splits a response string into a verdict and a description, both trimmed of excess whitespace.

    Parameters:
    - response (str): The response string containing a verdict and description separated by '|'.

    Returns:
    - tuple: A tuple containing the verdict and description as separate strings.
    """
    # Split the response into verdict and description at the first occurrence of '|'
    verdict, description = response.split('|')
    
    # Return both components stripped of any leading/trailing whitespace
    return verdict.strip(), description.strip()
