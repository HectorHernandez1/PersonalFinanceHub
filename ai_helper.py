from langchain_core.messages import HumanMessage, SystemMessage
import os
import pandas as pd
from typing import List
from vendor_mapping import get_category_from_vendor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AIHelper:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        # AI_PROVIDER selects the backend: "ollama" (local) or "openai" (cloud)
        self.provider = os.getenv('AI_PROVIDER', 'ollama').lower()
        self.llm = None

        if self.provider == 'openai':
            self._init_openai()
        elif self.provider == 'ollama':
            self._init_ollama()
        else:
            print(f"Unknown AI_PROVIDER '{self.provider}'. Expected 'openai' or 'ollama'. AI features disabled.")

    def _init_openai(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("OPENAI_API_KEY not set. AI features disabled.")
            return
        try:
            from langchain_openai import ChatOpenAI
            model = os.getenv('OPENAI_MODEL', 'gpt-5-nano')
            # gpt-5-nano does not support custom temperature, uses default (1)
            self.llm = ChatOpenAI(model=model, openai_api_key=api_key)
            print(f"AIHelper using OpenAI model '{model}'")
        except ImportError:
            print("langchain_openai package not installed. AI features disabled.")
        except Exception as e:
            print(f"Failed to initialize OpenAI: {e}")

    def _init_ollama(self):
        model = os.getenv('OLLAMA_MODEL', 'gemma4:e4b')
        base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        try:
            from langchain_ollama import ChatOllama
            self.llm = ChatOllama(model=model, base_url=base_url, temperature=0)
            print(f"AIHelper using Ollama model '{model}' at {base_url}")
        except ImportError:
            print("langchain_ollama package not installed. AI features disabled.")
        except Exception as e:
            print(f"Failed to initialize Ollama ({model} @ {base_url}): {e}")

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
            print(f"AI category guess ({self.provider}) failed for merchant '{merchant_name}': {e}")
            return "Other"

    def add_category(self, df: pd.DataFrame, category_cache: dict) -> pd.DataFrame:
        """
        Add categories to transactions using vendor mapping first, then rule-based logic, and finally AI categorization.

        Args:
            df (pd.DataFrame): DataFrame with merchant_name column
            category_cache (dict): Dictionary of available categories

        Returns:
            pd.DataFrame: DataFrame with category column added/updated
        """
        # Add category column if it doesn't exist
        if 'category' not in df.columns:
            df['category'] = 'Other'

        # First, check vendor mapping for known vendors
        df['category'] = df.apply(
            lambda row: get_category_from_vendor(row['merchant_name']) or row['category'],
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
