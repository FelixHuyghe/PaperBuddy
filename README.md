# PaperBuddy
PaperBuddy was a project I created in under 24 hours during the June 2024 Mistral LLM Hackathon in Paris.


It aims to help students and researchers when reading scientific papers.
Development to launch it on HuggingFace spaces is still in progress, (right now the pdf reader itself is hosted on a local webserver), but this code should give an idea about the project.


The user uploads a document, receives an introduction to the paper, and can then click through to 'chat' with the paper.


This chat interface is augmented with a RAG that is connected to a database containing over 40k papers related to NLP! 


Stay tuned for the HF release or DM me to get access to the database where I hosted the embeddings.

## Stack
LLM: Mistral 7b through the Groq API

Fronted: Streamlit

RAG: Postgres database with pgvector for ANN search

Embeddings: HF Sentence embeddings


<img width="754" alt="image" src="https://github.com/FelixHuyghe/PaperBuddy/assets/46262936/2a8c4a83-1096-468c-81de-24bcd145e852">
<img width="1601" alt="original" src="https://github.com/FelixHuyghe/PaperBuddy/assets/46262936/85ded31d-c4e5-412c-a631-c54d750bfad6">
