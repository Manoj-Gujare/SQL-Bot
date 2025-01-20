import os
import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY=os.getenv("GROQ_API_KEY")

llm = ChatGroq(model="llama3-8b-8192")

class SQLAssistant:
    def __init__(self, db):
        self.db = db

    def get_sql_chain(self):
        template = """
        You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
        Based on the table schema below, write a SQL query that would answer the user's question. Take the conversation history into account.
        
        <SCHEMA>{schema}</SCHEMA>
        
        Conversation History: {chat_history}
        
        Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, not even backticks.
        
        Question: {question}
        SQL Query:
        """
        prompt = ChatPromptTemplate.from_template(template)

        def get_schema(_):
            return self.db.get_table_info()

        return (
            RunnablePassthrough.assign(schema=get_schema)
            | prompt
            | llm
            | StrOutputParser()
        )

    def get_response(self, user_query: str, chat_history: list):
        try:
            sql_chain = self.get_sql_chain()

            template = """
            You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
            Based on the table schema below, question, sql query, and sql response, write a natural language response.
            Do not mention any interpretation, suggestions and avoid writing like according to database or something like that.
            <SCHEMA>{schema}</SCHEMA>

            Conversation History: {chat_history}
            SQL Query: <SQL>{query}</SQL>
            User question: {question}
            SQL Response: {response}
            """
            prompt = ChatPromptTemplate.from_template(template)

            chain = (
                RunnablePassthrough.assign(query=sql_chain).assign(
                    schema=lambda _: self.db.get_table_info(),
                    response=lambda vars: self.db.run(vars["query"]),
                )
                | prompt
                | llm
                | StrOutputParser()
            )

            result = chain.invoke({
                "question": user_query,
                "chat_history": chat_history,
            })

            generated_query = sql_chain.invoke({
                "question": user_query,
                "chat_history": chat_history,
            })

            logging.info(f"Generated Query: {generated_query}")
            return result, generated_query
        except Exception as e:
            logging.error(f"Error generating response: {e}")
            return "An error occurred while processing your query.", ""
