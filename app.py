import models as mod
import data_manipulator as man
import plotter


def main():
    analytical_data = mod.dynamic_double_pasternak()
    measured_data = man.import_data()
    measured_data, superposed_data = man.rescale_and_fit(measured_data, analytical_data)

    plotter.measured_and_superposed(measured_data, superposed_data)


main()
