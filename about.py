import streamlit as st
from PIL import Image

image = Image.open('Med.png')

def about():
    st.image(image= image,  width= 300)
    st.title("A propos de :green[Medbot] 🤖")
    st.write("#### :green[Medbot] est un chatbot d'IA doté d'une mémoire conversationnelle, conçu pour permettre aux utilisateurs d'avoir accés à des informations médicales et de soins de santé primaires. 📄")
    st.write("#### Il utilise de grands modèles de langage pour fournir aux utilisateurs des interactions en langage naturel transparentes et adaptées au contexte afin de mieux comprendre leurs requetes et extraire les entités pertinentes 🌐")
    st.write("#### Propulsé par [Langchain](https://github.com/hwchase17/langchain), [OpenAI](https://platform.openai.com/docs/models/gpt-3-5), [Streamlit](https://github.com/streamlit/streamlit), [Mayo Clinic](https://mayoclinic.org) ⚡")
    st.write("#####  :grey[Gallas]  ")
