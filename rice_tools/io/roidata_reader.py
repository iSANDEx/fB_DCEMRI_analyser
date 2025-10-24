"""
roidata_reader.py - Atomic functions for reading csv ROI extracts
"""

import os
import pandas as pd

def read_dynamic(input_df, sequence=None, patientid=None, visitnro=None):

    return True

def read_t1vfa():

    return True

def read_csv(path_to_input_datafile, logger=None):
    """Main function to read the all_rois.csv

    Returns:
        _type_: _description_
    """
    # Check the path and data file exist:
    if not os.path.isfile(path_to_input_datafile):
        if logger is not None:
            logger.error(f'Data file {path_to_input_datafile} does not exist, check the path and/or file name are valid')
        else:
            print(f'[ERROR]: Data file {path_to_input_datafile} does not exist, check the path and/or file name are valid')
        return pd.DataFrame()
    
    # The file exists, so let's load it into a dataframe
    src_path, fext = os.path.splitext(path_to_input_datafile)
    
    if fext.endswith('csv'):
        data_df = pd.read_csv(path_to_input_datafile)
    elif fext.endswith('json'):
        data_df = pd.read_json(path_to_input_datafile)
    elif fext.endswith('pkl'): 
        data_df = pd.read_pickle()
    else:
        if logger is not None:
            logger.error(f'Opening {fext} file format not yet implemented')
            return pd.DataFrame()
        
    return data_df