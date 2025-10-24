"""
dicom_reader.py - Atomic functions for reading a single DICOM file.
"""

import pandas as pd
import pydicom as dcm
from ..utils import flatten_tags_dictionary, get_filelist_recursively, parse_mixed_datetime


def load_dicom_folder(path_to_dicom_folder, tags_to_read, fext='dcm', read_pixel_tag=False, logger=None):

    dcmlist = get_filelist_recursively(path_to_dicom_folder, fext)

    if logger is not None:
        logger.info(f"{len(dcmlist)} {fext.upper()} files to process inside {path_to_dicom_folder}")

    # Pass the list to the dicom reader:
    dicom_metadata_hdr = flatten_tags_dictionary(tags_to_read, tag_to_skip=["_comment"])
    dicomMetadataList = []

    if logger is not None:
        logger.debug("Loading DICOM metadata, please wait...")

    for dcmfile in dcmlist:
        dcm_metadata = load_dicom_file(dcmfile, tags_to_read, read_pixel_tag)
        dicomMetadataList.append(dcm_metadata['metadata'])

    if logger is not None:
        logger.debug("All DICOM metadata loaded")

    dicom_dataframe = pd.DataFrame(columns=dicom_metadata_hdr, data=dicomMetadataList)#.astype(dtype_df_dict)

    dicom_dataframe = sort_timing_dicom_dataframe(dicom_dataframe)

    if logger is not None:
        logger.debug("DICOM metadata sorted in a dataframe")

    return dicom_dataframe



def load_dicom_file(path_to_dicom_file, tags_to_read, read_pixel_tag=False):

    # Reads an individual DICOM file and returns the metadata and image (if required)

    dicom_object = dcm.dcmread(path_to_dicom_file, stop_before_pixels = not(read_pixel_tag))

    dicom_metadata_fields = flatten_tags_dictionary(tags_to_read)
    dicom_metadata = [None]*len(dicom_metadata_fields)

    for tagSubSetName, tagSubSetFields in tags_to_read.items():
        # print(f'TagSubSetName: {tagSubSetName}')
        for tagName, tagValue in tagSubSetFields.items():
            try:
                dicom_metadata[dicom_metadata_fields.index(tagName)] = dicom_object[tagValue['hex']].value
            except Exception:
                # print(f'Attribute {tagName} does not exist, skipping it...')
                pass
    
    # Add the filepath:
    dicom_metadata[dicom_metadata_fields.index('AbsFilePath')] = path_to_dicom_file
    dicom_object = {'metadata': dicom_metadata}

    if read_pixel_tag:
        dicom_object['image'] = dicom_object.pixel_array

    return dicom_object


