import torch
import re
import numpy as np
from transformers import (
    DonutProcessor, 
    VisionEncoderDecoderModel,
)
from features.cheque import (
    spell_check,
    amount_letter_number_match,
)

# Determine the device to use based on the availability of CUDA (GPU)
device = "cuda" if torch.cuda.is_available() else "cpu"

def load_cheque_parser(folder_name):
    """
    Loads a cheque parsing processor and model from a specified directory and moves the model to the appropriate device.

    This function loads a DonutProcessor and a VisionEncoderDecoderModel. The model is moved to a GPU if available, otherwise to CPU.

    Parameters:
    - folder_name (str): The directory where the processor and model's pretrained weights are stored.

    Returns:
    - tuple: A tuple containing the loaded processor and model.
    """
    # Load the DonutProcessor from the pretrained model directory
    processor = DonutProcessor.from_pretrained(folder_name)
    
    # Load the VisionEncoderDecoderModel from the pretrained model directory
    model = VisionEncoderDecoderModel.from_pretrained(folder_name)
    
    # Move the model to the available device (GPU or CPU)
    model.to(device)
    
    # Return the processor and model as a tuple
    return processor, model


def parse_text(image, processor, model):
    """
    Parses text from an image using a pre-trained model and processor, and formats the output.

    Parameters:
    - image: The image from which to parse text.
    - processor: The processor instance equipped with methods for handling input preprocessing and decoding outputs.
    - model: The pre-trained VisionEncoderDecoderModel used to generate text from image data.

    Returns:
    - dict: A dictionary containing parsed and formatted cheque details.
    """
    # Prepare the initial task prompt and get decoder input IDs from the tokenizer
    task_prompt = "<parse-cheque>"
    decoder_input_ids = processor.tokenizer(
        task_prompt, 
        add_special_tokens=False, 
        return_tensors="pt",
    ).input_ids

    # Convert image to pixel values suitable for the model input
    pixel_values = processor(image, return_tensors="pt").pixel_values

    
    # Generate outputs from the model using the provided pixel values and decoder inputs
    outputs = model.generate(
        pixel_values.to(device),                                   # Ensure pixel values are on the correct device (CPU/GPU)
        decoder_input_ids=decoder_input_ids.to(device),            # Move decoder inputs to the correct device
        max_length=model.decoder.config.max_position_embeddings,   # Set the maximum output length
        pad_token_id=processor.tokenizer.pad_token_id,             # Define padding token
        eos_token_id=processor.tokenizer.eos_token_id,             # Define end-of-sequence token
        use_cache=True,                                            # Enable caching to improve performance
        bad_words_ids=[[processor.tokenizer.unk_token_id]],        # Prevent generation of unknown tokens
        return_dict_in_generate=True,                              # Return outputs in a dictionary format
    )

    # Decode the output sequences to text
    sequence = processor.batch_decode(outputs.sequences)[0]
    
    # Remove special tokens and clean up the sequence
    sequence = sequence.replace(processor.tokenizer.eos_token, "").replace(processor.tokenizer.pad_token, "")
    
    # Remove the initial task prompt token
    sequence = re.sub(r"<.*?>", "", sequence, count=1).strip()
    
    # Convert the cleaned sequence to JSON and format the output
    json = processor.token2json(sequence)
    
    return {
        key: (value if value != '' else 'missing') 
        for attribute 
        in json['cheque_details']
        for key, value 
        in attribute.items()
    }


def evaluate_cheque_fraud(parsed_data, model_fraud_detection):
    """
    Evaluates potential fraud in a cheque by analyzing the consistency of spelling and the match between 
    numerical and textual representations of the amount.

    Parameters:
    - parsed_data (dict): Dictionary containing parsed data from a cheque, including amounts in words and figures.
    - model_fraud_detection: A trained model used to predict whether the cheque is valid or fraudulent.

    Returns:
    - tuple: A tuple containing the fraud evaluation result ('valid' or 'fraud'), spelling check message,
             and amount match message.
    """
    # Check spelling for the amount in words and correct it if necessary
    spelling_is_correct, amount_in_text_corrected = spell_check(
        parsed_data['amt_in_words'],
    )

    # Check if the corrected amount in words matches the amount in figures
    amount_match = amount_letter_number_match(
        amount_in_text_corrected, 
        parsed_data['amt_in_figures'],
    )

    # Handle the case where amount_match is a tuple, using only the first element if so
    amount_match_value = amount_match[0] if isinstance(amount_match, tuple) else amount_match
        
    # Prepare the input for the fraud detection model
    model_input = np.array([spelling_is_correct, amount_match_value])

    # Predict fraud using the model, reshaping input to match expected format
    prediction = model_fraud_detection.predict(
        model_input.reshape(1, -1)
    )
    
    # Construct messages regarding the spelling and value match
    spelling = f'Spelling is correct: {spelling_is_correct}'
    value_match = f'Numeric and alphabetic values match: {amount_match}'
    
    # Return the evaluation result along with explanatory messages
    return np.where(prediction[0] == 1, 'valid', 'fraud').item(), spelling, value_match
