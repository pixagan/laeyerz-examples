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
# Developed by : Anil Variyar

import os
import sys
from pathlib import Path
import uuid
from datetime import datetime
import csv
from io import StringIO
from io import BytesIO
from typing import Dict


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
from laeyerz_nodes.fileloaders.PdfLoader import PdfLoader
from laeyerz_nodes.dataprocessors.TextProcessor import TextProcessorNode
from laeyerz_nodes.embeddings.SentenceTransformerNode import SentenceTransformerNode as Embeddings
from laeyerz_nodes.vectorstores.FaissNode import FaissNode as VectorStore

from laeyerz.nodes.llm.PromptNode import PromptNode


from dotenv import load_dotenv, find_dotenv
load_dotenv()


from laeyerz.utils.KeyManager import KeyManager


class ChatInput(BaseModel):
    query: str


class DocChatApp:

    def __init__(self):

        self.store_flow    = None
        self.retrieve_flow = None

        self.api =  FastAPI(
                                title="DocChat API for App",
                                description="The API for the DocChat App",
                                version="1.0.0"
                            )

        self.api.add_middleware(
                                    CORSMiddleware,
                                    allow_origins=["*"],  # Your Frontend URL
                                    allow_credentials=True,
                                    allow_methods=["*"],  # Allows all methods
                                    allow_headers=["*"],  # Allows all headers
                                )


        self.km            = KeyManager('../../.env')


        self.chat_history = []

        self.setup_components()
        self.setup_store_flow()
        self.setup_retrieve_flow()
        self.setup_routes()


    def setup_components(self):

        self.pdf_loader    = PdfLoader("PdfLoader")

        #Combine text into a single string
        self.combine_text  = TextProcessorNode("CombinePages")

        #Split Text
        self.split_text     = TextProcessorNode("SplitText")

        #Text to Embeddings
        self.embedding_model  = Embeddings("Embeddings")
        self.embedding_model2 = Embeddings("Embeddings2")

        #Create Vector Store
        self.vector_store = VectorStore("DocumentStore")

        api_key = self.km.get('OPENAI_API_KEY')
        self.llm_node = LLM("LLM", config={"api_key": api_key, "model":"gpt-5-mini"})


        prompt_template = {
        "roles": {
                "instructions":"developer",
                "context":"user",
                "query":"user",
        }
        }

        promptNode = PromptNode("Prompt", config={}, template=prompt_template)
        promptNode.add_prompt_inputs(
            [
                {"name": "instructions", "type": "str"},
                {"name": "context", "type": "list"},
                {"name": "query", "type": "str"}
            ]
        )
        self.promptNode = promptNode



    def setup_store_flow(self):
        print("Setting up store flow")

        #-----Creating thh Flow
        store_flow = Flow("DocumentStore")

        #-----adding nodes
        store_flow.add_node(self.pdf_loader)
        store_flow.add_node(self.combine_text)
        store_flow.add_node(self.split_text)
        store_flow.add_node(self.embedding_model)
        store_flow.add_node(self.vector_store)

        #-----adding edges
        store_flow.add_edge("START", "PdfLoader|extract_pdf_text")
        store_flow.add_edge("PdfLoader|extract_pdf_text", "CombinePages|combine_pages")
        store_flow.add_edge("CombinePages|combine_pages", "SplitText|split_text")
        store_flow.add_edge("SplitText|split_text", "Embeddings|encode")
        store_flow.add_edge("Embeddings|encode", "DocumentStore|store")
        store_flow.add_edge("DocumentStore|store", "END")


        #---adding data sources
        store_flow.add_data_source("PdfLoader|extract_pdf_text|loaded_file", "INPUTS|file")
        store_flow.add_data_source("CombinePages|combine_pages|pages", "PdfLoader|extract_pdf_text|doc_pages")
        store_flow.add_data_source("SplitText|split_text|text", "CombinePages|combine_pages|text")
        store_flow.add_data_source("Embeddings|encode|sentences", "SplitText|split_text|chunks")
        store_flow.add_data_source("DocumentStore|store|vectors", "Embeddings|encode|embeddings")
        store_flow.add_data_source("DocumentStore|store|metadata", "SplitText|split_text|chunks")

        store_flow.finalize()

        self.store_flow = store_flow


    def setup_retrieve_flow(self):
        print("Setting up retrieve flow")


        #------ Creating the Workflow ------
        retrieve_flow = Flow("DocChat")

        #-----Adding the Nodes
        retrieve_flow.add_node(self.embedding_model2)
        retrieve_flow.add_node(self.vector_store)
        retrieve_flow.add_node(self.promptNode)
        retrieve_flow.add_node(self.llm_node)


        #-----_adding the edges
        retrieve_flow.add_edge("START", "Embeddings2|encode")
        retrieve_flow.add_edge("Embeddings2|encode", "DocumentStore|search")
        retrieve_flow.add_edge("DocumentStore|search", "Prompt|generate_prompt_openai")
        retrieve_flow.add_edge("Prompt|generate_prompt_openai", "LLM|call_llm")
        retrieve_flow.add_edge("LLM|call_llm", "END")


        #Data sources

        llm_instructions = "You are a smart assistant. Answer the user query purely based on the context provided. Do not speculate or make up any information. If the information requested is not found in the context respond with: Sorry the information you specified cannot be found in the context you specified."

        retrieve_flow.add_data_source("Embeddings2|encode|sentences", "INPUTS|query")

        retrieve_flow.add_data_source("DocumentStore|search|query_vector", "Embeddings2|encode|embeddings")
        retrieve_flow.set_node_input("DocumentStore|search|k", 2)

        retrieve_flow.set_node_input("Prompt|generate_prompt_openai|instructions", llm_instructions)
        retrieve_flow.add_data_source("Prompt|generate_prompt_openai|context", "DocumentStore|search|results")
        retrieve_flow.add_data_source("Prompt|generate_prompt_openai|query", "INPUTS|query")

        retrieve_flow.add_data_source("LLM|call_llm|messages", "Prompt|generate_prompt_openai|messages")
        retrieve_flow.set_node_input("LLM|call_llm|tools", [])

        #output of the the chat node
        retrieve_flow.set_outputs(['LLM|call_llm|content'])

        retrieve_flow.finalize()

        self.retrieve_flow = retrieve_flow







    def setup_routes(self):

        @self.api.get("/")
        async def load_index():
            return {"message": "Welcome to DocChat API"}


        @self.api.get("/api/history")
        async def load_history():
            return {"chats": self.chat_history}


        @self.api.post("/api/store")
        async def store_pdf(file: UploadFile = File(...)):

            file_content = await file.read()
            self.store_flow.run({"file": file_content})
            
            return {"message": "PDF stored successfully"}


        @self.api.post("/api/chat")
        async def query(chat_input: ChatInput):
            chat_response = self.retrieve_flow.run({"query": [chat_input.query]})
            self.chat_history.insert(0, {"query":  chat_input.query, "response": chat_response})
            return {"chat_response": chat_response}


        @self.api.get("/api/document")
        async def load_document():
            print("Loading document")
            pages = self.store_flow.graph_state.get_values("PdfLoader|extract_pdf_text","doc_pages")
            return {"doc_pages": pages}


    def run_api(self):
        uvicorn.run(self.api, host="0.0.0.0", port=6031)


    def store_file(self, file: UploadFile):
        self.store_flow.run(file)


    def chat(self, query: str):
        self.retrieve_flow.run(query)
        chat_response = self.chat_history.append({"query": query, "response": response})
        return chat_response



if __name__ == "__main__":
    app = DocChatApp()
    app.run_api()