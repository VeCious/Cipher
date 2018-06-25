#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    File: Store.py
    Author: Ve
    Version: 0.1.3
    Date: 24/06/2018
    Modified: 25/06/2018
    License: MIT
    Python: 2.7.13
"""

import os, io, json
json.encoder.FLOAT_REPR = lambda x: format(x, '.2f')

class Store(dict):
    """
    Simple dict wrapper to add save and load methods for saving/loading JSON files.
    """
    
    def __init__(self, dictionary = {}):
        """
        Store object constructor
        
        dictionary : dict, optional
            Initial dictionary to populate the object from (the default is an empty dict)
        
        """
        if len(dictionary) > 0:
            self.update(dictionary)
        pass
    #enddef

    def __getattr__(self, key):
        """
        Magic Getter
        
        Parameters
        ----------
        key : mixed|False
            Key to get from the dictionary
        """
        return False if key not in self else self[key]
    #enddef

    def __setattr__(self, key, value):
        """
        Magic Setter
        
        Parameters
        ----------
        key : str
            Key for the dictionary member
        value : any
            Value of the dictionary memeber
        """
        self[key] = value
    #enddef

    def __str__(self):
        """
        Returns Store object as a formatted JSON string
        """
        return json.dumps(self, encoding = 'utf-8', indent = 4)
    #enddef

    def save(self, path, encoding = 'utf-8'):
        """
        Save Store object as a JSON file.
        If the directory does not exists the method will attempt to create it.
        
        Parameters
        ----------
        path : str
            Path to save the JSON file at.
        encoding : str, optional
            Character encoding. (the default is 'utf-8')
        
        """
        try:
            if not os.path.exists(os.path.dirname(path)):
                ''' If the top-level directory for the filename does not exits, create it '''
                os.makedirs(os.path.dirname(path))
            with io.open(path, 'w+', encoding = encoding) as fp:
                json.dump(self, fp, encoding = encoding, indent = 4, ensure_ascii=False)
        except Exception as error:
            raise error
        return self
    #enddef

    def load(self, path, encoding = 'utf-8'):
        """
        Load JSON file
        Keys and Values from the JSON file will overwrite any existing keys.
        
        Parameters
        ----------
        path : str
            Path to load a JSON file from
        encoding : str, optional
            Character encoding. (the default is 'utf-8')
        
        """
        try:
            with io.open(path, 'r', encoding = encoding) as fp:
                self.update(json.load(fp, encoding = encoding))
        except Exception as error:
            raise error
        return self
    #enddef

    def remove(self, *args):
        """
        Removes keys from the dictionary
        
        """
        for arg in args:
            if arg in self:
                self.pop(arg)
    #enddef
#endclass