import streamlit as st
from database import DatabaseConnector
from sql_chain import SQLAssistant
from utils import configure_logging
from config import DATABASE_SETTINGS


# Configure logging
configure_logging()

st.set_page_config(page_title="Chat with Databse", page_icon=":speech_balloon:")
st.title("Chat with MySQL")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with st.sidebar:
    st.subheader("Settings")
    st.text_input("Host", value=DATABASE_SETTINGS["host"], key="Host")
    st.text_input("Port", value=DATABASE_SETTINGS["port"], key="Port")
    st.text_input("User", value=DATABASE_SETTINGS["user"], key="User")
    st.text_input("Password", type="password", value=DATABASE_SETTINGS["password"], key="Password")
    st.text_input("Database", value=DATABASE_SETTINGS["database"], key="Database")

    if st.button("Connect"):
        db_connector = DatabaseConnector(
            st.session_state["User"],
            st.session_state["Password"],
            st.session_state["Host"],
            st.session_state["Port"],
            st.session_state["Database"]
        )
        with st.spinner("Connecting to database..."):
            db = db_connector.connect()
            if db:
                st.session_state.db = db
                st.success("Connected to database!")
            else:
                st.error("Could not establish a connection.")

if "db" in st.session_state:
    sql_assistant = SQLAssistant(st.session_state.db)
    st.chat_message("ai").write("Hello! I'm a SQL assistant. Ask me anything about your database.")
    user_query = st.chat_input("Type a message...")
    if user_query and user_query.strip():
        st.chat_message("user").write(user_query)
        st.session_state.chat_history.append(user_query)

        with st.spinner("Processing..."):
            response, generated_query = sql_assistant.get_response(
                user_query,
                st.session_state.chat_history,
            )
            if response:
                st.chat_message("ai").write(response)
                st.markdown(f"**Generated SQL Query:**")
                st.code(generated_query)
          

        st.session_state.chat_history.append(response)
else:
    st.error("Connect to the Database")
