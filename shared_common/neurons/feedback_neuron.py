# common/neurons/feedback_neuron.py
from .base_neuron import BaseNeuron

class FeedbackNeuron(BaseNeuron):
    def __init__(self, session_id, dendrite_input, feedback_data=None, synapse_state=None):
        super().__init__(session_id, dendrite_input, synapse_state=synapse_state)
        self.feedback_data = feedback_data  # 反馈数据，例如执行的效果

    def to_json(self):
        base_data = super().to_json()
        base_data["feedback_data"] = self.feedback_data
        return base_data
