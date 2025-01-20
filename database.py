import logging
from langchain_community.utilities import SQLDatabase
import streamlit as st


class DatabaseConnector:
    def __init__(self, user: str, password: str, host: str, port: str, database: str):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.db = None

    def connect(self):
        try:
            db_uri = f"mysql+mysqlconnector://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
            self.db = SQLDatabase.from_uri(db_uri)
            logging.info("Connected to database successfully.")
            return self.db
        except Exception as e:
            logging.error(f"Error connecting to database: {e}")
            st.error("Failed to connect to database. Please check your credentials and try again.")
            return None
