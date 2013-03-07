#!/usr/bin/python 
'''this file generates the different classes for the behaviors'''

import os
import os.path
import configparse


AB_header = """


'''DO NOT MODIFY THIS FILE!!!! (modify behavior_config instead)'''
'''this class is generated by a script (generate_behaviors.py) that generates a function for each behavior'''
'''changes to this file will be overwritten!'''
import logging
import util.nullhandler
import os
import inspect

logging.getLogger('Borg.Brain.AllBehaviors').addHandler(util.nullhandler.NullHandler())

class AllBehaviors(object):

    '''this class is used to call behaviors from other behaviors'''

    # storage for the instance reference
    __instance = None

    def __init__(self):
        \"\"\" Create singleton instance \"\"\"
        # Check whether we already have an instance
        if AllBehaviors.__instance is None:
            AllBehaviors.__instance = AllBehaviors.__impl()# Create and remember instance


        # Store instance reference as the only member in the handle
        self.__dict__['_Singleton__instance'] = AllBehaviors.__instance


    def __getattr__(self, attr):
        \"\"\" Delegate access to implementation \"\"\"
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        \"\"\" Delegate access to implementation \"\"\"
        return setattr(self.__instance, attr, value)


    class __impl:

        def __init__(self):
            self.logger = logging.getLogger('Borg.Brain.AllBehaviors')

        def list_module(self, name):
            mods = []
            for i in dir(name):
                item = getattr(name, i)
                if inspect.isclass(item):
                    mods.append(item)
            return mods      

        def simple_name(self, name):
            return name.lower().replace('_', '').replace('-', '')

        def __getattr__(self, attr):
            if attr in self.__dict__:
                return self.__dict__[attr]

            attr = attr.lower()
            path = os.getenv("BORG") + "/brain/src/behavior/" + attr + "/" + attr + ".py"
            init_path = os.getenv("BORG") + "/brain/src/behavior/" + attr + "/__init__.py"
            mod_path = "behavior." + attr + "." + attr

            if os.path.exists(path):
                if os.path.exists(init_path):
                    exec("import " + mod_path)
                else:
                    raise Exception("Behavior " + attr + " exists but does not have __init__.py file so it cannot be imported")
            else:
                raise Exception("Behavior " + attr + " does not exist")

            simple_name = self.simple_name(attr)

            mods = self.list_module(eval(mod_path))
            for m in mods:
                if self.simple_name(m.__name__) == simple_name:
                    self.__dict__[attr] = m
                    return m

            raise Exception("Behavior " + attr + " has no behavior selector")
"""

AB_definition = """
        def %s(self, params):
            import behavior.%s.%s
            return behavior.%s.%s.%s(params)
"""

behavior_class = """

'''DO NOT MODIFY THIS FILE!!!!'''
'''this class is generated by a script (generate_behaviors.py) that generates a class for each behavior'''
'''changes to this file will be overwritten!'''

import basebehavior.abstractbehavior

import time #TODO: temp, remove later
import os
import os.path
import memory
import logging
import util.nullhandler
import bbie.bbie

%s

class %s(basebehavior.abstractbehavior.AbstractBehavior):

    def behavior_init():
        bbie_setting = ["no_time","max_succes"] #TODO: get this from behavior_config
        self.bbie = bbie.BBIE(self.name, bbie_setting)
        self.logger = logging.getLogger('Borg.Brain.Behavior.' + self.get_name())
        self.logger.addHandler(util.nullhandler.NullHandler())

    def get_name(self):
        return "%s"

    def check_postcondition(self):
        m = memory.Memory()
        return eval(%s)

    def load_exceptions(self):
        self._all_exceptions = %s

    def select_implementation(self):
        '''select which of the implementations of this behavior should be run'''

        #destroy (possibly) the old running behavior
        self.selected_implementation = None

        if (self._best_behaviors == None or len(self._best_behaviors) == 0):
            #best_behaviors will be returned as a list of tuples of (expected_time, implementation)
            self._best_behaviors = bbie.bbie.get_best_implementations(os.environ['BORG']+"/brain/src/bbie/ie_files/"+self.get_name().lower()+".pkl")
            #self._best_behaviors = [(time.time() + 50000, 1)] #TODO: remove, and enable line above

        #take top behavior from the list, and remove it from the list
        if (isinstance(self._best_behaviors, list) and len(self._best_behaviors)>0):
            # This is the default case where multiple versions are returned.
            to_run = self._best_behaviors[0]
            self._best_behaviors = self._best_behaviors[1:]

            self._expected_time, b_id = to_run
            self._implementation_id = b_id
        else:
            # In thsi case, no versions are returned.
            self._expected_time = 86400
            self._implementation_id = 1

        #now select the implementation:
        cleanname = self.simple_name(self.name)
        zero_path = os.environ['BORG'] + "/brain/src/behavior/" + cleanname + "/" + cleanname + "_0.py"

        #if a _0 implementation exists, run that one:
        if (os.path.exists(zero_path)):
            module = self.name.lower() + "_0"
        else:
            module = self.name.lower() + "_" + str(b_id)
        exec("import " + module)
        selected_class = self.find_class(eval(module))
        if not selected_class:
            raise Exception("No implementation available in selected file " + module)

        self.selected_implementation = selected_class(self)

        #pass the params the newly selected implementation:
        self.selected_implementation.set_params(self.params)
"""


