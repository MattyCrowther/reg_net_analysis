from equivalent.abstract_equivalent import EquivalentProperty
from identifiers import identifiers

class ActivatorEquivalent(EquivalentProperty):
    def __init__(self):
        e = identifiers.roles.stimulator
        super().__init__(e)

class ActivatedEquivalent(EquivalentProperty):
    def __init__(self):
        e = identifiers.roles.stimulated
        super().__init__(e)

class RepressorEquivalent(EquivalentProperty):
    def __init__(self):
        e = identifiers.roles.inhibitor
        super().__init__(e)

class RepressedEquivalent(EquivalentProperty):
    def __init__(self):
        e = identifiers.roles.inhibited
        super().__init__(e)

class ModifierEquivalent(EquivalentProperty):
    def __init__(self):
        e = identifiers.roles.modifier
        super().__init__(e)

class ProductEquivalent(EquivalentProperty):
    def __init__(self):
        e = identifiers.roles.product
        super().__init__(e)

class ModifiedEquivalent(EquivalentProperty):
    def __init__(self):
        e = identifiers.roles.modified
        super().__init__(e)

class TemplateEquivalent(EquivalentProperty):
    def __init__(self):
        e = identifiers.roles.template
        super().__init__(e)

class SynonymEquivalent(EquivalentProperty):
    def __init__(self):
        e = identifiers.roles.synonym
        super().__init__(e)

class BindingSiteEquivalent(EquivalentProperty):
    def __init__(self):
        e = identifiers.roles.interaction_binding_site
        super().__init__(e)