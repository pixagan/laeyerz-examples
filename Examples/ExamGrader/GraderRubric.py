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

def rubric_check_prompt(subject:str, question: str, rubric: str,  submission: str):

    
        role = """You are an exam grading asssistant, grading exam questions for a """ + subject + """ Exam."""
                
        question = """The exam question the student has answered is : ' """ + question + """ , """

        rubric_instructions_math = """ """

        instructions = """You will be given:
1. The exam question
2. A grading rubric describing how to grade the student's submission
3. The student’s submission
4. The required response format
        
How to grade the exam:
    - Strictly use the rubric provided as the basis for grading the submission.
    - Stick to the criterion in the rubric, do not make up your own criterion
    - Check for each point in the rubric using the criterion mentioned by the rubric.
    - Award marks strictly as specified by the rubric
    - DO NOT AWARD ANY POINTS FOR ANY WORK DONE THAT DOES NOT CONFORM TO THE RUBRIC MENTIONED
    - If you are unsure about whether marks should be awarded or not for any specific point because you are unable to compare reliably with the rubric, 
      award strictly and then flag the point by setting the confidence flag to High or Low, low implying the instructor needs to review the grade
      awarded for that point.
    - Respond using the response format specified

How to grade the exam:
    - The rubric contains metrics describing what the solution should or should not contains and how many marks to award or deduct for each
    - Each metric contains keypoints that the grader needs to look at and strictly use to grade the exam
    - For each point the rubric specifies a match type(added below) describing how that particular point needs to be checked by the grader
    - Use the Keypoints along with the match_type to grade each point.

 When grading the exam point by point on the rubric, the grader looks to match the point with the solution in the following ways:
    Solution Match Types:
    * EXACT -  Exactly matches letter by letter , word by word as mentioned in the rubric point (rare but say for Math expressions etc)
    * EXPLICIT - A point has to be clearly explained, shown, it cannot be implied or implicit in the steps or working. It has to be explicitly specified.
    * EQUIVALENT - Has to use the same method, approach or describe the same idea, but small rewording, or using slighlty different notation is ok as the meaning or the notion is clear and is explained in correctly.
    * SEMANTIC -  The approach or wording can be different, as long as it is valid and implies clearly the same meaning or method as the point in the rubric. Should not be used too often. Only if the instructors instructions allow for leniency.
    
        """

        response_format = """
        Respond in the following JSON format:
        {
        "grading":[{
            "metric":<metric_name>",
            "keypoints":
            "score": <score>,
            "confidence":"High/Low"
            "explanation": "Explain briefly why the score was awarded or deducted and how it matches the match_type specified in the rubric.",
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
            {"role":"user","content":"The grading rubric is: " + rubric},
            {"role":"user","content":"The student's submission is: " + submission},
        ]
    
    
        return {
         "messages":messages
        }


rubric_check = Node('RubricCheck')
rubric_check_prompt_inputs = [
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
        "name":"rubric",
        "type":"str",
        "description":"The rubric for the grader",
        "source":""
    },
    {
        "name":"submission",
        "type":"str",
        "description":"The student's submission",
        "source":""
    }
]
rubric_check_prompt_outputs = [
    {
      "name":"messages",
      "type":"str",
      "description":"The output prompt in message format"
    }
]
rubric_check.set_function("rubric_check",rubric_check_prompt, {}, rubric_check_prompt_inputs, rubric_check_prompt_outputs)




rubric_llm = LLM("RubricLLM", config={"api_key": km["OPENAI_API_KEY"], "model":"gpt-5-mini"})





rubric_grader_flow = Flow("RubricGraderFlow")

rubric_grader_flow.add_node(rubric_check)
rubric_grader_flow.add_node(rubric_llm)


#def rubric_check_prompt(subject:str, question: str, rubric: str,  submission: str):
rubric_grader_flow.add_data_source("RubricCheck|rubric_check|subject", "INPUTS|subject")
rubric_grader_flow.add_data_source("RubricCheck|rubric_check|question", "INPUTS|question")
rubric_grader_flow.add_data_source("RubricCheck|rubric_check|rubric", "INPUTS|rubric")
rubric_grader_flow.add_data_source("RubricCheck|rubric_check|submission", "INPUTS|submission")

rubric_grader_flow.add_data_source("RubricLLM|call_llm|messages","RubricCheck|rubric_check|messages")



rubric_grader_flow.add_edge("START", "RubricCheck|rubric_check")
rubric_grader_flow.add_edge("RubricCheck|rubric_check", "RubricLLM|call_llm")
rubric_grader_flow.add_edge("RubricLLM|call_llm", 'END')


#Outputs
rubric_grader_flow.set_outputs(["RubricLLM|call_llm|content"])

