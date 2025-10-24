"""
Module: RICE_TOOLS
Author: Jose L. Ulloa
Created: 2025-08-12

Description:
    Briefly describe the purpose of this module.

Functions:
    main():
        The entry point of the application.

Example:
    >>> python -m rice_tools.config.checks...
"""

import os
import shutil

def check_additional_config_files(path_to_config, files_to_check=[], logger=None):
    """TODO: Need to re-think this function. The idea is that I can define a custom file, 
     but if it doesn't exist, take the corresponding default file defined in this folder

    Args:
        path_to_config (_type_): _description_
        files_to_check (_type_): _description_
        logger (_type_, optional): _description_. Defaults to None.
    """

#     files_to_check = ['pk_combinations', 'dicom_metadata']
#     fext = 'json'

#     for cfg_filename in files_to_check:
#         cfg_file = '.'.join([cfg_filename, fext])
#         src_filepath = os.path.join(os.path.dirname(__file__), cfg_file)
#         dst_filepath = os.path.join(path_to_config,cfg_file)
#         if not os.path.isfile(dst_filepath):
            
#             if logger is not None:
#                 logger.info(f'File {cfg_file} does not exist in {path_to_config}, copying the default one')
            
#             shutil.copyfile(src_filepath, dst_filepath)
    pass