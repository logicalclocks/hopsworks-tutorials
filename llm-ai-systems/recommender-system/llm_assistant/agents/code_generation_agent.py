import os
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.types import Command
import streamlit as st
import logging

class CodeGenerationAgent:
    def __init__(self, data):
        self.data = data
        self.available_features = self.data.columns
        self._feature_types = {col: str(self.data[col].dtype) for col in self.data.columns}
        self.formatted_feature_types = self.escape_curly_braces(str(self._feature_types))

        self._data_sample_json = self.data.head(3).to_dict(orient="records")
        self.formatted_data_sample_json = self.escape_curly_braces(self._data_sample_json)

        self.llm = ChatOpenAI(
            model_name='gpt-4o-2024-11-20',
            temperature=0,
            api_key=os.environ['OPENAI_API_KEY'],
        )
        self.prompt = self._get_prompt()
        self.chain = self._get_chain()


    def escape_curly_braces(self, text):
        """Escape curly braces in a string to prevent LangChain from treating them as variables."""
        if isinstance(text, str):
            return text.replace("{", "{{").replace("}", "}}")
        else:
            return str(text).replace("{", "{{").replace("}", "}}")
        

    def _get_system_message(self):
        return (
            "You are an expert Python data analyst specializing in e-commerce data.\n"
            "\n"
            "Your task is to generate Python code to answer a user's question about their purchase history.\n"
            "\n"
            "The code should:\n"
            "1. Use pandas to analyze the data\n"
            "2. Be efficient and clean\n"
            "3. Return a dictionary with the relevant results\n"
            "4. Include error handling\n"
            "5. Work with the provided dataframes without modification\n"
            "\n"
            "Available features:\n"
            f"{self.available_features}\n"
            "Feature types:\n"
            f"{self.formatted_feature_types}\n"
            "Sample data:\n"
            f"{self.formatted_data_sample_json}\n"
            "Important feature descriptions:\n"
            " - interaction_score: Type of interaction: 0 = ignore, 1 = click, 2 = purchase.\n"
            " - sales_channel_id: 1 = online, 2 = offline.\n"
            " - t_dat is present in milliseconds format.\n"
            " - For date comparisons, NEVER compare exact millisecond timestamps. Instead, convert timestamps to dates and compare at the day level.\n"
            " - When filtering for 'today', convert both the current time and the t_dat column to date objects (year, month, day) before comparison.\n"
            "\n"
            "Only generate Python code - no explanations.\n"
            "The code should define a function called `run_analysis` that takes the dataframe and returns a dictionary with the results.\n"
            "Always include proper date handling that compares dates at the day level, not millisecond level.\n"
        ) 


    def _get_human_message(self):
        return (
        "Generate Python code to answer this query: '{user_query}'\n"
        "Previous code errors (if present): '{error_message}'\n"
        "Previous code (if present): '{previous_code}'\n"
    )


    def _get_prompt(self):
        return ChatPromptTemplate.from_messages(
            [
                ("system", self._get_system_message()),
                ("human", self._get_human_message()),
            ]
        )


    def _get_chain(self):
        return self.prompt | self.llm
    

    def generate_code(self, user_query, error_message=None, previous_code=None):

        response = self.chain.invoke(
            {
                "user_query": user_query,
                "error_message": error_message,
                "previous_code": previous_code,
            }
        )

        code = response.content
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].split("```")[0].strip()

        return code
    

    def run_code(self, code):
        try:
            # Create namespace for execution
            namespace = {"pd": pd, "data": self.data}
            
            # Execute the code in the namespace
            exec(code, namespace, namespace)
            
            # Check if run_analysis was defined
            if "run_analysis" in namespace and callable(namespace["run_analysis"]):
                # Call the function and get its result
                function_result = namespace["run_analysis"](self.data)
                
                # Verify function_result is a dictionary
                if isinstance(function_result, dict):
                    # Create our final result
                    result = {
                        "context": function_result,
                        "success": True,
                        "code": code
                    }
                    return result
                else:
                    return {
                        "error": "run_analysis didn't return a dictionary", 
                        "success": False, 
                        "code": code
                    }
            else:
                return {
                    "error": "Generated code did not define a run_analysis function", 
                    "success": False, 
                    "code": code
                }
        except Exception as e:
            return {
                "error": f"Error executing code: {str(e)}", 
                "success": False, 
                "code": code
            }
        

    def generate_context(self, state):
        with st.spinner("🔮 Generating Context..."):
            code = self.generate_code(state["user_query"], state["error_message"], state["code"])

            result = self.run_code(code)

            if "error" in result.keys() and state["iterations"] < state["max_iterations"]:
                return Command(
                    update={
                        "error_message": result["error"],
                        "iterations": state["iterations"] + 1,
                        "code": code,
                    },
                    goto="generate_context",
                )

            return Command(
                update={
                    "context": str(result["context"]),
                    "iterations": state["iterations"] + 1,
                    "code": code,
                },
                goto="evaluate_context",
            )
