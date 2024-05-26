import os
from groq import Groq
import streamlit as st
from PyPDF2 import PdfReader

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.write("# Welcome to PaperBuddy! 👋")

uploaded_file = st.file_uploader("Choose the paper you want to analyze!", type=["pdf"])
if uploaded_file:
    # Advanced security XD files not stored for long
    with open("../compressed.tracemonkey-pldi-09.pdf", "wb") as f:
        f.write(uploaded_file.getvalue())
    st.success("File saved successfully!")

    # To read the file as a pdf
    pdf_reader = PdfReader(uploaded_file)
    number_of_pages = len(pdf_reader.pages)

    st.write(f"Number of pages: {number_of_pages}")

    paper_text = ""
    for page in range(number_of_pages):
        page_text = pdf_reader.pages[page].extract_text()
        paper_text += page_text

    st.session_state["full_text"] = paper_text
    # Prepare a summary or key information to query Groq
    context_summary = paper_text[:500]

    if st.button("Give me an introduction to the paper"):
        # st.write("Summary of the Paper:")
        # st.text(context_summary)
        # print("Summary of the Paper:")
        print(context_summary)

        # Example Groq Request to get background information
        query = f"Provide some background information about the following topic: {context_summary}"

        client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
        )
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": query,
                }
            ],
            model="mixtral-8x7b-32768",
        )

        response_content = chat_completion.choices[0].message.content
        st.write("Background Information from Mistral:")
        st.write(response_content)
        print("Background Information from Mistral:")
        print(response_content)

    # except Exception as e:
    #   st.error(f"An error occurred: {e}")
    #  print(f"An error occurred: {e}")

    if st.button("Dive in!"):
        st.switch_page("pages/pdf_viewer.py")
