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
from laeyerz.utils.ExportToView import export_to_view

params = {}

# =========================
# Node 1 – OrderParser
# =========================

def parse_order(order: dict):

    print("OrderParser received:", order)

    subtotal = 0
    for item in order["items"]:
        subtotal += item["price"] * item["qty"]

    print("Subtotal:", subtotal)

    return {
        "subtotal": subtotal
    }

node1 = Node("OrderParser")

node1_inputs = [
    {
        "name": "order",
        "type": "dict",
        "description": "Customer order",
        "inputType": "source",
        "source": "INPUTS|order",
        "value": None
    }
]

node1_outputs = [
    {
        "name": "subtotal",
        "type": "float",
        "description": "Subtotal of the order"
    }
]

node1.set_function("parse_order", parse_order, params, node1_inputs, node1_outputs)


# =========================
# Node 2 – TaxCalculator
# =========================

def calculate_tax(subtotal: float):

    print("TaxCalculator received subtotal:", subtotal)

    tax = subtotal * 0.18  # 18% GST
    #total = subtotal + tax

    print("Tax:", tax)

    return {
        "tax": tax,
    }

node2 = Node("TaxCalculator")

node2_inputs = [
    {
        "name": "subtotal",
        "type": "float",
        "description": "Subtotal from OrderParser",
        "inputType": "source",
        "source": "OrderParser|parse_order|subtotal",
        "value": None
    }
]

node2_outputs = [
    {"name": "tax", "type": "float", "description": "Tax amount"},
    #{"name": "final_total", "type": "float"}
]

node2.set_function("calculate_tax", calculate_tax, params, node2_inputs, node2_outputs)


# =========================
# Node 3 – InvoiceGenerator
# =========================

def generate_invoice(order: dict, subtotal: float, tax: float):

    print("InvoiceGenerator received raw order + subtotal")

    invoice_text = f"""
    Invoice ID: {order['order_id']}
    Customer: {order['customer_name']}
    Subtotal: ₹{subtotal}
    Tax: ₹{tax}
    Total: ₹{subtotal + tax}
    """

    print("Invoice Text:", invoice_text)

    return {
        "invoice_text": invoice_text
    }

node3 = Node("InvoiceGenerator")

node3_inputs = [
    {
        "name": "order",
        "type": "dict",
        "description": "Original order",
        "inputType": "source",
        "source": "INPUTS|order",
        "value": None
    },
    {
        "name": "subtotal",
        "type": "float",
        "description": "Subtotal from OrderParser",
        "inputType": "source",
        "source": "OrderParser|parse_order|subtotal",
        "value": None
    },
    {
        "name": "tax",
        "type": "float",
        "description": "Tax from TaxCalculator",
        "inputType": "source",
        "source": "TaxCalculator|calculate_tax|tax",
        "value": None
    }
]

node3_outputs = [
    {
        "name": "invoice_text",
        "type": "str",
        "description": "Generated invoice"
    }
]

node3.set_function("generate_invoice", generate_invoice, params, node3_inputs, node3_outputs)


# =========================
# Build Flow
# =========================

flow = Flow("ECommerce Order Flow")

flow.add_node(node1)
flow.add_node(node2)
flow.add_node(node3)

flow.add_edge("START", "OrderParser|parse_order")
flow.add_edge("OrderParser|parse_order", "TaxCalculator|calculate_tax")
flow.add_edge("TaxCalculator|calculate_tax", "InvoiceGenerator|generate_invoice")
flow.add_edge("InvoiceGenerator|generate_invoice", "END")

#data connections

flow.add_data_source("OrderParser|parse_order|subtotal", "INPUTS|subtotal")
flow.add_data_source("TaxCalculator|calculate_tax|tax", "INPUTS|tax")
flow.add_data_source("InvoiceGenerator|generate_invoice|invoice_text", "INPUTS|invoice_text")

flow.finalize()

# =========================
# Run Example
# =========================

input_data = {
    "order": {
        "order_id": "ORD1001",
        "customer_name": "Anil",
        "items": [
            {"name": "Laptop", "price": 800, "qty": 1},
            {"name": "Mouse", "price": 20, "qty": 2},
            {"name": "Keyboard", "price": 30, "qty": 1}
        ]
    }
}

flow.set_outputs(['InvoiceGenerator|generate_invoice|invoice_text'])

output = flow.run(input_data)

print("Final Output:", output)

for key, value in output.items():
    print("------------------",key,"------------------------")
    print("\n")
    print(value)

#export_to_view(flow, "QuickStart_view.json")


#simple_flow.export_flow("QuickStart.json")
#simple_flow.export_run(output)

