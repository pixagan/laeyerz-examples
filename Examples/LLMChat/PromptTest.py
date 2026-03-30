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
RAG module for Retrieval Augmented Generation example
in the Laeyerz framework.
"""

import os

from laeyerz.flow.Flow import Flow
from laeyerz_nodes.llm.OpenAINode import OpenAINode as LLM
from laeyerz_nodes.llm.PromptNode import PromptNode
from laeyerz.utils.KeyManager import KeyManager

key_manager = KeyManager('YOUR_API_KEY_PATH_HERE')
api_key = key_manager.get('OPENAI_API_KEY')

#create LLM node
llm = LLM("LLMNode", config={"api_key": api_key, "model":"gpt-5-mini"})

#-------- Configure the Inputs to the LLM -----------
#pick the llm model

tools = []

instructions = "You are a helpful assistant that can summarize the given text"
query = """Artificial intelligence (AI) refers to the ability of computer systems to perform tasks that traditionally require human intelligence. These tasks include learning from experience, reasoning through problems, recognizing patterns, understanding language, perceiving the environment, and making decisions. At its core, AI aims to create machines that can mimic or augment human cognitive abilities in a wide range of situations.

AI is a major field within computer science that develops theories, techniques, and software enabling machines to analyze information, adapt to new inputs, and take actions that help them achieve defined objectives. This involves multiple subfields, such as machine learning—which allows systems to improve performance through data—natural language processing, computer vision, robotics, and expert systems. Together, these technologies enable computers to make sense of complex environments and act intelligently within them.

Modern AI systems work by processing large amounts of data, identifying meaningful patterns, and learning rules or behaviors that help them solve specific problems. They can operate autonomously or as tools that enhance human decision-making. The ultimate goal of AI research is to build systems that are reliable, flexible, and capable of working efficiently in real-world scenarios, thereby increasing productivity, improving user experiences, and supporting better decisions across industries."""


prompt_template = {
   "roles": {
        "instructions":"developer",
        "query":"user",
   }
}

promptN = PromptNode("Prompt", config={}, template=prompt_template)
promptN.add_prompt_inputs(
    [
        {"name": "instructions", "type": "str"},
        {"name": "query", "type": "str"}
    ]
)


#print("Actions : ",promptN.actions)
print("Inputs : ",promptN.actions['generate_prompt_openai'].inputs)
print("Outputs : ",promptN.actions['generate_prompt_openai'].outputs)

#--------- Process the LLM Output -----------

llm_flow = Flow("LLM")

#edges
llm_flow.add_node(promptN)
llm_flow.add_node(llm)

#edges
llm_flow.add_edge("START", "Prompt|generate_prompt_openai")
llm_flow.add_edge("Prompt|generate_prompt_openai", "LLMNode|call_llm")
llm_flow.add_edge("LLMNode|call_llm", "END")

#data_sources
llm_flow.add_data_source("Prompt|generate_prompt_openai|instructions", "INPUTS|instructions")
llm_flow.add_data_source("Prompt|generate_prompt_openai|query", "INPUTS|query")

llm_flow.add_data_source("LLMNode|call_llm|messages", "Prompt|generate_prompt_openai|messages")
llm_flow.set_node_input("LLMNode|call_llm|tools", [])

llm_flow.set_outputs(["LLMNode|call_llm|content"])


flow_outputs = llm_flow.run(
    {
        "instructions": instructions,
        "query": query
    }
)

print("***************** Flow Outputs *****************")
for key, value in flow_outputs.items():
    print("Output: ", value)


