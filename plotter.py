import matplotlib.pyplot as plt


def measured_and_superposed(measured_data, superposed_data):
    plt.scatter(measured_data['x_axis'], measured_data['min'], c='r')
    plt.scatter(measured_data['x_axis'], measured_data['max'], c='g')
    plt.plot(measured_data['x_axis'], measured_data['y_axis'])
    plt.plot(superposed_data['x_axis'], superposed_data['y_axis'])
    plt.grid(True)
    plt.show()


def plot_4(data_1, data_2, data_3, data_4):
    plt.plot(data_1)
    plt.plot(data_2)
    plt.plot(data_3)
    plt.plot(data_4)
    plt.grid(True)
    plt.show()


def plot(data_1, data_2):
    plt.plot(data_1['y_axis'])
    plt.plot(data_2['y_axis'])
    plt.grid(True)
    plt.show()
