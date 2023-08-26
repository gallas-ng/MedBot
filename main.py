import streamlit as st
import firebase_admin
import json

from about import about
from account import app, send_feedback
from firebase_admin import credentials
from firebase_admin import auth
from st_on_hover_tabs import on_hover_tabs
from PIL import Image

st.set_page_config( page_icon="💬", page_title="ChatBot-Medical")
image = Image.open('Med.png')
st.markdown('<style>' + open('style.css').read() + '</style>', unsafe_allow_html=True)

with st.sidebar:
    st.sidebar.image(image)
    tabs = on_hover_tabs(tabName=['Votre Bot', 'FeedBack', 'A propos'], 
                         iconName=['assistant', 'feedback', 'star'],
                         default_choice=0,
                         styles = {'navtab': {'background-color':'#f1eded',
                                                  'color': '#818181',
                                                  'font-size': '12px',
                                                  'font-family' : 'sans-serif',
                                                  'transition': '.3s',
                                                  'white-space': 'nowrap',
                                                  'text-transform': 'uppercase'},
                                    'tab' :{'background-color':'#fff'},
                                       'tabOptionsStyle': {':hover :hover': {'color': 'green',
                                                            'cursor': 'pointer'}},
                                       'iconStyle':{'position':'fixed',
                                                    'left':'7.5px',
                                                    'text-align': 'left',
                                                    'color' : '#55B43B',
                                       'tabStyle' : {'list-style-type': 'none',
                                                     'margin-bottom': '40px',
                                                     'padding-left': '30px'},'background-color': '#f1eded'}})

if tabs == 'Votre Bot':
    app()

elif tabs == 'FeedBack':
    st.title("Partagez votre experience avec l'equipe :green[MedBot] :email:")
    if st.session_state.signout:
        message = st.text_area('Votre Message')
        email = st.session_state.useremail
        if st.button('Envoyer'):
            send_feedback(message= message, user= email)
            st.success('Votre message a été envoyé avec succés.')
            message = ""
    else:
        st.write(' :smile: Veuillez vous identifier pour envoyer votre feedback')

elif tabs == 'A propos':
    about()


if not firebase_admin._apps:
    key_dict = json.loads(st.secrets['textkey'])
    cred = credentials.Certificate(key_dict)
    firebase_admin.initialize_app(cred)