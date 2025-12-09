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

import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

from laeyerz.nodes.llm.OpenAILLMNode import OpenAILLMNode as LLM
from laeyerz.flow import Flow

#flow = Flow("SelfReviewLLM")

drafter = LLM("Drafter")
drafter_instructions = """You are a highly capable assistant. 
Write the best possible answer to the user request.
User request:
<user_request>
Write your answer clearly and thoroughly.
"""

critic = LLM("Critic")
critic_instruction = """
You are now an impartial critic evaluating the answer below.

Answer to evaluate:
<draft>

List problems, errors, missing details, unclear parts, bias, or logical issues.
If the answer is excellent and requires no improvement, say "NO ISSUES".
"""

refiner = LLM("Refiner")
refiner_instruction = """
You are now an assistant improving your own work.

Original answer:
<draft>

Issues to fix:
<critique>

Rewrite the answer addressing every issue. 
Provide the improved answer only.
"""



def self_review_llm(user_request):

    max_iters =  3
    #draft = drafter.run(f"Write an initial answer.\n\nUser request:\n{user_request}")
    messages = [
                {"role": "developer", "content": drafter_instructions},
                {"role": "user", "content": user_request}
                ]
    tools = []
    model= "gpt-4o-mini"

    draft = drafter.call_llm(messages, model, tools)
    draft = draft['message'].content

    print("Initial Draft:", draft)

    for i in range(max_iters):
        print(f"\n=== ITERATION {i+1} ===")


        
        messages= [
                {"role": "developer", "content": critic_instruction},
                {"role": "user", "content": draft}
                ]
        tools= []
        model= "gpt-4o-mini"
        
        critique = critic.call_llm(messages, model, tools)
        critique = critique['message'].content
        print("Critique:", critique)
        print("****************")



        if "NO ISSUES" in critique:
            print("\n✓ Converged — stopping loop.")
            return draft
            break

      

        messages = [
                {"role": "developer", "content": refiner_instruction},
                {"role": "user", "content": draft},
                {"role": "user", "content": critique}
                ]
        tools: []
        model: "gpt-4o-mini"
        

        draft = refiner.call_llm(messages, model, tools)
        draft = draft['message'].content
        print("Refined Draft:", draft)
        print("****************")
        return draft



final_answer = self_review_llm("Explain quantum computing to a 12-year-old.")
print("--------------------------------")
print("\nFINAL ANSWER:\n", final_answer)




