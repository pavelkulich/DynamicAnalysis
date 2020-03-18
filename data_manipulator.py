import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
from scipy import interpolate


def import_data(path="data/deflection.csv", separator=";", flip=True):
    data = pd.read_csv(path, separator)
    if flip:
        data_flip = -data.reindex(index=data.index[::-1]).reset_index(drop=True)
        # print(data_flip)
        return data_flip

    return data


# method finds scaling and moving coefficient in order to adjust analytical models with respect to measured data
def get_rescale_coeffs(base_data, data):
    # local min and max finding for measured data
    base_data['min'] = \
        base_data.iloc[argrelextrema(base_data['y_axis'].values, np.less_equal, order=20)[0]]['y_axis']
    base_data['max'] = \
        base_data.iloc[argrelextrema(base_data['y_axis'].values, np.greater_equal, order=20)[0]][
            'y_axis']

    base_data_low_1 = base_data['x_axis'][base_data['min'].nsmallest(2).index[0]]
    base_data_low_2 = base_data['x_axis'][base_data['min'].nsmallest(2).index[1]]
    base_data_high = base_data['x_axis'][base_data['max'].nlargest(1).index[0]]
    base_data_diff = base_data_high - base_data_low_2

    data_low_index = data['y_axis'].nsmallest(1).index[0]
    data_high_index = data['y_axis'].nlargest(1).index[0]
    data_low = data['x_axis'][data_low_index]
    data_high = data['x_axis'][data_high_index]
    data_diff = data_high - data_low

    # coeff calculation
    scale_linear_coeff = base_data_diff / data_diff
    scale_constant_coeff_1 = scale_linear_coeff * data_high - base_data_high
    scale_constant_coeff_2 = scale_constant_coeff_1 + (base_data_low_2 - base_data_low_1)

    return scale_linear_coeff, scale_constant_coeff_1, scale_constant_coeff_2


# method for adjusting data (scale and move)
def scale_axis(data, coeff_1, coeff_2):
    data['x_axis'] = data['x_axis'] * coeff_1 * 0.85 - coeff_2 * 0.95  # TODO: 0.85 a 0.95 budou paramatry ev. algoritmu
    return data


# method returns superposed product made from two dataframes
def superposition(data_1, data_2):
    data_1, data_2 = crop_data(data_1, data_2)
    superposed_data = data_2.copy()
    superposed_data['y_axis'] = superposed_data['y_axis'] + data_1['y_axis']

    return superposed_data


# method cuts non-common ends of two dataframes
def crop_data(data_1, data_2):
    first_data1_index = data_1['x_axis'][0]
    last_data2_index = data_2['x_axis'][data_2.index[-1]]

    while data_2['x_axis'][0] < first_data1_index:
        data_2 = data_2.drop([0]).copy().reset_index(drop=True)

    while data_1['x_axis'][data_1.index[-1]] > last_data2_index:
        data_1 = data_1.drop([data_1.index[-1]]).copy().reset_index(drop=True)

    return data_1, data_2


# method resamples data to base_data base
def resample_data(base_data, data):
    if base_data.shape[0] == data.shape[0]:
        return data

    x = data['x_axis']
    y = data['y_axis']
    f = interpolate.interp1d(x, y)

    first_x_val = base_data['x_axis'][0]
    last_x_val = base_data['x_axis'][base_data.shape[0] - 1]
    x_range = (last_x_val - first_x_val) / base_data.shape[0]
    x_new = np.arange(first_x_val, last_x_val, x_range)
    y_new = f(x_new)

    resampling_product = pd.DataFrame(list(zip(base_data['x_axis'], y_new)), columns=["x_axis", "y_axis"])
    return resampling_product


def rescale_and_fit(measured_data, analytical_data):
    # analytical models scaling and moving
    coeff_1, coeff_2, coeff_3 = get_rescale_coeffs(measured_data, analytical_data)
    analytical_data_1 = scale_axis(analytical_data.copy(), coeff_1, coeff_2)
    analytical_data_2 = scale_axis(analytical_data.copy(), coeff_1, coeff_3)

    # analytical models superposition and crop and resampling with respect to measured data
    sup_data = superposition(analytical_data_1.copy(), analytical_data_2.copy())
    superposed_data, measured_data = crop_data(sup_data, measured_data)
    resampled_data = resample_data(measured_data, sup_data)

    return measured_data, resampled_data
