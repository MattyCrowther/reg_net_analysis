class Node:
    def __init__(self,id,type, **kwargs):
        self._type = str(type)
        self._id=id
        self._properties = kwargs
            
    def __eq__(self, obj):
        if not isinstance(obj, Node):
            return False
        if obj.id == self._id:
            return True
        return False
        
    def __hash__(self):
        return hash(str(self._id))

    def __str__(self):
        return self._id

    def __getitem__(self, item):
        return self._properties[item]
    
    @property
    def id(self):
        return self._id

    @property
    def type(self):
        return self._type
    
    @property
    def properties(self):
        return self._properties