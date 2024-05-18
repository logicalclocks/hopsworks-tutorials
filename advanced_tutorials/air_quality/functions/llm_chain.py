import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from langchain.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema.output_parser import StrOutputParser
import torch
import datetime
from typing import Any, Dict, Union
from functions.context_engineering import get_context_data


def load_model(model_id: str = "teknium/OpenHermes-2.5-Mistral-7B") -> tuple:
    """
    Load the LLM and its corresponding tokenizer.

    Args:
        model_id (str, optional): Identifier for the pre-trained model. Defaults to "teknium/OpenHermes-2.5-Mistral-7B".

    Returns:
        tuple: A tuple containing the loaded model and tokenizer.
    """
    
    # Load the tokenizer for Mistral-7B-Instruct model
    tokenizer = AutoTokenizer.from_pretrained(
        model_id,
    )

    # Set the pad token to the unknown token to handle padding
    tokenizer.pad_token = tokenizer.unk_token

    # Set the padding side to "right" to prevent warnings during tokenization
    tokenizer.padding_side = "right"

    # BitsAndBytesConfig int-4 config
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True, 
        bnb_4bit_use_double_quant=True, 
        bnb_4bit_quant_type="nf4", 
        bnb_4bit_compute_dtype=torch.bfloat16,
    )

    # Load the Mistral-7B-Instruct model with quantization configuration
    model_llm = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="auto",
        quantization_config=bnb_config,
    )

    # Configure the pad token ID in the model to match the tokenizer's pad token ID
    model_llm.config.pad_token_id = tokenizer.pad_token_id

    return model_llm, tokenizer


def get_prompt_template():
    """
    Retrieve a template for generating prompts in a conversational AI system.

    Returns:
        str: A string representing the template for generating prompts. 
            This template includes placeholders for system information, 
            instructions, previous conversation, context, date and user query.
    """
    prompt_template = """<|im_start|>system
    You are one of the best air quality experts in the world. 

    ###INSTRUCTIONS:
    - If you don't know the answer, you will respond politely that you cannot help.
    - Use the context table with air quality indicators for city provided by user to generate your answer.
    - You answer should be at least one sentence.
    - Do not show any calculations to the user.
    - Make sure that you use correct air quality indicators for the corresponding date.
    - Add a rich analysis of the air quality level, such as whether it is safe, whether to go for a walk, etc.
    - Do not mention in your answer that you are using context table.
    <|im_end|>

    ### CONTEXT:
    {context}

    IMPORTANT: Today is {date_today}.

    <|im_start|>user
    {question}<|im_end|>
    <|im_start|>assistant"""
    return prompt_template


def get_llm_chain(tokenizer, model_llm):
    """
    Create and configure a language model chain.

    Args:
        tokenizer: The tokenizer corresponding to the language model.
        model_llm: The pre-trained language model for text generation.

    Returns:
        LLMChain: The configured language model chain.
    """
    # Create a text generation pipeline using the loaded model and tokenizer
    text_generation_pipeline = transformers.pipeline(
        model=model_llm,                      # The pre-trained language model for text generation
        tokenizer=tokenizer,                  # The tokenizer corresponding to the language model
        task="text-generation",               # Specify the task as text generation
        use_cache=True, 
        do_sample=True, 
        temperature=0.4, 
        top_p=1.0,
        top_k=0,
        max_new_tokens=512, 
        eos_token_id=tokenizer.eos_token_id, 
        pad_token_id=tokenizer.eos_token_id,   
    )

    # Create a Hugging Face pipeline for Mistral LLM using the text generation pipeline
    mistral_llm = HuggingFacePipeline(
        pipeline=text_generation_pipeline,
    )

    # Create prompt from prompt template 
    prompt = PromptTemplate(
        input_variables=["context", "question", "date_today"],
        template=get_prompt_template(),
    )

    # Create LLM chain 
    llm_chain = prompt | mistral_llm | StrOutputParser()

    return llm_chain


def generate_response(
    user_query: str, 
    feature_view, 
    model_air_quality, 
    encoder, 
    model_llm, 
    tokenizer, 
    llm_chain=None,
    verbose: bool = False,
) -> str:
    """
    Generate response to user query using LLM chain and context data.
    
    Args:
        user_query (str): The user's query.
        feature_view: Feature view for data retrieval.
        model_llm: Language model for text generation.
        tokenizer: Tokenizer for processing text.
        model_air_quality: Model for predicting air quality.
        encoder: Label Encoder for the city_name column.
        llm_chain: LLM Chain.
        verbose (bool): Whether to print verbose information. Defaults to False.
        
    Returns:
        str: Generated response to the user query.
    """
    # Get context data based on user query
    context = get_context_data(
        user_query,
        feature_view,
        model_air_quality, 
        encoder,
        model_llm=model_llm, 
        tokenizer=tokenizer, 
    )
        
    # Get today's date in a readable format
    date_today = f'{datetime.date.today().strftime("%A")}, {datetime.date.today()}'
    
    # Print today's date and context information if verbose mode is enabled
    if verbose:
        print(f"🗓️ Today's date: {date_today}")
        print(f'📖 {context}')
        print('===' * 5)
        
    # Invoke the language model chain with relevant context
    model_output = llm_chain.invoke({
        "context": context, 
        "date_today": date_today,
        "question": user_query,
    })

    # Return the generated text from the model output
    return model_output.split('<|im_start|>assistant')[-1].strip()


def generate_response_openai(
    user_query: str, 
    feature_view, 
    model_air_quality, 
    encoder, 
    client,
    verbose=True,
):
    
    context = get_context_data(
        user_query,
        feature_view,
        model_air_quality,
        encoder,
        client=client,
    )
    
    # Get today's date in a readable format
    date_today = f'{datetime.date.today().strftime("%A")}, {datetime.date.today()}'
    
    # Print today's date and context information if verbose mode is enabled
    if verbose:
        print(f"🗓️ Today's date: {date_today}")
        print(f'📖 {context}')
        print('===' * 5)
    
    instructions = get_prompt_template().split('<|im_start|>user')[0]
    
    instructions_filled = instructions.format(
        context=context,
        date_today=date_today
    )

    completion = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[
            {"role": "system", "content": instructions_filled},
            {"role": "user", "content": user_query},
        ]
    )

    # Extract and return the assistant's reply from the response
    if completion and completion.choices:
        last_choice = completion.choices[0]
        if last_choice.message:
            return last_choice.message.content.strip()
    return "" 
    