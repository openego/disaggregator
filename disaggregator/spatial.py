# -*- coding: utf-8 -*-
# Written by Fabian P. Gotzens, 2019.

# This file is part of disaggregator.

# disaggregator is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.

# disaggregator is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.

# You should have received a copy of the GNU General Public License
# along with disaggregator.  If not, see <https://www.gnu.org/licenses/>.
"""
Provides functions for spatial disaggregation
"""

from .data import (elc_consumption_HH, heat_consumption_HH, gas_consumption_HH,
                   population, households_per_size, income, stove_assumptions,
                   living_space, hotwater_shares)
import pandas as pd
import logging
logger = logging.getLogger(__name__)


def disagg_households_power(by, weight_by_income=False):
    """
    Perform spatial disaggregation of electric power in [GWh/a] by key and
    possibly weight by income.

    Parameters
    ----------
    by : str
        must be one of ['households', 'population']
    weight_by_income : bool, optional
        Flag if to weight the results by the regional income (default False)

    Returns
    -------
    pd.DataFrame or pd.Series
    """
    if by == 'households':
        # Bottom-Up: Power demand by household sizes in [GWh/a]
        power_per_HH = elc_consumption_HH(by_HH_size=True) / 1e3
        df = households_per_size() * power_per_HH
    elif by == 'population':
        # Top-Down: Power demand for entire country in [GWh/a]
        power_nuts0 = elc_consumption_HH() / 1e3
        distribution_keys = population() / population().sum()
        df = distribution_keys * power_nuts0
    else:
        raise ValueError("`by` must be in ['households', 'population']")

    if weight_by_income:
        df = adjust_by_income(df=df)

    return df


def disagg_households_heat(by, weight_by_income=False):
    """
    Perform spatial disaggregation of heat demand in [MWh/a] by key.

    Parameters
    ----------
    by : str
        must be one of ['households', 'population', 'buildings']

    Returns
    -------
    pd.DataFrame
    """
    if by not in ['households', 'buildings']:
        raise ValueError('The heating demand of households depends mainly on '
                         'the different household sizes and the building '
                         'types but not on the absolute population. Thus, '
                         'please pass `by=` either as "households" or '
                         '"buildings".')

    # Bottom-Up: Heat demand by household sizes in [MWh/a]
    df_heat_specific = heat_consumption_HH(by=by).T.unstack()
    df = pd.DataFrame(columns=df_heat_specific.index)
    base = households_per_size() if by == 'households' else living_space()
    for col, ser in base.iteritems():
        for idx in heat_consumption_HH(by=by).index:
            df.loc[:, (idx, col)] = ser
    df *= df_heat_specific
    return df


def disagg_households_gas(how='top-down', weight_by_income=False):
    """
    Perform spatial disaggregation of gas demand and possibly adjust
    by income.

    Parameters
    ----------
    how : str, optional
        must be one of ['top-down', 'bottom-up']
    adjust_by_income : bool, optional
        Flag if to weight the results by the regional income (default False)

    Returns
    -------
    pd.DataFrame or pd.Series
    """
    if how == 'top-down':
        logger.info('Calculating regional gas demands top-down.')
        gas_nuts0 = gas_consumption_HH()
        # Derive distribution keys
        df_ls_gas = living_space(aggregate=True, internal_id_2=11,
                                 internal_id_3=1).sum(axis=1)
        df_HH = households_per_size().sum(axis=1)
        d_keys_space = df_ls_gas / df_ls_gas.sum()
        d_keys_HW_cook = df_HH / df_HH.sum()
        # Calculate
        df = (pd.DataFrame(index=df_ls_gas.index)
                .assign(Cooking=d_keys_HW_cook * gas_nuts0['Cooking'],
                        HotWater=d_keys_HW_cook * gas_nuts0['HotWater'],
                        SpaceHeating=d_keys_space * gas_nuts0['SpaceHeating']))
    elif how == 'bottom-up':
        # The bottom-up logic requires the heat demand of households
        df_heat_dem = disagg_households_heat(by='households')

        logger.info('Calculating regional gas demands bottom-up:')
        logger.info('1. Cooking based on household sizes in [MWh/a]')
        df_stove = stove_assumptions()
        df_heat_cook = pd.DataFrame(df_heat_dem['Cooking'])
        for idx, row in df_stove.iterrows():
            df_heat_cook.update(df_heat_cook.filter(axis=0, regex=idx)
                                * row.stoves_percentage_gas
                                / row.stoves_efficiency_gas)

        logger.info('2. Hot water (decentralised) based on household sizes'
                    ' in [MWh/a]')
        df_WW_shares = hotwater_shares()
        df_WW = pd.DataFrame(df_heat_dem['HotWater'])
        for idx, row in df_WW_shares.iterrows():
            df_WW.update(df_WW.filter(axis=0, regex=idx)
                         * row.share_decentralised_gas
                         / 0.95)  # efficiency assumption gas boilers

        logger.info('3. Space heating + hot water (centralised) based on '
                    'living space in [MWh/a]')
        df_ls_gas = living_space(aggregate=True, internal_id_2=11,
                                 internal_id_3=1)

        df_hc_only = (heat_consumption_HH(by='buildings')
                      .T.loc[:, 'SpaceHeatingOnly'])
        df_hc_HW = (heat_consumption_HH(by='buildings')
                    .T.loc[:, 'SpaceHeatingPlusHotWater'])
        df_spaceheat = df_ls_gas.multiply(df_hc_only)
        df_spaceheat_HW = df_ls_gas.multiply(df_hc_HW)
        for idx, row in df_WW_shares.iterrows():
            df_spaceheat.update(df_spaceheat.filter(axis=0, regex=idx)
                                * (1.0 - row.share_centralised))
            df_spaceheat_HW.update(df_spaceheat_HW.filter(axis=0, regex=idx)
                                   * row.share_centralised)

        logger.info('4. Merging results')
        df = (pd.DataFrame(index=df_heat_dem.index)
                .assign(Cooking=df_heat_cook.sum(axis=1),
                        HotWaterDecentral=df_WW.sum(axis=1),
                        SpaceHeatingOnly=df_spaceheat.sum(axis=1),
                        SpaceHeatingPlusHotWater=df_spaceheat_HW.sum(axis=1)))

    if weight_by_income:
        df = adjust_by_income(df=df)

    return df


def disagg_CTS():
    raise NotImplementedError('Not here yet, to be done by TU Berlin.')
    return


def disagg_industry():
    raise NotImplementedError('Not here yet, to be done by TU Berlin.')
    return


# --- Utility functions -------------------------------------------------------


def adjust_by_income(df):
    income_keys = income() / income().mean()
    return df.multiply(income_keys, axis=0)