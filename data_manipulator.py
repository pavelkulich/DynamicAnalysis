import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
from scipy import interpolate
import matplotlib.pyplot as plt


class Manipulator:
    def __init__(self, measured_data):
        self.measured_data = measured_data
        self.measured_data.columns = ['x_axis', 'y_axis']
        self.measured_sampling_interval = np.abs(self.measured_data['x_axis'][1] - self.measured_data['x_axis'][0])
        self.analytical_data = None
        self.analytical_sampling_interval = None

    def set_analytical_data(self, analytical_data):
        self.analytical_data = analytical_data
        self.analytical_sampling_interval = np.abs(
            self.analytical_data['x_axis'][1] - self.analytical_data['x_axis'][0])
        print(self.analytical_data)

    def get_significant_points(self, order=300, tolerance=0.2):
        self.measured_data['min'] = \
            self.measured_data.iloc[argrelextrema(self.measured_data['y_axis'].values, np.less_equal, order=order)[0]][
                'y_axis']
        self.measured_data['min'] = self.measured_data['min'].fillna(0)
        self.measured_data['min'] = self.measured_data.iloc[np.abs(self.measured_data['min'].values) >= tolerance]['min']

    def get_measured_data(self):
        return self.measured_data

    def move_and_superpose(self):
        if self.analytical_data is not None:
            if 'min' in self.measured_data.columns:
                measured_mins = self.measured_data[self.measured_data['min'] < 0]
                max_x_list = []
                min_x_list = []
                counter = 1
                data_list = []
                for _, row in measured_mins.iterrows():
                    # TODO: optimalizace; neni nutne pocitat pro kazdy gen
                    moved_analytical_data = self.__get_new_x_axis(row)

                    # crop data with x less 0
                    moved_analytical_data = moved_analytical_data.drop(
                        moved_analytical_data[moved_analytical_data['x_axis'] < 0].index)

                    max_x_list.append(np.max(moved_analytical_data['x_axis']))
                    min_x_list.append(np.min(moved_analytical_data['x_axis']))

                    if counter != 1:
                        idx = moved_analytical_data.iloc[(prev_moved_analytical_data['x_axis'] - np.min(
                            moved_analytical_data['x_axis'])).abs().argsort()[:1]].index[0]
                        moved_analytical_data = moved_analytical_data.set_index(
                            moved_analytical_data.index + idx + prev_moved_analytical_data.idxmin()[0])

                    prev_moved_analytical_data = moved_analytical_data.copy()
                    moved_analytical_data.columns = [f'x_axis_{counter}', f'y_axis_{counter}']
                    data_list.append(moved_analytical_data)

                    counter += 1

                max_x = np.max(max_x_list)
                min_x = np.min(min_x_list)

                self.measured_data = self.measured_data.drop(
                    self.measured_data[self.measured_data['x_axis'] > max_x].index)
                self.measured_data = self.measured_data.drop(
                    self.measured_data[self.measured_data['x_axis'] < min_x].index)

                presup_analytical_data = pd.concat(data_list, axis=1)

                sup_analytical_data = pd.DataFrame()
                for iter in range(1, counter):
                    if iter != 1:
                        sup_analytical_data['x_axis'].fillna(presup_analytical_data[f'x_axis_{iter}'], inplace=True)
                        sup_analytical_data['y_axis'] = sup_analytical_data['y_axis'] + presup_analytical_data[
                            f'y_axis_{iter}'].fillna(0)
                    else:
                        sup_analytical_data['x_axis'] = presup_analytical_data[f'x_axis_{iter}']
                        sup_analytical_data['y_axis'] = presup_analytical_data[f'y_axis_{iter}'].fillna(0)


                return sup_analytical_data

            else:
                self.get_significant_points()
                self.move_and_superpose()
        else:
            print('Please set analytical data')
            return None

    # def __crop_tails(self):

    def __get_new_x_axis(self, row):
        analytical_min = self.analytical_data[
            self.analytical_data['y_axis'] == self.analytical_data['y_axis'].min()]

        first_index = 0
        last_index = self.analytical_data.index[-1]
        extreme_index = analytical_min.index[0]

        analytical_first_new_x = self.analytical_data['x_axis'][first_index] + row['x_axis']
        analytical_last_new_x = self.analytical_data['x_axis'][last_index] + row['x_axis']
        analytical_extreme_new_x = self.analytical_data['x_axis'][extreme_index] + row['x_axis']

        new_x_r = np.linspace(analytical_extreme_new_x, analytical_last_new_x,
                              last_index - extreme_index + 1)
        new_x_l = np.linspace(analytical_first_new_x,
                              analytical_extreme_new_x - self.analytical_sampling_interval, extreme_index)
        new_x = np.concatenate((new_x_l, new_x_r))
        moved_analytical_data = self.analytical_data.copy()
        moved_analytical_data['x_axis'] = new_x

        return moved_analytical_data


#####################

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

    plt.plot(measured_data['x_axis'], measured_data['y_axis'])
    plt.scatter(measured_data['x_axis'], measured_data['min'])
    plt.scatter(measured_data['x_axis'], measured_data['max'])
    plt.show()

    # analytical models superposition and crop and resampling with respect to measured data
    sup_data = superposition(analytical_data_1.copy(), analytical_data_2.copy())
    superposed_data, measured_data = crop_data(sup_data, measured_data)
    resampled_data = resample_data(measured_data, sup_data)

    return measured_data, resampled_data
