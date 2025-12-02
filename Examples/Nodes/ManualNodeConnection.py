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
QuickStart module for getting started with Laeyerz
in the Laeyerz framework.
"""

from laeyerz.flow.Flow import Flow
from laeyerz.flow.Node import Node
from laeyerz.flow.AppState import AppState



params = {}


def model0(input0:str)->(str):

    print("Model 0 :", input0)

    output = input0+"_model0"
    outputs = {
        "output0":output
    }

    return outputs

node0 = Node("Model0")
node0_inputs = [
    {
        "name":"input0",
        "type":"str",
        "description":"Input to the model",
        "sourceType":"input"
    }
]
node0_outputs = [
    {
        "name":"output0",
        "type":"str",
        "description":"Output from the model"
    }
]
node0.set_function("model0",model0, params, node0_inputs, node0_outputs)






def model1(input1:str)->(str):

    print("Model 1 :", input1)

    output = input1 + "_model1"
    outputs = {
        "output1":output
    }

    return outputs


node1 = Node("Model1")
node1_inputs = [
    {
        "name":"input1",
        "type":"str",
        "description":"Input to the model",
        "sourceType":"input"
    }
]
node1_outputs = [
    {
        "name":"output1",
        "type":"str",
        "description":"Output from the model"
    }
]
node1.set_function("model1",model1, params, node1_inputs, node1_outputs)


#run the flow
input_data = {
    "input0": "Hello, world!"
}


outputs0 = node0.run(input_data)
input1_data = {
    "input1": outputs0["output0"]
}
outputs1 = node1.run(input1_data)


print("Output0 : ", outputs0)
print("Output1 : ", outputs1)
