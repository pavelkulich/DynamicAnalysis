import models
import data_manipulator as dtm
import db_manager as dbm
import plotter
import pandas as pd
import numpy as np

DEBUG = True


def debug(func, *args):
    if DEBUG:
        func(*args)


measurement_id = 22

db = dbm.DBExporter(dbtype='sqlite', dbname='vut_db.sqlite')
measured_data = db.columns_from_datatable(measurement_id)

params = pd.DataFrame(np.array([[3e7, 300, 5e5, 1e8, 15, 8e4]]), columns=['EI', 'm', 'c', 'k', 'v', 'Q'])
model = models.Model('dynamic_single_winkler')
analytical_data = model.calculate_model(params)

man = dtm.Manipulator(measured_data)
man.set_analytical_data(analytical_data)
debug(plotter.plot_deflection_for_ga, measured_data)
#
man.get_significant_points()
debug(plotter.plot_deflection_for_ga, measured_data)

super_data = man.move_and_superpose()
measured_data = man.get_measured_data()

debug(plotter.plot_deflection_for_ga, measured_data, super_data)


class GA:
    pass

# plotter.plot_deflection_for_ga(analytical_data, 'Deflection')