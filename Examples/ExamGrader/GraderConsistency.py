# Copyright 2026 Pixagan Technologies
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


from laeyerz.utils.KeyManager import KeyManager
from laeyerz.flow.Flow import Flow
from laeyerz.flow.Node import Node

from laeyerz_nodes.llm.OpenAINode import OpenAINode as LLM

import simplejson as json

km = KeyManager('../../.env')


def consistency_check_theory(subject:str, question: str, submission: str):

    consistency_check = """
    """

    role = """You are an exam analysis assistant, analyzing exam submissions for a """ + subject + """ Exam."""
            
    question = """The exam question the student is answering is : ' """ + question + """ , """

    rubric_instructions_math = """ """

    instructions = """You will be given:
1. The exam question
2. The student’s submission
3. The required response format

What you need to do:

Check the consistency of the student's solution with itself. 
- Is there a basic logic to the students solution. 
- Do the points mentioned stay consistent with the previous lines of the exams
-In case of a problem with Math like steps like a Mathematical Proof, Derivation, Math Solution
    - Are the steps consistent with the previous ones
    - Are the steps logical 
    
Respond in the format specified stating if the solution is consistent with itself.
Point out any issues in consistency poit by point 
- 

    """

    response_format = """
    Respond in the following JSON format:
    {
    "consistency":"YES/NO"
    "points":[{
        "point":Point 1",
        "explanation": "Inconsistent with previous step because of ...",
    }],
    ""
    }
    ONLY RETURN THE JSON RESPONSE, NO OTHER TEXT. DO NOT TOTAL THE SCORE, JUST RETURN THE SCORE GIVEN OR DEDUCTED FOR EACH CRITERIA.
    """


    messages = [
        {"role":"developer","content":role},
        {"role":"developer","content":instructions},
        {"role":"developer","content":response_format},
        {"role":"user","content":question},
        {"role":"user","content":"The student's submission is: " + submission},
    ]


    return {
     "messages":messages
    }



consistency_check = Node('ConsistencyCheck')
consistency_check_inputs = [
     {
        "name":"subject",
        "type":"str",
        "description":"The question to grade",
        "source":""
    },
    {
        "name":"question",
        "type":"str",
        "description":"The question to grade",
        "source":""
    },
    {
        "name":"submission",
        "type":"str",
        "description":"The student's submission",
        "source":""
    }
]
consistency_check_outputs = [
    {
      "name":"messages",
      "type":"str",
      "description":"The output prompt in message format"
    }
]
consistency_check.set_function("consistency_check",consistency_check_theory, {}, consistency_check_inputs, consistency_check_outputs)


consistency_llm = LLM("ConsistencyLLM", config={"api_key": km["OPENAI_API_KEY"], "model":"gpt-5-mini"})



consistency_grader_flow = Flow("ConsistencyGraderFlow")

consistency_grader_flow.add_node(consistency_check)
consistency_grader_flow.add_node(consistency_llm)

#DataFlow

consistency_grader_flow.add_data_source("ConsistencyCheck|consistency_check|subject", "INPUTS|subject")
consistency_grader_flow.add_data_source("ConsistencyCheck|consistency_check|question", "INPUTS|question")
consistency_grader_flow.add_data_source("ConsistencyCheck|consistency_check|submission", "INPUTS|submission")

consistency_grader_flow.add_data_source("ConsistencyLLM|call_llm|messages","ConsistencyCheck|consistency_check|messages")


#Edges
consistency_grader_flow.add_edge("START", "ConsistencyCheck|consistency_check")
consistency_grader_flow.add_edge("ConsistencyCheck|consistency_check", "ConsistencyLLM|call_llm")
consistency_grader_flow.add_edge("ConsistencyLLM|call_llm", 'END')


consistency_grader_flow.set_outputs(["ConsistencyLLM|call_llm|content"])

