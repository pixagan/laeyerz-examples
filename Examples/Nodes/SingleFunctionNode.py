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
Creating a single function node module for getting started with Laeyerz
in the Laeyerz framework.
"""

from laeyerz.flow.Flow import Flow
from laeyerz.flow.Node import Node
from laeyerz.flow.AppState import AppState

## Create a Functional Node
params = {}

def inputnode(input0:str)->(str):
    return input0


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


node_inputs = {
    "input0":"Hello"
}
outputs = node0.run(node_inputs)

print("Outputs:", outputs)





