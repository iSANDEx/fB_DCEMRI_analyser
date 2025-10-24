"""
dicom_batch.py - Functions to read multiple DICOM files or entire studies.
"""
from datetime import datetime as dtime
from .dicom_image import load_imaging_data

def load_patient_data(df_metadata, patient_id, visits_nro, sequence_patterns, usePhilipsReScale, logger=None):

    # Filter the main dataframe to get the patient of interest:
    patient_in_df = df_metadata[df_metadata['PatientID'].isin([patient_id])]
    # StudyID
    study_id = patient_in_df["StudyID"].unique().tolist()

    if len(study_id) > 1:

        if logger is not None:
            logger.warning(f'The StudyID for patient {patient_id} is not unique {study_id} ')

        else:
            print(f'[WARNING]: The StudyID for patient {patient_id} is not unique {study_id} ')

    study_id = study_id[0]
    # For the selected patient, gets the study dates. There are up to 2 visits per patient, the earliest must be the visit 1:
    visits_dates = sorted(patient_in_df['StudyDate'].unique().tolist())

    if len(visits_dates) > 2:
        if logger is not None:
            logger.warning(f'[WARNING]: There are more than 2 visits for patient {patient_id}. Considering only the earlier two')
        else:
            print(f'[WARNING]: There are more than 2 visits for patient {patient_id}. Considering only the earlier two')
        visits_dates = visits_dates[:2]

    visits_id = dict(zip([1, 2],visits_dates))

    patient_data = {'StudyID': study_id,
                    'Visits': {}}

    for visit_idx, visit_date in visits_id.items():
        if visit_idx in visits_nro:
            visit_df = patient_in_df[patient_in_df['StudyDate'].isin([visit_date])]
            patient_data['Visits'][visit_idx] = {
                'VisitID': visit_date,
                'Date': dtime.strptime(visit_date, "%Y%m%d"),
                'Sequences': dict([(sequence,{}) for sequence in sequence_patterns])
                }
            # Load the imaging data for each sequence
            for sequence_pattern in sequence_patterns:
                sequence_df = visit_df[visit_df['AbsFilePath'].str.contains(sequence_pattern)]
                if not sequence_df.empty:
                    image_array, image_itk, image_parameters = load_imaging_data(sequence_df, usePhilipsReScale, logger=logger)
                    patient_data['Visits'][visit_idx]['Sequences'][sequence_pattern]['itk'] = image_itk
                    patient_data['Visits'][visit_idx]['Sequences'][sequence_pattern]['nparray'] = image_array
                    patient_data['Visits'][visit_idx]['Sequences'][sequence_pattern]['metadata'] = image_parameters
    
    return patient_data


def read_dicom_folder(folder_path):
    pass  # TODO: implement
