# common/neurons/perception_neuron.py
from .base_neuron import BaseNeuron

class PerceptionNeuron(BaseNeuron):
    def __init__(self, session_id, dendrite_input, extracted_information=None, synapse_state=None):
        super().__init__(session_id, dendrite_input, synapse_state=synapse_state)
        self.extracted_information = extracted_information  # 感知到的具体信息（如运单号）
    
    def to_json(self):
        base_data = super().to_json()
        base_data["extracted_information"] = self.extracted_information
        return base_data
