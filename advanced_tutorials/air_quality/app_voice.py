import streamlit as st
import whisper
import tempfile

# Function to load the model (adjust the model size as needed)
def load_whisper_model(model_name='base'):
    model = whisper.load_model(model_name)
    return model

# Function to transcribe and translate audio
def transcribe_and_translate_audio(model, audio_file):
    # Save the uploaded file to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
        tmp_file.write(audio_file.getvalue())
        tmp_filename = tmp_file.name

    # Transcribe and translate the audio file
    result = model.transcribe(tmp_filename, task="translate")
    return result['text']

# Streamlit app
def main():
    st.title('Speech to Text Translation with Whisper')
    st.write("Upload an audio file, and the app will transcribe and translate the speech to English text using OpenAI’s Whisper model.")

    # Load the Whisper model
    model = load_whisper_model()

    # Audio file uploader
    audio_file = st.file_uploader("Choose an audio file...", type=['wav', 'mp3', 'ogg'])

    if audio_file is not None:
        # Display a message while the model is transcribing and translating the audio
        with st.spinner('Transcribing and translating the audio...'):
            transcription = transcribe_and_translate_audio(model, audio_file)
            st.text_area("Transcribed and Translated Text", transcription, height=300)

if __name__ == "__main__":
    main()
