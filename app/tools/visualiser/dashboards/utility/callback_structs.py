from dash.dependencies import Input, Output, State

class CallbackComponent:
    def __init__(self, components):
        self._components = components

    def __getattr__(self, name):
        for component in self._components:
            if name == component.component_id:
                return component.component_id
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __iter__(self):
        for component in self._components:
            if isinstance(component, (Input, Output, State)):
                yield component

    def add(self,component):
        self._components.append(component)

class Callback:
    def __init__(self, function,inputs, outputs, states=None):
        self._function = function

        input_objs = []
        for identifier,properties in inputs.items():
            if isinstance(properties,list):
                for property in properties:
                    input_objs.append(Input(identifier, property))
            else:
                input_objs.append(Input(identifier, properties))

        output_objs = []
        for identifier,properties in outputs.items():
            if isinstance(properties,list):
                for property in properties:
                    output_objs.append(Output(identifier, property))
            else:
                output_objs.append(Output(identifier, properties))


        if states is None:
            states = {}
        state_objs = []
        for identifier,properties in states.items():
            if isinstance(properties,list):
                for property in properties:
                    state_objs.append(State(identifier, property))
            else:
                state_objs.append(State(identifier, properties))

        self.inputs = CallbackComponent(input_objs)
        self.outputs = CallbackComponent(output_objs)
        self.states = CallbackComponent(state_objs)
    
    def add_input(self,identifier,properties):
        self.inputs.add(Input(identifier,properties))

    def add_output(self,identifier,properties):
        self.inputs.add(Output(identifier,properties))

    def add_state(self,identifier,properties):
        self.inputs.add(State(identifier,properties))

    def to_struct(self):
        return (
            self._function,
            self.inputs,
            self.outputs,
            self.states
        )

class Callbacks:
    def __init__(self, **callbacks):
        for callback_name, callback in callbacks.items():
            setattr(self, callback_name, callback)

    def __iter__(self):
        for identifier, callback in self.__dict__.items():
            if isinstance(callback, Callback):
                yield identifier, callback

    def new_callback(self,callback_name,function,inputs,outputs,states=None):
        callback = Callback(function,inputs,outputs,states)
        self.add_callback(callback_name,callback)

    def add_callback(self,callback_name,callback):
        setattr(self,callback_name,callback)

    def update_callback(self,callback_name,inputs=None,
                        outputs=None,states=None):
        for name,callback in self:
            if name == callback_name:
                if inputs is not None:
                    for identifier,properties in inputs.items():
                        callback.add_input(identifier,properties)
                if outputs is not None:
                    for identifier,properties in outputs.items():
                        callback.add_output(identifier,properties)
                if states is not None:
                    for identifier,properties in states.items():
                        callback.add_state(identifier,properties)
