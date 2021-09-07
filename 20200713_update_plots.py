import common.sdcv19 as sdcv19
import pandas as pd

import os

from common.kalman_filter import plot_kf_estimate
from common.kalman_filter import kf

import datetime


sddata = sdcv19.get_county_newcases()
#import pdb; pdb.set_trace()
z = sddata['TOTAL']


quiet_period_start = pd.Timestamp(2020,4,20)
quiet_period_stop = pd.Timestamp(2020,5,20)

quiet_period = z.loc[(z.index>=pd.Timestamp(2020,4,20))&(z.index<=pd.Timestamp(2020,6,15))]
qpv = quiet_period.var()


estimate_df = kf(z,10*qpv,20)[0]
fig, (ax1,ax2) = plot_kf_estimate(estimate_df)
ax2.text(0,-0.2, "Figure last updated {date:%Y-%m-%d %I:%M %p}.\nLatest estimates: x={x:.1f}; dx={dx:.1f} ".format(date=datetime.datetime.now(),x=estimate_df.iloc[-1,1],dx=estimate_df.iloc[-1,2]), size=12, ha="center", 
         transform=ax2.transAxes)

THIS_PATH = os.path.abspath(os.path.dirname(__file__))
figfilename = os.path.join(THIS_PATH,'plots','kf_estimate.svg')
fig.savefig(figfilename)
