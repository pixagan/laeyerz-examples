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


def compare_answers_prompt(subject:str, question: str, answer: str,  submission: str):

    
        role = """You are an exam analysis asssistant, analyzing exam submissions for a """ + subject + """ Exam."""
                
        question = """The exam question the student is answering is : ' """ + question + """ , """

        rubric_instructions_math = """ """

        instructions = """You will be given:
1. The exam question
2. A sample solution for the problem
3. The student’s submission
4. The required response format
        
What you need to do:
    - Compare the student's submission with the sample solution given by the instructor.
    - List out point by point how the student's solution is different from the sample solution
    - Start by listing out the Similarities
    - Listing out the Differences
    
        """

        response_format = """
        Respond in the following JSON format:
        {
          "similar": [
            {
              "point": "Point 1",
              "explanation": "Explain briefly what is similar to the sample solution."
            }
          ],
          "difference": [
            {
              "point": "Point 1",
              "explanation": "Explain briefly what is different compared to the sample solution."
            }
          ]
        }

        Rules:
        - Return at least 1 Similar point and at least 1 Different point when applicable.
        - ONLY RETURN THE JSON RESPONSE, NO OTHER TEXT.
        """
    
    
        messages = [
            {"role":"developer","content":role},
            {"role":"developer","content":instructions},
            {"role":"developer","content":response_format},
            {"role":"user","content":question},
            {"role":"user","content":"The correct answer the student's submission has been compared to is: " + answer},
            {"role":"user","content":"The student's submission is: " + submission},
        ]
    
    
        return {
         "messages":messages
        }



compare_answers = Node('CompareAnswers')
compare_answers_inputs = [
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
        "name":"answer",
        "type":"str",
        "description":"The correct answer to the question",
        "source":""
    },
    {
        "name":"submission",
        "type":"str",
        "description":"The student's submission",
        "source":""
    }
]
compare_answers_outputs = [
    {
      "name":"messages",
      "type":"str",
      "description":"The output prompt in message format"
    }
]
compare_answers.set_function("compare_answers",compare_answers_prompt, {}, compare_answers_inputs, compare_answers_outputs)



compare_llm = LLM("CompareLLM", config={"api_key": km["OPENAI_API_KEY"], "model":"gpt-5-mini"})


comparative_grader_flow = Flow("ComparativeGraderFlow")


comparative_grader_flow.add_node(compare_answers)
comparative_grader_flow.add_node(compare_llm)



comparative_grader_flow.add_data_source("CompareAnswers|compare_answers|subject", "INPUTS|subject")
comparative_grader_flow.add_data_source("CompareAnswers|compare_answers|question", "INPUTS|question")
comparative_grader_flow.add_data_source("CompareAnswers|compare_answers|answer", "INPUTS|answer")
comparative_grader_flow.add_data_source("CompareAnswers|compare_answers|submission", "INPUTS|submission")

comparative_grader_flow.add_data_source("CompareLLM|call_llm|messages","CompareAnswers|compare_answers|messages")


comparative_grader_flow.add_edge("START", "CompareAnswers|compare_answers")
comparative_grader_flow.add_edge("CompareAnswers|compare_answers", "CompareLLM|call_llm")
comparative_grader_flow.add_edge("CompareLLM|call_llm", 'END')


#Outputs
comparative_grader_flow.set_outputs(["CompareLLM|call_llm|content"])

