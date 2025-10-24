"""
get_rois.py - Atomic functions for extracting roi values from different types of sequences
"""

import numpy as np
import pandas as pd

def extract_roi(source_volume, segmentation_mask, roi_metadata, segment_index=0, baseline_index=0, logger=None):
    """_summary_
    EXTRACT_ROI: gets the values inside a roi defined by the segmentation mask. 

    Args:
        source_volume (_type_): Numpy NDarray sorted as [nt, nz, nx, ny] (if 4D) and [nz, nx, ny] (if 3D)
        segmentation_mask (_type_): _description_ NRRD Segmentation mask file
        roi_metadata (dict): contains the Imaging parameters that are going to be used for quantification: time, z-location, flip angle and tr

    """

    # Check the dimensions and sizes are consistent:
    source_vol_shape = source_volume.shape
    if source_volume.ndim == 4:
        nt, nz, nx, ny = source_vol_shape
    elif source_volume.ndim == 3:
        nz, nx, ny = source_vol_shape
        source_volume = source_volume[np.newaxis, :, :, :]
        nt = 1

    # The 4th dimension in the mask is the number of labels
    mask_shape = segmentation_mask.shape
    nsegments, msk_nx, msk_ny, msk_nz = (list(mask_shape) + [None] * (4 - len(mask_shape)))[:4]

    if segment_index >= nsegments:
        # If here, the segment index points to a non-existing segment
        segment_index = nsegments - 1

    # To ensure they are consistent with the ordering given in the dicom readers, need to permute the axes:
    # The segmentation mask is [nlabel, nx, ny, nz], the dicom output is sorted as [nt, nz, nx, ny]
    # TODO: verify the correct order of nx and ny in the segmentation data!!!
    segmentation_mask = np.permute_dims(segmentation_mask, [0, -1, 2, 1]) 

    # Check the sizes are consistent with the background_volume:
    if any([nx != msk_nx, ny != msk_ny, nz != msk_nz]):
        if logger is not None:
            logger.error('Dimensions of background volume and foreground mask are not consistent. Stopped')
        else:
            print(f'Dimensions of background volume ({nx}x{ny}x{nz}) and foreground mask ({msk_nx}x{msk_ny}x{msk_nz})are not consistent. Stopped')
        return pd.DataFrame()
    
    # Loop over the non-null mask slices and extract the values from the corresponing slices in the source volume:
    # The information is arranged into a bigger dataframe that is saved, 
    # but at this level, this script only passes an individual dataframe:
    roi_header = ['slice_index', 'time_index', 
                  'mean','median','stddev',
                  'delta_mean', 'delta_median', 'delta_stddev',
                  'pc_enh_mean', 'pc_enh_median', 'pc_enh_stddev', 
                  'bline', 'TR', 'FA', 'time', 'zloc']
    roi_data = []

    for indz in range(msk_nz):
        nnzero = np.count_nonzero(segmentation_mask[segment_index, indz, :, :])
        if nnzero > 0:
            # Baseline only makes sense if nt > 1:
            if nt > 1:
                baseline_roi = np.median(source_volume[:baseline_index, indz, :, :], axis=0)
                masked_baseline = np.ma.array(baseline_roi, mask = (segmentation_mask[segment_index, indz, :, :] == 0))
            for indt in range(nt):
                masked_array = np.ma.array(source_volume[indt, indz, :, :], mask = (segmentation_mask[segment_index, indz, :, :] == 0))
                # Check the documentation at https://numpy.org/devdocs/reference/routines.ma.html#masked-array-operations
                # to see how to apply functions to the masked array
                array_mean, array_median, array_stddev = [masked_array.mean(), np.ma.median(masked_array), np.ma.std(masked_array)]
                if nt > 1:
                    masked_delta = masked_array - masked_baseline
                    pc_enh = 100 * masked_delta / masked_baseline
                    delta_mean, delta_median, delta_stddev = [masked_delta.mean(), np.ma.median(masked_delta), np.ma.std(masked_delta)]
                    pc_enh_mean, pc_enh_median, pc_enh_stddev = [pc_enh.mean(), np.ma.median(pc_enh), np.ma.std(pc_enh)]
                else:
                    delta_mean, delta_median, delta_stddev, pc_enh_mean, pc_enh_median, pc_enh_stddev = [0]*6
                    
                roi_data.append([indz, indt, array_mean, array_median, array_stddev, 
                                 delta_mean, delta_median, delta_stddev,
                                 pc_enh_mean, pc_enh_median, pc_enh_stddev,
                                 baseline_index, 
                                 roi_metadata['TR'], roi_metadata['FA'],
                                 roi_metadata['TimeMatrix'][indz, indt],
                                 roi_metadata['SliceMatrix'][indz, indt]])
    
    roi_df = pd.DataFrame(columns=roi_header, data=roi_data)
    # if logger is not None:
    #     logger.debug(roi_df.head())

    return roi_df


