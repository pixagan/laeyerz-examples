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

from GraderComparative import comparative_grader_flow
from GraderConsistency import consistency_grader_flow
from GraderRubric import rubric_grader_flow

from dotenv import load_dotenv, find_dotenv
load_dotenv()



class GraderInputConsistency(BaseModel):
    subject: str
    question: str
    submission: str


class GraderInputRubric(BaseModel):
    subject: str
    question: str
    rubric: str
    submission: str

class GraderInputComparative(BaseModel):
    subject: str
    question: str
    answer: str
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


        self.consistency_grader  = consistency_grader_flow
        self.comparative_grader  = comparative_grader_flow
        self.rubric_grader       = rubric_grader_flow

        self.setup_routes()


    def setup_routes(self):

        @self.api.get("/")
        async def load_index():
            return {"message": "Welcome to Grader API"}



        @self.api.post("/api/grade/consistency")
        async def grade_consistency(grader_input: GraderInputConsistency):

            grader_inputs = {
                "subject": grader_input.subject,
                "question": grader_input.question,
                "submission": grader_input.submission,
            }

            print("grader_inputs", grader_inputs)

            flow_response = self.consistency_grader.run(grader_inputs)

            print("grader_response", flow_response)

            final_response = json.loads(flow_response['ConsistencyLLM|call_llm|content'], strict=False)
            
            print("final_response", final_response)

            return final_response



        @self.api.post("/api/grade/compare")
        async def grade_compare(grader_input: GraderInputComparative):

            grader_inputs = {
                "subject": grader_input.subject,
                "question": grader_input.question,
                "answer": grader_input.answer,
                "submission": grader_input.submission
            }

            flow_response = self.comparative_grader.run(grader_inputs)


            final_response = json.loads(flow_response['CompareLLM|call_llm|content'], strict=False)


            print("final_response", final_response)
            return final_response



        @self.api.post("/api/grade/rubric")
        async def grade_rubric(grader_input: GraderInputRubric):

            grader_inputs = {
                "subject": grader_input.subject,
                "question": grader_input.question,
                "rubric": grader_input.rubric,
                "submission": grader_input.submission
            }

            flow_response = self.rubric_grader.run(grader_inputs)

            final_response = json.loads(flow_response['RubricLLM|call_llm|content'], strict=False)

            print("final_response", final_response)
            return final_response



    def run_api(self):
        uvicorn.run(self.api, host="0.0.0.0", port=6030)



if __name__ == "__main__":
    app = GraderApp()
    app.run_api()