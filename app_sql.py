import streamlit as st
import os
from langchain_experimental.sql import SQLDatabaseChain
from langchain.utilities import SQLDatabase
from langchain_google_genai import GoogleGenerativeAI
from langchain.chains import create_sql_query_chain
from langchain_ollama import ChatOllama

# Initialize the database and LLM
db = SQLDatabase.from_uri("mysql+pymysql://root:Mishra%40123@localhost/new_data", sample_rows_in_table_info=3)
llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=os.environ["GOOGLE_API_KEY"])

chain = create_sql_query_chain(llm, db)

# Column mapping: real to masked
column_mapping = {
    "variable_name": "masked_column_1",
    "value": "masked_column_2",
    "year": "masked_column_3",
    "rank": "masked_column_4",
    # Add all your real to masked column mappings here
}

# Reverse column mapping: masked to real
reverse_column_mapping = {v: k for k, v in column_mapping.items()}

# Function to mask column names in a question
def mask_question(question):
    for real_col, masked_col in column_mapping.items():
        question = question.replace(real_col, masked_col)
    return question

# Function to unmask column names in the SQL query
def unmask_query(query):
    for masked_col, real_col in reverse_column_mapping.items():
        query = query.replace(masked_col, real_col)
    return query

# Function to execute query
def execute_query(question):
    # Mask the question to replace real column names with masked ones
    masked_question = mask_question(question)
    
    # Generate SQL query from the masked question
    response = chain.invoke({"question": masked_question})
    
    # Clean the generated SQL query
    cleaned_query = response.strip('```sql\n').strip('\n```')
    
    # Unmask the SQL query to replace masked column names with real ones
    unmasked_query = unmask_query(cleaned_query)
    
    # Execute the unmasked query on the real database
    result = db.run(unmasked_query)
    return unmasked_query, result

# Streamlit UI
st.title("AI-Powered SQL Query App")

# Custom CSS for beautification
st.markdown("""
    <style>
    body {
        background-color: #F5F5F5;
    }
    .main {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 20px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        font-size: 16px;
        padding: 8px 20px;
    }
    .stTextInput>div>input {
        padding: 10px;
        border-radius: 8px;
        border: 2px solid #4CAF50;
        font-size: 16px;
    }
    .result-box {
        padding: 10px;
        border: 2px solid #ddd;
        border-radius: 10px;
        margin-top: 20px;
        background-color: #f9f9f9;
    }
    .sql-query-box {
        background-color: #e6f7ff;
        padding: 10px;
        border-left: 5px solid #007ACC;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Input box for asking a question
st.subheader("Ask a SQL-related question:")
user_question = st.text_input("")

# Button to submit the question
if st.button("Get Answer"):
    if user_question:
        with st.spinner("Generating SQL query and fetching results..."):
            try:
                # Execute the query and display the result
                query, result = execute_query(user_question)

                # Display generated SQL query
                st.markdown("**Generated SQL Query:**", unsafe_allow_html=True)
                st.markdown(f"<div class='sql-query-box'><code>{query}</code></div>", unsafe_allow_html=True)

                # Display result
                st.markdown("**Query Result:**", unsafe_allow_html=True)
                st.markdown(f"<div class='result-box'>{result}</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a question.")
