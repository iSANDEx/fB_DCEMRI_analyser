"""
mask_reader.py - Atomic functions for reading mask files
"""
import cv2
import numpy as np
from slicerio import read_segmentation as read_seg

def read_mask(path_to_mask_file):
    
    if path_to_mask_file.endswith('nrrd'):
        # Load nrrd file    
        segmentation_data = read_seg(path_to_mask_file)

    return segmentation_data

def build_mask(mask_definition_df, df_filter):
    """
    This script draws a mask in a SINGLE SLICE
    Given a volume size, it draws a mask according to the mask_definition parameters, which are compatible with opencv:
    mask_definition = {
        'shape': 'circle', 'rectangle' or 'polygon',
        'centre': (Cx, Cy, Cz),
        'radius': Rxy                
    }

    Args:
        volume_size (_type_): _description_
        mask_definition (_type_): _description_
    """
    # Create a mask that can be used to get more precise summaries:
    mask_sub_df = mask_definition_df[mask_definition_df['PatientID'].isin([df_filter['PatientID']])]
    if not mask_sub_df.empty:
        mask_sub_df = mask_sub_df[mask_sub_df['StudyDate'].isin([df_filter['VisitID']])]
        if not mask_sub_df.empty:
            anatomies = mask_sub_df['Anatomy'].unique().tolist()
            # Size must be unique for every patient/visit date (it was derived from a single sequence)
            [Nx, Ny, Nz] = [mask_sub_df[col].unique()[0] for col in ['Nx', 'Ny', 'Nz']]
            # To be consistent with Slicer's segmentation mask (seg.nrrd), the order is (nlabel, nx, ny, nz)
            image_mask = {'voxels': np.zeros((len(anatomies), Ny, Nx, Nz), dtype='uint8'),
                        'labels': {}}
            
            for idx, anatomy in enumerate(anatomies):
                image_mask['labels'][anatomy] = idx
                # Get the ROI parameters from the df:
                mask_slice = np.zeros((Ny, Nx), dtype='uint8')
                [Cx, Cy, Cz, Radius] = [mask_sub_df[mask_sub_df['Anatomy'].isin([anatomy])][col].values[0] for col in ['Cx','Cy','Cz','Radius']]
                cv2.circle(mask_slice, (Cy, Cx), Radius, [255]*1, -1)
                image_mask['voxels'][idx, :, :, Cz] = mask_slice

                # cv2.imshow('Image Display', mask_slice)
                # cv2.waitKey(0)
        else:
            image_mask = []
    else:
        image_mask = []

    return image_mask