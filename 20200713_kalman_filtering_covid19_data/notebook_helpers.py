
import filterpy
import pandas as pd
import numpy as np

import os

from filterpy.kalman import KalmanFilter 
from filterpy.common import Q_discrete_white_noise

import matplotlib.pyplot as plt
from numpy.polynomial import polynomial as P


CSVFILEPATH = os.path.join('/Users/jen/projects/covid19-san-diego/csv','sandiego_data_by_zipcode.csv')


def plot_figure1(estimate_df):
    ''' Plot Rolling Mean and Kalman Estimate for Series Data
    Inputs: 
        estimate_df: Pandas Dataframe with Kalman Filter estimates (z, x, dx, r, v11, v21, v12, v22)
    Returns:
        fig, ax
    '''
    fig,ax = plt.subplots(1,1,figsize=(16,8))
    estimate_df['z'].plot(marker='.',markersize=10,linestyle='none',
        label='Reported New Cases',ax=ax)
    #ax.plot(estimate_df.index,estimate_df['x'],label='Kalman Filter Estimate')
    estimate_df['x'].plot(ax=ax,linewidth=6,label='Kalman Filter Estimate of $ x $')
    ax.fill_between(estimate_df.index,
        estimate_df['x']-np.sqrt(estimate_df['v11']),
        estimate_df['x']+np.sqrt(estimate_df['v11']),
        color=(1,.3,0,.05),label="+/- 1$ \sigma $ bounds for Kalman Filter Estimate of $ x $")
        
    #Plot rolling LLSQ fits
    ndays = 14
    for ndays in [4,7,14]:
        days = np.arange(0,ndays)
        estimate_df['z'].rolling(ndays).apply(lambda x: P.polyfit(days,x,1)[0]).plot(ax=ax,label='{}-day LLSQ Estimate of $ x $'.format(ndays))
    
    ax.legend()
    
    ax.set_title("Figure 1: Comparison of Kalman Filter and Rolling Window Linear Least Squares Fits\nfor Estimation of New Reported Covid19 Cases Per Day in San Diego County "
    )
    ax.set_xlabel('Date')
    ax.set_ylabel('Reported New Cases')
    return (fig,ax)
    
def plot_figure2(estimate_df):
    ''' Plot Rolling Mean and Kalman Estimate for Series Data
    Inputs: 
        estimate_df: Pandas Dataframe with Kalman Filter estimates (z, x, dx, r, v11, v21, v12, v22)
    Returns:
        fig, ax
    '''
    fig,ax = plt.subplots(1,1,figsize=(16,8))
    estimate_df['z'].diff().plot(marker='.',markersize=10,linestyle='none',
        label='Reported New Cases',ax=ax)
    #ax.plot(estimate_df.index,estimate_df['x'],label='Kalman Filter Estimate')
    estimate_df['dx'].plot(ax=ax,linewidth=6,label='Kalman Filter Estimate of $ \dot x $')
    ax.fill_between(estimate_df.index,
        estimate_df['dx']-np.sqrt(estimate_df['v22']),
        estimate_df['dx']+np.sqrt(estimate_df['v22']),
        color=(1,.3,0,.05), label='+/- 1$ \sigma $ Bounds for Kalman Filter Estimate of $ \dot x $')
        
    #Plot rolling LLSQ fits

    for ndays in [4,7,14]:
        days = np.arange(0,ndays)
        estimate_df['z'].rolling(ndays).apply(lambda x: P.polyfit(days,x,1)[1]).plot(ax=ax,label='{}-day LLSQ Estimate of $ \dot x $'.format(ndays))
    
    ax.legend()
    ax.set_xlabel('Date')
    ax.set_ylabel('Daily Rate of Change in Reported New Cases')
    ax.set_title("Figure 2: Comparison of Kalman Filter and Rolling Window Linear Least Squares Fits\nfor Estimation of Daily Rate of Change of New Reported Covid19 Cases Per Day in San Diego County "
    )
    return (fig,ax)
    
    
