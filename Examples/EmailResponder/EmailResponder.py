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

from laeyerz.nodes.llm.OpenAILLMNode import OpenAILLMNode as LLM
from laeyerz.flow.Flow import Flow
from laeyerz.flow.Node import Node


#---------- Response Detector Node ----------


def promptDfun(content:str)->(list):
    messages = [
        {
            "role": "user",
            "content": content
        }
    ]
    outputs = {
        "prompt": messages
    }
    return outputs

promptD = Node("PromptD")

promptD_inputs = [
    {
        "name": "content",
        "type": "str",
        "description": "The content to be processed",
        "inputType": "source",
        "source":"",
        "value":None
    }
]
promptD_outputs = [
    {
        "name": "prompt",
        "type": "list",
        "description": "The output from the node",
        "sourceType": "output"
    }
]
promptD.set_function("promptD",promptDfun, {}, promptD_inputs, promptD_outputs)


detector_instructions = """You are a smart email classifier assistant. 
For the email provided check if any actions are required.
Also specifically check if the email requires a response. If so respond with 'Needs Response' else response with 'No Response'"""

responseDetector = LLM("ResponseDetector", {}, detector_instructions)
#-----------------------------------------------------------------------


def promptKFun(content:str)->(list):
    messages = [
        {
            "role": "user",
            "content": content
        }
    ]
    outputs = {
        "prompt": messages
    }
    return outputs

promptK = Node("PromptK")

promptK_inputs = [
    {
        "name": "content",
        "type": "str",
        "description": "The content to be processed",
        "inputType": "source",
        "source":"",
        "value":None
    }
]
promptK_outputs = [
    {
        "name": "prompt",
        "type": "list",
        "description": "The output from the node",
        "sourceType": "output"
    }
]
promptK.set_function("promptK", promptKFun, {}, promptK_inputs, promptK_outputs)


keypointExtractor_instructions = """You are a smart email assistant. From the email extract the key points mentioned in the email such that they can be used to formulate a response. 
Also extract any actions to be performed. 
Each point should also have a mention of if needs responding."""

keypointExtractor = LLM("KeypointExtractor",{}, keypointExtractor_instructions)


#----------------------------------------------------------------------

def promptWfun(content:str)->(list):
    messages = [
        {
            "role": "user",
            "content": content
        }
    ]
    outputs = {
        "prompt": messages
    }
    return outputs

promptW = Node("PromptW")
promptW_inputs = [
    {
        "name": "content",
        "type": "str",
        "description": "The content to be processed",
        "inputType": "source",
        "source":"",
        "value":None
    }
]
promptW_outputs = [
    {
        "name": "prompt",
        "type": "list",
        "description": "The output from the node",
        "sourceType": "output"
    }
]
promptW.set_function("promptW",promptWfun, {}, promptW_inputs, promptW_outputs)


draftWriter_instructions = """You are a smart email responder. 
Go over the keypoints provided and depending on whether they require a response, draft a response for each point. 
Use any other information provided to answer if queries if required.
Once all the response points have been created, blend them into a coherent email."""

draftWriter = LLM("DraftWriter", {}, draftWriter_instructions)



#-------------------------------------------------------------------



email_responder = Flow("Email Responder")

#email_responder.add_node("UserInput")
email_responder.add_node(promptD)
email_responder.add_node(responseDetector)

email_responder.add_node(promptK)
email_responder.add_node(keypointExtractor)

email_responder.add_node(promptW)
email_responder.add_node(draftWriter)

#edge
#"node|action|output"->"node|action|input"
email_responder.add_edge("START", "PromptD|promptD")
email_responder.add_edge("PromptD|promptD", "ResponseDetector|call_llm")

email_responder.add_edge("ResponseDetector|call_llm", "PromptK|promptK")
email_responder.add_edge("PromptK|promptK", "KeypointExtractor|call_llm")

email_responder.add_edge("KeypointExtractor|call_llm", "PromptW|promptW")
email_responder.add_edge("PromptW|promptW", "DraftWriter|call_llm")

email_responder.add_edge("DraftWriter|call_llm", "END")


#add data sources to the sockets
email_responder.add_data_source("PromptD|promptD|content", "INPUTS|user_query")

email_responder.add_data_source("ResponseDetector|call_llm|messages", "PromptD|promptD|prompt")
email_responder.set_node_input("ResponseDetector|call_llm|model", "gpt-4o-mini")
email_responder.set_node_input("ResponseDetector|call_llm|tools", [])

email_responder.add_data_source("PromptK|promptK|content", "INPUTS|user_query")

email_responder.add_data_source("KeypointExtractor|call_llm|messages", "PromptK|promptK|prompt")
email_responder.set_node_input("KeypointExtractor|call_llm|model", "gpt-4o-mini")
email_responder.set_node_input("KeypointExtractor|call_llm|tools", [])

email_responder.add_data_source("PromptW|promptW|content", "KeypointExtractor|call_llm|content")

email_responder.add_data_source("DraftWriter|call_llm|messages", "PromptW|promptW|prompt")
email_responder.set_node_input("DraftWriter|call_llm|model", "gpt-4o-mini")
email_responder.set_node_input("DraftWriter|call_llm|tools", [])

email_responder.finalize()


email_input = {
    "user_query": '''
Subject: Request for Audit Deadline Confirmation
Hi [Name of recipient],
I hope this email finds you well.
Could you please confirm when the deadline for the upcoming audit is due?
This information will help ensure our team has sufficient time to prepare and submit all necessary documentation accurately and on schedule.
Thank you for your assistance.
Best regards,
[Your Name]'''
}

email_responder.run(email_input)









