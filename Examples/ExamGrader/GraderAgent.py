import os
from laeyerz.agent.ToolReasoningAgent import ToolReasoningAgent
from laeyerz_nodes.llm.OpenAINode import OpenAINode as LLM   
from laeyerz.utils.KeyManager import KeyManager

from GraderComparative import comparative_grader_flow
from GraderConsistency import consistency_grader_flow
from GraderRubric import rubric_grader_flow

#Path to .env file with API Keys
km = KeyManager('../../.env')

llm = LLM('Model', config={"api_key":km['OPENAI_API_KEY'], "model":"gpt-5-mini"})

agent = ToolReasoningAgent( name="GraderAgent", config = {
        "api_key_path":'../../.env',
        "reasoner":llm, 
        "role":"You are an exam grader", 
        "instructions":"""You will be provided a subject, question, answer, and submission. You are also given 3 grading tools to use. Depending on the user request the inputs and the type of question, use the relevant grader to evaluate the
        submission. You may use more than one tool if required.""",
        "tools":{}
    }
)


#--------Setting up Tools ----------------------------------
def grade_comparative(subject:str, question:str, answer:str, submission:str):
    outputs = comparative_grader_flow.run({"subject":subject, "question":question, "answer":answer, "submission":submission})
    return outputs['CompareLLM|call_llm|content']

agent.add_tool({
    "name": "grade_comparative",
    "description": "Grade a comparative question",
    "parameters": [
        {
            "name": "subject",
            "type": "string",
            "description": "The subject of the question"
        },
        {
            "name": "question",
            "type": "string",
            "description": "The question to grade"
        },
        {
            "name": "answer",
            "type": "string",
            "description": "The answer to grade"
        },
        {
            "name": "submission",
            "type": "string",
            "description": "The submission to grade"
        }
    ],
    "function": grade_comparative
})




def grade_consistency(subject:str, question:str, submission:str):
    outputs = consistency_grader_flow.run({"subject":subject, "question":question, "submission":submission})
    return outputs['ConsistencyLLM|call_llm|content']


agent.add_tool({
    "name": "grade_consistency",
    "description": "Grade a consistency question",
    "parameters": [
        {
            "name": "subject",
            "type": "string",
            "description": "The subject of the question"
        },
        {
            "name": "question",
            "type": "string",
            "description": "The question to grade"
        },
        {
            "name": "submission",
            "type": "string",
            "description": "The submission to grade"
        }
    ],
    "function": grade_consistency
})



def grade_rubric(subject:str, question:str, rubric:str, submission:str):
    outputs = rubric_grader_flow.run({"subject":subject, "question":question, "rubric":rubric, "submission":submission})
    return outputs['RubricLLM|call_llm|content']


agent.add_tool({
    "name": "grade_rubric",
    "description": "Grade a rubric question",
    "parameters": [
        {
            "name": "subject",
            "type": "string",
            "description": "The subject of the question"
        },
        {
            "name": "question",
            "type": "string",
            "description": "The question to grade"
        },
        {
            "name": "rubric",
            "type": "string",
            "description": "The rubric to grade"
        },
        {
            "name": "submission",
            "type": "string",
            "description": "The submission to grade"
        }
    ],
    "function": grade_rubric
})





question_theory = """State Lenz’s Law. Using it, explain how the law of conservation of energy is obeyed in electromagnetic induction."""

answer_theory     = """
Lenz’s law states that:
The direction of induced current in a circuit is such that it opposes the change in magnetic flux that produces it.
This is represented mathematically by the negative sign in Faraday’s law: E=-dΦ/dt

Conservation of Energy Explanation:
When a magnet is moved towards a coil, the magnetic flux linked with the coil changes.An induced current is produced.
The magnetic field due to this induced current opposes the motion of the magnet.Therefore, an external force must be applied to keep the magnet moving.The work done by the external force is converted into electrical energy in the circuit.
If the induced current did not oppose the change in flux, energy would be produced without doing work, violating the law of conservation of energy.
Thus, Lenz’s law ensures conservation of energy."""

submission_theory = """Lenz's law states that the direction of induced current in a circuit is such,  that it opposes the change in magnetic flux that produces it.
     Faraday's law Equation can be mathematically represented as E=dΦ/dt
    When a magnet is moved toward a coil the changing flux induces a current whose field opposes the magnet’s approach; an external force must do work against this opposition. That work is converted into electrical energy in the circuit, so no energy is produced for free—Lenz’s law thus ensures conservation of energy.
    """

rubric_theory = """Marking Scheme : Total = 4 Marks, 
    Correct statement of Lenz’s Law : 1 mark,
    Mention of opposition to change in flux	: 0.5 mark,
    Represent Faraday's law Equation E=-dΦ/dt,: 0.5 marks
    Explanation using magnet–coil example :	1 mark, 
    Linking to conservation of energy clearly : 1 mark.
    """


#-------------- Run Agent ------------------------------

agent.run_agent({
    "subject": "Physics",
    "question": question_theory,
    "answer": answer_theory,
    "submission": submission_theory,
    "rubric": rubric_theory
})