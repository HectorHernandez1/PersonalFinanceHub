from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import os
from typing import List

class AIHelper:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            try:
                self.llm = ChatOpenAI(model="gpt-4.1-nano", openai_api_key=self.openai_api_key, temperature=0)
            except ImportError:
                self.llm = None
                print("langchain_openai package not installed. OpenAI features will be unavailable.")
        else:
            self.llm = None
            print("OPENAI_API_KEY environment variable not set. OpenAI features will be unavailable.")

    def guess_category_openai(self, merchant_name: str, categories: List[str]) -> str:
        if not self.llm or not categories:
            return "Other"
        categories_str = ", ".join(categories)
        prompt = (
            f"Classify the following merchant into one of these spending categories: {categories_str}.\n"
            f"Merchant: {merchant_name}\n"
            f"Category:"
        )
        try:
            messages = [
                SystemMessage(content="You are a helpful assistant that classifies merchants into spending categories."),
                HumanMessage(content=prompt)
            ]
            response = self.llm.invoke(messages)
            category = response.content.strip()
            if category not in categories:
                return "Other"
            return category
        except Exception as e:
            print(f"AI category guess (OpenAI) failed for merchant '{merchant_name}': {e}")
            return "Other"
