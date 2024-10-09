import streamlit as st
import os
from langchain_experimental.sql import SQLDatabaseChain
from langchain.utilities import SQLDatabase
from langchain_google_genai import GoogleGenerativeAI
from langchain.chains import create_sql_query_chain
from langchain_ollama import ChatOllama
import speech_recognition as sr

# Defining the column names to be sent to the LLM
spends_dict = {
    "Base": "apple",
    "TV1 Spends": "banana",
    "Google Youtube Spends": "cherry",
    "Branded Paid Search Spends": "dragonfruit",
    "OOH Spends": "elephant",
    "Meta Spends": "falcon",
    "Twitter Ad Spends": "giraffe",
    "Tiktok Spends": "hippo",
    "TV2 Spends": "iguana",
    "Competitor2 Ad Spend Impact": "jellyfish",
    "Competitor1 Ad Spend Impact": "kangaroo" ,
}
spends_dict1 = {
    "Base": "apple",
    "TV1": "banana",
    "TV1 Spends": "banana",  # Multiple keys for same value
    "Google Youtube": "cherry",
    "Google Youtube Spends": "cherry",
    "Branded Paid Search": "dragonfruit",
    "Branded Paid Search Spends": "dragonfruit",
    "OOH": "elephant",
    "OOH Spends": "elephant",
    "Meta": "falcon",
    "Meta Spends": "falcon",
    "Twitter": "giraffe",
    "Twitter Ad Spends": "giraffe",
    "Tiktok": "hippo",
    "Tiktok Spends": "hippo",
    "TV2": "iguana",
    "TV2 Spends": "iguana",
    "Competitor 2": "jellyfish",
    "Competitor2 Ad Spend Impact": "jellyfish",
    "Competitor 1": "kangaroo",
    "Competitor1 Ad Spend Impact": "kangaroo" ,
    "oh": "elephant" 
}



# Initialize the database and LLM
db = SQLDatabase.from_uri("mysql+pymysql://root:Mishra%40123@localhost/new_data")
llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=os.environ["GOOGLE_API_KEY"])
# model = ChatOllama(model="llama3.2:1b", temperature=0)
short_db = SQLDatabase.from_uri("mysql+pymysql://root:Mishra%40123@localhost/new_short_data")
chain = create_sql_query_chain(llm, short_db)

# def convert_query(original_query: str, new_table_name: str, original_spends , replaced_spends) -> str:
#     # Replace the original table name with the new table name
#     converted_query = original_query.replace('shorter_data', new_table_name)  
#     if(original_spends != None):  
#         converted_query = converted_query.replace(replaced_spends, original_spends)    

#     return converted_query
def convert_query(original_query: str, new_table_name: str, replaced_spends: str, spends_dict: dict) -> str:
    # Replace the original table name with the new table name
    converted_query = original_query.replace('shorter_data', new_table_name)
    
    # Find the original spend category from the spends_dict
    original_spends = next((key for key, value in spends_dict.items() if value == replaced_spends), None)
    
    # Replace the original spends in the query if found
    if original_spends is not None:
        converted_query = converted_query.replace(replaced_spends, original_spends)

    return converted_query


import re
def convert_question(question: str, spends_dict: dict):
    original_spends = None
    replaced_value = None

    # Iterate over the spends dictionary
    for spend_category, spend_value in spends_dict.items():
        # Create a case-insensitive regex pattern for the spend category
        pattern = re.compile(re.escape(spend_category), re.IGNORECASE)
        
        # Check if the spend category is present in the question
        if pattern.search(question):
            # Save the original spend category (case-preserving)
            original_spends = spend_category
            replaced_value = spend_value  # Value from the dictionary
            
            # Replace the spend category in the question with the corresponding value
            question = pattern.sub(spend_value, question, count=1)
            break  # Assuming only one category will be replaced

    # If no spend category was found, return the original question
    return question, original_spends, replaced_value

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

# Function to execute query
def execute_query(question):
    question , original_spends , replaced_spends = convert_question(question,spends_dict1)
    print(question)
    # Generate SQL query from the question
    response = chain.invoke({"question": question})
    # response = llm.invoke("I am having a mySQL database with columns namely 'variable_name' , 'year' , 'rank' , 'value' and also the command used to see all rows of the databse is SELECT * FROM new_data.contributions_masked_data;. Write a query according to the question below -> " + question)
    # response = llm.invoke(question)
    # Clean the generated SQL query
    # print(response)
    cleaned_query = response.strip('```sql\n').strip('\n```')
    # print(cleaned_query)
    # Execute the query
    new_table_name = 'contributions_masked_data'
    converted_query = convert_query(cleaned_query, new_table_name,replaced_spends , spends_dict)
    print(converted_query)
    result = db.run(converted_query)
    return converted_query, result

# def execute_query(question):
    # response = llm.invoke("I am having a SQL database with columns namely 'variable_name' , 'year' , 'rank' , 'value'. Write a query according to the question below -> " + question)
    # print(response)
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

if st.button("🎤"):
    user_question = recognize_speech()
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

# Button to submit the question
if st.button("Get Answer"):
    if user_question:
        with st.spinner("Generating SQL query and fetching results..."):
            try:
                # Execute the query and display the result
                query, result = execute_query(user_question)
                # natural_response = model.invoke("the question is this - " + user_question +"the answer is this in percentage - " + str(result) + "Write the answer in natural language in one line only like the value of this is this . Don't say anything vague . I expect only a one line state,ment from you .").content
                # Display generated SQL query
                st.markdown("**Generated SQL Query:**", unsafe_allow_html=True)
                st.markdown(f"<div class='sql-query-box'><code>{query}</code></div>", unsafe_allow_html=True)

                # Display result
                st.markdown("**Query Result:**", unsafe_allow_html=True)
                # st.markdown(f"<div class='result-box'>{natural_response}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='result-box'>{"The answer to your question is " + result}</div>", unsafe_allow_html=True)


            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a question.")
