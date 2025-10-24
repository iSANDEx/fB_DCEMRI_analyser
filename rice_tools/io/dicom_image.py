"""
dicom_image.py - Functions to reconstruct DICOM images from metadata and arrange them by sequence.
"""
import os
import itk
import sys
import numpy as np
import pandas as pd
import pydicom as dcm


def load_imaging_data(sequence_df, usePhilipsReScale, logger=None):

    # Get parameters of interest: SequenceID, TR, FA
    
    imaging_parameters = {
        'sequenceID': sequence_df['AbsFilePath'].apply(os.path.dirname).unique().tolist()[0]
    }

    flip_angle = sequence_df['FlipAngle'].unique().tolist()

    if len(flip_angle) > 1:

        if logger is not None:
            logger.warning(f'The dataset contains more than one flip angle ({flip_angle}), check the input')
 
        else:
            print(f'[WARNING]: The dataset contains more than one flip angle ({flip_angle}), check the input')

        sys.exit()

    imaging_parameters['FA'] = flip_angle[0]

    rep_time = sequence_df['RepetitionTime'].unique().tolist()

    if len(rep_time) > 1:

        if logger is not None:
            logger.warning(f'The dataset contains more than one flip angle ({flip_angle}), check the input')

        else:
            print(f'[WARNING]: The dataset contains more than one TR ({rep_time}), check the input')

        sys.exit()

    imaging_parameters['TR'] = rep_time[0]

    volume_array, slice_position_matrix, time_matrix, scan_details = get_image_dataset(sequence_df, use_philips_rescale=usePhilipsReScale, logger=logger)
    volume_itk, volume_metadata = create_itk_from_dicom(volume_array, scan_details, time_matrix, logger=logger)
    
    imaging_parameters['SliceMatrix'] = slice_position_matrix
    imaging_parameters['TimeMatrix'] = time_matrix
    imaging_parameters['ScanDetails'] = scan_details
    imaging_parameters['ITKMetadata'] = volume_metadata
    
    return volume_array, volume_itk, imaging_parameters

def create_itk_from_dicom(volume_asarray, subset_dicom_metadata, time_matrix, logger=None):
    # Identify whether the data is 3D or 4D:
    ndims = np.ndim(volume_asarray)
    eye = np.eye(ndims)
    
    eye[:3, :2] = np.array(subset_dicom_metadata['ImageOrientationPatient'].values[0]).reshape(2,3).T

    direction_matrix = itk.matrix_from_array(eye)

    # The DICOM convention is (x,y,z), but ITK's convention is (z, y, x)
    origin_vector = np.array(subset_dicom_metadata['ImagePositionPatient'].apply(pd.Series).min())
    spacing_vector = np.array(subset_dicom_metadata['spacing'])
    if ndims == 4:
        volume_as_list = np.split(volume_asarray, volume_asarray.shape[0], axis=0)

        itk_volume = itk.compose_image_filter(*volume_as_list)
        dyn_mode, c = np.unique(np.diff(time_matrix[1,:]), return_counts=True)
        time_spacing = dyn_mode[np.argmax(c)]
        spacing_vector = np.insert(spacing_vector, 0, time_spacing)
        origin_vector = np.insert(origin_vector, 0, 0)
    else:
        itk_volume = itk.GetImageFromArray(volume_asarray)    

    if logger is not None:
        logger.debug(f'Volume size: {itk_volume.shape}')

    else:
        print(f'Volume size: {itk_volume.shape}')

    itk_volume.SetSpacing(spacing_vector)
    itk_volume.SetOrigin(origin_vector)
    itk_volume.SetDirection(direction_matrix)
 
    itk_volume_metada = dict(itk_volume)

    if logger is not None:
        logger.debug(f'Metadata: {itk_volume_metada}')

    else:
        print(f'Metadata: {itk_volume_metada}')

    return itk_volume, itk_volume_metada

