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
import sys
from pathlib import Path
import uuid
from datetime import datetime
import csv
from io import StringIO
from io import BytesIO
from typing import Dict
import simplejson as json


from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from laeyerz.utils.KeyManager import KeyManager
from laeyerz.flow.Flow import Flow
from laeyerz.flow.Node import Node
from laeyerz_nodes.llm.OpenAINode import OpenAINode as LLM
from laeyerz_nodes.llm.PromptNode import PromptNode


from dotenv import load_dotenv, find_dotenv
load_dotenv()



class GraderInput(BaseModel):
    subject: str
    topic: str
    question: str
    answer: str
    rubric: str
    submission: str


class GraderApp:

    def __init__(self):

        self.grader_flow    = None
    

        self.api =  FastAPI(
                                title="Grader API for App",
                                description="The API for a Sample Grader App",
                                version="1.0.0"
                            )

        self.api.add_middleware(
                                    CORSMiddleware,
                                    allow_origins=["*"],
                                    allow_credentials=True,
                                    allow_methods=["*"],  # Allows all methods
                                    allow_headers=["*"],  # Allows all headers
                                )


        self.km            = KeyManager('../../.env')


        self.setup_components()
        self.setup_grader_flow()
        self.setup_routes()



    def setup_components(self):


        def grader_prompt_builder(question: str, answer: str, rubric: str,  submission: str):

            
            role = """You are an exam grading asssistant grading theory exam questions for a """ + """ Exam."""
                    
            instructions = """You will be provided the exam question and a grading rubric that specifies the criteria for grading the question.
            You will be provided the student's submission for the question. Use the grading rubric to grade the submission against the question and the criteria.
            You will also be provided the answer key showing the correct answer to the question that the submission should be compared to.
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
                {"role":"user","content":"The question is: " + question},
                {"role":"user","content":"The answer key the studennt's submission has been compared to is: " + answer},
                {"role":"user","content":"The grading rubric is: " + rubric},
                {"role":"user","content":"The student's submission is: " + submission},
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



        grader_llm = LLM("GraderLLM", config={"api_key": self.km["OPENAI_API_KEY"], "model":"gpt-5-mini"})



        def verifier_prompt_builder(question: str, rubric: str, answer: str, submission: str, grade: str):

            role = """You are an exam grading validator agent grading questions with mathematical content for a """  + """ Exam."""
                    
            instructions = """You will be provided the exam question and a grading rubric that specifies the criteria for grading the question.
            You will also be provided the answer key showing the correct answer to the question that the student's submission has been compared to.
            You will be provided the student's submission for the question.
            
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
                "metric_name":"<metric_name>",
                "isCorrect": <isCorrect>,
                "reason": "Explain briefly why the grading assigned for this metric is incorrect or inconsistent with the grading rubric.",
            }
            ]
            },
            "other":["If required provide any other comments or observations not specified above about why the grading is incorrect.]
            ONLY RETURN THE JSON RESPONSE, NO OTHER TEXT.
            """



            messages = [
                {"role":"developer","content":role},
                {"role":"developer","content":instructions},
                {"role":"developer","content":response_format},
                {"role":"user","content":"The question is: " + question},
                {"role":"user","content":"The answer key the studennt's submission has been compared to is: " + answer},
                {"role":"user","content":"The grading rubric is: " + rubric},
                {"role":"user","content":"The student's submission is: " + submission},
                {"role":"user","content":"The grade breakdown assigned by the grader to be reviewed is: " + grade},
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



        verifier_llm = LLM("VerifierLLM", config={"api_key": self.km["OPENAI_API_KEY"], "model":"gpt-5-mini"})



       

        self.grader_prompt = grader_prompt
        self.grader_llm = grader_llm
        self.verifier_prompt = verifier_prompt
        self.verifier_llm = verifier_llm



    def setup_grader_flow(self):
        print("Setting up store flow")

        grader_flow = Flow("GraderFlow")

        grader_flow.add_node(self.grader_prompt)
        grader_flow.add_node(self.grader_llm)
        grader_flow.add_node(self.verifier_prompt)
        grader_flow.add_node(self.verifier_llm)

        grader_flow.add_data_source("GraderPrompt|grader_prompt|question", "INPUTS|question")
        grader_flow.add_data_source("GraderPrompt|grader_prompt|rubric", "INPUTS|rubric")
        grader_flow.add_data_source("GraderPrompt|grader_prompt|answer", "INPUTS|answer")
        grader_flow.add_data_source("GraderPrompt|grader_prompt|submission", "INPUTS|submission")


        grader_flow.add_data_source("GraderLLM|call_llm|messages","GraderPrompt|grader_prompt|messages")

        grader_flow.add_data_source("VerifierPrompt|verifier_prompt|question", "INPUTS|question")
        grader_flow.add_data_source("VerifierPrompt|verifier_prompt|rubric", "INPUTS|rubric")
        grader_flow.add_data_source("VerifierPrompt|verifier_prompt|answer", "INPUTS|answer")
        grader_flow.add_data_source("VerifierPrompt|verifier_prompt|submission", "INPUTS|submission")
        grader_flow.add_data_source("VerifierPrompt|verifier_prompt|grade", "GraderLLM|call_llm|content")


        grader_flow.add_data_source("VerifierLLM|call_llm|messages","VerifierPrompt|verifier_prompt|messages")

        grader_flow.add_edge("START", "GraderPrompt|grader_prompt")
        grader_flow.add_edge("GraderPrompt|grader_prompt", "GraderLLM|call_llm")
        grader_flow.add_edge("GraderLLM|call_llm", "VerifierPrompt|verifier_prompt")
        grader_flow.add_edge("VerifierPrompt|verifier_prompt", "VerifierLLM|call_llm")
        grader_flow.add_edge("VerifierLLM|call_llm", 'END')


        #Outputs
        grader_flow.set_outputs(['GraderLLM|call_llm|content','VerifierLLM|call_llm|content'])


        self.grader_flow = grader_flow




    def setup_routes(self):

        @self.api.get("/")
        async def load_index():
            return {"message": "Welcome to Grader API"}


        @self.api.post("/api/grade")
        async def grade_question(grader_input: GraderInput):

            grader_inputs = {
                "question": grader_input.question,
                "answer": grader_input.answer,
                "rubric": grader_input.rubric,
                "submission": grader_input.submission
            }

            print("grader_inputs", grader_inputs)

            flow_response = self.grader_flow.run(grader_inputs)

            print("grader_response", flow_response)

            
            grader_response = json.loads(flow_response['GraderLLM|call_llm|content'], strict=False)
            verifier_response = json.loads(flow_response['VerifierLLM|call_llm|content'], strict=False)
  
            print("--------------------------------")
            print("grader_response", grader_response)
            print("verifier_response", verifier_response)
            print("--------------------------------")

            #Convert verifier response to dictionary
            verifier_dict = {}
            for point in verifier_response['review']:
                verifier_dict[point['metric_name']] = {
                    "isCorrect": point['isCorrect'],
                    "reason": point['reason']
                }
            
            grade_list = []

            print("verifier_dict", verifier_dict)

            print("--------------------------------")

            #Assemble final flow response which is a combination of grader and verifier
            for point in grader_response['grading']:
                gp = {}
                gp['metric_name'] = point['metric']
                gp['score'] = point['score']
                gp['explanation'] = point['explanation']
                gp['isCorrect'] = verifier_dict[point['metric']]['isCorrect']
                gp['reason'] = verifier_dict[point['metric']]['reason']
                grade_list.append(gp)


            final_response = {
                "grading": grade_list,
            }

            print("final_response", final_response)
                

            return final_response


    def run_api(self):
        uvicorn.run(self.api, host="0.0.0.0", port=6030)



if __name__ == "__main__":
    app = GraderApp()
    app.run_api()