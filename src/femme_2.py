import os
import streamlit as st
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex
from llama_index.readers.file import PDFReader
from openai import OpenAI as OpenAI_API  # Use OpenAI API for Zero-Shot functionality

# Hardcoded API Key
os.environ["OPENAI_API_KEY"] = "your-api-key"

st.set_page_config(page_title="Femme", page_icon="🧠")

# Static Answers dictionary remains the same
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

sample_questions = list(static_answers.keys())

# Chat history initialization
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Function to handle the chat conversation
def chat():
    # Get user input
    user_input = st.text_input("You:", "", key="user_input")

    if user_input:
        # Display user input in the chat history
        st.session_state.chat_history.append(f"User: {user_input}")

        # Check if it's a static question
        if user_input in static_answers:
            response = static_answers[user_input]['answer']
            sources = static_answers[user_input]['sources']

            st.session_state.chat_history.append(f"Bot: {response}")
            st.session_state.chat_history.append(f"Sources: {', '.join(sources)}")

        else:
            # Handle dynamic queries using Zero-shot
            response = zero_shot_response(user_input)
            st.session_state.chat_history.append(f"Bot: {response}")

    # Display chat history
    for message in st.session_state.chat_history:
        st.write(message)

# Function to generate zero-shot response
def zero_shot_response(user_input):
    prompt = f"Answer the following question based on your knowledge: {user_input}"
    
    try:
        response = OpenAI_API.Completion.create(
            engine="text-davinci-003",  # Choose your preferred model
            prompt=prompt,
            max_tokens=150,
            temperature=0.7,
        )
        return response.choices[0].text.strip()
    
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return "Sorry, I couldn't generate a response."

# Function to load the index from the folder path
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

# Run the chat function
chat()
