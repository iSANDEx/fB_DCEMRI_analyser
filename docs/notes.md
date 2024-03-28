# General notes and draws
<!-- A simple "notebook" to write down equations, diagrams, etc. that I can use when communicating results (e.g. slides decks, reports, web-based, etc.) -->

## Folder structure of the Tests directory
```
Test_Nro
     
    ├── datasets
    │   ├── PatientID: <Initials>-<Study_Code>(e.g CR-ANON18218)
    │   │   ├── Patient's Visit 1
    │   │   │   <Initials>-<Treatment_Point>-<date_of_visit(yyyymmdd)> 
    │   │   │   (e.g. CR-Pre-Treatment-20230120)
    │   │   │   ├── DCE MRI Seq. Nro: <Int> (e.g. 301)
    │   │   │   │   ├── DCE Time point: <Int> (e.g. 1)
    │   │   │   │   │   └── 3D Volume: <SeqNro>_<Seq Name>.nii.gz (e.g.301_dyn_ethrive.nii.gz)
    │   │   │   │   ├── ...
    │   │   │   │   │   └── ...
    │   │   │   │   ├── DCE Time point: <Int> (e.g. 6)
    │   │   │   │   │   └── 3D Volume: <SeqNro>_<Seq Name>.nii.gz (e.g.301_dyn_ethrive.nii.gz) 
    │   │   │   │     
    │   │   │   ├── Pre-Registered 4D Volume: 
    │   │   │       <Initials>-<Treatment_Point>_<date_of_visit>.nii.gz 
    │   │   │       (e.g. CR-Pre-Treatment-20221212.nii.gz)
    │   │   │   
    │   │   ├── Patient's Visit 2
    │   │   │   <Initials>-<Treatment_Point>-<date_of_visit(yyyymmdd)> 
    │   │   │   (e.g. CR-Post-Treatment-20230120)
    │   │   │   ├── DCE MRI Seq. Nro: <Int> (e.g. 301)
    │   │   │   │   ├── DCE 1st Time point: <Int> (e.g. 1)
    │   │   │   │   │   └── 3D Volume: <SeqNro>_<Seq Name>.nii.gz (e.g.301_dyn_ethrive.nii.gz)
    │   │   │   │   ├── ...
    │   │   │   │   │   └── ...
    │   │   │   │   ├── DCE n-th Time point: <Int> (e.g. 6)
    │   │   │   │   │   └── 3D Volume: <SeqNro>_<Seq Name>.nii.gz (e.g.301_dyn_ethrive.nii.gz) 
    │   │   │   │ 
    │   │   │   ├── Post-Registered 4D Volume:
    │   │   │   │ <Initials>-<Treatment_Point>_<date_of_visit>.nii.gz 
    │   │   │   │ (e.g. CR-Post-Treatment-20230120.nii.gz)
    │   │   │   │ 
    │   │   │   ├── Deformation Map Inter-visit Registration (only Post-Treatment visits):
    │   │   │   │ <"deformation_map">_<Registration_Method>_<Timepoint_of_Reference_Volume>_<Initials>-<Treatment_Point>_<date_of_visit>.nii.gz 
    │   │   │   │ (e.g. deformation_map_Elastix_fixedVol001_CR-Post-Treatment-20230120.nii.gz)
    │   │   │   │ 
    │   │   │   ├── Aligned Reference Volume Inter-visit Registration (only Post-Treatment visits):
    │   │   │   │ <"inter_visit_aligned">_<Registration_Method>_<Timepoint_of_Reference_Volume>_<Initials>-<Treatment_Point>_<date_of_visit>.nii.gz 
    │   │   │   │ (e.g. inter_visit_aligned_ants_fixedVol001_CR-Post-Treatment-20230120.nii.gz)
    │   │
    │   ├── ... (PatientID)
    │   
    ├── description.json (Text file describing the experiment, json format)
    │
    ├── parameters (Folder with the registration hyperparameters parameters used in the test)
    │   ├── For Elastix Registration Method: 
    │   │   <"Par"><XXXX>_<description>.txt 
    │   │   (e.g. Par0032_bsplines.txt)
    │   │   
    │   ├── For ANTs Registration Method: 
    │   │   <Descriptive_Name>.json 
    │   │   (e.g. DefaultANTspy.json)
    │   
    └── rois (Folder holding ROIs drawn in ImageJ, anything in here is only for visualisation, it not used by in any of the analysis programmed)
        ├── Multiple_ROIs_<Description>.zip
        └── Single_ROI_<Description>.roi
```
