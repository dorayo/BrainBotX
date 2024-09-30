# common/neurons/base_neuron.py
import json

class BaseNeuron:
    def __init__(self, session_id, dendrite_input, axon_output=None, synapse_state=None):
        self.session_id = session_id  # 会话ID，唯一标识请求
        self.dendrite_input = dendrite_input  # 输入数据，如感知数据、历史数据
        self.axon_output = axon_output if axon_output else {}  # 输出数据
        self.synapse_state = synapse_state if synapse_state else {}  # 神经元状态，信号状态

    def to_json(self):
        return json.dumps({
            "session_id": self.session_id,
            "dendrite_input": self.dendrite_input,
            "axon_output": self.axon_output,
            "synapse_state": self.synapse_state
        })

    @staticmethod
    def from_json(json_str):
        data = json.loads(json_str)
        return BaseNeuron(
            session_id=data["session_id"],
            dendrite_input=data["dendrite_input"],
            axon_output=data.get("axon_output", {}),
            synapse_state=data.get("synapse_state", {})
        )
