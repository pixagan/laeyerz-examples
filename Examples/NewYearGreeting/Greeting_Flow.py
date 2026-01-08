from laeyerz.flow.Node import Node
from laeyerz.flow.Flow import Flow
from laeyerz.nodes.llm.OpenAILLMNode import OpenAILLMNode as LLM
from laeyerz.utils.KeyManager import KeyManager

key_manager = KeyManager("../../.env")

api_key = key_manager.get('OPENAI_API_KEY')


def prompt1(instructions:str, tone:str, max_words:str, query:str)->(dict):
    
    messages = [
        {"role": "developer", "content": instructions},
        {"role": "user", "content":"Tone : " + tone},
        {"role": "user", "content":"Max Words : "+str(max_words)},
        {"role": "user", "content":"Greeting for: " + query}
    ]

    outputs = {
        "prompt": messages
    }
    return outputs

prompt1Node = Node("Prompt1")

prompt1_inputs = [
    {
        "name": "instructions",
        "type": "str",
        "description": "The content to be processed",
        "inputType": "source",
        "source":""
    },
    {
        "name": "tone",
        "type": "str",
        "description": "The content to be processed",
        "inputType": "source",
        "source":""
    },
    {
        "name": "max_words",
        "type": "str",
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
prompt1_outputs = [
    {
        "name": "prompt",
        "type": "list",
        "description": "The output from the node",
        "sourceType": "output"
    }
]
prompt1Node.set_function("prompt", prompt1, {}, prompt1_inputs, prompt1_outputs)


#create LLM node
llm = LLM("TextGen", config={"api_key": api_key})



def prompt2(instructions:str, occasion:str, emoji_density:str, text:str)->(list):

    print("Instructions : ", instructions)
    print("Occasion : ", occasion)
    print("emoji Density : ", emoji_density)
    print("Text : ", text)
    
    ascii_messages = [
        {"role": "developer", "content": instructions},
        {"role": "user", "content":"occasion : " + occasion},
        {"role": "user", "content":"emoji density : " + emoji_density},
        {"role": "user", "content":"query : " + text}
    ]
    
    outputs = {
        "prompt": ascii_messages
    }

    print("Outputs : ", outputs)
    return outputs



prompt2Node = Node("Prompt2")

prompt2_inputs = [
    {
        "name": "instructions",
        "type": "str",
        "description": "The content to be processed",
        "inputType": "source",
        "source":""
    },
    {
        "name": "occasion",
        "type": "str",
        "description": "The content to be processed",
        "inputType": "source",
        "source":""
    },
    {
        "name": "emoji_density",
        "type": "str",
        "description": "The content to be processed",
        "inputType": "source",
        "source":""
    },
    {
        "name": "text",
        "type": "str",
        "description": "The content to be processed",
        "inputType": "source",
        "source":""
    }
]
prompt2_outputs = [
    {
        "name": "prompt",
        "type": "list",
        "description": "The output from the node",
        "sourceType": "output"
    }
]
prompt2Node.set_function("prompt", prompt2, {}, prompt2_inputs, prompt2_outputs)


llm2 = LLM("ASCIIGen", config={"api_key": api_key})


greetingFlow = Flow("GreetingFlow")

greetingFlow.add_node(prompt1Node)
greetingFlow.add_node(llm)
greetingFlow.add_node(prompt2Node)
greetingFlow.add_node(llm2)


greetingFlow.add_edge("START", "Prompt1|prompt")
greetingFlow.add_edge("Prompt1|prompt", "TextGen|call_llm")
greetingFlow.add_edge("TextGen|call_llm", "Prompt2|prompt")
greetingFlow.add_edge("Prompt2|prompt", "ASCIIGen|call_llm")
greetingFlow.add_edge("ASCIIGen|call_llm", "END")


text_instructions = "You are a greeting generator. Given the receipient name and description and mood of greeting, generate ONE custom Happy New Year message including emojis."
card_instructions = """Convert the Happy New Year Message into a colourful text-based greeting card.
    Combine emoji decorations, simple ascii drawings (fireworks, sparkles etc) with stylized version of the text provided. 
    """



greetingFlow.set_node_input("Prompt1|prompt|instructions", text_instructions)
greetingFlow.add_data_source("Prompt1|prompt|tone", "INPUTS|tone")
greetingFlow.add_data_source("Prompt1|prompt|max_words", "INPUTS|max_words")
greetingFlow.add_data_source("Prompt1|prompt|query", "INPUTS|query")

greetingFlow.add_data_source("TextGen|call_llm|messages", "Prompt1|prompt|prompt")
greetingFlow.set_node_input("TextGen|call_llm|model", "gpt-5-mini")
greetingFlow.set_node_input("TextGen|call_llm|tools", [])

greetingFlow.set_node_input("Prompt2|prompt|instructions", card_instructions)
greetingFlow.add_data_source("Prompt2|prompt|occasion", "INPUTS|occasion")
greetingFlow.add_data_source("Prompt2|prompt|emoji_density", "INPUTS|emoji_density")
greetingFlow.add_data_source("Prompt2|prompt|text", "TextGen|call_llm|content")

greetingFlow.add_data_source("ASCIIGen|call_llm|messages", "Prompt2|prompt|prompt")
greetingFlow.set_node_input("ASCIIGen|call_llm|model", "gpt-5-mini")
greetingFlow.set_node_input("ASCIIGen|call_llm|tools", [])



greetingFlow.set_node_outputs(['ASCIIGen|call_llm|content'])

greetingFlow.finalize()

query = "For my friend, Friends"


outputs = greetingFlow.run({
    "query":query,
    "tone":"Casual & upbeat",
    "max_words":20,
    "occasion":"Christmas",
    "emoji_density":"high"
})


print("Output 1 : ", outputs)