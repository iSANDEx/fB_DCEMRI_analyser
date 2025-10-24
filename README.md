# fB_DCEMRI_analyser
 Set of tools to analyse function Breast-DCE-MRI data
 

# Pipelines Usage
## Extract ROI values from all dataset and arrange them as a dataframe (csv)
* Using segmentation mask defined manually in slicer (files ```.seg.nrrd```)
``` python 
python -m rice_tools.pipelines.export_segmasks -c '/Users/joseulloa/Data/FTV_DCEMRI_Phase02/data_analysis/config/batch_subjects_segmask.json' 
```
Output will be stored in ```data_analysis/output/all_rois.csv```
* Using synthetic circular ROI defined in a single slice (coordinates taken from ```info/slice_references.csv```)
``` python
python -m rice_tools.pipelines.export_ssliceref -c '/Users/joseulloa/Data/FTV_DCEMRI_Phase02/data_analysis/config/batch_subjects_ssliceref.json' 
```
Output will be stored in ```data_analysis/output/sslice_roi.csv```

## Plot Time course of dynamic series
* Plot Time course of the median over a single slice ROI - Batch
```python
python -m rice_tools.pipelines.process_dynamic -c '/Users/joseulloa/Data/FTV_DCEMRI_Phase02/data_analysis/config/batch_subjects_ssliceref_{CURVE}_{ROI}.json' 
```
Where {ROI} = ['tumour', 'asc_aorta', 'desc_aorta'] and {CURVE} = ['pcenh', 'sigint']

* Plot Time course of the average multiple slice ROI (```.seg.nrrd```) - Batch
```python
python -m rice_tools.pipelines.process_dynamic -c '/Users/joseulloa/Data/FTV_DCEMRI_Phase02/data_analysis/config/batch_subjects_segmask_{CURVE}.json' 
```
Where {CURVE} = ['pcenh', 'sigint']

Output will be plots saved as image within each patient/subject folder

# 
