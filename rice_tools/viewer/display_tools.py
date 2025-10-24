"""
display_tools.py - Atomic functions for displaying image data
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt

def overlay_mask(background_volume, foreground_mask, time_index=None, figure_title=None, segment_index=0, logger=None, savepath=None):

    bckgrnd_shape = background_volume.shape
    # Cleverer way to get the sizes, padding shape with None so we can safely unpack:
    # nt, nz, nx, ny = (list(bckgrnd_shape) + [None] * (4 - len(shape)))[:4]

    # However, it assumes the dimensions order nt,nz,nx,ny, but for 3D, it is nz, nx, ny, 
    # so will have to stick to the std way:
    if background_volume.ndim == 4:
        nt, nz, nx, ny = bckgrnd_shape
    elif background_volume.ndim == 3:
        nz, nx, ny = bckgrnd_shape
        background_volume = background_volume[np.newaxis, :, :, :]
        nt = None
        # force the time_index to be 0:
        time_index = None

    if time_index is None:
        time_index = 0

    if background_volume.ndim == 1:
        if logger is not None:
            logger.warning('Dataset contains only 1 dimension')
        else:
            print('[WARNING]: Dataset contains only 1 dimension')  

    if logger is not None:
        logger.info(f'Nx:{nx}, Ny:{ny}, Nz:{nz}, Nt:{nt}')
    else:
        print(f'Nx:{nx}, Ny:{ny}, Nz:{nz}, Nt:{nt}')

    # The 4th dimension in the mask is the number of labels
    mask_shape = foreground_mask.shape
    nsegments, msk_nx, msk_ny, msk_nz = (list(mask_shape) + [None] * (4 - len(mask_shape)))[:4]

    if segment_index >= nsegments:
        # If here, the segment index points to a non-existing segment
        segment_index = nsegments-1

    # To ensure they are consistent with the ordering given in the dicom readers, need to permute the axes:
    # The segmentation mask is [nlabel, nx, ny, nz], the dicom output is sorted as [nt, nz, nx, ny]
    foreground_mask = np.permute_dims(foreground_mask, [0,-1, 2, 1]) 

    # Check the sizes are consistent with the background_volume:
    if any([nx != msk_nx, ny != msk_ny, nz != msk_nz]):
        if logger is not None:
            logger.error(f'Dimensions of background volume ({nx}x{ny}x{nz}) and foreground mask ({msk_nx}x{msk_ny}x{msk_nz}) are not consistent. Stopped')
        else:
            print(f'Dimensions of background volume ({nx}x{ny}x{nz}) and foreground mask ({msk_nx}x{msk_ny}x{msk_nz}) are not consistent. Stopped')
        return False

    # Identify no-null mask slices
    nonzeroidx = []
    for indz in range(msk_nz):
        nnzero = np.count_nonzero(foreground_mask[segment_index, indz, :, :])
        if nnzero > 0:
            nonzeroidx.append(indz)

    nfigs = len(nonzeroidx)
    nrows = int(np.ceil(np.sqrt(nfigs)))
    ncols = int(np.ceil(nfigs/nrows))

    fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(6.0*ncols, 6.0*nrows))
    if nfigs > 1:
        axr = ax.ravel()
    else:
        axr = [ax]

    for nfig in range(nfigs):
        contours, hierarchy = cv2.findContours(foreground_mask[segment_index, nonzeroidx[nfig], :, :], 
                                               cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)#CHAIN_APPROX_SIMPLE)
        masked_slice = cv2.cvtColor(cv2.normalize(background_volume[time_index, nonzeroidx[nfig], :,:], None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U),
                                    cv2.COLOR_GRAY2RGB)
        cv2.drawContours(masked_slice,
                         contours, -1, (255, 255, 0), 1) # Draw all contours in yellow (RGB) with thickness 1


        # Get the centroid of the first contour and zoom in based on them:
        if contours:
            M = cv2.moments(contours[0])
            # Flatten contour points:
            points = contours[0].reshape(-1, 2)
        else:
            M['m00'] = 0
            points = np.array([[nx, ny]])


        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
        else:
            cx, cy = nx//2, ny//2 # Handle cases where m00 is zero (e.g., empty or invalid contour)

        # Define a bounding box centred at the contour centroid but large enough to fully contain the contour

        # Find the farthest point in both x and y
        max_dx = np.max(np.abs(points[:, 0] - cx))
        max_dy = np.max(np.abs(points[:, 1] - cy))

        # Make the box square by using the largest distance
        # half_side = int(max(max_dx, max_dy))

        # Make the box quarter of the imaging size:
        half_side = max(nx//4, ny//4)

        # Compute top-left and bottom-right corners
        x1 = cx - half_side
        y1 = cy - half_side
        x2 = cx + half_side
        y2 = cy + half_side

        # Clip to image boundaries
        x1 = max(x1, 0)
        y1 = max(y1, 0)
        x2 = min(x2, nx - 1)
        y2 = min(y2, ny - 1)

        # Draw the square
        cv2.rectangle(masked_slice, (x1, y1), (x2, y2), (255, 0, 0), 2)
        # and crosshair:
        cv2.line(masked_slice, (x1, cy), (x2, cy), (255,0,0), 1)
        cv2.line(masked_slice, (cx, y1), (cx, y2), (255,0,0), 1)

        axr[nfig].imshow(masked_slice)
        # Apply the square as a zoom:
        axr[nfig].axis([x1, x2, y2, y1])
        axr[nfig].set_xlabel(f'Slice Index: {nonzeroidx[nfig]:0d}')

    fig.suptitle(figure_title)

    if savepath is not None:
        fig.savefig(savepath.replace('.png', f'_timepoint_{time_index}.png'))
        plt.close()
    else:
        plt.show()


    return True