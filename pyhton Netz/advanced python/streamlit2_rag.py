                                    #RAG(Retrieval augmented generation)

import os
import psycopg2
import streamlit as st
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate

# Database connection
def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="chat_app",
        user="postgres",
        password="Gmail@1234",
    )

# Save message to the database
def save_message_to_db(user_id, user_message, ai_response):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO chat_history1 (user_id, message, response)
            VALUES (%s, %s, %s)
            """,
            (user_id, user_message, ai_response),
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        st.error(f"Error saving message: {e}")

# Retrieve chat history from the database
def get_chat_history_from_db(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT timestamp, message, response
            FROM chat_history1
            WHERE user_id = %s
            ORDER BY timestamp ASC
            """,
            (user_id,),
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        st.error(f"Error fetching chat history: {e}")
        return []

# LangChain initialization
MODEL = "llama3.2:3b"
model = Ollama(model=MODEL)
embeddings = OllamaEmbeddings(model=MODEL)

vectorstore_path = r"C:\Users\Nisha kadian\Documents\pyhton Netz\chroma_db"
vectorstore = Chroma(persist_directory=vectorstore_path, embedding_function=embeddings)
retriever = vectorstore.as_retriever()

template = """
Answer the question based on the context below. If you cannot 
answer the question, reply "I do not know".

Context: {context}

Question: {question}
"""
prompt = PromptTemplate.from_template(template)

users_db = {
    "user1": {"password": "password1", "user_id": 1},
    "user2": {"password": "password2", "user_id": 2},
}

# Initialize Streamlit session state
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}

# Streamlit UI configuration
st.set_page_config(page_title="RAG Chatbot", layout="centered")

# Authenticate user
def authenticate_user(username, password):
    user = users_db.get(username)
    if user and user["password"] == password:
        return user["user_id"]
    return None

# Login function
def login():
    st.title("Login to RAG-based Chatbot")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user_id = authenticate_user(username, password)
        if user_id:
            st.session_state.username = username
            st.session_state.user_id = user_id
            if username not in st.session_state.chat_histories:
                st.session_state.chat_histories[username] = []
            st.success("Login successful!")
            return True
        else:
            st.error("Invalid credentials!")
            return False
    return False

# Chat function
def chat():
    if "username" not in st.session_state:
        st.error("You need to log in first!")
        return

    username = st.session_state.username
    user_id = st.session_state.user_id

    st.title(f"Hello, {username}!")
    user_message = st.text_input("Ask your question:")

    if st.button("Send") and user_message:
        history = st.session_state.chat_histories.get(username, [])

        # Retrieve relevant documents
        context_docs = retriever.get_relevant_documents(user_message)
        if not context_docs:
            st.write("")
            return

        # Combine context
        context = " ".join(doc.page_content for doc in context_docs)

        # Generate response
        query_with_context = prompt.format(context=context, question=user_message)
        response_message = model(query_with_context)

        # Update chat history
        history.append(f"User: {user_message}")
        history.append(f"AI: {response_message}")
        st.session_state.chat_histories[username] = history

        # Save to database
        save_message_to_db(user_id, user_message, response_message)

        # Display chat history
        st.write("### Chat History")
        for message in history:
            st.write(message)

# View chat history
def chat_history():
    if "username" not in st.session_state:
        st.error("You need to log in first!")
        return

    user_id = st.session_state.user_id
    rows = get_chat_history_from_db(user_id)

    if rows:
        st.write("### Your Chat History")
        for timestamp, message, response in rows:
            st.write(f"{timestamp} - User: {message}")
            st.write(f"{timestamp} - AI: {response}")
    else:
        st.write("No chat history available.")

# Logout function
def logout():
    if "username" in st.session_state:
        del st.session_state.username
        del st.session_state.user_id
        st.success("Logged out successfully!")

# Main function
def main():
    if "username" not in st.session_state:
        if login():
            chat()
    else:
        menu = ["Chat", "Chat History", "Logout"]
        choice = st.sidebar.selectbox("Select Option", menu)

        if choice == "Chat":
            chat()
        elif choice == "Chat History":
            chat_history()
        elif choice == "Logout":
            logout()

if __name__ == "__main__":
    main()
