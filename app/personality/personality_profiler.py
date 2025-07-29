import os
import json
from datetime import datetime
from app.llm.client import query_llm

class PersonalityProfiler:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.filepath = f"data/personalities/{user_id}.json"
        self.traits = self._load_traits()
        print(f"🎭 PersonalityProfiler initialized for user_id: {user_id}")

    def _load_traits(self) -> dict:
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Failed to load traits for {self.user_id}: {e}")
        return {}

    def _save_traits(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        try:
            with open(self.filepath, "w") as f:
                json.dump(self.traits, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save traits for {self.user_id}: {e}")

    def infer_traits_from_text(self, text: str):
        prompt = (
            f"Analyze the following user message and infer any personality traits "
            f"(e.g., optimism, anxiety, confidence, introversion, ambition):\n\n"
            f"{text}\n\n"
            f"Return a JSON dictionary like {{'trait': 'value'}}."
        )

        try:
            response = query_llm(prompt)
            new_traits = json.loads(response.strip())
            print(f"🧠 Inferred traits for {self.user_id}: {new_traits}")
        except Exception as e:
            print(f"❌ Trait inference failed for {self.user_id}: {e}")
            new_traits = {}

        for trait, value in new_traits.items():
            self.traits[trait] = {
                "value": value,
                "last_updated": datetime.now().isoformat()
            }

        self._save_traits()

    def get_traits(self) -> dict:
        return self.traits
