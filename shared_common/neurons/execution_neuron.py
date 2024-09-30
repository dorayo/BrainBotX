# common/neurons/execution_neuron.py
from .base_neuron import BaseNeuron

class ExecutionNeuron(BaseNeuron):
    def __init__(self, session_id, dendrite_input, execution_result=None, synapse_state=None):
        super().__init__(session_id, dendrite_input, synapse_state=synapse_state)
        self.execution_result = execution_result  # 执行的结果（成功或失败）

    def to_json(self):
        base_data = super().to_json()
        base_data["execution_result"] = self.execution_result
        return base_data
