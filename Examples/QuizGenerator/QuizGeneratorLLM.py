from laeyerz.utils.KeyManager import KeyManager

from laeyerz.flow.Flow import Flow
from laeyerz.flow.Node import Node

#from laeyerz_nodes.llm.OpenAINode import OpenAINode as LLM
from laeyerz_nodes.llm.OpenAINode import OpenAINode as LLM

km = KeyManager('YOUR_API_KEY_PATH_HERE')


generator_llm = LLM('Generator', config={"api_key":km['OPENAI_API_KEY'], "model":"gpt-5-mini"})

quizzer_llm   = LLM('Quizzer', config={"api_key":km['OPENAI_API_KEY'], "model":"gpt-5-mini"})

html_llm = LLM('HTMLGenerator', config={"api_key":km['OPENAI_API_KEY'], "model":"gpt-5-mini"})

params = {}

def concept_generator(topic:str, level:str)->(str):

    instructions = """ 
    Given the topic and the level specified, generate a lesson on the topic.
    """

    messages = [
                {"role": "developer", "content": instructions},
                {"role": "user", "content": "The topic is : " + topic + "and the level is " + level},   
            ]

    response = generator_llm.call_llm(messages)

    output = response['message'].content

    return output

concept_node = Node("Concept")
concept_inputs = [
    {
        "name":"topic",
        "type":"str",
        "description":"Input to the model",
        "inputType":"source",
        "source":"",
        "value":None
    },
    {
        "name":"level",
        "type":"str",
        "description":"Input to the model",
        "inputType":"source",
        "source":"",
        "value":None
    }
]
concept_outputs = [
    {
        "name":"concept",
        "type":"str",
        "description":"Output from the model"
    }
]
concept_node.set_function("concept",concept_generator, params, concept_inputs, concept_outputs)



def quiz_generator(concept:str, level:str, nQuestions:int)->(str):

    instructions = """ 
    Convert the concept into a quiz into the number of questions specified at the level specified.
    Only use the information provided to create the questions.
    Respond in the JSON format:
    {
      "nQuestions":5,
      "questions":[
         {
           "question" : "Question 1",
           "options" : [],
           "correct_answer": <index of correct option>
         }
      ]
    }
    """

    messages = [
                {"role": "developer", "content": instructions},
                {"role": "user", "content": "The concept is : " + concept + "at the level " + level + "Number of Questions " + str(nQuestions)},
                
            ]

    response = generator_llm.call_llm(messages)

    output = response['message'].content

    return output



quiz_node = Node("Quizzer")
quiz_inputs = [
    {
        "name":"concept",
        "type":"str",
        "description":"Input to the model",
        "inputType":"source",
        "source":"",
        "value":None
    },
    {
        "name":"level",
        "type":"str",
        "description":"Input to the model",
        "inputType":"source",
        "source":"",
        "value":None
    },
    {
        "name":"nQuestions",
        "type":"str",
        "description":"Input to the model",
        "inputType":"source",
        "source":"",
        "value":None
    }
]
quiz_outputs = [
    {
        "name":"quiz",
        "type":"str",
        "description":"Output from the model"
    }
]
quiz_node.set_function("quiz",quiz_generator, params, quiz_inputs, quiz_outputs)


def html_generator(quiz:str)->(str):

    instructions = """ 
    You will be provided a quiz in JSON format. Convert the quiz provided into a interactive html page.
    Keep the correct answer hidden and when the student hits the submit button, show the correct answer along with the correct grade.
    Respond in the following format:
    <HTML>
      Website HTML code
    </HTML>
    """

    messages = [
                {"role": "developer", "content": instructions},
                {"role": "user", "content": "Quiz : " + quiz},
            ]

    response = html_llm.call_llm(messages)

    output = response['message'].content

    return output

html_node = Node("HTMLGenerator")
html_inputs = [
    {
        "name":"quiz",
        "type":"str",
        "description":"Input to the model",
        "inputType":"source",
        "source":"",
        "value":None
    }
]
html_outputs = [
    {
        "name":"htmlpage",
        "type":"str",
        "description":"Output from the model"
    }
]
html_node.set_function("htmlpage",html_generator, params, html_inputs, html_outputs)




#Flow
quiz_gen = Flow('Quiz Generator')

#Nodes
quiz_gen.add_node(concept_node)
quiz_gen.add_node(quiz_node)
quiz_gen.add_node(html_node)

#Edges
quiz_gen.add_edge("START", "Concept|concept")
quiz_gen.add_edge("Concept|concept", "Quizzer|quiz")
quiz_gen.add_edge("Concept|concept", "Quizzer|quiz")
quiz_gen.add_edge("Quizzer|quiz", "HTMLGenerator|htmlpage")
quiz_gen.add_edge("HTMLGenerator|htmlpage", "END")


#Connections
quiz_gen.add_data_source("Concept|concept|topic", "INPUTS|topic")
quiz_gen.add_data_source("Concept|concept|level", "INPUTS|level")

quiz_gen.add_data_source("Quizzer|quiz|concept", "Concept|concept|concept")
quiz_gen.add_data_source("Quizzer|quiz|level", "INPUTS|level")
quiz_gen.add_data_source("Quizzer|quiz|nQuestions", "INPUTS|nQuestions")

quiz_gen.add_data_source("HTMLGenerator|htmlpage|quiz", "Quizzer|quiz|quiz")


quiz_gen.set_outputs(['HTMLGenerator|htmlpage|htmlpage'])

inputs = {
    "topic":'Neural Networks',
    "level":'beginner',
    "nQuestions":"5"
}

outputs = quiz_gen.run(inputs)

print("Outputs : ", outputs)

print(outputs['HTMLGenerator|htmlpage|htmlpage'])
