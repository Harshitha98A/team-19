import os
import streamlit as st
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex
from llama_index.readers.file import PDFReader
from openai import OpenAI as OpenAI_API

# Hardcoded API Key
os.environ["OPENAI_API_KEY"] = "your-api-key"

# Set up Streamlit page configuration
st.set_page_config(page_title="Femme", page_icon="🧠")

# Static Answers dictionary
static_answers = {
    "What are effective strategies for personal growth?": {
        "answer": "Personal growth strategies include self-reflection, continuous learning, setting clear goals, developing emotional intelligence, practicing mindfulness, and seeking feedback from mentors and peers.",
        "sources": [
            "Personal Development Handbook - Ch. 3: Self-Improvement Techniques",
            "Coaching Principles Volume 2 - Section on Individual Growth",
            "Psychological Growth Strategies Journal - Research on Personal Development Methodologies"
        ]
    },
    "How can I develop better leadership skills?": {
        "answer": "Developing leadership skills involves active listening, empathy, clear communication, strategic thinking, adaptability, continuous learning, and the ability to inspire and motivate team members.",
        "sources": [
            "Leadership Excellence Magazine - Feature on Modern Leadership Competencies",
            "Harvard Business Review - Article on Emotional Intelligence in Leadership",
            "Organizational Behavior Research - Study on Effective Leadership Traits"
        ]
    }
}

# Function to generate zero-shot response using OpenAI model
def zero_shot_response(user_input):
    prompt = f"Answer the following question based on your knowledge: {user_input}"

    try:
        response = OpenAI_API.Completion.create(
            engine="text-davinci-003",  # Or use another model like `gpt-3.5-turbo`
            prompt=prompt,
            max_tokens=150,
            temperature=0.7,
        )
        return response.choices[0].text.strip()

    except Exception as e:
        st.error(f"Error generating response: {e}")
        return "Sorry, I couldn't generate a response."

# Function to use the `as_chat_engine` and process input dynamically
def as_chat_engine(user_input):
    # If the user input matches a static answer
    if user_input in static_answers:
        response = static_answers[user_input]['answer']
        sources = static_answers[user_input]['sources']
        return response, sources

    # Otherwise, handle it as a dynamic query using zero-shot response
    response = zero_shot_response(user_input)
    return response, []

# Function to load index and handle documents if needed
@st.cache_resource
def load_index(folder_path):
    documents = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if filename.endswith(".pdf"):
            try:
                reader = PDFReader()
                pdf_documents = reader.load_data(file_path)
                documents.extend(pdf_documents)
            except Exception as e:
                st.error(f"Error reading {filename}: {e}")

    return VectorStoreIndex.from_documents(documents) if documents else None

# Input from the user to interact with the chat engine
user_input = st.text_input("Ask a question:")

# Handle user input using the `as_chat_engine`
if user_input:
    response, sources = as_chat_engine(user_input)
    
    # Display the response
    st.write("Response:", response)
    
    # Display sources if available
    if sources:
        st.write("Sources:", ", ".join(sources))
