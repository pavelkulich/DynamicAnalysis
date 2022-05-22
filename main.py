import models
import db_manager as dbm
import plotter
import pandas as pd
import numpy as np
import ga
import time
import os
import shutil
import matplotlib.pyplot as plt
import csv
import time


def remove_folder_content(dir_name):
    for filename in os.listdir(dir_name):
        file_path = os.path.join(dir_name, filename)
        try:
            shutil.rmtree(file_path)
        except OSError:
            os.remove(file_path)


# remove_folder_content('logs')
# remove_folder_content('plots')

# DEBUG = False
DEBUG = True

start = time.time()

# id 17
measurement_id = 17

db = dbm.DBExporter(dbtype='sqlite', dbname='vut_db.sqlite')
db_data = db.columns_from_datatable(measurement_id)
db_data.columns = ['x_axis', 'y_axis1', 'y_axis2']

# plotter.plot_1(db_data)

# data manipulation
measured_data = pd.DataFrame()
measured_data['x_axis'] = db_data['x_axis']
measured_data['y_axis'] = (db_data['y_axis1'] + db_data['y_axis1']) / 2

mean_window = 50
measured_data['y_axis'] = measured_data['y_axis'].iloc[::-1].rolling(window=mean_window).mean()
measured_data['x_axis'] = measured_data['x_axis'].iloc[:-(mean_window - 1)]
measured_data = measured_data.dropna(how='all')

measured_data.to_csv("id17.csv")

model = models.Model('dynamic_double_pasternak', False)

try:
    # for i in range(20):
    gen_algs = ga.GA(model, measured_data, 50, 15)
    gen_algs.run_optimization()
    # gen_algs.run_optimization(file)

    end = time.time()

    print(f'Time: {int(end - start)}')
except:
    with open('logs/error.csv', 'a', newline='') as csvfile:
        fieldnames = ['Err']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writerow({'Err': 'Algorithm Error'})
    time.sleep(3)
    # os.system("shutdown /p")
finally:
    time.sleep(3)
    # os.system("shutdown /p")
