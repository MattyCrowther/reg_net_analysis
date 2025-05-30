from entities.abstract_entity import ConceptualEntity
from entities.abstract_entity import PhysicalEntity
from equivalent import interaction_equivalent as ce
from property import interactions as ins

class Interaction(ConceptualEntity):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        if equivalents == []:
            equiv = []
        else:
            equiv = equivalents
        if restrictions == []:
            res = []
        else:
            res = restrictions
        p = properties
        super().__init__(properties=p,
        equivalents=equiv,restrictions=res)

class Activation(Interaction):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        if equivalents == []:
            equiv = [ce.ActivationRoleEquivalent()]
        else:
            equiv = equivalents
        if restrictions == []:
            res = []
        else:
            res = restrictions
        
        p = properties + [ins.Activator(PhysicalEntity),
                          ins.Activated(PhysicalEntity),
                          ins.BindingSite(PhysicalEntity)]
        super().__init__(properties=p,equivalents=equiv,restrictions=res)

class Repression(Interaction):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        if equivalents == []:
            equiv = [ce.RepressionRoleEquivalent()]
        else:
            equiv = equivalents
        if restrictions == []:
            res = []
        else:
            res = restrictions
        
        p = properties + [ins.Repressor(PhysicalEntity),
                          ins.Repressed(PhysicalEntity),
                          ins.BindingSite(PhysicalEntity)]
        super().__init__(properties=p,equivalents=equiv,restrictions=res)

class GeneticProduction(Interaction):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        if equivalents == []:
            equiv = [ce.GeneticProductionRoleEquivalent()]
        else:
            equiv = equivalents
        if restrictions == []:
            res = []
        else:
            res = restrictions
        p = properties + [ins.Template(PhysicalEntity),
                          ins.Product(PhysicalEntity)]
        super().__init__(properties=p,
        equivalents=equiv,restrictions=res)


class Degradation(Interaction):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        if equivalents == []:
            equiv = [ce.DegradationRoleEquivalent()]
        else:
            equiv = equivalents
        if restrictions == []:
            res = []
        else:
            res = restrictions
        super().__init__(properties=properties,
        equivalents=equiv,restrictions=res)

class Binds(Interaction):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        if equivalents == []:
            equiv = [ce.BindsRoleEquivalent()]
        else:
            equiv = equivalents
        if restrictions == []:
            res = []
        else:
            res = restrictions
        super().__init__(properties=properties,
        equivalents=equiv,restrictions=res)

class Conversion(Interaction):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        if equivalents == []:
            equiv = [ce.ConversionRoleEquivalent()]
        else:
            equiv = equivalents
        if restrictions == []:
            res = []
        else:
            res = restrictions
        super().__init__(properties=properties,
        equivalents=equiv,restrictions=res)


class Transcription(Interaction):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        if equivalents == []:
            equiv = [ce.TranscriptionRoleEquivalent()]
        else:
            equiv = equivalents
        if restrictions == []:
            res = []
        else:
            res = restrictions
        p = properties + [ins.Activator(PhysicalEntity),
                          ins.Activated(PhysicalEntity)]
        super().__init__(properties=p,
        equivalents=equiv,restrictions=res)