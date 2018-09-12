#!/usr/bin/env python

import gsw
from ctd import DataFrame, Series
import os

def derive_ts(cast,sCol='sal00',pCol='Pressure [dbar]',tCol='t090C'):
    """
    Function to add SA, CT, and sigma0 to a cast

    Parameters
    ----------
    
    
    """
    cast['SA'] = gsw.SA_from_SP(cast[sCol].values, cast[pCol].values,
                                cast.longitude, cast.latitude)
    cast['CT'] = gsw.CT_from_t(cast[sCol].values, cast[tCol].values,
                                cast[pCol].values)
    cast['sigma0_CT'] = gsw.sigma0_CT_exact(cast['SA'].values, cast['CT'].values)
    return cast

def proc_cnv(fname, remove_upcast=True, keep=None):
    """
    Function to read and process a seabird cnv file.
	
    By default will keep in-situ temp, sal and pressure and will calculate
    depth, conservative salinity, absolute temperature and density.
    Additional

    Parameters
    ----------
    fname : string
        Name of file

    remove_upcast : boolean, default True
        Upcast will be removed unless remove_upcast is set to False

    keep : list
        List of columns variable in the cnv to keep

    Returns
    -------

    dataframe : DataFrame

    """
    
    # 00-Split, clean 'bad pump' data, and apply flag.
    # Read cnv
    cast = DataFrame.from_cnv(fname)

    # store cast name
    name = os.path.basename(fname).split('.')[0]

    # save lat and long
    lat = cast.latitude
    lon = cast.longitude

    # discard upcast if required
    if remove_upcast:
        cast = cast.split()[0]

    cast["latitude"] = lat
    cast["longitude"] = lon

    keep_cols = ['latitude',
                'longitude',
                't090C', 'sal00'
                ]

    if keep is not None:
        assert type(keep) is list, ('keep must be a list')
        keep_cols.extend(keep)

    # Removed unwanted columns.
    keep = set(keep_cols)

    null = map(cast.pop, keep.symmetric_difference(cast.columns))
    del null

    # index is Pressure - derive depth and set as index
    p = cast.index.values.astype(float)
    cast['z'] = -gsw.z_from_p(p, lat)
    cast = cast.reset_index()
    cast = cast.set_index('z',drop=True)

    # 05-Bin-average.
    cast = cast.apply(Series.bindata, **dict(delta=1.))
    cast.index.name = 'z'

    # 06-interpolate.
    cast = cast.apply(Series.interpolate)

    # Add metadata to the DataFrame.
    cast.lat = cast["latitude"].mean()
    cast.lon = cast["longitude"].mean()

    # Add Absolute Salinity and Conservative Temperature 
    cast = derive_ts(cast)
    
    # Add ID as a column then convert to index to create multilevel index
    # useful for stacking multiple casts
    cast["ID"] = [name]*len(cast)
    cast = cast.reset_index()
    cast = cast.set_index(["ID","z"],drop=True)

    return cast

