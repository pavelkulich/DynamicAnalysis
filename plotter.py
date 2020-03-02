import matplotlib.pyplot as plt


def measured_and_superposed(measured_data, superposed_data):
    plt.scatter(measured_data['x_axis'], measured_data['min'], c='r')
    plt.scatter(measured_data['x_axis'], measured_data['max'], c='g')
    plt.plot(measured_data['x_axis'], measured_data['y_axis'])
    plt.plot(superposed_data['x_axis'], superposed_data['y_axis'])
    plt.grid(True)
    plt.show()
