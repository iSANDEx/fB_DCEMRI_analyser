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
    >>> python -m rice_tools.pipelines.export_segmasks -c PATH_TO_CONFIG
"""

import os
import sys
import glob
import argparse
import pandas as pd
from difflib import SequenceMatcher

from ..config import Conf #, check_additional_config_files
from ..utils import validate_path, setup_logging, extract_roi
from ..io import load_dicom_folder, load_patient_data, read_mask
from ..viewer import overlay_mask

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

    # Load the dicom metadata from the folder to process and sort it as a dataframe:

    dcm_meta_struct = Conf(os.path.join(os.path.expandvars(config_structure['path']['config']), 
                                        config_structure['dicom']['metadatacfg']
                                        )
                            )
    
    dicom_df = load_dicom_folder(os.path.expandvars(config_structure['path']['raw']),
                                 dcm_meta_struct.__dict__, 
                                 fext=config_structure['dicom']['ext'],
                                 read_pixel_tag=False,
                                 logger=logger)
    
    # Load Baseline information from the info folder:
    sslice_ref_df = pd.read_csv(os.path.join(os.path.expandvars(config_structure['path']['info']), 
                                config_structure['roi']['sslice_ref_file'])
                                )

    # Read the images and segmentation masks
    patientsID = dicom_df['PatientID'].unique().tolist()
    if config_structure['dicom']['patients_id'][0] == 'all':
        config_structure['dicom']['patients_id'] = patientsID
    # Add an attribute to the config file to allow selecting a single patient, a group of patients or all of them
    # Similarly, add an attribute to select a single visit or both
    # And also, an attribute to select one of more sequence patterns (already exist)
    roi_list = []
    for patient_id in patientsID:

        if patient_id in config_structure['dicom']['patients_id']:
            logger.debug(f'Processing Patient {patient_id}')
            patient_dict = load_patient_data(dicom_df, 
                                             patient_id, 
                                             config_structure['dicom']['visits_id'],
                                             config_structure['dicom']['sequence_patterns'], 
                                             config_structure['dicom']['usePhilipsRescale'], 
                                             logger=logger)
            
            # Load the mask
            for visit_nro in config_structure['dicom']['visits_id']:

                if visit_nro in patient_dict['Visits'].keys():
                    visit_id = patient_dict['Visits'][visit_nro]['VisitID']
                    # Outputfolder for each patient/visit. inside this folder, all outputs will be stored
                    outputfolder = os.path.join(os.path.expandvars(config_structure['path']['analysis']),
                                                patient_id, visit_id)

                    # Load the segmentation mask to extract ROI values:
                    mask_pattern = f"{patient_id}_{visit_id}"
                    mask_folder_pattern = os.path.join(os.path.expandvars(config_structure['path']['rois']),
                                                       f'*{mask_pattern}*.seg.nrrd')
                    seg_bin_mask = glob.glob(mask_folder_pattern)

                    if len(seg_bin_mask) > 0:
                        # Ensure the output analysis folder exists, or create one if needed.
                        os.makedirs(outputfolder, exist_ok=True)
                        # No mask, no proc
                        segment_index = 0 
                        img_mask = read_mask(seg_bin_mask[segment_index])

                        # Change the Segment_X to a more meaningful name, e.g. tumour3d (to differentiate the single slice circular ROIs)
                        segid = img_mask['segments'][segment_index]['id']
                        roi_label = 'tumour3d' if segid.startswith('Segment') else segid # identify the segment name from the image_mask

                        # Here we run all the processes for each sequence in the patient/visit folder:
                        for sequence in config_structure['dicom']['sequence_patterns']:

                            if patient_dict['Visits'][visit_nro]['Sequences'][sequence]:
                                fig_title = f"{mask_pattern.replace('_',' ')} - {sequence}"
                                # TODO: This is only for test, once I'm happy with that, this should be removed from this function
                                # Test match between mask and patient data. 
                                # Remember Mask were drawn over High-res Spatial DCE (sequence pattern 'Dyn')
                                mfig = overlay_mask(patient_dict['Visits'][visit_nro]['Sequences'][sequence]['nparray'], 
                                                    img_mask['voxels'],
                                                    logger = logger,
                                                    figure_title = fig_title,
                                                    time_index = 1,
                                                    savepath = os.path.join(outputfolder, 
                                                                            f'roi_segments_{sequence}_{patient_id}_{visit_id}_{roi_label}.png')
                                )
                                # Get the minimum baseline among the anatomies (later on it must be refined, but for now should be ok)
                                # However, this baseline is only valid for the Ultrafast dynamic (4D) no the high spatial resoltution dynamic (Dyn)
                                si_bline = sslice_ref_df.loc[(sslice_ref_df['PatientID']==patient_id) & (sslice_ref_df['StudyDate']==int(visit_id)) & (sslice_ref_df['SequencePattern'].str.startswith(sequence))]

                                # compute similarity for each row
                                # si_bline["Anatomy"].apply(lambda x: SequenceMatcher(None, roi_label, x).ratio()).idxmax()

                                if si_bline.empty:
                                    bline_index = 1 #if sequence.lower().startswith('dyn') else si_bline

                                else:
                                    # Get the index by looking for the most similar Anatomy value, compute similarity for each row using SequenceMatcher
                                    bline_index = si_bline.loc[si_bline["Anatomy"].apply(lambda x: SequenceMatcher(None, roi_label, x).ratio()).idxmax(), "BaseLine"] # si_bline['BaseLine'].max()

                                roi_df = extract_roi(patient_dict['Visits'][visit_nro]['Sequences'][sequence]['nparray'],
                                                     img_mask['voxels'],
                                                     roi_metadata=patient_dict['Visits'][visit_nro]['Sequences'][sequence]['metadata'],
                                                     segment_index=segment_index,
                                                     baseline_index=bline_index, # if it is not a dynamic sequence (i.e. nt<=1)==> it is not used 
                                                     logger=logger)
                                
                                if not roi_df.empty:
                                    roi_df['PatientID'] = patient_id

                                    roi_df['VisitID']   = visit_id
                                    roi_df['VisitNro']  = visit_nro
                                    roi_df['Sequence']  = sequence                            
                                    roi_df['ROI label'] = roi_label

                                    logger.debug(roi_df.head())
                                    roi_df.to_csv(os.path.join(outputfolder, f'roi_{sequence}.csv'))
                                    roi_list.append(roi_df)
                    else:
                        logger.error(f'Cannot find suitable segmentation mask fitting the pattern {mask_folder_pattern}')

        else:
            print(f'Patient {patient_id} not in the processing list')
    if roi_list:
        all_rois_df = pd.concat(roi_list)
        all_rois_df.to_csv(os.path.join(os.path.expandvars(config_structure['path']['analysis']),
                                        '.'.join([config_structure['output']['roidata_name'],
                                                  config_structure['output']['fmt']])))

    print('All done. Bye!')


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