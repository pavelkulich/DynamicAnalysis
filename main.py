import models
import pandas as pd
import ga
import os
import shutil
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

# measured data manipulation block
measured_data = pd.read_csv("data/train_u.csv", sep=",")
measured_data.columns = ['x_axis', 'y_axis']

w = 3.304e-4
E = 2.1e11

measured_data["y_axis"] = measured_data["y_axis"] * w * E

# mean_window = 200
# measured_data['y_axis'] = measured_data['y_axis'].iloc[::-1].rolling(window=mean_window).mean()
# measured_data['x_axis'] = measured_data['x_axis'].iloc[:-(mean_window - 1)]
# measured_data = measured_data.dropna(how='all')

# plotter.plot_1(measured_data)

# manipulator = man.Manipulator(measured_data)
# measured_data = manipulator.get_significant_points()

# data manipulation
# measured_data = pd.DataFrame()
# measured_data['x_axis'] = db_data['x_axis']
# measured_data['y_axis'] = (db_data['y_axis1'] + db_data['y_axis1']) / 2



# measured_data.to_csv("id17.csv")

model = models.Model('dynamic_single_winkler_moment', False)

# try:
# for i in range(20):
gen_algs = ga.GA(model, measured_data, 10, 2)
gen_algs.run_optimization()
# gen_algs.run_optimization(file)

end = time.time()

print(f'Time: {int(end - start)}')
# except:
#     with open('logs/error.csv', 'a', newline='') as csvfile:
#         fieldnames = ['Err']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#
#         writer.writerow({'Err': 'Algorithm Error'})
#     time.sleep(3)
#     # os.system("shutdown /p")
# finally:
#     time.sleep(3)
#     # os.system("shutdown /p")
