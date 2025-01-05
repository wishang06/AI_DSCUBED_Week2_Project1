import os
import streamlit as st
from dotenv import load_dotenv
from rich.console import Console
from src.core.engine import BasicChatContextEngine
from src.clients.openai_client import ClientOpenAI
from src.clients.anthropic_client import ClientAnthropic

class ModelSelector:
    PROVIDERS = {
        'gemini': 'Gemini',
        'openai': 'OpenAI',
        'openrouter': 'OpenRouter',
        'anthropic': 'Anthropic'
    }
    
    MODELS = {
        'gemini': [
            'google/gemini-1.5-pro-002',
            'google/gemini-1.5-flash-002',
        ],
        'openai': [
            'gpt-4o',
            'gpt-4o-mini'
        ],
        'openrouter': [
            'meta-llama/llama-3.3-70b-instruct',
            'qwen/qwen-2.5-72b-instruct',
            'amazon/nova-pro-v1',
        ],
        'anthropic': [
            'claude-3-5-sonnet-latest',
            'claude-3-5-haiku-latest'
        ]
    }

def create_client(provider: str):
    if provider == 'gemini':
        projectid = os.getenv("GOOGLE_CLOUD_PROJECT", "articulate-case-443521-c2")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "australia-southeast1")
        return ClientOpenAI.create_gemini(projectid, location)
    
    elif provider == 'openai':
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("Error: OPENAI_API_KEY environment variable not set")
            return None
        return ClientOpenAI.create_openai(api_key)
    
    elif provider == 'openrouter':
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            st.error("Error: OPENROUTER_API_KEY environment variable not set")
            return None
        return ClientOpenAI.create_openrouter(api_key)
    
    elif provider == 'anthropic':
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            st.error("Error: ANTHROPIC_API_KEY environment variable not set")
            return None
        return ClientAnthropic(api_key)
    return None

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "engine" not in st.session_state:
        st.session_state.engine = None

def display_chat_history():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def main():
    load_dotenv()
    initialize_session_state()
    
    st.title("🤖 LLMgine Chat")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")
        provider = st.selectbox(
            "Select Provider",
            options=list(ModelSelector.PROVIDERS.keys()),
            format_func=lambda x: ModelSelector.PROVIDERS[x]
        )
        
        model = st.selectbox(
            "Select Model",
            options=ModelSelector.MODELS[provider] if provider else []
        )
        
        system_prompt = st.text_area(
            "System Prompt",
            value="You are a helpful assistant.",
            help="Set the behavior of the AI assistant"
        )
        
        if st.button("Initialize Chat"):
            client = create_client(provider)
            if client:
                st.session_state.engine = BasicChatContextEngine(
                    client=client,
                    model_name=model,
                    system_prompt=system_prompt
                )
                st.session_state.messages = []
                st.rerun()

    # Main chat interface
    if st.session_state.engine:
        display_chat_history()
        
        if prompt := st.chat_input("What's on your mind?"):
            st.chat_message("user").markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = st.session_state.engine.execute(prompt)
                    st.markdown(response.content)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response.content}
                    )
                    
                    # Display token usage
                    st.caption(
                        f"Tokens: {response.tokens_input} (input) + "
                        f"{response.tokens_output} (output) = "
                        f"{response.tokens_input + response.tokens_output} total"
                    )
    else:
        st.info("Please configure and initialize the chat in the sidebar.")

if __name__ == "__main__":
    main()