import models
import db_manager as dbm
import plotter
import pandas as pd
import numpy as np
import ga
import time
import os
import shutil


def remove_folder_content(dir_name):
    for filename in os.listdir(dir_name):
        file_path = os.path.join(dir_name, filename)
        try:
            shutil.rmtree(file_path)
        except OSError:
            os.remove(file_path)


remove_folder_content('logs')
remove_folder_content('plots')

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

for i in range(20):
    gen_algs = ga.GA(model, measured_data, 500, 20)
    gen_algs.run_optimization(i)

end = time.time()

print(f'Time: {int(end - start)}')
