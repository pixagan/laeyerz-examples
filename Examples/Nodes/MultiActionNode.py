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


class CustomNode1(Node):

    def __init__(self, name:str):
        super().__init__(name)
        
        self.add_actions()
        
    def add_actions(self):

        model0_inputs = [
            {
                "name":"input0",
                "type":"str",
                "description":"Input to the model",
                "inputType":"source",
                "source":"INPUTS|input0",
                "value":None
            }
        ]
        model0_outputs = [
            {
                "name":"output0",
                "type":"str",
                "description":"Output from the model"
            }
        ]

        self.add_action("model0", self.model0, params, model0_inputs, model0_outputs, True)

        model1_inputs = [
            {
                "name":"input0",
                "type":"str",
                "description":"Input to the model",
                "inputType":"source",
                "source":"Model0|model0|output0",
                "value":None
            }
        ]
        model1_outputs = [
            {
                "name":"output0",
                "type":"str",
                "description":"Output from the model"
            }
        ]

        self.add_action("model1", self.model1, params, model1_inputs, model1_outputs)



    def model0(self, input0:str)->(str):
        print("Model 0 :", input0)
        output = input0+"_model0"
        outputs = {
            "output0":output
        }
        return outputs

    def model1(self, input0:str)->(str):
        print("Model 1 :", input0)
        output = input0+"_model1"
        outputs = {
            "output0":output
        }
        return outputs



params = {}
cn1 = CustomNode1("CN1")

node_inputs = {
    "input0":"Hello"
}
outputs = cn1.run("model0", node_inputs)

print("Outputs:", outputs)





