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

from laeyerz.utils.KeyManager import KeyManager
from laeyerz.flow.Flow import Flow
from laeyerz.flow.Node import Node

from laeyerz_nodes.llm.OpenAINode import OpenAINode as LLM

import simplejson as json

km = KeyManager('../../.env')

def grader_prompt_builder(question: str, answer: str, rubric: str,  submission: str):

    
    role = """You are an exam grading asssistant grading theory exam questions for a """ + """ Exam."""
            
    instructions = """You will be provided the exam question and a grading rubric that specifies the criteria for grading the question.
    You will be provided the student's submission for the question. Use the grading rubric to grade the submission against the question and the criteria.
    Respond in the format specifed in the response format.
    If you have any doubts about the grading, flag the question for review so it can be rechecked.
    """
    
    response_format = """
    Respond in the following JSON format:
    {
    "grading":[{
        "metric":<metric_name>",
        "score": <score>,
        "explanation": "Explain briefly why the score was given or deducted.",
    }],
    "review": <review>
    }
    ONLY RETURN THE JSON RESPONSE, NO OTHER TEXT. DO NOT TOTAL THE SCORE, JUST RETURN THE SCORE GIVEN OR DEDUCTED FOR EACH CRITERIA.
    """


    messages = [
        {"role":"developer","content":role},
        {"role":"developer","content":instructions},
        {"role":"developer","content":response_format},
        {"role":"user","content":question},
        {"role":"user","content":answer},
        {"role":"user","content":rubric},
        {"role":"user","content":submission}
    ]


    return {
     "messages":messages
    }




grader_prompt = Node('GraderPrompt')
grader_prompt_inputs = [
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
grader_prompt_outputs = [
    {
      "name":"messages",
      "type":"str",
      "description":"The output prompt in message format"
    }
]
grader_prompt.set_function("grader_prompt",grader_prompt_builder, {}, grader_prompt_inputs, grader_prompt_outputs)



grader_llm = LLM("GraderLLM", config={"api_key": km["OPENAI_API_KEY"], "model":"gpt-5-mini"})



def verifier_prompt_builder(question: str, rubric: str, answer: str, submission: str, grade: str):

    role = """You are an exam grading validator agent grading questions with mathematical content for a """  + """ Exam."""
            
    instructions = """You will be provided the exam question and a grading rubric that specifies the criteria for grading the question.
    You will be provided the student's submission for the question and where required the correct answer.
    You will also be provided the grading assigned by the grader for the question including steps of why the grades have been assigned.
    For questions with mathematical steps, you will also be provided the correct answer to the question.
    Check for any inconsistencies in the grading assigned by the grader and provide a review of the grading.
    
    
    For math questions, the grader has been allowed to provide marks for an alternative approach as long as the the approach is equivant, steps are provided and are logical and correct and the answer is correct.
    
    If the grading is correct simply respond with grading_is_correct field as true.
    If you see inaccuracies or inconsistencies in the grading, set the grading_is_correct field to false and provide a review of why and where the grading is incorrect flagging any inconsistencies.
    If a mistake requires partial credit etc you may suggest that.
    """
    
    response_format = """
    Respond in the following JSON format:
    {
    "grading_is_correct": <grading_is_correct>,
    "review": [
      {
        "metric":<metric_name>",
        "reason": "Explain briefly why the grading assigned for this metric is incorrect or inconsistent with the grading rubric.",
      }
    },
    "other":["If required provide any other comments or observations not specified above about why the grading is incorrect.]
    ONLY RETURN THE JSON RESPONSE, NO OTHER TEXT.
    """



    messages = [
       {"role":"developer","content":role},
        {"role":"developer","content":instructions},
        {"role":"developer","content":response_format},
        {"role":"user","content":question},
        {"role":"user","content":answer},
        {"role":"user","content":rubric},
        {"role":"user","content":submission},
        {"role":"user","content":grade},
    ]


    return {
     "messages":messages
    }



verifier_prompt = Node('VerifierPrompt')
verifier_prompt_inputs = [
    {
        "name":"question",
        "type":"str",
        "description":"The question to grade",
        "source":""
    },
    {
        "name":"answer",
        "type":"str",
        "description":"The correct answer for the question",
        "source":""
    },
    {
        "name":"rubric",
        "type":"str",
        "description":"The grading rubric to be used",
        "source":""
    },
    {
        "name":"submission",
        "type":"str",
        "description":"The student's submission",
        "source":""
    },
    {
        "name":"grade",
        "type":"str",
        "description":"The grade breakdown assigned to be reviewed",
        "source":""
    }
]
verifier_prompt_outputs = [
    {
      "name":"messages",
      "type":"str",
      "description":"The output prompt in message format"
    }
]
verifier_prompt.set_function("verifier_prompt",verifier_prompt_builder, {}, verifier_prompt_inputs, verifier_prompt_outputs)



verifier_llm = LLM("VerifierLLM", config={"api_key": km["OPENAI_API_KEY"], "model":"gpt-5-mini"})