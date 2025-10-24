"""
Module: RICE_TOOLS
Author: Jose L. Ulloa
Created: 2025-08-12

Description:
    Main script to host utility functions. Later on this will be re-formatted as a proper module

Functions:
    flatten():
        Flatten a dicom metadata dictionary with up to 2 levels.

Example:
    >>> python -m utils.main -c PATH_TO_CONFIG
"""

import os
import glob
import pandas as pd

def flatten_tags_dictionary(tag_dictionary, tag_to_skip=[]):
    """_summary_
        Flatten a dicom metadata dictionary with up to 2 levels.
        This is only used to create the dataframe, not to read the dicom files

    Args:
        tag_dictionary (_type_): A 2-level dictionary (see dicom_metadata.json)

    Returns:
        _type_: The output is a 1-d list containing the 2nd level tags 
    """

    upper_level_tags = tag_dictionary.keys()
    flattened_tags = []
    for ul_tag in upper_level_tags:
        subsetDataLabels = list(tag_dictionary[ul_tag].keys())
        flattened_tags += subsetDataLabels

    # Add the absolute filepath to the dataframe:
    flattened_tags.append('AbsFilePath')

    return flattened_tags

def validate_path(path_dict):
    """
    _summary_

    """
    are_path_valid = True

    for key, value in path_dict.items():
        path2check = os.path.expandvars(value)
        if os.path.isdir(path2check):
            are_path_valid *= True
        else:
            if (key == "analysis") | (key == "logs"):
                print(f'[INFO]: Creating analysis folder {path2check}')
                os.makedirs(path2check, exist_ok=True)
            else:
                are_path_valid *= False
                print(f'[ERROR]: Folder path {path2check} does not exist, check the folder names')

    return are_path_valid

def get_filelist_recursively(folder_path, file_extension="dcm"):
    """
    Recursively retrieves all DICOM files (or any file matching the FILE_EXTENSION argument) from a folder and its sub-folders.

    Parameters:
        folder_path (str): The path to the folder to search.
        file_extension (str): The file extension to look for (default is "dcm").

    Returns:
        list: A list of absolute file paths to the DICOM files.

    Example usage:
    folder_path = "/path/to/dicom/folder"
    dcm_files = get_dcm_files_recursively(folder_path)
    print(f"Found {len(dcm_files)} DICOM files.")
    for dcm_file in dcm_files:
        print(dcm_file)
    
    """
    if not os.path.isdir(folder_path):
        raise ValueError(f"The folder path '{folder_path}' does not exist or is not a directory.")

    # Use glob to search recursively for files with the specified extension
    search_pattern = os.path.join(folder_path, f"**/*.{file_extension}")
    dcm_files = glob.glob(search_pattern, recursive=True)

    return dcm_files


# Function to parse mixed datetime formats
def parse_mixed_datetime(ts, format='%Y%m%d%H%M%S.%f'):
    """
    # Ensure all values have milliseconds (force `.0000` if missing) before the conversion:
    """

    ts_f = ts.apply(lambda x: f"{x}.0000" if pd.notna(x) and "." not in str(x) else x)

    return pd.to_datetime(ts_f, format=format, errors="coerce")
