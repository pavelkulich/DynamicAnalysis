import matplotlib.pyplot as plt
import numpy as np
import os


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


######################
def plot_deflections_overview(data, head):
    fig = plt.figure()
    fig.set_size_inches(19, 11)
    plt.plot(data['time'], data.loc[:, data.columns != 'time'])
    plt.title(
        f'Location: {head.location[0]}, track: {head.track[0]}, train: {head.train[0]}, USP: {"Yes" if head.usp[0] else "No"}, date: {head.date[0]}',
        fontsize=25)
    plt.grid(True)
    plt.xticks(np.arange(min(data['time']), max(data['time']), 1.0))
    plt.xlabel('Time [s]')
    plt.ylabel('Deflection [mm]')
    plt.legend(data.columns[data.columns != 'time'], fontsize=18, loc='lower right')
    # plt.savefig(os.path.join(f'{os.path.dirname(__file__)}/images/', f'{head.filename[0].split(".")[0]}'))
    # plt.close(fig=fig)
    plt.show()


def plot_deflection_for_ga(*args):
    fig = plt.figure()
    # mng = plt.get_current_fig_manager()
    # mng.window.state("zoomed")

    for arg in args:
        plt.plot(arg['x_axis'], arg['y_axis'])

        if 'min' in arg.columns:
            plt.scatter(arg['x_axis'], arg['min'], color='red')
        # plt.legend(arg.columns[arg.columns != 'time'], fontsize=18, loc='lower right')

    plt.subplots_adjust(left=0.05, bottom=0.08, right=0.95, top=0.95)
    # plt.title('Deflection')
    plt.grid(True)
    # plt.xticks(np.arange(min(data['x_axis']), max(data['x_axis']), 0.2))
    plt.xlabel('Time [s]', fontsize=15)
    plt.ylabel('Deflection [mm]', fontsize=15)

    # plt.savefig(os.path.join(f'{os.path.dirname(__file__)}/images/', f'{head.filename[0].split(".")[0]}'))
    # plt.close(fig=fig)

    plt.show()
