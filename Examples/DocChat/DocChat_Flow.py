import numpy as np
from laeyerz.flow.Flow import Flow
from laeyerz.flow.Node import Node
from laeyerz.nodes.llm.OpenAILLMNode import OpenAILLMNode as LLM
from laeyerz.nodes.fileloaders.PdfLoader import PdfLoader
from laeyerz.nodes.dataprocessors.TextProcessor import TextProcessorNode
from laeyerz.nodes.embeddings.SentenceTransformerNode import SentenceTransformerNode as Embeddings
from laeyerz.nodes.vectorstores.FaissNode import FaissNode as VectorStore
from laeyerz.utils.KeyManager import KeyManager


key_manager = KeyManager("../../.env")


#-------------------- Workflow 1 : Document Store -----

#-------Nodes -------
pdf_loader = PdfLoader("PdfLoader")

#Combine text into a single string
combine_text  = TextProcessorNode("CombinePages")

#Split Text
split_text = TextProcessorNode("SplitText")

#Text to Embeddings
embedding_model = Embeddings("Embeddings")

#Create Vector Store
vector_store = VectorStore("DocumentStore")

#-----Creating thh Flow
store_flow = Flow("DocumentStore")

#-----adding nodes
store_flow.add_node(pdf_loader)
store_flow.add_node(combine_text)
store_flow.add_node(split_text)
store_flow.add_node(embedding_model)
store_flow.add_node(vector_store)

#-----adding edges
store_flow.add_edge("START", "PdfLoader|load_pdf")
store_flow.add_edge("PdfLoader|load_pdf", "CombinePages|combine_pages")
store_flow.add_edge("CombinePages|combine_pages", "SplitText|split_text")
store_flow.add_edge("SplitText|split_text", "Embeddings|encode")
store_flow.add_edge("Embeddings|encode", "DocumentStore|store")
store_flow.add_edge("DocumentStore|store", "END")


#---adding data sources
store_flow.add_data_source("PdfLoader|load_pdf|filename", "INPUTS|filename")
store_flow.add_data_source("CombinePages|combine_pages|pages", "PdfLoader|load_pdf|doc_pages")
store_flow.add_data_source("SplitText|split_text|text", "CombinePages|combine_pages|text")
store_flow.add_data_source("Embeddings|encode|sentences", "SplitText|split_text|chunks")
store_flow.add_data_source("DocumentStore|store|vectors", "Embeddings|encode|embeddings")
store_flow.add_data_source("DocumentStore|store|metadata", "SplitText|split_text|chunks")

store_flow.finalize()



#Calling doc store to store doc
filename = "Wikipedia_Snippet_long.pdf"
store_flow.run({"filename":filename})

#----------_Workflow 2 : Document chat ---------------------

#-custom prompt construction node
def prompt(instructions:str, context:str, query:str)->(dict):

    print("Context : ", context )

    context_text = ""
    for chunk in context:
        context_text += chunk["metadata"] + "\n"
    
    messages = [
        {"role": "developer", "content": instructions},
        {"role": "user", "content":"Context : "+ context_text},
        {"role": "user", "content":"Query : " + query[0]}
    ]

    outputs = {
        "prompt": messages
    }
    return outputs


promptNode = Node("Prompt")

prompt_inputs = [
    {
        "name": "instructions",
        "type": "str",
        "description": "The content to be processed",
        "inputType": "source",
        "source":""
    },
    {
        "name": "context",
        "type": "list",
        "description": "The content to be processed",
        "inputType": "source",
        "source":""
    },
    {
        "name": "query",
        "type": "str",
        "description": "The content to be processed",
        "inputType": "source",
        "source":""
    }
]
prompt_outputs = [
    {
        "name": "prompt",
        "type": "list",
        "description": "The output from the node",
        "sourceType": "output"
    }
]
promptNode.set_function("prompt", prompt, {}, prompt_inputs, prompt_outputs)


#LLM Node
api_key = key_manager.get('OPENAI_API_KEY')
llm_node = LLM("LLM", config={"api_key": api_key})

#------ Creating the Workflow ------
chat_flow = Flow("DocChat")

#-----Adding the Nodes
chat_flow.add_node(embedding_model)
chat_flow.add_node(vector_store)
chat_flow.add_node(promptNode)
chat_flow.add_node(llm_node)


#-----_adding the edges
chat_flow.add_edge("START", "Embeddings|encode")
chat_flow.add_edge("Embeddings|encode", "DocumentStore|search")
chat_flow.add_edge("DocumentStore|search", "Prompt|prompt")
chat_flow.add_edge("Prompt|prompt", "LLM|call_llm")
chat_flow.add_edge("LLM|call_llm", "END")


#Data sources

llm_instructions = "You are a smart assistant. Answer the user query purely based on the context provided. Do not speculate or make up any information. If the information requested is not found in the context respond with: Sorry the information you specified cannot be found in the context you specified."

chat_flow.add_data_source("Embeddings|encode|sentences", "INPUTS|query")

chat_flow.add_data_source("DocumentStore|search|query_vector", "Embeddings|encode|embeddings")
chat_flow.set_node_input("DocumentStore|search|k", 2)

chat_flow.set_node_input("Prompt|prompt|instructions", llm_instructions)
chat_flow.add_data_source("Prompt|prompt|context", "DocumentStore|search|results")
chat_flow.add_data_source("Prompt|prompt|query", "INPUTS|query")

chat_flow.add_data_source("LLM|call_llm|messages", "Prompt|prompt|prompt")
chat_flow.set_node_input("LLM|call_llm|model", "gpt-5-mini")
chat_flow.set_node_input("LLM|call_llm|tools", [])

#output of the the chat node
chat_flow.set_node_outputs(['LLM|call_llm|content'])

chat_flow.finalize()





#chatting with the document
user_query = ["What is the main topic of the document?"]
outputs = chat_flow.run({"query":user_query})

#view the output
for key, value in outputs.items():
    print("------------------",key,"------------------------")
    print("\n")
    print(value)