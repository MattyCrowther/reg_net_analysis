import re
import validators

class Edge:
    def __init__(self,n,v,type,**kwargs):
        self._type = str(type)
        self._properties = kwargs
        self._n = n
        self._v = v
          
    def __str__(self):
        return f'{self._n} - {self._type} - {self._v}'

    def __eq__(self, obj):
        if not isinstance(obj, Edge):
            return False
        if obj.n == self._n and obj._type == self.type and obj._v == self.v:
            return True
        return False

    def __hash__(self):
        return hash(str(self.type+self.n.key+self.v.key))
        
    def __getitem__(self, item):
        return self.properties[item]

    @property
    def id(self):
        return f'{self._n}_{self._type}_{self._v}'
    
    @property
    def type(self):
        return self._type

    @property
    def n(self):
        return self._n
    
    @property
    def v(self):
        return self._v
    
    @property
    def properties(self):
        return self._properties