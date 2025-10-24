__author__ = 'jose.ulloa'

# Enable importing files to upper locations
# from .sub-folder import function <[function1, function2, ...]>]
from .conf import Conf
from .checks import check_additional_config_files

# TODO: Centralise creation of dicom_metadata.json and pk_combination.json in here. 
# If they are not available in the data/config folder, takes the default from here