'''
File: alist.py
Description: Alist class and functions
Author: Kobby K.A. Nuamah (knuamah@ed.ac.uk)

'''

from copy import deepcopy


class Alist:

    def __init__(self, **kwargs):
        self.attributes = {
            Attributes.ID: kwargs[Attributes.ID] if Attributes.ID in kwargs else "0",
            Attributes.OP: kwargs[Attributes.OP] if Attributes.OP in kwargs else 'value',
            Attributes.SUBJECT: kwargs[Attributes.SUBJECT] if Attributes.SUBJECT in kwargs else '',
            Attributes.PROPERTY: kwargs[Attributes.PROPERTY] if Attributes.PROPERTY in kwargs else '',
            Attributes.OBJECT: kwargs[Attributes.OBJECT] if Attributes.OBJECT in kwargs else '',
            Attributes.OPVAR: kwargs[Attributes.OPVAR] if Attributes.OPVAR in kwargs else '',
            Attributes.COV: kwargs[Attributes.COV] if Attributes.COV in kwargs else 0.0,
            Attributes.TIME: kwargs[Attributes.TIME] if Attributes.TIME in kwargs else '',
            Attributes.EXPLAIN: kwargs[Attributes.EXPLAIN] if Attributes.EXPLAIN in kwargs else '',
            Attributes.FNPLOT: kwargs[Attributes.FNPLOT] if Attributes.FNPLOT in kwargs else '',
            Attributes.CONTEXT: kwargs[Attributes.CONTEXT] if Attributes.CONTEXT in kwargs else '',
            'meta': {
                'cost' : kwargs[Attributes.COST] if Attributes.COST in kwargs else 0.0,
                'depth' : 0,
                'state' : States.UNEXPLORED,
                'data_sources' : [],
                'branch_type': Branching.OR,
                'node_type': NodeTypes.ZNODE
            }
        }

        for k in set(kwargs) - {Attributes.OP, Attributes.SUBJECT, Attributes.PROPERTY, Attributes.OBJECT,
                                Attributes.OPVAR, Attributes.COV, Attributes.TIME, Attributes.EXPLAIN,
                                Attributes.FNPLOT, Attributes.CONTEXT}:
            self.attributes[k] = kwargs[k]

        # self.id = kwargs[Attributes.ID] if Attributes.ID in kwargs else "0"
        # self.cost = kwargs[Attributes.COST] if Attributes.COST in kwargs else 0.0
        # self.depth = 0
        # self.state = States.UNEXPLORED
        # self.data_sources = set()
        # self.branch_type = Branching.OR
        # self.node_type = NodeTypes.ZNODE

        self.children = []
        self.parent = []
        # these are for set comprehension operations when a node spawns new nodes after reducing
        self.nodes_to_enqueue_only = []
        self.nodes_to_enqueue_and_process = []
        self.parent_decomposition = ''

        
    @property
    def id(self):
        return self.attributes[Attributes.ID]

    @id.setter
    def id(self, value):
        self.attributes[Attributes.ID] = value

    @property
    def cost(self):
        return self.attributes['meta']['cost']

    @cost.setter
    def cost(self, value):
        self.attributes['meta']['cost'] = value

    @property
    def depth(self):
        return self.attributes['meta']['depth']

    @depth.setter
    def depth(self, value):
        self.attributes['meta']['depth'] = value
    
    @property
    def state(self):
        return self.attributes['meta']['state']

    @state.setter
    def state(self, value):
        self.attributes['meta']['state'] = value
    
    @property
    def data_sources(self):
        return self.attributes['meta']['data_sources']

    @data_sources.setter
    def data_sources(self, value):
        self.attributes['meta']['data_sources'] = value

    @property
    def branch_type(self):
        return self.attributes['meta']['branch_type']

    @branch_type.setter
    def branch_type(self, value):
        self.attributes['meta']['branch_type'] = value

    @property
    def node_type(self):
        return self.attributes['meta']['node_type']

    @node_type.setter
    def node_type(self, value):
        self.attributes['meta']['node_type'] = value


    def set(self, attribute, value):
        """
        Sets the value of an attribute. 
        Do not use this for instantiating a variable.
        """
        self.attributes[attribute] = value
        if attribute == Attributes.ID:
            self.id = value

    def get(self, attribute):
        """ 
        Returns the value assigned to the attribute, 
        not necessarily its instantiated value
        """
        if attribute in self.attributes:
            return self.attributes[attribute]
        else:
            return None

    # def link_child(self, child):
    #     child.depth = self.depth + 1
    #     child.id = f"{self.depth + 1}{self.id}{len(self.children) + 1}"
    #     child.set(Attributes.ID, child.id)
    #     self.children.append(child)
    #     child.parent.append(self)

    def copy(self):
        """ create a copy of the alist"""
        new_alist_attrs = deepcopy(self.attributes)
        new_alist = Alist(**new_alist_attrs)
        new_alist.id = "0"
        new_alist.cost = 0
        new_alist.depth = 0
        new_alist.state = States.UNEXPLORED
        new_alist.nodes_to_enqueue_only = []
        new_alist.nodes_to_enqueue_and_process = []
        new_alist.data_sources = deepcopy(self.data_sources)
        return new_alist

    def get_alist_json_with_metadata(self):
        alist = deepcopy(self.attributes)
        alist[Attributes.ID] = self.id
        return alist

    def is_instantiated(self, attr_name):
        """ 
        Returns FALSE if the value of the attribute is a variable
        or an empty string.
        """
        if attr_name in self.attributes and not str(self.attributes[attr_name]).startswith((VarPrefix.AUXILLIARY, VarPrefix.NESTING, VarPrefix.PROJECTION)):
            return True
        elif attr_name not in self.attributes or not self.attributes[attr_name]:
            return False
        else:
            if attr_name in [Attributes.SUBJECT, Attributes.OBJECT, Attributes.PROPERTY, Attributes.TIME]:
                return self.is_instantiated(self.attributes[attr_name])
            elif str(self.attributes[attr_name]).startswith((VarPrefix.AUXILLIARY, VarPrefix.NESTING, VarPrefix.PROJECTION)) or \
                    isinstance(self.attributes[attr_name], dict):
                return False
            else:
                return True

    def variables(self):
        """ Returns a list of all variables in the alist"""
        variables = {x: y for (x, y) in self.attributes.items()
                     if str(x).startswith((VarPrefix.AUXILLIARY, VarPrefix.NESTING, VarPrefix.PROJECTION)) or
                     str(y).startswith((VarPrefix.AUXILLIARY,
                                        VarPrefix.NESTING, VarPrefix.PROJECTION))
                     }
        return variables

    def instantiated_attributes(self):
        """ Returns a dictionary of variables and their instantiations"""
        variables = {x: y for (x, y) in self.attributes.items()
                     if self.is_instantiated(x)}
        return variables

    def uninstantiated_attributes(self):
        variables = set(self.variables())
        inst_variables = set(self.instantiated_attributes())
        return variables - inst_variables

    def instantiation_value(self, attrName):
        """
        Get the value that the attribute is instantiated with.
        For an attribute whose values is a variables, 
        find the value that the variable is instantiated to.
        """
        if attrName not in self.attributes:
            return None
        if str(self.attributes[attrName]).startswith((VarPrefix.AUXILLIARY, VarPrefix.NESTING, VarPrefix.PROJECTION)):
            return self.instantiation_value(self.attributes[attrName])
        else:
            return self.attributes[attrName]

    def variable_references(self, varName):
        """ Get all attribute names that reference the variable name"""
        varRefs = {x: y for (x, y) in self.attributes.items() if y == varName}
        return varRefs

    def projection_variables(self):
        variables = {x: y for (x, y) in self.attributes.items()
                     if str(x).startswith(VarPrefix.PROJECTION)
                     }
        if variables:
            return variables
        else:
            return None

    def nesting_variables(self):
        variables = {x: y for (x, y) in self.attributes.items()
                     if str(x).startswith(VarPrefix.NESTING) or isinstance(y, dict)
                     }
        if variables:
            return variables
        else:
            return None

    def uninstantiated_nesting_variables(self):
        variables = {x: y for (x, y) in self.attributes.items()
                     if str(x).startswith((VarPrefix.AUXILLIARY, VarPrefix.NESTING, VarPrefix.PROJECTION)) 
                        and isinstance(y, dict) 
                        and x != Attributes.CONTEXT
                     }
        if variables:
            return variables
        else:
            return None

    def instantiated_nesting_variables(self):
        variables = {x: y for (x, y) in self.attributes.items()
                     if str(x).startswith((VarPrefix.AUXILLIARY, VarPrefix.NESTING, VarPrefix.PROJECTION)) and (isinstance(y, dict) == False)
                     }
        if variables:
            return variables
        else:
            return None

    def instantiate_variable(self, varName, varValue, insert_missing=True):
        """
        Instantiate a variable and instantiate other variables that reference it
        """

        # change all instances to the varValue except for occurence in OPVAR
        # instantiate matching variable names only, or attributes whose values
        # match the variables

        if insert_missing or varName in self.attributes:
            self.attributes[varName] = varValue

        for (k, v) in self.attributes.items():
            if str(v) == varName and \
                    str(k).startswith((VarPrefix.AUXILLIARY, VarPrefix.NESTING, VarPrefix.PROJECTION)):
                self.attributes[k] = varValue
            if str(v) == varName and \
                    str(v).startswith((VarPrefix.AUXILLIARY, VarPrefix.NESTING, VarPrefix.PROJECTION)):
                if insert_missing or k in self.attributes:
                    self.attributes[v] = varValue

    def get_object_level_attributes(self):
        olattrs = {x: y for (x, y) in self.attributes.items()
                   if x not in [Attributes.OP, Attributes.OPVAR]
                   }
        return olattrs

    def __lt__(alist1, alist2):
        return alist1.cost < alist2.cost

    def __str__(self):
        return str(self.get_alist_json_with_metadata())


# Alist States
class States:
    IGNORE = -1
    UNEXPLORED = 0
    EXPLORED = 1
    REDUCIBLE = 2
    PRUNED = 3


# branching options
class Branching:
    OR = 'or'
    AND = 'and'


# Alist attribute names
class Attributes:
    ID = 'id'
    SUBJECT = 's'
    PROPERTY = 'p'
    OBJECT = 'o'
    TIME = 't'
    COV = 'u'
    OP = 'h'
    OPVAR = 'v'
    SOURCE = 'kb'
    COST = 'l'
    EXPLAIN = 'xp'
    FNPLOT = 'fp'
    CONTEXT = 'cx'


# variable prefixes
class VarPrefix:
    PROJECTION = '?'
    AUXILLIARY = '$'
    NESTING = '#'


class NodeTypes:
    ZNODE = 'znode'
    HNODE = 'hnode'
    FACT = 'fact'


class Contexts:
    # user contexts
    nationality = 'nationality'
    accuracy = 'accuracy'
    speed = 'speed'

    # environment contexts
    datetime = 'datetime'
    device = 'device'
    place = 'place'
