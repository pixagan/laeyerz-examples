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

from laeyerz.flow.Flow import Flow
from laeyerz.nodes.llm.OpenAILLMNode import OpenAILLMNode as LLM
from laeyerz.nodes.fileloaders.PdfLoader import PdfLoader
from laeyerz.nodes.dataprocessors.TextProcessor import TextProcessorNode
#from laeyerz.nodes.DataProcessors import TextProcessor

#Flow 1

flow1 = Flow("DocSummarizer")

#Snippet from Wikipedia
#Pdf Input Node
pdf_loader = PdfLoader("PdfLoader")
file = pdf_loader.load_pdf("Wikipedia_Snippet_long.pdf")
print(file)

#pdf_input_node.input_map([("pdf_path", "INPUTS:pdf_path")])
#flow1.add_node(pdf_input_node)

print("--------------------------------")

# #Text Processor
combine_text  = TextProcessorNode("CombinePages")
document_text = combine_text.combine_pages(file)
print(document_text)
# document_processor_node.input_map([("text", "pdf_input_node:text")])
# flow1.add_node(document_processor_node)


#LLM Node
llm_node = LLM("LLM")
llm_output = llm_node.call_llm(messages=[
    {"role": "system", "content": "You are a helpful assistant that summarizes documents. Summarize the document provided below"},
    {"role": "user", "content": document_text}],
    model="gpt-4o-mini",
    tools=[]
    )

print("-----Document Summary: --------------------------------")
print(llm_output["content"])



#Building the flow for automation

# flow1.add_node(pdf_loader)
# flow1.add_node(combine_text)
# flow1.add_node(llm_node)

# flow1.add_edge("START", "PDFLoader|load_pdf")
# flow1.add_edge("PDFLoader|load_pdf", "CombinePages|combine_pages")
# flow1.add_edge("CombinePages|combine_pages", "LLM|call_llm")
# flow1.add_edge("LLM|call_llm", "END")


# input_data = {}
# output = flow1.run(input_data)



