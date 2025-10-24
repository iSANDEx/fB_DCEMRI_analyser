"""
plotter.py - Reusable plotting functions.
"""
import matplotlib.pyplot as plt

def plot_timeseries(df_to_plot, tseries_axis, tseries_label, disp=False, figax=None):
    if figax is None:
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8.0, 6.0))
    else:
        fig, ax = figax # FIGAX is just a list from a previous call to this function
    
    ax.plot(df_to_plot[tseries_axis['xaxis']], 
            df_to_plot[tseries_axis['yaxis']],
            marker='.',
            color=tseries_label['colour'],
            label=tseries_label['legend'])
    
    if tseries_axis['fill_area'] is not None:
        ax.fill_between(df_to_plot[tseries_axis['xaxis']], 
                        df_to_plot[tseries_axis['yaxis']] + df_to_plot[tseries_axis['fill_area']], 
                        df_to_plot[tseries_axis['yaxis']] - df_to_plot[tseries_axis['fill_area']],
                        alpha=0.25, interpolate=True)
    

    # Plot baseline as reference:
    if 'baseline' in tseries_axis.keys():
        bline_index = int(df_to_plot[tseries_axis['baseline']].unique()[0])
        bline_time = df_to_plot[tseries_axis['xaxis']][bline_index]
        ax.axvline(x=bline_time, 
                   color=tseries_label['colour'], 
                   linestyle='-.', 
                   label=f'Baseline ({bline_time:.1f}[s])')
    
    ax.grid(True)
    ax.set_xlabel(tseries_label['xlabel'])
    ax.set_ylabel(tseries_label['ylabel'])
    ax.set_title(tseries_label['title'])
    ax.legend(loc='upper left')

    if disp:
        plt.show()

    return fig, ax

def plot_t1vfa(df_to_plot, tseries_axis, tseries_label, disp=False, figax=None):

    return True

def plot_multiseries(df_to_plot, tseries_axis, tseries_label, disp=False):
    """This plots multi-series in one go (not suitable for multiple visits)
    The logic to separate it, is because a plot with more than two lines gets confused
    If we want to check differences between visits, do it on a parameter basis and use plot_timeseries
    Xaxis must be the same for every data, so it shouldn't be given as a list!!
    Args:
        df_to_plot (_type_): _description_
        tseries_axis (_type_): each element is a list with the different lines to plot
        tseries_label (_type_): ditto tseries_axis
        disp (bool, optional): _description_. Defaults to False.
        figax (_type_, optional): _description_. Defaults to None.
    """
    # Ensure all figures are closed before drawing a new one:
    plt.close()
    
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8.0, 6.0))

    for idx_serie, (yserie, legend, marker) in enumerate(zip(tseries_axis['yaxis'], tseries_label['legend'], tseries_label['markers'])):
        
        ax.plot(df_to_plot[tseries_axis['xaxis']], 
                df_to_plot[yserie],
                marker = marker,
                # color = clr,
                label = legend)
        
        if tseries_axis['fill_area'] is not None:
            ax.fill_between(df_to_plot[tseries_axis['xaxis']], 
                        df_to_plot[yserie] + df_to_plot[tseries_axis['fill_area'][idx_serie]], 
                        df_to_plot[yserie] - df_to_plot[tseries_axis['fill_area'][idx_serie]],
                        alpha=0.25, interpolate=True)

    # Plot baseline as reference - This is only one per plot (multiseries doesn't show multiple visits):
    if 'baseline' in tseries_axis.keys():
        bline_index = int(df_to_plot[tseries_axis['baseline']].unique()[0])
        bline_time = df_to_plot[tseries_axis['xaxis']][bline_index]
        ax.axvline(x=bline_time,  
                color='k', 
                linestyle='-.', 
                label=f'Baseline ({bline_time:.1f}[s])')


    ax.grid(True)
    ax.set_xlabel(tseries_label['xlabel'])
    ax.set_ylabel(tseries_label['ylabel'])
    ax.set_title(tseries_label['title'])
    ax.legend(loc='upper left')

    if disp:
        plt.show()
    
    
    return fig, ax

