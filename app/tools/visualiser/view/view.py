import re

class View:
    def __init__(self, elements=None): 
        self._elements = elements
        
    def __len__(self):
        return len(self._elements)

    def __iter__(self):
        for n in self._elements:
            yield n

    def __getitem__(self, item):
        return self._elements[item]
    
    def add_element(self,element):
        self._elements.append(element)
    
    def remove_element(self, element):
        if isinstance(element, str):
            self._elements = [el for el in self._elements if el.identifier != element]
        else:
            if element in self._elements:
                self._elements.remove(element)

    def relationships(self):
        for element in self._elements:
            for rel_type,rels in element.relationships.items():
                for rel in rels:
                    yield (element,rel_type,rel)

    def get_element(self,element_id):
        for element in self._elements:
            if element.identifier == element_id:
                return element

    def get_relationship(self,source_id,target_id):
        element = self.get_element(source_id)
        for rt,rels in element.relationships.items():
            for rel in rels:
                if rel == target_id:
                    return rt
                
    def has_element(self,element):
        return element in [e.identifier for e in self._elements]
    
    def add(self, element):
        self._elements.append(element)