implementation_template = """

'''
this is an automatically generated template, if you don't rename it, it will be overwritten!
'''

import basebehavior.behaviorimplementation


class %s_x(basebehavior.behaviorimplementation.BehaviorImplementation):

    '''this is a behavior implementation template'''

    #this implementation should not define an __init__ !!!


    def implementation_init(self):

        #define list of sub-behavior here
        pass

    def implementation_update(self):

        #you can do things here that are low-level, not consisting of other behaviors

        #in this function you can check what behaviors have failed or finished
        #and do possibly other things when something has failed
        pass



"""


def create_name( name ):
    '''create function and classnames from all the names of the behaviors'''

    parts = name.split('_')
    name0 = parts[0] + "".join([parts[i][0].upper() + parts[i][1:]  for i in range(1, len(parts))])
    name1 = "".join(name.split('_'))
    name2 = "".join([parts[i][0].upper() + parts[i][1:]  for i in range(len(parts))])
    return (name0, name1, name1, name2)


def create_all_behaviors_file(names):
    '''write all the functions to a file'''
    fi = open( os.environ['BORG'] + "/brain/src/basebehavior/" + 'allbehaviors.py', 'w')
    fi.write( AB_header )
    #for elem in names:
    #    fi.write('\n')
    #    #the double [1] index below is intentional!
    #    #TODO: make this better by fixing create_name and dependencies
    #    fi.write( AB_definition % (create_name(elem)[0], create_name(elem)[1], create_name(elem)[1], create_name(elem)[1], create_name(elem)[2], create_name(elem)[3]) )
    #    fi.write('\n')
    fi.close()


def create_main_behavior_classes(names, postconditions, exceptions, descriptions):
    '''create behavior classes'''

    for name, postc, exc, desc in zip(names, postconditions, exceptions, descriptions):


        cleanname = name.replace('_','')


        loc = os.environ['BORG'] + "/brain/src/behavior/" + cleanname + "/"
        #loc = ""

        #TODO: fix the creation of folders: (test!)
        #create directory if necessary
        if (not os.path.exists(loc)):
            os.chdir(os.environ['BORG'] + "/brain/src/behavior/")
            os.mkdir(cleanname)


        #import all the implementations of this behavior:
        #implementations = find_implementations(name)
        #imp_tekst = "\n"
        #for impl in implementations:
        #    print "adding: " + impl
        #    #imp_tekst = imp_tekst + impl + "\n"

        #place an __init__ file in the directory:
        fi = open( loc + '__init__.py', 'w')
        fi.write("")
        fi.close()

        #create the main file for the behavior
        full_name = create_name(name)[3]
        full_name_low = full_name.lower()
        fi = open( loc + full_name_low + '.py', 'w')
        postc = "\"" + postc + "\""
        exceptions = "['False','True']"
        fi.write( behavior_class % ( "'''" + desc + "'''", full_name, full_name, postc, exc ))
        fi.close()

        #create an implementation template:
        fi = open( loc + full_name_low + '_x.py', 'w')
        fi.write( implementation_template % ( full_name ))
        fi.close()


def find_implementations(behaviorname):
    '''find all implementations of a behavior, to include them'''

    #remove underscores:
    behaviorname = behaviorname.replace('_','')
    
    beh_path = os.path.abspath(os.environ['BORG'] + '/brain/src/behavior/' + behaviorname + '/')
    print "looking in : " + beh_path
    imports = []
    files = os.listdir(beh_path)
    for filename in files:
        if (behaviorname == filename[0:len(behaviorname)]):
            if (filename[len(behaviorname)] == '_'):
                if (filename[len(behaviorname) + 1] != 'x' and filename[-3:] == '.py'):
                    imports.append("import " + filename[:-3])

    return imports


#start generating:
print "generating behavior classes..."


#read all information about the behaviors:
option_dict = configparse.ParameterDict()
names = []
postconditions = []
exceptions = []
descriptions = []
conf_location = os.path.abspath(os.environ['BORG'] + '/brain/src/config/behaviors_config')

configparse.parse_config(conf_location, option_dict)
for section in option_dict.option_dict.keys():
    names.append(section)
    exception_read = False
    postcondition_read = False
    description_read = False
    for variable in option_dict.option_dict[section]:
        if (variable == "postcondition"):
            postconditions.append(option_dict.option_dict[section][variable])
            postcondition_read = True
        if (variable == "exceptions"):
            exceptions.append(option_dict.option_dict[section][variable])
            exception_read = True
    if (variable == "description"):
        descriptions.append(option_dict.option_dict[section][variable])
        description_read = True

    #fall back defaults for the behaviors:
    if (not postcondition_read):
        postconditions.append("False")
    if (not exception_read):
        exceptions.append("[]")
    if (not description_read):
        descriptions.append("For this behavior, no description has been entered in the behaviors_config file")



create_all_behaviors_file(names)
create_main_behavior_classes(names, postconditions,exceptions,descriptions)

print "done!"
