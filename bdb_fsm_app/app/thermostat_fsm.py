class FSM:

    def __init__(self):
        self.states = {'heating':{'heating_rate':1}, 'cooling':{'heating_rate':0}}
        self.initial_state = list(self.states.keys())[0]
        self.inputs = {'temperature':0}
        self.transitions = [
            {'trigger': 'heat', 'source': ['heating', 'cooling'], 'dest': 'heating', 'conditions':'check_low_temp'},
            {'trigger': 'cool', 'source': ['heating', 'cooling'], 'dest': 'cooling', 'conditions':'check_high_temp'}
        ]

    def check_low_temp(self):
        if self.inputs['temperature'] < 18:
            return True
        else:
            return False

    def check_high_temp(self):
        if self.inputs['temperature'] > 22:
            return True
        else:
            return False

    def get_output(self, in_state = None):
        if in_state == None:
            in_state = self.state
        return self.states[in_state]

    def get_transition(self):
        for transition in self.transitions:
            func = getattr(self, 'may_' + transition['trigger'])
            if func():
                return getattr(self, transition['trigger'])
        return None

    def get_input_keys(self):
        return list(self.inputs.keys)

    def update_inputs(self, dict):
        if self.inputs.keys() == dict.keys():
            flag = 0
            for key, value in dict.items():
                if not isinstance(value, type(self.inputs[key])):
                    flag = 1
            if flag == 0:
                self.inputs = {k: dict[k] for k in self.inputs}
                return True
        return False

    def initialize_fsm(self, init_dict):
        self.update_inputs(init_dict['data']['input'])
        init_state = init_dict['data']['to']
        transition_func = getattr(self, 'to_' + init_state)
        transition_func()

    def run_fsm(self, input_dict):
        initial_state=self.state
        final_state=self.state
        self.update_inputs(input_dict)
        transition = self.get_transition()
        if transition is not None:
            transition()
            final_state=self.state
        output = self.get_output()

        fsm_info = {
            'data':{
                'entity': 'fsm',	
                'from':initial_state,
                'to': final_state,
                'input' : self.inputs,
                'output': self.get_output()
            }
        }

        return fsm_info
        
        
    def verify_transition(self, info_dict):
        init_state = info_dict["data"]["from"]
        final_state = info_dict["data"]["to"]
        inputs = info_dict["data"]["input"]
        to_init_state = getattr(self, 'to_' + init_state)
        to_init_state()
        self.update_inputs(inputs)
        to_final_state = getattr(self, 'may_' + final_state)
        if to_final_state():
            return True
        else:
            return False
