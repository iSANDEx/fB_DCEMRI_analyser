"""
get_timeseries.py - Atomic function to get the time series from a single sequence in the full dataframe
"""
from datetime import datetime as dtime
from numpy import diff, median, linspace
from pandas import DataFrame as pd_df

def extract_tseries(source_df, df_filter, tseries_stats, logger=None):
    """_summary_
    EXTRACT_TSERIES: Get the timeseries values from a particular sequence, in the format (time, value)

    Args:
        source_df (_type_): dataframe with all data extracted from ROIs
        df_filters (_type_): _description_ filters to groupby the dataframe
    """

    # Sequence patterns allowed are only 'Dyn' & '4D'
    allowed_seqs = ['Dyn','4D']
    # df_filter is a dictionary with the following structure:
    # {'PatientID': patient_id, (string)
    #  'VisitNro': visit_nro, (string)
    #  'Sequence': sequence, (string)} 
    if df_filter['Sequence'] in allowed_seqs:
        # Do everything
        # Select the segment to plot (checking for its existence in the df must be done in the script that calls this one)
        source_segment_df = source_df[source_df['ROI label'].isin([df_filter['ROI label']])]
        # Select the Sequence to plot
        sequences_df = source_segment_df[source_segment_df['Sequence'].isin([df_filter['Sequence']])]
        # for patient in config_structure['dicom']['patients_id']:
        patient_df = sequences_df[sequences_df['PatientID'].isin([df_filter['PatientID']])]
        # for visit in config_structure['dicom']['visits_id']:
        patient_visit_df = patient_df[patient_df['VisitNro'].isin([df_filter['VisitNro']])]

        # now we have a single dataset - Average the slices and get a single value per timpoint:
        stats_subgroup = patient_visit_df.groupby(by=tseries_stats['grouping_index'])[[tseries_stats['xaxis'],
                                                                                       tseries_stats['yaxis'],
                                                                                       tseries_stats['baseline']]]
        mean_over_time = stats_subgroup.mean()
        mean_over_time.rename(columns={tseries_stats['yaxis']: 'mean'}, inplace=True)

        # TODO: This must be changed to work also when multiple slices are used
        if stats_subgroup.count().max().values[0] > 1:
            # There is more than 1 slice, so the fill_regions are the std deviation of the mean across slices:
            std_over_time = stats_subgroup.std()
            std_over_time.rename(columns={tseries_stats['yaxis']: 'std'}, inplace=True)
        else: 
            # There is only 1 slice, so the fill_region is the std deviation over the single ROI
            std_over_time = patient_visit_df.groupby(by=tseries_stats['grouping_index'])[[tseries_stats['fill_area']]].mean()
            std_over_time.rename(columns={tseries_stats['fill_area']: 'std'}, inplace=True)


        # display mean with ranges defined by the std
        avg_dynamic = mean_over_time.join(std_over_time, lsuffix='', rsuffix='1').reset_index()
        # Remove the time axis from std_over_time, this is just duplicated from mean_over_time
        if f"{tseries_stats['xaxis']}1" in avg_dynamic.columns:
            avg_dynamic.drop([f"{tseries_stats['xaxis']}1"], axis=1, inplace=True)
        
        # If sequence == '4D' ==> re-define the time axis to be equally spaced and start at Dt
        # Adjust the time axis to:
        if ( df_filter['Sequence'] == '4D' ) & ( tseries_stats['xaxis'] == 'time'):
            abs_time = avg_dynamic[tseries_stats['xaxis']]
            dt = round(median(diff(abs_time)), 1)
            nt = len(abs_time)
            avg_dynamic[tseries_stats['xaxis']] = linspace(0.0, dt * nt, num=nt, endpoint=False)
        
    else:
        avg_dynamic = pd_df()

    return avg_dynamic


