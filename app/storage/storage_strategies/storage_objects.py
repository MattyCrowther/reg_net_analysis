class StorageObject():
    def __init__(self, identifier, object_type,
                 properties=None, relationships=None):
                
        self._identifier = identifier
        self._object_type = object_type
        self._properties = properties or {}
        self._relationships = relationships or {}

    @property
    def identifier(self):
        return self._identifier

    @property
    def object_type(self):
        return self._object_type

    @property
    def properties(self):
        return self._properties

    @property
    def relationships(self):
        return self._relationships

    def to_dict(self):
        dict_data = {}
        for k,v in self._properties.items():
            dict_data[k] = v
        dict_data["object_type"] = self.object_type
        return dict_data
    
    def add_property(self, key, value):
        self._properties[key] = value

    def add_relationship(self, key, obj):
        if key not in self._relationships:
            self._relationships[key] = []
        self._relationships[key].append(obj)

    def remove_relationship(self,key,obj):
        if isinstance(obj,StorageObject):
            obj = obj.identifier
        if key not in self._relationships:
            raise ValueError(f'{key} not relationship in {self._identifier}')
        self._relationships[key].remove(obj)

    def __eq__(self, value):
        if not isinstance(value,StorageObject):
            return False
        if self.identifier != value.identifier:
            return False
        if self.object_type != value.object_type:
            return False
        if self.properties != value.properties:
            return False
        if self.relationships != value.relationships:
            return False
        return True