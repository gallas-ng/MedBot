import streamlit as st
import asyncio
import pandas as pd
import json

from bot import chatbot
from google.cloud import firestore
from firebase_admin import auth
from google.oauth2 import service_account
from google.cloud.firestore import FieldFilter

key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="medbot-480e8")

def app():
    st.title('Bienvenue sur :green[MedBOT] :female-doctor:, votre assistant de santé virtuel')

    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'useremail' not in st.session_state:
        st.session_state.useremail = ''


    def login():
        try:
            user = auth.get_user_by_email(email)
            st.success('Connection réussie')
            st.session_state.username = user.uid
            st.session_state.useremail = user.email

            st.session_state.signedout = True
            st.session_state.signout = True

        except:
            st.warning('La connection a echouée')

    def logout():
        st.session_state.signedout = False
        st.session_state.signout = False
        st.session_state.username = ''

    if 'signedout' not in st.session_state:
        st.session_state.signedout = False
    if 'signout' not in st.session_state:
        st.session_state.signout = False

    if not st.session_state.signedout:
        choice = st.selectbox('Connection / Inscription', ['Connection', 'Inscription'])


        if choice == 'Connection':
            email = st.text_input("Email")
            password = st.text_input("Mot de passe", type='password')

            st.button('Connection', on_click=login)
            
        else:
            email = st.text_input("Email")
            username = st.text_input("Nom Complet")
            password = st.text_input("Mot de passe", type='password')

            if st.button('Inscription'):
                if email == '':
                    st.warning('Email non autorisé')
                else:
                    user = auth.create_user(email = email, password = password, uid = username)

                    st.success('Compte créé avec succés')
                    st.markdown('Veuillez renseigner votre email et mot de passe pour vous connecter !')
                    st.balloons()

    if st.session_state.signout:
        st.button('Deconnexion', on_click=logout)
        email = st.session_state.useremail
       
        if email == "admin@medbot.com":
            st.write('#### Session Administrateur :technologist: ')
            df = pd.read_csv('mayo_clinic.csv')
            st.write(df)
            st.divider()


            st.write('Listes des utilisateurs')
            list_users = auth.list_users()
            if st.button('Voir la liste'):
                data = []
                with st.expander('---'):
                    for user in list_users.users:
                        data.append([user.uid, user.email])
                    # Afficher les données dans un tableau avec Streamlit
                    st.table(data)           
            st.divider()


            st.write('Liste des Feedbacks')
            fb = db.collection('feedbacks')

            for i,feed in enumerate(fb.stream()):
                msg = feed.to_dict()
                with st.expander(f"Retour de {msg['user']}"):
                    st.text(f"Message : {msg['message']}")
                    st.text_input('Reponse', key= i)
                    st.button('Envoyer', on_click= '', key= (f"btn' {i}"))
            st.divider()

            st.write('Historique des conversations')

            for user in list_users.users:
                chats = get_user_chats(str(user.email))
                with st.expander(f"Historique de {user.uid}"):
                    for i,chat in enumerate(chats):
                        st.text(f"Requete {i}: {chat['request']}")
                        st.text(f"Reponse {i}: {chat['response']}")
                        
        else:
            asyncio.run(chatbot(user_name= email))


def send_feedback(message, user):
     """
     Cette methode permet aux clients d'envoyer des retours sur l'experience vecu de l'application
     """
     doc_ref = db.collection("feedbacks").document()
     doc_ref.set({
        "message": message,
        "user": user 
            })

def get_user_chats(email):
    chats_ref = db.collection('chat_history').where(filter=FieldFilter("user", "==", email))
    chat_history = []
    for chat in chats_ref.stream():
        chat_history.append(chat.to_dict())
    return chat_history
