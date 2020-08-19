import models
import data_manipulator as dtm
import db_manager as dbm
import plotter
import pandas as pd
import numpy as np
import ga
import time

# DEBUG = False
DEBUG = True

start = time.time()
print(start)

def debug(func, *args):
    if DEBUG:
        func(*args)


measurement_id = 17

# db = dbm.DBExporter(dbtype='sqlite', dbname='vut_db.sqlite')
# measured_data = db.columns_from_datatable(measurement_id)

tenzometric = pd.read_csv('data/44 t.asc', sep='\t', header=0, skiprows=[1])
t1 = tenzometric['T1']
t2 = tenzometric['T2']
t_avg = (t1 + t2) / 2 + 63

measured_data = pd.DataFrame(zip(tenzometric['x'], -t_avg), columns=['x_axis', 'y_axis'])
# print(measured_data)



# model = models.Model('dynamic_single_winkler')
# model = models.Model('dynamic_single_winkler')
model = models.Model('dynamic_double_pasternak', True)

gen_algs = ga.GA(model, measured_data, 500, 40)
gen_algs.run_optimization()

end = time.time()

print(int(end-start))

# params = pd.DataFrame(np.array([[3e7, 300, 5e5, 1e8, 25, 15e4]]), columns=['EI', 'm', 'c', 'k', 'v', 'Q'])
# model = models.Model('dynamic_single_wiłnkler')
# analytical_data = model.calculate_model(params)
#
# man = dtm.Manipulator(measured_data)
# man.set_analytical_data(analytical_data)
# debug(plotter.plot_deflection_for_ga, measured_data)
# #
# man.get_significant_points()
# debug(plotter.plot_deflection_for_ga, measured_data)
#
# man.move_and_superpose()
# super_data = man.get_superposed_resampled()
# measured_data = man.get_measured_data()
#
# debug(plotter.plot_deflection_for_ga, measured_data, super_data)




class GA:
    pass

# plotter.plot_deflection_for_ga(analytical_data, 'Deflection')
