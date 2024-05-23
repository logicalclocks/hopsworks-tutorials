# ⚙️ Private PDF search using LLMs and RAG  
  * [Helper video describing how to implement this LLM PDF system](https://www.youtube.com/watch?v=8YDANJ4Gbis) 

# ⚙️ RAG, Fine-tune a LLM, UI for querying

This project is an AI system built on Hopsworks that
  * creates vector embeddings for PDF files in a google drive folder (you can also use local/network directories) and indexes them for retrieval augmented generation (RAG) in Hopsworks Feature Store with Vector Indexing
  * creates an instruction dataset for fine-tuning using a teacher model (GPT by default, but you can easily configure to use a powerful private model such as Llama-3-70b)
  * trains and hosts in the model registry a fine-tuned open-source foundation model (Mistral 7b by default, but can be easily changed for other models such as Llama-3-8b)
  * provides a UI, written in Streamlit/Python, for querying your PDFs that returns answers, citing the page/paragraph/url-to-pdf in its answer.

![Hopsworks Architecture for Private PDFs Indexed for LLMs](../..//images/llm-pdfs-architecture.gif)

## 📖 Feature Pipeline
The Feature Pipeline does the following:

 * Download any new PDFs from the google drive.
 * Extract chunks of text from the PDFs and store them in a Vector-Index enabled Feature Group in Hopsworks.
 * Use GPT (or Llama-3-70b) to generate an instruction set for the fine-tuning of a foundation LLM and store the instruction dataset as a feature group in Hopsworks.

## 🏃🏻‍♂️Training Pipeline
This step is optional if you also want to create a fine-tuned model. 
The Training Pipeline does the following:

 * Uses the instruction dataset and LoRA to fine-tune the open-source LLM (Mistral-7B-Instruct-v0.2 by default).
 * Saves the fine-tuned model to Hopsworks Model Registry.

## 🚀 Inference Pipeline
* A chatbot written in Streamlit that answers questions about the PDFs you uploaded using RAG and your embedded LLM (either an off-the-shelf model, like Mistral-7B-Instruct-v0.2, or your fine-tuned LLM.

## 🕵🏻‍♂️ Google Drive Credentials Creation

To create your Google Drive credentials, please follow the steps outlined in this guide: [Google Drive API Quickstart with Python](https://developers.google.com/drive/api/quickstart/python). This guide will walk you through setting up your project and downloading the necessary credentials files.

After completing the setup, you will have two files: `credentials.json` and `client_secret.json`. These are your authentication files from your Google Cloud account.

Next, integrate these files into your project:

1. Create a directory named `credentials` at the root of your forked repository.

2. Place both `credentials.json` and `client_secret.json` files inside this credentials directory.

Now, you are ready to download your PDFs from the Google Drive!


