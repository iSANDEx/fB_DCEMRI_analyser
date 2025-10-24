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
    >>> python -m rice_tools.pipelines.load_roidata -c PATH_TO_CONFIG
"""

import os
import sys
import argparse
# import pandas as pd

from ..config import Conf #, check_additional_config_files
from ..utils import validate_path, setup_logging, extract_tseries
from ..io import read_csv, plot_timeseries

def main(config_structure):

    """
    Main entry point of the application.
    Extract the ROI signal from each dataset, ultra fast, dynamic & T1W

    
    Args:
        CONFIG_STRUCTURE

    Returns:
        None
    """

    # Check the path from the config files exist or not. 
    # if the output folder (i.e. "path.analysis" attribute) does not exist, it is created. Everything else, issues an error message

    valid_path = validate_path(config_structure['path'])
    if not valid_path:
        print('[ERROR]: There is something wrong with the path. Check the folder names and try again')
        sys.exit(1)
    
    # Setup log before anything else
    logger = setup_logging(config_structure['logging']['loglevel'], 
                           os.path.join(os.path.expandvars(config_structure['path']['logs']),
                                        '_'.join([os.path.splitext(os.path.basename(__file__))[0],
                                                  config_structure['logging']['logfile']])
                                        )
                        )

    # # Ensure dicom_metadata and pk_combinations config json files are available in the data folder, otherwise, take the default ones:
    # check_additional_config_files(os.path.expandvars(config_structure['path']['config']))

    # Load the csv datafile:
    all_data_df = read_csv(os.path.join(os.path.expandvars(config_structure['path']['analysis']),
                                        '.'.join([config_structure['output']['roidata_name'],
                                                  config_structure['output']['fmt']]
                                                )
                                        ),
                            logger=logger)

    # Define the stats to plot:
    tseries_stats = {'xaxis': 'time',
                     'grouping_index': 'time_index',
                     'baseline': 'bline'}
    tseries_label = {'xlabel': 'time [sec]'}

    # Get the label from the config file, as the pattern:
    roi_items = all_data_df['ROI label'].unique()
    roi_label = config_structure['roi']['segment_label']
    # Search for the pattern in roi_items:
    idx = next((i for i, s in enumerate(roi_items) if roi_label in s), -1)
    if idx > 0:
        df_filter = {'ROI label': roi_items[idx]}
        logger.debug(f'Will generate plots from {roi_items[idx]} ROI')
    else:
        # Just take the first item in roi_items:
        df_filter = {'ROI label': roi_items[0]} 

    if config_structure['roi']['curve_to_plot'] == 'pc_enh':
        tseries_stats['yaxis'] = 'pc_enh_mean'
        tseries_stats['fill_area'] = 'pc_enh_stddev'

        tseries_label['ylabel'] = 'PE [%]'
        title_sufix = 'PE'
    elif config_structure['roi']['curve_to_plot'] == 'sig_int':
        tseries_stats['yaxis'] = 'median'
        tseries_stats['fill_area'] = 'stddev'

        tseries_label['ylabel'] = 'Signal Average'
        title_sufix = 'SI'
    else:
        logger.error(f"Curve to plot {config_structure['roi']['curve_to_plot']} is not valid")

    # Loop over the patients and visits to get the (time, values) pairs
    for patient in config_structure['dicom']['patients_id']:
        df_filter['PatientID'] = patient
        for sequence in config_struct['dicom']['sequence_patterns']:
            figax=None
            df_filter['Sequence'] = sequence
            tseries_label['title'] = f"{patient} - {sequence} - {title_sufix} - {df_filter['ROI label']}"
            for visit in config_structure['dicom']['visits_id']:
                df_filter['VisitNro'] = visit
                tseries_data = extract_tseries(all_data_df, df_filter, 
                                            tseries_stats=tseries_stats, 
                                            logger=logger)
                if not tseries_data.empty:
                    tseries_label['legend'] = f'Visit {visit:02d}'
                    tseries_label['colour'] = config_structure['roi']['plot_visit_colour'][visit-1]
                    figax = plot_timeseries(tseries_data,
                                            tseries_axis={'xaxis': tseries_stats['xaxis'],
                                                        'yaxis': 'mean', 
                                                        'fill_area': 'std',
                                                        'baseline': tseries_stats['baseline']},
                                            tseries_label = tseries_label,
                                            figax=figax,
                                            disp=(config_structure['logging']['loglevel']=='DEBUG'))
                else:
                    logger.error(f"There is no Timeseries for sequence {sequence} of patient {patient} on visit {visit}")

            if (figax is not None) & (config_structure['logging']['loglevel'] !='DEBUG'):
                figax[0].savefig(os.path.join(os.path.expandvars(config_structure['path']['analysis']),
                                              patient, 
                                              f"{config_structure['output']['roidata_name']}_{config_structure['roi']['curve_to_plot']}_{df_filter['ROI label']}_{sequence}.png"))


if __name__ == "__main__":

    """ 
    _summary_
    
    Construct the argument parser and parse the arguments

    """
    # Initialise logging

    ap = argparse.ArgumentParser()
    ap.add_argument('-c', '--confpath', required=True,
                help='path to the configuration file. It assumes ')
    args = vars(ap.parse_args())

    # Convert the configuration file into a structure array
    config_struct = Conf(args['confpath'])
    
    main(config_struct)