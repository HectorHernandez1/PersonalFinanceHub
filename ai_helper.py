from openai import OpenAI
import os
from typing import List

class AIHelper:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            try:
                self.openai = OpenAI(api_key=self.openai_api_key)
            except ImportError:
                self.openai = None
                print("openai package not installed. OpenAI features will be unavailable.")
        else:
            self.openai = None
            print("OPENAI_API_KEY environment variable not set. OpenAI features will be unavailable.")

    def guess_category_openai(self, merchant_name: str, categories: List[str]) -> str:
        if not self.openai or not categories:
            return "Other"
        categories_str = ", ".join(categories)
        prompt = (
            f"Classify the following merchant into one of these spending categories: {categories_str}.\n"
            f"Merchant: {merchant_name}\n"
            f"Category:"
        )
        try:
            response = self.openai.chat.completions.create(
                #model="gpt-3.5-turbo",
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that classifies merchants into spending categories."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=20,
                temperature=0
            )
            category = response.choices[0].message.content.strip()
            if category not in categories:
                return "Other"
            return category
        except Exception as e:
            print(f"AI category guess (OpenAI) failed for merchant '{merchant_name}': {e}")
            return "Other"
