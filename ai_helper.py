from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import os
import pandas as pd
from typing import List

class AIHelper:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            try:
                # gpt-4.1-nano
                self.llm = ChatOpenAI(model="gpt-5-nano", openai_api_key=self.openai_api_key, temperature=0)
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
            f"You must respond with ONLY one of the exact category names listed above. Do not add any explanation or additional text.\n"
        )
        try:
            #print(f"DEBUG - AI Prompt: {prompt}")
            messages = [
                SystemMessage(content="You are a helpful assistant that classifies merchants into spending categories."),
                HumanMessage(content=prompt)
            ]
            response = self.llm.invoke(messages)
            category = response.content.strip()
            #print(f"DEBUG - AI Response: {category}")
            if category not in categories:
                return "Other"
            return category
        except Exception as e:
            print(f"AI category guess (OpenAI) failed for merchant '{merchant_name}': {e}")
            return "Other"

    def add_category(self, df: pd.DataFrame, category_cache: dict) -> pd.DataFrame:
        """
        Add categories to transactions using rule-based logic and AI categorization.
        
        Args:
            df (pd.DataFrame): DataFrame with merchant_name column
            category_cache (dict): Dictionary of available categories
            
        Returns:
            pd.DataFrame: DataFrame with category column added/updated
        """
        # Add category column if it doesn't exist
        if 'category' not in df.columns:
            df['category'] = 'Other'
        
        # Check if merchant_name contains "return" or "refund"
        df['category'] = df.apply(
            lambda row: "Refunds & Returns" if 'return' in row['merchant_name'].lower() or 'refund' in row['merchant_name'].lower() else row['category'],
            axis=1
        )

        # Check merchant_name for payments
        df['category'] = df.apply(
            lambda row: "Payments" if 'payment' in row['merchant_name'].lower() else row['category'],
            axis=1
        )
        
        # Use AI to categorize transactions with 'Other' category
        other_mask = df['category'] == 'Other'
        if other_mask.any():
            other_transactions = df[other_mask]
            for idx, row in other_transactions.iterrows():
                ai_category = self.guess_category_openai(
                    row['merchant_name'], 
                    list(category_cache.keys())
                )
                if ai_category != 'Other':
                    df.loc[idx, 'category'] = ai_category

        return df
