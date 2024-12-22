from config import *
from text_processing import process_and_save_all, text_input, system_prompt, user_prompt





cache = {}
#process_and_save_all(text_input, system_prompt, user_prompt, context_cache=cache)

with open('qwen_processed_mephi.json', "r", encoding="utf-8") as f:
    data = json.load(f)
    entities, relations = data["entities"], data["relations"]