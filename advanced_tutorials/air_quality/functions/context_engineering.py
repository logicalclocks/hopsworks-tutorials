import xml.etree.ElementTree as ET
import re
import inspect
from typing import get_type_hints
import json
import datetime
import torch
import sys
import pandas as pd
from openai import OpenAI
from functions.air_quality_data_retrieval import get_data_for_date, get_data_in_date_range, get_future_data
from typing import Any, Dict, List


def get_type_name(t: Any) -> str:
    """Get the name of the type."""
    name = str(t)
    if "list" in name or "dict" in name:
        return name
    else:
        return t.__name__


def serialize_function_to_json(func: Any) -> str:
    """Serialize a function to JSON."""
    signature = inspect.signature(func)
    type_hints = get_type_hints(func)

    function_info = {
        "name": func.__name__,
        "description": func.__doc__,
        "parameters": {
            "type": "object",
            "properties": {}
        },
        "returns": type_hints.get('return', 'void').__name__
    }

    for name, _ in signature.parameters.items():
        param_type = get_type_name(type_hints.get(name, type(None)))
        function_info["parameters"]["properties"][name] = {"type": param_type}

    return json.dumps(function_info, indent=2)


def get_function_calling_prompt(user_query):
    fn = """{"name": "function_name", "arguments": {"arg_1": "value_1", "arg_2": value_2, ...}}"""
    example = """{"name": "get_data_in_date_range", "arguments": {"date_start": "2024-01-10", "date_end": "2024-01-14", "city_name": "<city_name>"}}"""

    prompt = f"""<|im_start|>system
You are a helpful assistant with access to the following functions:

{serialize_function_to_json(get_data_for_date)}

{serialize_function_to_json(get_data_in_date_range)}

{serialize_function_to_json(get_future_data)}

###INSTRUCTIONS:
- You need to choose one function to use and retrieve paramenters for this function from the user input.
- If the user query contains 'will', it is very likely that you will need to use the get_future_data function.
- Do not include feature_view, model and encoder parameters.
- Provide dates STRICTLY in the YYYY-MM-DD format.
- Generate an 'No Function needed' string if the user query does not require function calling.

IMPORTANT: Today is {datetime.date.today().strftime("%A")}, {datetime.date.today()}.

To use one of there functions respond STRICTLY with:
<onefunctioncall>
    <functioncall> {fn} </functioncall>
</onefunctioncall>

###EXAMPLES

EXAMPLE 1:
- User: Hi!
- AI Assiatant: No Function needed.

EXAMPLE 2:
- User: Is this Air Quality level good or bad?
- AI Assiatant: No Function needed.

EXAMPLE 3:
- User: When and what was the minimum air quality from 2024-01-10 till 2024-01-14 in <city_name>?
- AI Assistant:
<onefunctioncall>
    <functioncall> {example} </functioncall>
</onefunctioncall>
<|im_end|>

<|im_start|>user
{user_query}
<|im_end|>

<|im_start|>assistant"""
    
    return prompt


def generate_hermes(user_query: str, model_llm, tokenizer) -> str:
    """Retrieves a function name and extracts function parameters based on the user query."""

    prompt = get_function_calling_prompt(user_query)
    
    tokens = tokenizer(prompt, return_tensors="pt").to(model_llm.device)
    input_size = tokens.input_ids.numel()
    with torch.inference_mode():
        generated_tokens = model_llm.generate(
            **tokens, 
            use_cache=True, 
            do_sample=True, 
            temperature=0.2, 
            top_p=1.0, 
            top_k=0, 
            max_new_tokens=512, 
            eos_token_id=tokenizer.eos_token_id, 
            pad_token_id=tokenizer.eos_token_id,
        )

    return tokenizer.decode(
        generated_tokens.squeeze()[input_size:], 
        skip_special_tokens=True,
    )


def function_calling_with_openai(user_query: str, client) -> str:
    """
    Generates a response using OpenAI's chat API.
    
    Args:
        user_query (str): The user's query or prompt.
        instructions (str): Instructions or context to provide to the GPT model.
        
    Returns:
        str: The generated response from the assistant.
    """
    
    instructions = get_function_calling_prompt(user_query).split('<|im_start|>user')[0]
    
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": instructions},
            {"role": "user", "content": user_query},
        ]
    )

    # Extract and return the assistant's reply from the response
    if completion and completion.choices:
        last_choice = completion.choices[0]
        if last_choice.message:
            return last_choice.message.content.strip()
    return ""    


def extract_function_calls(completion: str) -> List[Dict[str, Any]]:
    """Extract function calls from completion."""    
    completion = completion.strip()
    pattern = r"(<onefunctioncall>(.*?)</onefunctioncall>)"
    match = re.search(pattern, completion, re.DOTALL)
    if not match:
        return None
    
    multiplefn = match.group(1)
    root = ET.fromstring(multiplefn)
    functions = root.findall("functioncall")
        
    return [json.loads(fn.text) for fn in functions]


def invoke_function(function, feature_view, model, encoder) -> pd.DataFrame:
    """Invoke a function with given arguments."""
    # Extract function name and arguments from input_data
    function_name = function['name']
    arguments = function['arguments']

    # Using Python's getattr function to dynamically call the function by its name and passing the arguments
    function_output = getattr(sys.modules[__name__], function_name)(
        **arguments, 
        feature_view=feature_view, 
        model=model, 
        encoder=encoder,
    )
    
    if type(function_output) == str:
        return function_output
    
    # Round the 'pm2_5' value to 2 decimal places
    function_output['pm2_5'] = function_output['pm2_5'].apply(round, ndigits=2)
    return function_output


def get_context_data(user_query: str, feature_view, model_air_quality, encoder, model_llm=None, tokenizer=None, client=None) -> str:
    """
    Retrieve context data based on user query.

    Args:
        user_query (str): The user query.
        feature_view: Feature View for data retrieval.
        model_llm: The language model.
        tokenizer: The tokenizer.
        model_air_quality: The air quality model.
        encoder: The encoder.

    Returns:
        str: The context data.
    """
    
    if client:
        # Generate a response using LLM
        completion = function_calling_with_openai(user_query, client) 
     
    else:
        # Generate a response using LLM
        completion = generate_hermes(
            user_query, 
            model_llm, 
            tokenizer,
        )
        
    # Extract function calls from the completion
    functions = extract_function_calls(completion)

    # If function calls were found
    if functions:
        # Invoke the function with provided arguments
        data = invoke_function(functions[0], feature_view, model_air_quality, encoder)
        # Return formatted data as string
        if isinstance(data, pd.DataFrame):
            return f'Air Quality Measurements for {functions[0]["arguments"]["city_name"]}:\n' + '\n'.join(
                [f'Date: {row["date"]}; Air Quality: {row["pm2_5"]}' for _, row in data.iterrows()]
            ) 
        # Return message if data is not updated
        return data
    
    # If no function calls were found, return an empty string
    return ''
