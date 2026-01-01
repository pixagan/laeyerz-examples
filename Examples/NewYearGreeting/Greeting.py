# Copyright 2025 Pixagan Technologies
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
ASCII Greeting Card Generator module for generating ASCII greeting cards
in the Laeyerz framework.
"""

from laeyerz.nodes.llm.OpenAILLMNode import OpenAILLMNode as LLM
from laeyerz.utils.KeyManager import KeyManager


key_manager = KeyManager("API KEY PATH HERE")
api_key = key_manager.get('OPENAI_API_KEY')



llm = LLM("Model", config={"api_key": api_key})
model = "gpt-5-mini"

tools = []


instructions = """You are a helpful assistant. 
Given the receipient name and description and mood of greeting, 
generate ONE custom Happy New Year message including emojis.
"""

moods= ["Casual & upbeat", 
"Warm & heartfelt", 
"Funny & playful", 
"Short & sweet", 
"Inspirational",  
"Nostalgic + hopeful", 
"Poetic & warm"
]

max_words = 20

query = "For my friend, Friends"


messages = [
    {"role": "developer", "content": instructions},
    {"role": "user", "content":"Tone : " + moods[0]},
    {"role": "user", "content":"Max Words : "+str(max_words)},
    {"role": "user", "content": "query: " + query}
]


message = llm.call_llm(messages, model, tools)


output_text = message['message'].content
print(output_text)


#-------- Node 2 ----------------------
card_instruction = """Convert the Happy New Year Message into a colourful text-based greeting card.
    Combine emoji decorations, simple ascii drawings (fireworks, sparkles etc) with stylized version of the text provided. 
    """
occasion = "Christmas"
emoji_density = "high"

model_ascii = "gpt-5.2"

ascii_messages = [
    {"role": "developer", "content": card_instruction},
    {"role": "user", "content":"occasion : " + occasion},
    {"role": "user", "content":"emoji density : " + emoji_density},
    {"role": "user", "content":"query : " + output_text},
    
]


ascii_image = llm.call_llm(ascii_messages, model_ascii, tools)


output_text = ascii_image['message'].content
print(output_text)