def get_dcemri_parameters(source_df, df_filter, tseries_stats, logger=None):

    allowed_seqs = ['4D']
    dcemri_pars = {}
    if df_filter['Sequence'] in allowed_seqs:
        dce_signal = extract_tseries(source_df, df_filter, tseries_stats, logger=None)

        # Select the segment to plot (checking for its existence in the df must be done in the script that calls this one)
        source_segment_df = source_df[source_df['ROI label'].isin([df_filter['ROI label']])]
        # Select the Sequence to plot
        sequences_df = source_segment_df[source_segment_df['Sequence'].isin([df_filter['Sequence']])]
        # for patient in config_structure['dicom']['patients_id']:
        patient_df = sequences_df[sequences_df['PatientID'].isin([df_filter['PatientID']])]
        # for visit in config_structure['dicom']['visits_id']:
        patient_visit_df = patient_df[patient_df['VisitNro'].isin([df_filter['VisitNro']])]

        if not patient_visit_df.empty:
            TR = patient_visit_df['TR'].unique()[0] / 1000.0
            FA = int(patient_visit_df['FA'].unique()[0])
            bline = int(patient_visit_df[tseries_stats['baseline']].unique()[0])
            visitDate = patient_visit_df['VisitID'].unique()[0].astype(str)
            dcemri_pars['mri'] = {'TR': TR,
                                'FA': FA,
                                'BAT': bline,
                                'VisitDate': dtime.strptime(visitDate, '%Y%m%d')}
            dcemri_pars['dce'] = {'signal': dce_signal}
        else:
            dcemri_pars = {}
    return dcemri_pars

def extract_t1vfa(source_df, df_filter, tseries_stats, logger=None):
    """_summary_
    EXTRACT_T1VFA: Get the Signal Intensity for every Flip Angle acquired
    If the flag use3FA=True, get an additional sample from the 4D dynamic series.
    Given the 4D sequence has not dummy scans, use the 2nd or 3rd timepoint:

    Args:
        source_df (_type_): dataframe with all data extracted from ROIs
        df_filters (_type_): _description_ filters to groupby the dataframe
    """

    # Sequence patterns allowed are only 'FA*' & '4D' (if use3FA=True)
    allowed_seqs = ['FA5', 'FA15', '4D']

    # df_filter is a dictionary with the following structure:
    # {'PatientID': patient_id, (string)
    #  'VisitNro': visit_nro, (string)
    #  'Sequence': sequence, (string),
    #  'flags': {
    #       'use3FA': _bool_
    #       }
    # } 
    if df_filter['Sequence'] in allowed_seqs:
        # Do everything
        # Select the segment to plot (checking for its existence in the df must be done in the script that calls this one)
        source_segment_df = source_df[source_df['ROI label'].isin([df_filter['ROI label']])]
        # Select the Sequence to plot
        sequences_df = source_segment_df[source_segment_df['Sequence'].isin([df_filter['Sequence']])]
        # for patient in config_structure['dicom']['patients_id']:
        patient_df = sequences_df[sequences_df['PatientID'].isin([df_filter['PatientID']])]
        # for visit in config_structure['dicom']['visits_id']:
        patient_visit_df = patient_df[patient_df['VisitNro'].isin([df_filter['VisitNro']])]

        # now we have a single dataset - Average the slices and get a single value per timpoint:
        stats_subgroup = patient_visit_df.groupby(by=tseries_stats['grouping_index'])[[tseries_stats['xaxis'],
                                                                                       tseries_stats['yaxis']]]
        mean_over_time = stats_subgroup.mean()
        mean_over_time.rename(columns={tseries_stats['yaxis']: 'mean'}, inplace=True)

        # TODO: This must be changed to work also when multiple slices are used
        if stats_subgroup.count().max().values[0] > 1:
            # There is more than 1 slice, so the fill_regions are the std deviation of the mean across slices:
            std_over_time = stats_subgroup.std()
            std_over_time.rename(columns={tseries_stats['yaxis']: 'std'}, inplace=True)
        else: 
            # There is only 1 slice, so the fill_region is the std deviation over the single ROI
            std_over_time = patient_visit_df.groupby(by=tseries_stats['grouping_index'])[[tseries_stats['fill_area']]].mean()
            std_over_time.rename(columns={tseries_stats['fill_area']: 'std'}, inplace=True)


        # display mean with ranges defined by the std
        avg_t1vfa = mean_over_time.join(std_over_time, lsuffix='', rsuffix='1').reset_index()
        # Remove the time axis from std_over_time, this is just duplicated from mean_over_time
        if f"{tseries_stats['xaxis']}1" in avg_t1vfa.columns:
            avg_t1vfa.drop([f"{tseries_stats['xaxis']}1"], axis=1, inplace=True)
        
        
    else:
        avg_t1vfa = pd_df()

    return avg_t1vfa
