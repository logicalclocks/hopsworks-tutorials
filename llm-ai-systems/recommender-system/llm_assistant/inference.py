import os
import streamlit as st
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from llm_assistant.graph import GraphState, build_graph


def get_context_data(project, customer_id):
    fs = project.get_feature_store() 

    feature_view = fs.get_feature_view(
        name="llm_assistant_context",
        version=1,
    )

    data = feature_view.query.read()

    data_filtered = data[data["customer_id"] == customer_id]

    return data_filtered


def get_llm_assistant_graph(project, customer_id):
    # Retrieve context data
    data = get_context_data(project, customer_id)
    # Build graph
    graph = build_graph(data)
    return graph


def handle_llm_assistant_page(project, customer_id):
    """Handle LLM Assistant page with chat interface"""
    st.subheader("💬 LLM Fashion Assistant")
    
    # Check for API key
    if 'OPENAI_API_KEY' not in os.environ:
        st.warning("Please provide your OpenAI API Key in the Interaction Dashboard")
        return
        
    # Initialize ALL session state variables if they don't exist
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "llm_graph" not in st.session_state:
        st.session_state.llm_graph = None
        
    if "last_refresh_customer" not in st.session_state:
        st.session_state.last_refresh_customer = None
    
    # Add a refresh button to the sidebar
    with st.sidebar:
        st.divider()
        st.subheader("🤖 Assistant Controls")
        refresh_clicked = st.button(
            "🔄 Refresh Assistant Data", 
            help="Update the assistant with your latest interactions data",
            type="primary" if st.session_state.llm_graph is None else "secondary",
        )

        # Add example questions section
        st.divider()
        st.subheader("📝 Example Questions")
        example_questions = [
            "What items I clicked on recently?",
            "Describe the last three items I bought.",
            "Can you describe my last interactions data?",
            "What interactions I did today?",
            "Provide my purchase history",
            "What's my total spending for all time?",
            "Do I prefer online or offline shopping?",
            "What colors do I buy most often?",
        ]
        
        # Display questions as a markdown bullet list
        questions_md = "\n".join([f"* {question}" for question in example_questions])
        st.markdown(questions_md)
    
    # Initialize graph if it doesn't exist or if refresh button was clicked
    if st.session_state.llm_graph is None or refresh_clicked:
        with st.spinner("Loading assistant with latest data..."):
            st.session_state.llm_graph = get_llm_assistant_graph(project, customer_id)
            st.session_state.last_refresh_customer = customer_id
        st.success("✅ Assistant ready with your latest data!")
    
    # If customer changed, we also need to refresh
    elif st.session_state.last_refresh_customer != customer_id:
        with st.spinner(f"Switching to customer {customer_id[:8]}..."):
            st.session_state.llm_graph = get_llm_assistant_graph(project, customer_id)
            st.session_state.last_refresh_customer = customer_id
        st.success("✅ Assistant ready with new customer data!")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about your fashion data, interactions, or recommendations..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process with LLM Assistant using the already built graph
        with st.chat_message("assistant"):
            with st.spinner("🧠 Thinking..."):
                try:
                    # Set up the state for this query
                    user_query = prompt
                    state = GraphState(
                        messages=[HumanMessage(content=user_query)],
                        user_query=user_query,
                        customer_id=customer_id,
                        context=None,
                        context_quality="unknown",
                        iterations=0,
                        max_iterations=3,
                        error_message=None,
                        code=None,
                    )
                    
                    # Run the cached graph with the new state
                    config = RunnableConfig(recursion_limit=25)
                    final_state = st.session_state.llm_graph.invoke(state, config=config)
                    
                    # Extract response from final state
                    try:
                        # Handle different possible structures of final_state
                        if isinstance(final_state, dict):
                            if "messages" in final_state:
                                messages = final_state["messages"]
                                if isinstance(messages, list) and messages:
                                    response = messages[-1].content
                                else:
                                    response = messages.content if hasattr(messages, "content") else str(messages)
                            else:
                                response = "I couldn't generate a response from the state dictionary."
                        else:
                            # Try to access as an object
                            messages = getattr(final_state, "messages", None)
                            if messages and isinstance(messages, list):
                                response = messages[-1].content
                            elif messages:
                                response = messages.content if hasattr(messages, "content") else str(messages)
                            else:
                                response = "I couldn't generate a response from the state object."
                    except Exception as parsing_error:
                        response = f"Processed your request but had trouble formatting the response: {str(parsing_error)}"
                    
                    st.markdown(response)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Error processing your request: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})