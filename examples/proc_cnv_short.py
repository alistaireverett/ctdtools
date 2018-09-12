#!/usr/bin/env python

from glob import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from ctdtools import ctdtools

pattern = '*.cnv'
fnames = glob(pattern)
all_casts = pd.DataFrame()

# loop through all cnvs in current folder and append to DataFrame
for fname in fnames:
        cast = ctdtools.proc_cnv(fname)
        all_casts = all_casts.append(cast)

# plot the data so we can see what we've got
fig1,ax1 = plt.subplots(1,2,sharey=True)
fig2,ax2 = plt.subplots(1)

for name,prof in all_casts.groupby('ID'):
        prof.loc[name]['SA'].plot(ax=ax1[0],label=name)
        prof.loc[name]['CT'].plot(ax=ax1[1],label=name)
        prof.plot('SA','CT',ax=ax2,label=name,legend=False)

ax1[0].invert_yaxis()

# add mean profiles to plot
all_casts.groupby('z')['SA'].mean().plot(ax=ax1[0],c='k',label='Av')
all_casts.groupby('z')['CT'].mean().plot(ax=ax1[1],c='k',label='Av')
ax1[0].legend()

# save mean profile
mean_profile = all_casts.groupby('z')[['CT','SA']].mean()
mean_profile.to_csv('mean_profile.csv',';')

plt.show()
