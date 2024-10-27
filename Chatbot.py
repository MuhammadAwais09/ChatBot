from dotenv import load_dotenv
import streamlit as st
from langchain.agents import AgentType, initialize_agent
from langchain_community.chat_models import ChatOpenAI
from typing import Dict, Any
from langchain.memory import ConversationBufferMemory
import os
from langchain.tools import Tool
from datetime import datetime
import pytz
import openai


load_dotenv()

class CustomMemory(ConversationBufferMemory):
    def _get_input_output(self, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> tuple:
        input_str = inputs.get("input", "")
        chat_history = inputs.get("chat_history", [])
        input_str = f"Human: {input_str}\nChat History: {chat_history}\n"

        output_str = outputs.get("result", "")
        
        # Ensure compatibility with structured responses
        if isinstance(output_str, dict):
            output_str = output_str.get('text', '')  # Extract 'text' field if response is structured
        elif isinstance(output_str, str):
            output_str = output_str  # If it's a plain string, use it directly
        else:
            output_str = ""  # Fallback for unexpected output types

        return input_str, output_str

# Set Streamlit page configuration
st.set_page_config(page_title="🧠MemoryBot🤖", layout="centered")

def calculate_date_time():
    # Define the Abu Dhabi time zone
    abudhabi_tz = pytz.timezone('Asia/Dubai')  # UAE time zone (UTC+4)
    
    # Get the current time in Abu Dhabi
    abudhabi_time = datetime.now(abudhabi_tz)
    
    # Format the date and time
    date = abudhabi_time.strftime("%Y-%m-%d")
    time = abudhabi_time.strftime("%H:%M")
    
    return date, time

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Initialize session states
if "generated" not in st.session_state:
    st.session_state["generated"] = []
if "past" not in st.session_state:
    st.session_state["past"] = []
if "input" not in st.session_state:
    st.session_state["input"] = ""
if "stored_session" not in st.session_state:
    st.session_state["stored_session"] = []

def get_text():
    """
    Get the user input text.
    Returns:
        (str): The text entered by the user
    """
    input_text = st.text_input(
        "You: ",
        st.session_state.get("user_input", ""),
        key="input",
        placeholder="Enter a command or query here...",
        label_visibility="hidden",
    )
    return input_text

def new_chat():
    """
    Clears session state and starts a new chat.
    """
    save = []
    for i in range(len(st.session_state["generated"]) - 1, -1, -1):
        save.append("User :" + st.session_state["past"][i])
        save.append("Bot:" + st.session_state["generated"][i])
    st.session_state["stored_session"].append(save)
    st.session_state["generated"] = []
    st.session_state["past"] = []
    st.session_state["user_input"] = ""

st.sidebar.image("./assets/logo.png")

st.title(" Bridge2e TestBot ")
st.markdown(
    """ 
        > :black[Made By - Bridge2e]
        """
)

# Ask the user to enter their OpenAI API key
API_O = os.getenv("OPENAI_API_KEY")
if API_O is None:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")
if True:
    MODEL = "gpt-4"  # Use the latest model available

    # Load the tools
    memory = CustomMemory()
    agent = initialize_agent(
        [],
        ChatOpenAI(temperature=0, model_name=MODEL, openai_api_key=API_O),
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True
    )

# Add a button to start a new chat
st.sidebar.button("New Chat", on_click=new_chat, type="primary")

# Get the user input
user_input = get_text()

def process_input(user_input):
    # Prepare the chat history for the agent
    chat_history = st.session_state.get("past", []) + st.session_state.get("generated", [])
    
    # Prepare the input for the agent
    inputs = {
        "input": user_input,
        "chat_history": chat_history
    }

    # Parse commands for specific functionalities
    if user_input.startswith("/summarize"):
        text_to_summarize = user_input.replace("/summarize", "").strip()
        return f"Summary: {agent.run({'input': f'Summarize this: {text_to_summarize}', 'chat_history': chat_history})}"
    
    elif user_input.startswith("/translate"):
        text_to_translate = user_input.replace("/translate", "").strip()
        return f"Translation: {agent.run({'input': f'Translate this: {text_to_translate}', 'chat_history': chat_history})}"
    
    elif user_input.startswith("/paraphrase"):
        text_to_paraphrase = user_input.replace("/paraphrase", "").strip()
        return f"Paraphrase: {agent.run({'input': f'Rewrite this: {text_to_paraphrase}', 'chat_history': chat_history})}"
    
    elif user_input.startswith("/calculate"):
        calculation_query = user_input.replace("/calculate", "").strip()
        return f"Result: {agent.run({'input': f'Calculate this: {calculation_query}', 'chat_history': chat_history})}"
    
    elif user_input.startswith("/code"):
        code_query = user_input.replace("/code", "").strip()
        return f"Code Solution: {agent.run({'input': f'Generate or debug code: {code_query}', 'chat_history': chat_history})}"
    
    elif user_input.startswith("/classify"):
        text_to_classify = user_input.replace("/classify", "").strip()
        return f"Classification: {agent.run({'input': f'Classify the sentiment or content: {text_to_classify}', 'chat_history': chat_history})}"
    
    elif user_input.startswith("/story"):
        prompt_for_story = user_input.replace("/story", "").strip()
        return f"Story: {agent.run({'input': f'Generate a story based on: {prompt_for_story}', 'chat_history': chat_history})}"
    
    elif user_input.startswith("/time"):
        date, time = calculate_date_time()
        return f"Today's Date: {date}, Current Time: {time}"

    else:
        return agent.run({'input': user_input, 'chat_history': chat_history})

# Generate the output using the agent and the user input, and add the input/output to the session
if user_input:
    with st.spinner("Processing..."):
        output = process_input(user_input)
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output)

download_str = []
# Display the conversation history using an expander, and allow the user to download it
with st.expander("Conversation", expanded=True):
    for i in range(len(st.session_state["generated"]) - 1, -1, -1):
        st.info(st.session_state["past"][i], icon="🧐")
        st.success(st.session_state["generated"][i], icon="🤖")
        download_str.append(st.session_state["past"][i])
        download_str.append(st.session_state["generated"][i])

for i, sublist in enumerate(st.session_state.stored_session):
    with st.sidebar.expander(label=f"Conversation-Session:{i}"):
        st.write(sublist)

with st.sidebar:
    st.markdown("---")
