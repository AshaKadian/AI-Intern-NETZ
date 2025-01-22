
import os
import streamlit as st
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate

# Initialize LangChain components
MODEL = "llama3.2:3b"
model = Ollama(model=MODEL)  # Load LLM
embeddings = OllamaEmbeddings(model=MODEL)  # Load embeddings

# Path for Chroma vector store
vectorstore_path = r"C:\Users\Nisha kadian\Documents\pyhton Netz\chroma_db"
vectorstore = Chroma(persist_directory=vectorstore_path, embedding_function=embeddings)
retriever = vectorstore.as_retriever()  # Create retriever from vectorstore

# Prompt template
template = """
Answer the question based on the context below. If you cannot 
answer the question, reply "I do not know".

Context: {context}

Question: {question}
"""
prompt = PromptTemplate.from_template(template)

# In-memory user database
users_db = {"user1": "password1", "user2": "password2"}

# Initialize session state for chat histories
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}  # Stores chat history per username

# Streamlit app layout
st.set_page_config(page_title="RAG Chatbot", layout="centered")

# Authentication process
def authenticate_user(username: str, password: str) -> bool:
    return users_db.get(username) == password

# Streamlit UI for login
def login():
    st.title("Login to RAG-based Chatbot")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if authenticate_user(username, password):
            st.session_state.username = username  # Store username in session state
            if username not in st.session_state.chat_histories:
                st.session_state.chat_histories[username] = []  # Initialize chat history for the user
            st.success("Login successful!")
            return True
        else:
            st.error("Invalid credentials!")
            return False
    return False

# Chat process
def chat():
    if "username" not in st.session_state:
        st.error("You need to log in first!")
        return

    username = st.session_state.username

    st.title(f"Hello, {username}!")
    user_message = st.text_input("Ask your question:")
    
    if st.button("Send") and user_message:
        history = st.session_state.chat_histories.get(username, [])
        
        # Retrieve relevant documents using the retriever
        context_docs = retriever.get_relevant_documents(user_message)
        if not context_docs:
            st.write("I do not know.")
            return
        
        # Combine the context into a single string
        context = " ".join(doc.page_content for doc in context_docs)
        
        # Format the prompt with context and user query
        query_with_context = prompt.format(context=context, question=user_message)
        
        # Generate response using the model
        response_message = model(query_with_context)
        
        # Update chat history for the user
        history.append(f"User: {user_message}")
        history.append(f"AI: {response_message}")
        if len(history) > 10:  # Maintain only the last 10 messages
            history = history[-10:]
        
        st.session_state.chat_histories[username] = history  # Update chat history

        # Show chat history
        st.write("### Chat History")
        for message in history:
            st.write(message)

        st.write(f"AI: {response_message}")

# Chat History retrieval
def chat_history():
    if "username" not in st.session_state:
        st.error("You need to log in first!")
        return

    username = st.session_state.username
    history = st.session_state.chat_histories.get(username, [])
    
    if history:
        st.write("### Your Chat History")
        for message in history:
            st.write(message)
    else:
        st.write("No chat history available.")

# Logout process
def logout():
    if "username" in st.session_state:
        del st.session_state.username  # Clear username
        st.success("Logged out successfully!")

# Streamlit app flow
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
