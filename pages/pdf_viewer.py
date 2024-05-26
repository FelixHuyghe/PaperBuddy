import os
import time
import streamlit as st
import streamlit.components.v1 as components
from bokeh.models.widgets import Button
from bokeh.layouts import layout
from bokeh.models import CustomJS
from bokeh.plotting import curdoc
from streamlit_bokeh_events import streamlit_bokeh_events
from groq import Groq
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

from db import get_nn


client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

api_key = os.environ["MISTRAL_API_KEY"]
# model = "mistral-large-latest"
model = "mixtral-8x7b-32768"
# client = MistralClient(api_key=api_key)

USE_RAG = False

# bootstrap 4 collapse example
# components.iframe(src="http://localhost:8888/web/viewer.html", width=1000, height=1000)
# Define a JavaScript function to be executed on button click
st.set_page_config(
    page_title="PaperBuddy",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None,
)
col1, col2 = st.columns([3, 1.3])

system_prompt = "You are an assistant tasked with the job of making scientific papers more easy to read! \
    You're job is to give answers to the user's questions that are short and clear \
        If the user just sends in a `quote` from the paper, you should try and explain it in layman's terms. \
        Also, you will be provided with extra papers that are relevant to the user's query by a RAG.\
        Please find below the papers:"

with col1:
    js_code = """
    <script>
    async function sendDataToStreamlit() {
        const data = { message: "Hello from JavaScript!" };
        await fetch('/streamlit_endpoint', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        console.log('Data sent to Streamlit');
    };
    </script>
    <script>
        window.addEventListener('message', function(event) {
        // Ensure the message is coming from the expected origin
        // Replace '*' with the specific origin you expect the message from
        //if (event.origin !== 'http://your-iframe-origin.com') {
        //    return;
        //}
        
        // Handle the message received from the iframe
        console.log('Message received in parant woohoow:', event.data);
        parent.window.token = event.data;
        return;
        });
    </script>
    """

    # Create an HTML button and attach the JavaScript function to its onclick event
    html_button = """
    <iframe src="http://localhost:8888/web/viewer.html" style="border-radius: .45rem; position: fixed; top: 0; left: 0; width: 100%; height: 100%; border: none; z-index: 1000;">
    ></iframe>
    <style>
        .styled-div {
            align-items: center;
            background-clip: padding-box;
            background-color: #fa6400;
            border: 1px solid transparent;
            border-radius: .25rem;
            box-shadow: rgba(0, 0, 0, 0.02) 0 1px 3px 0;
            box-sizing: border-box;
            color: #fff;
            cursor: pointer;
            display: inline-flex;
            font-family: system-ui,-apple-system,system-ui,"Helvetica Neue",Helvetica,Arial,sans-serif;
            font-size: 16px;
            font-weight: 600;
            justify-content: center;
            line-height: 1.25;
            margin: 0;
            min-height: 3rem;
            padding: calc(.875rem - 1px) calc(1.5rem - 1px) 0 calc(1.5rem - 1px); /* Modified padding */
            position: relative;
            text-decoration: none;
            transition: all 250ms;
            user-select: none;
            -webkit-user-select: none;
            touch-action: manipulation;
            vertical-align: baseline;
            width: auto;
            }

            .styled-div:hover,
            .styled-div:focus {
            background-color: #fb8332;
            box-shadow: rgba(0, 0, 0, 0.1) 0 4px 12px;
            }

            .styled-div:hover {
            transform: translateY(-1px);
            }

            .styled-div:active {
            background-color: #c85000;
            box-shadow: rgba(0, 0, 0, .06) 0 2px 4px;
            transform: translateY(0);
            }
    </style>
    """
    # Display the JavaScript and HTML button in Streamlit
    st.components.v1.html(html_button + js_code, height=850, width=1050)


def receive_new_message(prompt):
    msg = {"role": "user", "content": prompt}
    if (
        len(st.session_state.messages) > 1
        and st.session_state.messages[-2]["content"] == msg["content"]
    ):
        pass
    else:
        st.session_state["messages"].append(msg)
        st.chat_message(msg["role"]).write(msg["content"])
        if USE_RAG:
            extra_papers = get_nn(prompt, 5)
            new_system_prompt = system_prompt + extra_papers
            if "full_text" in st.session_state:
                new_system_prompt += st.session_state["full_text"]
            st.session_state["messages"][0]["content"] = system_prompt + extra_papers
        response = client.chat.completions.create(
            model=model, messages=st.session_state["messages"]
        )
        msg = response.choices[0].message.content
        st.session_state["messages"].append({"role": "assistant", "content": msg})
        st.experimental_rerun()


with col2:
    with st.container(height=850):
        # st.markdown(
        #    "<h3 style='text-align: left; color: orange;'>Welcome to PaperBuddy!</h1>",
        #    unsafe_allow_html=True,
        # )
        # st.caption("🚀 A Streamlit chatbot")

        if "messages" not in st.session_state:
            new_system_prompt = system_prompt
            if "full_text" in st.session_state:
                new_system_prompt += st.session_state["full_text"]
            st.session_state["messages"] = [
                {
                    "role": "system",
                    "content": new_system_prompt,
                },
                {
                    "role": "assistant",
                    "content": "Welcome to PaperBuddy!  How can I help you?",
                },
            ]

        for msg in st.session_state.messages:
            if msg["role"] != "system":
                st.chat_message(msg["role"]).write(msg["content"])

        if prompt := st.chat_input():
            receive_new_message(prompt)
            # st.chat_message("assistant").write(msg)

        loc_button = Button(
            label="Explain selected text",
            width=420,
            # height=35,
            # align="center",
            # css_classes=["custom_button_bokeh"],
            button_type="warning",
        )
        layout = layout([[loc_button]])
        curdoc().add_root(layout)

        loc_button.js_on_event(
            "button_click",
            CustomJS(
                code="""
                var selected = window.parent.token;
                document.dispatchEvent(new CustomEvent("GET_LOCATION", {detail: {selected_text: selected}}));
            """
            ),
        )
        result = streamlit_bokeh_events(
            loc_button,
            events="GET_LOCATION",
            key="get_location",
            refresh_on_update=False,
            override_height=75,
            debounce_time=550,
        )

        if result:
            if "GET_LOCATION" in result:
                prompt = result.get("GET_LOCATION")["selected_text"]
                result = None
                receive_new_message(prompt)
