import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import  AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.types import Command


class ResponseGeneratorAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name='gpt-4o-mini-2024-07-18',
            temperature=0.7,
            api_key=os.environ['OPENAI_API_KEY'],
        )
        self.prompt = self._get_prompt()
        self.chain = self._get_chain()


    def _get_system_message(self):
        return (
            "You are a helpful shopping assistant for a retail company.\n"
            "\n"
            "You have access to data about the user's purchase history and preferences.\n"
            "Generate a helpful, friendly response to their query using the provided context.\n"
            "Make the response conversational and engaging, highlighting the most relevant information.\n"
            "If the context contains any numerical data, ensure it's presented clearly.\n"
            "Do not mention that you're using context data - just incorporate it naturally.\n"
            "The context data is sufficient to answer the query, so be CONFIDENT and DIRECT in your response.\n"
            "Avoid phrases like 'it looks like' or 'it seems' - state facts definitively.\n"
            "Important feature descriptions:\n"
            " - interaction_score: Type of interaction: 0 = ignore, 1 = click, 2 = purchase.\n"
            " - sales_channel_id: 1 = online, 2 = offline\n"
            " - price values are not in dollars, they are in units, not to reveal the real information\n"
            "Provide a rich, engaging response including all details from the context data.\n"
        )


    def _get_human_message(self):
        return (
            "Based on the following context, please answer the user query:\n"
            "\n"
            "User query: {user_query}\n"
            "\n"
            "Context data: {context}\n"
        )
    

    def _get_prompt(self):
        return ChatPromptTemplate.from_messages(
            [
                ("system", self._get_system_message()),
                MessagesPlaceholder(variable_name="messages"),
                ("human", self._get_human_message()),
            ]
        )
    
    def _get_chain(self):
        return self.prompt | self.llm
    

    def generate_response(self, state):
        response_content = self.chain.invoke({
            "user_query": state["user_query"],
            "context": state["context"],
            "messages": state["messages"],
        }).content

        ai_message = AIMessage(content=response_content)

        return Command(
            update={
                "messages": ai_message,
            },
            goto="END",
        )
