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

import numpy as np


from laeyerz.flow.Flow import Flow
from laeyerz.nodes.llm.OpenAILLMNode import OpenAILLMNode as LLM
from laeyerz.nodes.fileloaders.PdfLoader import PdfLoader
from laeyerz.nodes.dataprocessors.TextProcessor import TextProcessorNode
from laeyerz.nodes.embeddings.SentenceTransformerNode import SentenceTransformerNode as Embeddings
from laeyerz.nodes.vectorstores.FaissNode import FaissNode as VectorStore
from laeyerz.utils.KeyManager import KeyManager

key_manager = KeyManager("YOUR API KEY PATH HERE")
api_key = key_manager.get('OPENAI_API_KEY')

#Flow 1
flow1 = Flow("DocumentStore")

#Pdf Input Node
#Snippet from Wikipedia
pdf_loader = PdfLoader("PdfLoader")
file = pdf_loader.load_pdf("Wikipedia_Snippet_long.pdf")

#Combine text into a single string
combine_text  = TextProcessorNode("CombinePages")
document_text = combine_text.combine_pages(file)
print(document_text)

#Split Text
split_text = TextProcessorNode("SplitText")
chunks = split_text.split_text(document_text)
print(chunks)

#Text to Embeddings
embedding_model = Embeddings("Embeddings")
embeddings = embedding_model.encode(chunks)
print(embeddings)

#Create Vector Store
vector_store = VectorStore("VectorStore")
vector_store.store(embeddings, chunks)



print("-------------Document Chat ------------------")
# Flow 2
flow1 = Flow("DocChat")


user_query = "What is the main topic of the document?"

embedding_query = embedding_model.encode(user_query)
print("Embedding Query : ")
print(embedding_query)

print("-------------Context-------------")
print(np.array(embedding_query).shape)
arr = np.array(embedding_query).reshape(1,-1)
print(arr.shape)
context = vector_store.search(np.array(embedding_query).reshape(1,-1))
print(context)

context_text = ""
for chunk in context:
    context_text += chunk["metadata"] + "\n"

print("-------------Context Text-------------")
#print(context_text)

# #LLM Node
llm_node = LLM("LLM", config={"api_key": api_key})
llm_output = llm_node.call_llm(messages=[
    {"role": "system", "content": "You are a helpful assistant that summarizes documents. Answer the user query based on the context provided."},
    {"role": "user", "content": "context: " + context_text},
    {"role": "user", "content": "user_query: " + user_query},
    ],
    model="gpt-4o-mini",
    tools=[]
    )

print("-------------LLM Output-------------")
print(llm_output["content"])