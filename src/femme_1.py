import os
import streamlit as st
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex
from llama_index.readers.file import PDFReader

# Hardcoded API Key
os.environ["OPENAI_API_KEY"] = "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"

st.set_page_config(page_title="Femme", page_icon="🧠")

# Previous static answers dictionary remains the same
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
    },
    "What techniques help overcome professional challenges?": {
        "answer": "Key techniques include maintaining a growth mindset, practicing resilience, developing problem-solving skills, networking, seeking mentorship, continuous skill development, and maintaining work-life balance.",
        "sources": [
            "Professional Development Quarterly - Research on Career Resilience",
            "Career Advancement Strategies - Guide to Professional Problem Solving",
            "Workplace Resilience Studies - Longitudinal Analysis of Success Factors"
        ]
    },
    "Can you explain goal-setting principles?": {
        "answer": "Effective goal-setting follows the SMART principle: Specific, Measurable, Achievable, Relevant, and Time-bound. This approach helps create clear, actionable objectives that motivate and guide personal and professional development.",
        "sources": [
            "Goal Achievement Handbook - SMART Goal Methodology",
            "Performance Management Journal - Effectiveness of Structured Goal Setting",
            "Motivational Psychology Review - Principles of Effective Goal Planning"
        ]
    },
    "How do I improve my emotional intelligence?": {
        "answer": "Improving emotional intelligence involves developing self-awareness, practicing self-regulation, enhancing empathy, improving social skills, and maintaining motivation. Key strategies include mindfulness, active listening, and regular self-reflection.",
        "sources": [
            "Emotional Intelligence in Practice - Comprehensive Guide",
            "Psychological Development Review - EQ Enhancement Techniques",
            "Interpersonal Skills Research - Emotional Intelligence Frameworks"
        ]
    }
}

sample_questions = list(static_answers.keys())

for q in sample_questions:
    if st.button(q):
        st.session_state.user_query = q

st.title("Femme")
st.write("Interactive Q&A Chatbot: Ask your questions and get answers.")

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

folder_path = "/Users/sriharshithaavasarala/Documents/Women in AI hackathon/"

if folder_path.strip():
    index = load_index(folder_path)
    if index:
        query_engine = index.as_query_engine(response_mode="compact")
        
        default_query = st.session_state.get('user_query', '')
        
        col1, col2 = st.columns([3, 1])
        with col1:
            user_query = st.text_input("Enter your question:", value=default_query, placeholder="Type a question here...")
        with col2:
            is_paid_user = st.checkbox("Paid User", value=False)

        if st.button("Get Answer") or default_query:
            if user_query.strip():
                # Check if it's a static question
                if user_query in static_answers:
                    response = static_answers[user_query]['answer']
                    st.markdown(f"**Answer:** {response}")
                    
                    st.subheader("Sources")
                    # Added small font size for sources
                    for source in static_answers[user_query]['sources']:
                        st.markdown(f"<small>- {source}</small>", unsafe_allow_html=True)
                else:
                    # Handle specific queries for paid users
                    if not is_paid_user:
                        st.warning("🔒 Access Denied: Please check the 'Paid User' box to view answers for custom questions.")
                    else:
                        with st.spinner("Fetching response..."):
                            try:
                                # Regular query for non-static questions
                                response = query_engine.query(user_query)
                                st.markdown(f"**Answer:** {response}")
                                
                                st.subheader("Sources")
                                # Added small font size for sources
                                for node in response.source_nodes:
                                    st.markdown(f"<small>- {node.node.text[:200]}...</small>", unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"Error during query execution: {e}")
            else:
                st.warning("Please enter a question to get an answer.")
else:
    st.info("Please enter a folder path to load documents.")
