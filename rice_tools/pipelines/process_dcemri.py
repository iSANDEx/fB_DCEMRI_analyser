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
import dcmri
import argparse
import numpy as np
import pandas as pd

from ..config import Conf #, check_additional_config_files
from ..utils import validate_path, setup_logging, get_dcemri_parameters
from ..io import read_csv, plot_multiseries

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
    # check_additional_config_files(os.path.expandvars(config_structure['path']['config']), 
    #                               files_to_check=[config_structure['dcemri']['parameters_cfg'],
    #                                               config_structure['dicom']['metadatacfg']],
    #                                logger=logger)

    # Load the csv datafile:
    all_data_df = read_csv(os.path.join(os.path.expandvars(config_structure['path']['analysis']),
                                        '.'.join([config_structure['output']['roidata_name'],
                                                  config_structure['output']['fmt']]
                                                )
                                        ),
                            logger=logger)

    # Load the PK Combinations options to define which DCMRI model to use:
    pk_combinations = Conf(os.path.join(os.path.expandvars(config_structure['path']['config']), 
                                        config_structure['dcemri']['parameters_cfg']
                                        )
                        )

    # DCEMRI constants
    r1_dcmri = dcmri.relaxivity(config_structure['dcemri']['B0'], 
                                agent=config_structure['dcemri']['ca_family'])

    # Define the stats to plot:
    tseries_stats = {'xaxis': 'time',
                     'grouping_index': 'time_index',
                     'baseline': 'bline'}
    
    tseries_label = {'xlabel': 'time [sec]',
                     'ylabel': 'CA concentration [mM]',
                     'markers': ['.', '.'],
                     'legend': ['Tissue','Blood'],
                     'colour': ['C0','C3']}

    model_label = {'xlabel': 'time [sec]',
                   'ylabel': 'CA concentration [mM]',
                   'markers': ['.', None],
                   'legend': ['Data','Model Fit (Tot Conc)'],
                   'colour': ['C0','C3']}
    
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

    tseries_stats['yaxis'] = 'median'
    tseries_stats['fill_area'] = 'stddev'

    title_sufix = 'SI'

    # Output dataframe:
    output_hdr = {'PatientID': [], 
                   'VisitID': [],
                   'VisitDate': [],
                   'ROIlabel': [], 
                   'WaterCompartments': [],
                   'PKmodel': [],
                   'Name': [],
                   'Description': [],
                   'Units': [],
                   'Mean': [],
                   'StdDev': []}
    output_data = []

    # Loop over the patients and visits to get the (time, values) pairs
    for patient in config_structure['dicom']['patients_id']:
        df_filter['PatientID'] = patient
        for sequence in config_struct['dicom']['sequence_patterns']:
            df_filter['Sequence'] = sequence
            tseries_label['title'] = f"{patient} - {sequence} - {title_sufix} - {df_filter['ROI label']}"
            model_label['title'] = f"{patient} - {sequence} - {title_sufix} - {df_filter['ROI label']}"
            for visit in config_structure['dicom']['visits_id']:
                figax = None
                df_filter['VisitNro'] = visit
                dcemri_data = get_dcemri_parameters(all_data_df, df_filter, 
                                            tseries_stats=tseries_stats, 
                                            logger=logger)
                
                if dcemri_data: # dcemri_data is a dictionary
                    # Append MRI pars from configuration file:
                    dcemri_data['mri'].update(config_structure['dcemri'])
                    # TODO: At this point I think I'm ready to plug the DCMRI tools:
                    time_axis = dcemri_data['dce']['signal']['time'].values
                    n0 = int(dcemri_data['dce']['signal']['bline'].unique()[0])
                    BAT = time_axis[n0]
                    dt = time_axis[1]
                    tacq = time_axis[-1] + dt
                    dyn_signal = dcemri_data['dce']['signal']['mean']
                    # 1. Get AIF (https://dcmri.org/api/dcmri.fake_aif.html)
                    syn_time, syn_aif, syn_gt = dcmri.fake_aif(tacq = tacq,
                                                                dt = dt,
                                                                BAT = BAT,
                                                                field_strength = dcemri_data['mri']['B0'],
                                                                agent = dcemri_data['mri']['ca_family'],
                                                                R10a = 1.0 / dcemri_data['mri']['refT1']['blood'],
                                                                S0 = dyn_signal[:n0].mean(),
                                                                model='SS',
                                                                TR=dcemri_data['mri']['TR'],
                                                                FA=dcemri_data['mri']['FA']
                                                                )

                    # 2. Calculate equivalent concentration of CA
                    ct_tissue = 1000.0 * dcmri.conc_ss(S = dyn_signal.values, 
                                                       TR = dcemri_data['mri']['TR'], 
                                                       FA = dcemri_data['mri']['FA'], 
                                                       T10 = dcemri_data['mri']['refT1']['tumour'], 
                                                       r1 = r1_dcmri, 
                                                       n0 = n0)
                    
                    ct_aif = 1000.0 * dcmri.conc_ss(S = syn_aif, 
                                                    TR = dcemri_data['mri']['TR'],
                                                    FA = dcemri_data['mri']['FA'], 
                                                    T10 = dcemri_data['mri']['refT1']['blood'], 
                                                    r1 = r1_dcmri, 
                                                    n0 = n0)
                    tseries_data = pd.DataFrame({'time':syn_time,
                                                 tseries_stats['baseline']: dcemri_data['mri']['BAT'],
                                                 'CA tissue': ct_tissue,
                                                 'CA blood': ct_aif})

                    # 2.a. Fancy graphs to display the CA concentrations
                    figax = plot_multiseries(tseries_data,
                                            tseries_axis={'xaxis': tseries_stats['xaxis'],
                                                        'yaxis': ['CA tissue', 'CA blood'], 
                                                        'fill_area': None,
                                                        'baseline': tseries_stats['baseline']},
                                            tseries_label = tseries_label,
                                            disp=(config_structure['logging']['loglevel']=='DEBUG'))

                    if (figax is not None) & (config_structure['logging']['loglevel'] !='DEBUG'):
                        figax[0].savefig(os.path.join(os.path.expandvars(config_structure['path']['analysis']),
                                                    patient, 
                                                    f"{config_structure['output']['roidata_name']}_concentration_curves_visit{visit:02d}.png"))

                    # 3. Run the PK model 
                    pk_model = dcmri.Tissue(
                        kinetics = config_structure['dcemri']['pk_kinetics'],
                        water_exchange = config_structure['dcemri']['water_exchange'],
                        ca = ct_aif / 1000.0, # mM -> M
                        t = tseries_data['time'],
                        r1 = r1_dcmri,
                        R10 = 1.0 / dcemri_data['mri']['refT1']['tumour'],
                        R10a = 1.0 / dcemri_data['mri']['refT1']['blood'],
                        TR = dcemri_data['mri']['TR'],
                        FA = dcemri_data['mri']['FA'],
                        n0 = n0,
                        # B1corr=1.0
                        )

                    pk_model.train(tseries_data[ tseries_stats['xaxis']], dyn_signal)
                    
                    # Optimised parameters can be retrieved with export_params() in the form of a dictionary:
                    # {parameter_name: [<description>, <mean_value>, <units>, <std_dev>]}
                    pk_results = pk_model.export_params()

                    for pkpar in pk_combinations[config_structure['dcemri']['water_exchange']][config_structure['dcemri']['pk_kinetics']]['pk_pars']:
                        [descr, mean_value, units, std_dev] = pk_results[pkpar]
                        output_data.append([patient, visit, dcemri_data['mri']['VisitDate'], df_filter['ROI label'], 
                                   config_structure['dcemri']['water_exchange'], config_structure['dcemri']['pk_kinetics'],
                                   pkpar, descr, units, mean_value, std_dev])
                        if pkpar == 'Ktrans':
                            model_label['legend'][1] = f'Model Fit (Ktrans={mean_value:.2e}[{units}])'

                    tseries_data['pk_signal'] = 1000.0 * pk_model.conc(sum=True)
                 

                    figax = plot_multiseries(tseries_data,
                                            tseries_axis={'xaxis': tseries_stats['xaxis'],
                                                        'yaxis': ['CA tissue', 'pk_signal'], 
                                                        'fill_area': None,
                                                        'baseline': tseries_stats['baseline']},
                                            tseries_label = model_label,
                                            disp=(config_structure['logging']['loglevel']=='DEBUG'))

                    if (figax is not None) & (config_structure['logging']['loglevel'] !='DEBUG'):
                        figax[0].savefig(os.path.join(os.path.expandvars(config_structure['path']['analysis']),
                                                      patient,
                                                      f"{config_structure['output']['roidata_name']}_PKmodel_{config_structure['dcemri']['water_exchange']}_{config_structure['dcemri']['pk_kinetics']}_visit{visit:02d}.png"))

                else:
                    logger.error(f"There is no Timeseries for sequence {sequence} of patient {patient} on visit {visit}")
    output_df = pd.DataFrame(columns=output_hdr, data=output_data)
    output_df.to_csv(os.path.join(os.path.expandvars(config_structure['path']['analysis']),
                                  f"PKparameters_{config_structure['dcemri']['water_exchange']}_{config_structure['dcemri']['pk_kinetics']}_{df_filter['ROI label']}.csv"
                                )
                    )


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