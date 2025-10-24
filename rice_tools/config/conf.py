import json
from json_minify import json_minify

class Conf:

    def __init__(self, confPath):

        """
        
        Load and store the configuration and update the object's dictionary
        """

        with open(confPath, 'r') as f:
            jminified = json_minify(f.read())
            conf = json.loads(jminified)

        self.__dict__.update(conf)

    def __getitem__(self, k):
        """_summary_
        
        Return the value associated with the supplied key
        
        Args:
            k (_type_): _description_

        Returns:
            _type_: _description_
        """
        
        return self.__dict__.get(k, None)
    

    def __additem__(self, key, value, parent=None):
        """_summary_
        
        Add a new attribute, up to the first level, defined by the key given in parent
        
        Args:
            k (_type_): _description_

        Returns:
            _type_: _description_
        """
        if parent in self.__dict__.keys():
            if isinstance(self.__dict__[parent], dict):
                self.__dict__[parent][key]=value
            else:
                print(f'[ERROR]: Value associated to {parent} Key is not a dictionary, nothing done')
        else:
            self.__dict__.update({key: value})


    def __upditem__(self, key, value):
        """_summary_
        
        Update an existing attribute
        
        Args:
            key (_type_): _description_
			value (_type_): _description_

        Returns:
            _type_: _description_
        """
        setattr(self, key, value)


    def __delitem__(self, key):
        """_summary_
        
        Return the value associated with the supplied key
        
        Args:
            key (_type_): _description_

        Returns:
            _type_: _description_
        """
        key_to_delete = self.__dict__.pop(key, None)
        
	
    def display_pair(self, key, value):
        """_summary_
        
        Display an attribute
        
        Args:
            key (_type_): _description_
			value (_type_): _description_

        Returns:
            _type_: _description_
        """
        print( f'{key}: {value}')


    def display(self, data=None, indent = 0 ):
        """_summary_
        
        Iterator to dsplay the content of the configuration structure, or a subset of it
        
        Args:
            data (_type_): _description_ (optional)
			vindent (_type_): _description_ (optional)

        Returns:
            _type_: _description_
        """
	
        if data is None:
            data = self.__dict__

        for key, value in data.items():
            print("\t" * indent + str(key) + ": {")
            if isinstance(value, dict):  # If the value is a dictionary, recurse
                self.display(value, indent + 1)
            else:  # Otherwise, just print the value
                print("\t" * (indent + 1) + str(value) )
                            
            print(''.join(['\t'] * (indent + 1))+'}')
