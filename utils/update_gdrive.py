import os
import sys
import shutil
import pandas as pd

def list_folder_content(path, show_hidden=False):
    if show_hidden:
        ddfldrlst = os.listdir(path)
    else:
        ddfldrlst = list(filter(lambda item: not item.startswith('.'),os.listdir(path)))      
    return ddfldrlst


HOMEPATH = os.getenv('HOME')
SRCPATH = os.path.join(HOMEPATH, 'Data' ,'fMRIBreastData', 'tests')
GDRIVEPATH = os.path.join(HOMEPATH, 'Library', 'CloudStorage', 'GoogleDrive-jose.ulloa@isandex.com', 'My\ Drive', 'fbMRIBreastData')
OUTPUTPATH = os.path.join(HOMEPATH, 'Data', 'fMRIBreastData', 'aux')
FOLDERLIST = sorted(list_folder_content(SRCPATH))

csv_file = pd.DataFrame()
csv_data = []
for folder in FOLDERLIST:
    path_to_test = os.path.join(SRCPATH, folder, 'datasets')
    # within each path_to_test there are multiple patients, each one with one or two visits:
    patient_list = list_folder_content(path_to_test)
    for patient in patient_list:
        path_to_patient = os.path.join(path_to_test, patient)
        visit_list = list_folder_content(path_to_patient)
        for visit in visit_list:
            path_to_visit = os.path.join(path_to_patient, visit)
            folders_in_visit = list_folder_content(path_to_visit)
            for folder_i in folders_in_visit:
                if folder_i.endswith('nii.gz'):
                    path_to_input_nii = os.path.join(path_to_visit, folder_i)
                    path_to_output_nii = path_to_input_nii.replace(SRCPATH, GDRIVEPATH)
                    # print(f'Path in Google Drive: {path_to_output_nii}')
                    # print(f'Does the path exist?: {os.path.isfile(path_to_output_nii)}')
                    csv_data.append([f'cp {path_to_input_nii} {path_to_output_nii}'])
                    
                    # shutil.copy2(path_to_input_nii, path_to_output_nii)

csv_df = pd.DataFrame(columns=['Path'], data=csv_data)
csv_df.to_csv(os.path.join(OUTPUTPATH, 'list.csv'), index=False)