def plot_figure3(estimate_df):
    ''' Plot Change in New Cases Per Day for Series Data
    Inputs: 
        estimate_df: Pandas Dataframe with Kalman Filter estimates (z, x, dx, r, v11, v21, v12, v22)
    Returns:
        fig, ax
    '''
    fig,ax1 = plt.subplots(1,1,figsize=(16,8))
    estimate_df['dx'].plot(ax=ax1,label='Kalman Filter Estimate of $ \dot x $')
    ax1.fill_between(estimate_df.index,
        estimate_df['dx']-np.sqrt(estimate_df['v22']),
        estimate_df['dx']+np.sqrt(estimate_df['v22']),
        color=(1,.3,0,.05),label="+/- 1$ \sigma $")
    ax1.legend(loc='upper left')
    ax1.set_title("Figure 3:  A Closer Look at Kalman Filter Estimate of Rate of Change of New Cases Per Day ($ \dot x $)")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("$ \dot x $")
    
    return (fig,ax1)
    
    
    
def load_data(csvfilepath):
    # Load the data and find differences
    df = pd.read_csv(csvfilepath,index_col=0,dtype={'Data through':'str'},parse_dates=['Data through'])
    df = df.drop(columns='Date Retrieved').fillna(0)
    df = df.diff()  
    return df.iloc[1:]

def quiet_period_variance(df:pd.DataFrame,quiet_period_start:pd.Timestamp,quiet_period_stop:pd.Timestamp):
    measurement_variance = df.iloc[(df.index>=quiet_period_start)&(df.index<=quiet_period_stop),:].var()
    measurement_variance[measurement_variance==0]=.05
    return measurement_variance

def kf(s,r,q):
    '''Perform Kalman Filter on pandas Series
    
    Inputs:
        s -- Pandas series with data to filter, index is datetime
        r -- measurement noise variance (use 10*quiet_period_variance)
        q -- process noise variance (use 20)
    
    Returns:
        f -- Kalman Filter model
    '''
    
    
    estimate_columns = ['z','x','dx','r','v11','v21','v12','v22']
    estimate_df = pd.DataFrame(index=s.index, columns=estimate_columns)
    estimate_df=estimate_df.fillna(0)
    
    # NCV model 
    f = KalmanFilter(dim_x=2,dim_z=1)
    # Initial condition
    f.x = np.array([s[0],s.diff()[1:5].mean()])
    
    # State transition matrix
    f.F = np.array([[1.,1.,],[0,1.,]])
    
    # Measurement Function
    f.H = np.array([[1.,0]])

    # Covariance Matrix
    f.P *= 1

    # Measurement Noise Covariance
    f.R = r

    # Add noise profile
    f.Q = Q_discrete_white_noise(dim=2, dt=1, var = q)
    for k in range(0,len(estimate_df)):
        z = s[k]
        f.predict()
        f.update(z)
        estimate_df.loc[estimate_df.index[k],'z'] = z
        estimate_df.loc[estimate_df.index[k],['x','dx']] = list(f.x)
        estimate_df.loc[estimate_df.index[k],'r'] = f.y**2
        estimate_df.loc[estimate_df.index[k],['v11','v21','v12','v22']] = list(np.reshape(f.P,4))
    return (estimate_df,f)
    


def plot_county_level_lls_vs_kalman(df):
    total_ts = figure(height=530,width=400,x_axis_type='datetime',x_axis_label='Date',
                      y_axis_label='Reported New Cases Per Day',title='San Diego County: New Reported Cases Per Day')
    # add a circle renderer with a size, color, and alpha
    total_ts.circle(pd.to_datetime(sddiff.index),sddiff['TOTAL'].values, size=5, color="navy", alpha=0.5,legend_label="Reported New Cases")
    total_ts.line(pd.to_datetime(fourteen_day_average.index),fourteen_day_average['TOTAL'].values,legend_label="Fourteen Day Average")
    total_ts.toolbar.logo = None
    total_ts.toolbar_location = None
    total_ts.legend.location = 'top_left'
    
    