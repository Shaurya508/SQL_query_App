#from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from sqlalchemy import create_engine
import os
from langchain.utilities import SQLDatabase
from langchain_google_genai import GoogleGenerativeAI

db_user = "root"
db_password = "Mishra@123"
db_host = "localhost"
db_name = "new_data"

# Create SQLAlchemy engine
# engine = create_engine(f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}")

# # Initialize SQLDatabase
# db = SQLDatabase(engine, sample_rows_in_table_info=3)

# if you are using MySQL

db = SQLDatabase.from_uri("mysql+pymysql://root:Mishra%40123@localhost/new_data", sample_rows_in_table_info=3)

# print(db.table_info)
from langchain.chains import create_sql_query_chain
llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=os.environ["GOOGLE_API_KEY"])

# chain = create_sql_query_chain(llm, db)
# response = chain.invoke({"question": "How many customers are there"})
# # print(response)
# cleaned_query = response.strip('```sql\n').strip('\n```')
# # print(cleaned_query)
# # Execute the cleaned query
# result = db.run(cleaned_query)
# print(result)
chain = create_sql_query_chain(llm, db)
def execute_query(question):
        # Generate SQL query from question
        response = chain.invoke({"question": question})
        print(response)
        print("###################################################")
        # Strip the formatting markers from the response
        cleaned_query = response.strip('```sql\n').strip('\n```')
        print(cleaned_query)
        print("###################################################")        
        # Execute the cleaned query
        result = db.run(cleaned_query)
        print("###################################################")        
        # Display the result
        print(result)
    
q1 = "What is the value of OOH Spends in the year 2019-2020 ?"
execute_query(q1)