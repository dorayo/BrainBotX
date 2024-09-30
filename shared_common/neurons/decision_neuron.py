# common/neurons/decision_neuron.py
from .base_neuron import BaseNeuron

class DecisionNeuron(BaseNeuron):
    def __init__(self, session_id, dendrite_input, action=None, context=None, synapse_state=None):
        super().__init__(session_id, dendrite_input, synapse_state=synapse_state)
        self.action = action  # 决策生成的动作
        self.context = context  # 决策时考虑的上下文信息

    def to_json(self):
        base_data = super().to_json()
        base_data["action"] = self.action
        base_data["context"] = self.context
        return base_data
