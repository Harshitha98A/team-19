import os
import streamlit as st
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, Settings
from llama_index.readers.file import PDFReader
from llama_index.core.memory import ChatMemoryBuffer


# Hardcoded API Key
os.environ["OPENAI_API_KEY"] = os.environ.get('OPENAI_API_KEY')

st.set_page_config(page_title="Femme", page_icon="🧠")

# Memory buffer for conversation context
memory = ChatMemoryBuffer.from_defaults(token_limit=3000)

# Configure chat settings
Settings.llm = OpenAI(
    model="gpt-3.5-turbo", 
    temperature=0.1,
    max_tokens=512
)

# Static answers dictionary
STATIC_QUESTIONS = {
    "What are effective strategies for personal growth?": {
        "answer": "Personal growth strategies include self-reflection, continuous learning, setting clear goals, developing emotional intelligence, practicing mindfulness, and seeking feedback from mentors and peers.",
        "sources": [
            "Personal Development Handbook - Ch. 3: Self-Improvement Techniques",
            "Coaching Principles Volume 2 - Section on Individual Growth"
        ]
    },
    # ... other static answers
}


@st.cache_resource
def load_chat_index(folder_path):
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


def render_suggestions():
    st.markdown("### Try asking about:")
    # Define your example queries
    suggestions = [
        "What is the best way to close a presentation?",
        "How should I prepare for a meeting with my skip?",
        "What advice do you have for starting a new role?",
    ]

    # Style for the container
    st.markdown("""
        <style>
        .suggestion-container {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    cols = st.columns(3)

    for idx, suggestion in enumerate(suggestions):
        col_idx = idx % 3
        with cols[col_idx]:
            if st.button(suggestion, key=f"suggestion_{idx}", use_container_width=True):
                # When button is clicked, set it as the query
                st.session_state.query = suggestion
                st.rerun()


def render_chat(chat_engine):
    # Initialize chat history in session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    # User input
    if prompt := st.chat_input("Ask a question"):
        # Check for static answers first
        if prompt in STATIC_QUESTIONS:
            response = STATIC_QUESTIONS[prompt]['answer']
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            # Display static answer
            with st.chat_message("assistant"):
                st.markdown(response)
                st.subheader("Sources")
                for source in STATIC_QUESTIONS[prompt]['sources']:
                    st.markdown(f"<small>- {source}</small>", unsafe_allow_html=True)
            # Store messages
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            # Generate response using chat engine
            with st.chat_message("assistant"):
                with st.spinner("Generating response..."):
                    response = chat_engine.chat(prompt)
                    st.markdown(response.response)
            # Store messages
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.messages.append({"role": "assistant", "content": response.response})


@st.cache_resource
def load_chat_index(folder_path):
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


def load_engine():
    folder_path = "./static"
    index = None
    chat_engine = None
    if folder_path.strip():
        index = load_chat_index(folder_path)
    if index:
        # Create chat engine with context-aware mode
        chat_engine = index.as_chat_engine(
            chat_mode="context",
            memory=memory,
            system_prompt=(
                "You are a professional career and personal development coach. "
                "Provide clear, actionable advice with empathy and practical insights. "
                "If a query is unclear, ask clarifying questions."
            )
        )
    else:
        st.info("Please enter a folder path to load documents.")
    return chat_engine


def main():
    chat_engine = load_engine()

    st.title("Femme")
    st.write("Interactive Q&A Chatbot: Ask your questions and get answers.")
    render_chat(chat_engine=chat_engine)
    # chat_page()

if __name__ == "__main__":
    main()

