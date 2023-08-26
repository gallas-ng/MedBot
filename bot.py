import os
import pickle
import streamlit as st
import tempfile
import asyncio
import json

from google.cloud import firestore
from streamlit_chat import message
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores import FAISS
from langchain.prompts.prompt import PromptTemplate
from google.oauth2 import service_account

key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="medbot-480e8")


os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
async def chatbot(user_name):
    try :
        async def storeDocEmbeds():
                    
                    # Write the uploaded file to a temporary file
                    with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tmp_file:
                        with open('mayo_clinic.csv', 'rb') as f:
                            contents = f.read()
                        tmp_file.write(contents)
                        tmp_file_path = tmp_file.name

                    # Load the data from the CSV file using Langchain
                    loader = CSVLoader(file_path=tmp_file_path, encoding="utf-8")
                    data = loader.load()

                    embeddings = OpenAIEmbeddings()
                    
                    vectors = FAISS.from_documents(data, embeddings)
                    os.remove(tmp_file_path)

                    with open('mayo_clinic' + ".pkl", "wb") as f:
                        pickle.dump(vectors, f)
                    
        async def getDocEmbeds():
                    
                    if not os.path.isfile('mayo_clinic' + ".pkl"):
                        # If not, store the vectors using the storeDocEmbeds function
                        # await storeDocEmbeds()
                        print('No Docs found !!!')
                    
                    with open('mayo_clinic' + ".pkl", "rb") as f:
                        #global vectors
                        vectors = pickle.load(f)
                        
                    return vectors

        async def conversational_chat(query):
                    
                    # Use the Langchain ConversationalRetrievalChain to generate a response to the user's query
                    result = chain({"question": query, "chat_history": st.session_state['history']})
                    
                    # Add the user's query and the chatbot's response to the chat history
                    st.session_state['history'].append((query, result["answer"]))
                    
                    # You can print the chat history for debugging :
                    #print("Log: ")
                    #print(st.session_state['history'])
                    
                    return result["answer"]
        def save_chat(request, response, user):

            doc_ref = db.collection("chat_history").document()
            doc_ref.set({
                "request": request,
                "response": response,
                "user" : user
            })
        
        with st.sidebar.expander(" 🛠️ ", expanded=False):

            # Add a button to reset the chat history
            if st.button("Réinitialiser le chat"):
                st.session_state['reset_chat'] = True

            # Allow the user to select a chatbot model to use
            #MODEL = st.selectbox(label='Model', options=['gpt-3.5-turbo','gpt-4'],)
            MODEL = 'gpt-3.5-turbo'

        if 'history' not in st.session_state:
            st.session_state['history'] = []

        if 'ready' not in st.session_state:
            st.session_state['ready'] = False

        if 'reset_chat' not in st.session_state:
            st.session_state['reset_chat'] = False



        # Display a spinner while processing the file
        with st.spinner("Un instant..."):
            # Generate embeddings vectors for the file
            vectors = await getDocEmbeds()

            _template = """You are a helpful Healthcare assistant. Given the following conversation and a follow-up question, rephrase the follow-up question to be a stand-alone question.
            You can assume that the question is about the information in CSV files. Don't try to make up an answer.
            Your answers should be short,friendly, in the same language.
            Chat History:
            {chat_history}
            Follow-up entry: {question}
            Standalone question:"""
            CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

            qa_template = """"You are an AI conversational helpful Healthcare assistant to answer therapeutic questions based on information from a csv file.
            You are given data from a csv file and a question, you must help the user find the information they need. If they don't give enough informations about their symptoms, ask to tell more about. 
            Only give responses for information you know about. Don't try to make up an answer.
            Your answers should be short,friendly, in the same language.
            question: {question}
            =========
            {context}
            =======
            """
            QA_PROMPT = PromptTemplate(template=qa_template, input_variables=["question", "context"])

            # old_chain = ConversationalRetrievalChain.from_llm(llm = ChatOpenAI(temperature=0.0,model_name=MODEL),
            #          condense_question_prompt=CONDENSE_QUESTION_PROMPT,qa_prompt=QA_PROMPT,retriever=vectors.as_retriever())
            # chain = ConversationalRetrievalChain.from_llm(llm = ChatOpenAI(temperature=0.0,model_name=MODEL),
            #   condense_question_prompt=CONDENSE_QUESTION_PROMPT,retriever=vectors.as_retriever())
            chain = ConversationalRetrievalChain.from_llm(llm= ChatOpenAI(temperature=0.0,model_name=MODEL),
            retriever=vectors.as_retriever(), verbose=True, return_source_documents=False, max_tokens_limit=4097, combine_docs_chain_kwargs={'prompt':QA_PROMPT})

            # Set the "ready" flag to True now that the chatbot is ready to chat
            st.session_state['ready'] = True

        if st.session_state['ready']:

            # If the chat history has not yet been initialized, initialize it now
            if 'generated' not in st.session_state:
                st.session_state['generated'] = ["Hello "+st.session_state.username+" ! Bienvenue sur votre nouvel Assistant Medical 🤗"]

            if 'past' not in st.session_state:
                st.session_state['past'] = ["Hey ! 👋"]

            #container for displaying the chat history
            response_container = st.container()

            #container for the user's text input
            container = st.container()

            with container:

                # Create a form for the user to enter their query
                with st.form(key='my_form', clear_on_submit=True):

                    user_input = st.text_input("Entrez Votre Question", placeholder="Parlons Santé ", key='input')
                    submit_button = st.form_submit_button(label='Envoyer')

                    # If the "reset_chat" flag has been set, reset the chat history and generated messages
                    if st.session_state['reset_chat']:
                    
                        st.session_state['history'] = []
                        st.session_state['past'] = ["Hey ! 👋"]
                        st.session_state['generated'] = ["Welcome "+st.session_state.username+" ! Bienvenue sur votre nouvel Assistant Medical 🤗"]
                        response_container.empty()
                        st.session_state['reset_chat'] = False

                if submit_button and user_input:

                    # Generate a response using the Langchain ConversationalRetrievalChain
                    output = await conversational_chat(user_input)

                    # Add the user's input and the chatbot's output to the chat history
                    st.session_state['past'].append(user_input)
                    st.session_state['generated'].append(output)
                    save_chat(request= user_input, response= output, user = user_name)


            if st.session_state['generated']:

                # Display the chat history
                with response_container:

                    for i in range(len(st.session_state['generated'])):
                        message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="avataaars", seed="Scooter")
                        message(st.session_state["generated"][i], key=str(i), avatar_style="bottts", seed="Kitty")

    except Exception as e:
        st.error(f"Error: {str(e)}")
