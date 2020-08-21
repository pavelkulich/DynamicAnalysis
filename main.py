import models
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

db = dbm.DBExporter(dbtype='sqlite', dbname='vut_db.sqlite')
measured_data = db.columns_from_datatable(measurement_id)
#
# tenzometric = pd.read_csv('data/44 t.asc', sep='\t', header=0, skiprows=[1])
# t1 = tenzometric['T1']
# t2 = tenzometric['T2']
# t_avg = (t1 + t2) / 2 + 63
#
# measured_data = pd.DataFrame(zip(tenzometric['x'], -t_avg), columns=['x_axis', 'y_axis'])
# print(measured_data)


# model = models.Model('dynamic_single_winkler')
# model = models.Model('dynamic_single_winkler')
model = models.Model('dynamic_double_pasternak', False)

gen_algs = ga.GA(model, measured_data, 5000, 50)
gen_algs.run_optimization()

end = time.time()

print(int(end - start))
