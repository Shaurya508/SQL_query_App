import os
import pandas as pd
import streamlit as st
import speech_recognition as sr
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_ollama import ChatOllama
import google.generativeai as genai

# Load the dataset
df = pd.read_csv('Contributions_Masked Data.csv')
# genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
# Initialize the LLM and agent executor
# llm = ChatGoogleGenerativeAI(model="gemini-1.0-pro", api_key='AIzaSyAuBv-5edS_S5QmEi5NBmrwvs8nIHSnJIQ', temperature=0.5)
llm = ChatOllama(model="gemma2:2b", temperature=0)
model = ChatOllama(model="gemma2:2b", temperature=0)

# model = ChatGoogleGenerativeAI(model="gemini-1.0-pro" , temperature=0.5)

agent_executor = create_pandas_dataframe_agent(
    llm,
    df,
    agent_type="zero-shot-react-description",
    verbose=True,
    return_intermediate_steps=True,
    allow_dangerous_code=True,
    # early_stopping_method='force',
    # max_iterations=5,
    # handle_parsing_errors=True
)

# Function to recognize speech
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Please speak your question...")
        audio = recognizer.listen(source)
        try:
            question = recognizer.recognize_google(audio)
            st.success(f"You said: {question}")
            return question
        except sr.UnknownValueError:
            st.error("Sorry, I did not understand that.")
        except sr.RequestError as e:
            st.error(f"Could not request results; {e}")
    return None

# Streamlit UI
st.set_page_config(page_title="DataFrame Agent with LLM", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
        .main {
            background-color: #f7f8fa;
            padding: 20px;
        }
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
        }
        .stButton > button:hover {
            background-color: #45a049;
        }
        .stTextInput > div > input {
            padding: 10px;
            font-size: 16px;
        }
    </style>
""", unsafe_allow_html=True)

def preprocess_question(question):
    return question.lower()

# Preprocess the dataframe columns to lowercase
# df['variable_name'] = df['variable_name'].str.lower()

# Updated Streamlit UI section for handling both text and voice inputs
st.title("📊 Chat with Dataframe 🤖")
st.write("### Ask a question about the dataset using text or voice input:")

col1, col2 = st.columns([1, 1])

# Speech Recognition button
with col1:
    st.markdown("#### Voice Input:")
    if st.button("🎤 Speak your question"):
        question = recognize_speech()
        if question:
            # question = preprocess_question(question)
            with st.spinner("Processing your question..."):
                response = agent_executor.invoke(question)
                st.markdown("#### Answer:")
                st.success(model.invoke(f"Write a summary of the final answer of the response. {response}").content)

# Text input for the question
with col2:
    st.markdown("#### Text Input:")
    question = st.text_input("Enter your question here:", key="input_question", placeholder="Type your question...")

    if st.button("Submit"):
        if question:
            # question = preprocess_question(question)
            with st.spinner("Processing your question..."):
                response = agent_executor.invoke(question)
                st.markdown("#### Answer:")
                st.success(model.invoke(f"Write a summary of the final answer of the response in a crisp manner. {response}").content)
                # st.success(response)
        else:
            st.warning("Please enter a question before submitting.")