def get_image_dataset(dataset_df, use_philips_rescale=True, logger=None):
    """ 
    This function loads the image corresponding a single dataset. 
    I define a single dataset as a set of dicom files within a single sequence (i.e. SeriesDescription is a single value) 
    It requires the image's height and width are the same for all the elements in the dataset. 
    It should be able to deal with 3D (volumetric) and dynamic (time) series, either 2D+time or 4D (3D + time)

    Args:
        dataset_df (_type_): _description_
        use_philips_rescale (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
    """
    # Ensure the dataset is a single dataset:
    patient_name = dataset_df['PatientID'].unique().tolist()

    if len(patient_name) > 1:

        if logger is not None:
            logger.warning(f'WARNING: The dataset contains more than one patient ({patient_name}), check the input')

        else:
            print(f'WARNING: The dataset contains more than one patient ({patient_name}), check the input')

        sys.exit()

    patientID = patient_name[0]

    scan_date = dataset_df['StudyDate'].unique().tolist()

    if len(scan_date) > 1:

        if logger is not None:
            logger.warning(f'The dataset contains more than one study date ({scan_date}), check the input')

        else:
            print(f'WARNING: The dataset contains more than one study date ({scan_date}), check the input')

        sys.exit()

    scan_date = scan_date[0]

    sequence_name = dataset_df['SeriesDescription'].unique().tolist()

    if len(sequence_name) > 1:

        if logger is not None:
            logger.warning(f'The dataset contains more than one sequence ({sequence_name}), check the input')

        else:
            print(f'WARNING: The dataset contains more than one sequence ({sequence_name}), check the input')

        sys.exit()

    sequence_name = sequence_name[0]

    # Rows and Columns must be the same for the whole series:
    nrows_list = dataset_df['Rows'].unique()
    ncols_list = dataset_df['Columns'].unique()
    
    if (len(nrows_list) > 1) | (len(ncols_list)>1):
    
        if logger is not None:
            logger.warning(f'Either the number of ROWS ({nrows_list}) or COLUMNS ({ncols_list}) is not consistent for the Series')
    
        else:
            print(f'WARNING: Either the number of ROWS ({nrows_list}) or COLUMNS ({ncols_list}) is not consistent for the Series')
    
    [w, h] = [ncols_list[0], nrows_list[0]]

    slice_locations = dataset_df['z'].unique().tolist()
    slice_locations.sort(reverse=False)
    
    ns = len(slice_locations)

    number_of_temporal_positions = dataset_df['NumberOfTemporalPositions'].unique()
    # numberOfTempPositions must be only 1 element length, because it must be the same for a single Series (afaik)
    temporal_positions = dataset_df['TemporalPositionIdentifier'].unique().tolist()
    temporal_positions.sort(reverse=False)

    
    if len(number_of_temporal_positions) > 1:

        if logger is not None:
            logger.warning(f'Check you are processing only one series, the length of temporal_positions is {len(number_of_temporal_positions)}')

        else:
            print(f'WARNING: Check you are processing only one series, the length of temporal_positions is {len(number_of_temporal_positions)}')

        sys.exit()

    nt = number_of_temporal_positions[0]

    if logger is not None:
        logger.info(f'Dataset {patientID}-{scan_date}-{sequence_name} contains {ns} slices and {nt} temporal positions of size {w}x{h} (WxH)')

    else:
        print(f'Dataset {patientID}-{scan_date}-{sequence_name} contains {ns} slices and {nt} temporal positions of size {w}x{h} (WxH)')

    # Image resolution and slice spacing
    # df_metadata_patient_visit_sequence['PixelSpacing']
    [resRows, resCols]= dataset_df['PixelSpacing'].apply(pd.Series).T.values.tolist()
    deltaRow, deltaCol = [np.unique(resRows), np.unique(resCols)]

    # resolution along the slice direction:
    # delta_z = dataset_df['SliceThickness'].unique()
    delta_z = dataset_df['SpacingBetweenSlices'].unique()

    if (len(deltaRow) > 1) | (len(deltaCol) > 1) | (len(delta_z) > 1):

        if logger is not None:
            logger.warning('Check you are processing only one series')
            logger.warning(f'\t the length of the resolutions parameters is not 1 for Rows ({len(deltaRow)}), Columns ({len(deltaCol)}) and/or slice ({len(delta_z)})')

        else:
            print('WARNING: Check you are processing only one series')
            print(f'\t the length of the resolutions parameters is not 1 for Rows ({len(deltaRow)}), Columns ({len(deltaCol)}) and/or slice ({len(delta_z)})')

        sys.exit()

    resx_W, resy_H, resz_Z = [deltaRow[0], deltaCol[0], delta_z[0]]
    if logger is not None:
        logger.info(f'Image resolution is {resx_W:.3f}x{resy_H:.3f}x{resz_Z:.2f} [mm/pixel] (WxHxZ)')
    else:
        print(f'Image resolution is {resx_W:.3f}x{resy_H:.3f}x{resz_Z:.2f} [mm/pixel] (WxHxZ)')


    # Load the data, remember the dataframe is already sorted by slice->time:
    # Remember the array order in numpy is W(rows), H(cols), Z(slice)
    image4D = np.full((nt, ns, w, h), np.nan)
    timeaxis_spatial_temporal = np.full((ns, nt), np.nan)
    zlocation_spatial_temporal = np.full((ns, nt), np.nan)

    for dicom_file_row, dicom_datafile in dataset_df.iterrows():
        dcm_object = dcm.dcmread(dicom_datafile['AbsFilePath'])
        slice_position = slice_locations.index(dicom_datafile["z"])
        time_position = temporal_positions.index(dicom_datafile["TemporalPositionIdentifier"])
        # print(f'Slice Position: {slice_position}')
        # print(f'Temporal Position: {time_position}')
        
        dcm_image_32bit = dcm_object.pixel_array.astype(np.float32)
        # if rescale:
        # According to this thread https://stackoverflow.com/questions/67889762/what-is-the-difference-between-rescale-slope-intercept-and-scale-slope-inter
        # The forumalea relevant are:
        # D = R * RS + RI; R= raw pixel value, RS Rescale Slope (0028,1053), RI Rescale Intercept (0028,1052)
        # P = D / (RS * SS); D= Displayed Value (in the scanner screen), RS Rescale Slope (0028,1053), SS Scale Slope (2005,100E) "PhilipsScaleSlope"
        dcm_image_32bit *= dicom_datafile['RescaleSlope']
        dcm_image_32bit += dicom_datafile['RescaleIntercept']
        if use_philips_rescale:
            dcm_image_32bit /= (dicom_datafile['RescaleSlope'] * dicom_datafile['PhilipsScaleSlope'])

        # image4D[:,:,slice_position, time_position] = dcm_image_32bit
        image4D[time_position, slice_position, :, :] = dcm_image_32bit
        # Get the timing (secs) and location (mm) of each slice, in secs. It allows to easily get the time axis when plotting the data
        timeaxis_spatial_temporal[slice_position, time_position] = dicom_datafile['perSliceAcquisitionTimeInSecs']
        zlocation_spatial_temporal[slice_position, time_position] = dicom_datafile['z']
    

    image4D = np.squeeze(image4D)
    scanDetails = {'scanDateTime': scan_date,
                   'sequenceName': sequence_name,
                   'spacing': [resx_W, resy_H, resz_Z],
                   'ImageOrientationPatient': dataset_df['ImageOrientationPatient'],
                   'ImagePositionPatient': dataset_df['ImagePositionPatient'],
                   'TR': dataset_df['RepetitionTime'].unique().tolist(),
                   'TE': dataset_df['EchoTime'].unique().tolist(),
                   'FA': dataset_df['FlipAngle'].unique().tolist(),
                   'ETL': dataset_df['EchoTrainLength'].unique().tolist()
                   }

    return image4D, zlocation_spatial_temporal, timeaxis_spatial_temporal, scanDetails