def sort_timing_dicom_dataframe(dicom_dataframe):
    # This is the main value added by reading the dicom files by ourselves:
    # Includes time attributes to plot dynamic series

    # Create datetime objects for the paired date and time attributes
    # They must be included as outer keys in TAGS_TO_READ 
    date_time_attr = ['InstanceCreation', 'Study', 'Series', 'Acquisition', 'Content']

    for datetime_tagName in date_time_attr:
        date_attr = datetime_tagName+'Date'
        time_attr = datetime_tagName+'Time'
        dicom_dataframe[datetime_tagName+'DateTime'] = parse_mixed_datetime(dicom_dataframe[date_attr] + dicom_dataframe[time_attr])

    # Additionally, merges the Study Date with Contrast Start/End to ensure they fit in the acquisition window:
    dicom_dataframe['ContrastBolusStartDateTime'] = parse_mixed_datetime(dicom_dataframe['StudyDate'] + dicom_dataframe['ContrastBolusStartTime'])
    dicom_dataframe['ContrastBolusEndDateTime'] = parse_mixed_datetime(dicom_dataframe['StudyDate'] + dicom_dataframe['ContrastBolusStopTime'])

    # Ensures PatientName is a string:
    dicom_dataframe['PatientName'] = dicom_dataframe['PatientName'].astype(str)

    # # Setup a per-slice timing:
    # # For each Series do the following:
    # #   - Sort, in ascending order, the TemporalPositionIdentifier
    # #   - Sort, in ascending order, the slice location (from - to +)
    # #   - Based on the dataframe index, loop over the Temporal position and populate the new field AcquisitionDateTimeSlice:
    # # 
    dicom_dataframe['perSliceAcquisitionTime'] = [None]*len(dicom_dataframe)
    dicom_dataframe['perSliceAcquisitionTimeInSecs'] = [None]*len(dicom_dataframe)
    dicom_dataframe['ContrastBolusStartTimeInSecs'] = [None]*len(dicom_dataframe)

    # Patient List:
    patientList = dicom_dataframe['PatientName'].unique().tolist()
    for patient in patientList:
        # Studies List for each patient:
        patient_in_df = dicom_dataframe[dicom_dataframe['PatientName'].isin([patient])]
        studies_in_patient = patient_in_df['StudyDate'].unique().tolist()
        for study_patient in studies_in_patient:
            study_in_patient = patient_in_df[patient_in_df['StudyDate'].isin([study_patient])]
            sequences_in_study = study_in_patient['SeriesDescription'].unique().tolist()
            # min acquisition time between Dyn eTHRIVE and 4D_THRIVE:
            df_aux = study_in_patient[(study_in_patient['SeriesDescription'].str.startswith('4D_THRIVE')) | (study_in_patient['SeriesDescription'].str.startswith('Dyn'))]
            min_time = df_aux['AcquisitionDateTime'].min(skipna=True)
            for sequence_study_patient in sequences_in_study:
                # We're now at the level of series.
                # For the timming, we're only interested in 4D_THRIVE_Ultrafast & Dyn eTHRIVE:
                if sequence_study_patient.startswith('4D_THRIVE') | sequence_study_patient.startswith('Dyn'):
                    serie_in_study = study_in_patient[study_in_patient['SeriesDescription'].isin([sequence_study_patient])]
                    # Additional Filter to remove the corrupted single file:
                    serie_in_study = serie_in_study[serie_in_study['AcquisitionNumber'].notna()]
                    # Now, we should be ready to assign the timings:
                    # Sort by temporal position:
                    serie_in_study.sort_values(by=['TemporalPositionIdentifier', 'SliceLocation'], ascending=(True, False), inplace=True)
                    nslices = len(serie_in_study['SliceLocation'].unique().tolist())
                    slice_order = range(0, nslices)
                    # Here loop over TimePos and slice location using the formula:
                    # AcquisitionTime  + TR * TempPos * Range(Slice)
                    TR = serie_in_study['RepetitionTime'].unique().tolist()
                    if len(TR) > 1:
                        print(f'WARNING!: There are more than 1 TR ({TR}) in the series. Using the first one available')
                    # else:
                        # print(f'TR: {TR[0]}ms')
                    TR = TR[0]

                    nt = serie_in_study['NumberOfTemporalPositions'].unique().tolist()
                    if len(nt) > 1:
                        print(f'ERROR: The number of temporal positions {nt} is not consistent through the series')
                        sys.exit()
                    # else:
                        # print(f'Number of Temporal Positions: {nt[0]}')                
                    nt = int(nt[0])
                    slices_positions = list(slice_order)*nt
                    perSliceAcquisitionDateTime = pd.to_timedelta([z*TR/1000.0 for z in slices_positions], unit='s')
                    # serie_in_study['perSliceAcquisitionDateTime'] = [None]*len(serie_in_study)
                    serie_in_study['perSliceAcquisitionDateTime'] = serie_in_study['AcquisitionDateTime'] + perSliceAcquisitionDateTime
                    
                    # Find the earliest AcquisitionEndTime (ignoring NaT values) -- But the min time in my case, is the start of the Dyn eTHRIVE acquisition
                    # min_time = serie_in_study['perSliceAcquisitionDateTime'].min(skipna=True)
                    # Compute time differences in seconds for the acquisition and contrast bolus
                    serie_in_study['perSliceAcquisitionTimeInSecs'] = (serie_in_study['perSliceAcquisitionDateTime'] - min_time).dt.total_seconds()
                    serie_in_study['ContrastBolusStartTimeInSecs'] = (serie_in_study['ContrastBolusStartDateTime'] - min_time).dt.total_seconds()

                    dicom_dataframe.loc[serie_in_study.index, 'perSliceAcquisitionDateTime'] = serie_in_study['perSliceAcquisitionDateTime']
                    dicom_dataframe.loc[serie_in_study.index, 'perSliceAcquisitionTimeInSecs'] = serie_in_study['perSliceAcquisitionTimeInSecs']
                    dicom_dataframe.loc[serie_in_study.index, 'ContrastBolusStartTimeInSecs'] = serie_in_study['ContrastBolusStartTimeInSecs']
                    
    # Add time axis in minutes too:
    dicom_dataframe[['perSliceAcquisitionTimeInMins', 'ContrastBolusStartTimeInMins']] = dicom_dataframe[['perSliceAcquisitionTimeInSecs', 'ContrastBolusStartTimeInSecs']]/60.0

    # Slicer3D uses the image position patient coordinate, rather than SliceLocation:
    dicom_dataframe[['x','y','z']] = dicom_dataframe['ImagePositionPatient'].apply(pd.Series)
    
    return dicom_dataframe


