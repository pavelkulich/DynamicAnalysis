import data_manipulator as man
import pandas as pd
import numpy as np
import random
import models
import data_manipulator as dtm
import db_manager as dbm
import plotter


class GA:
    def __init__(self, model, measured_data, pop_size, num_of_populations):
        self.__model: models.Model = model
        self.__measured_data = measured_data
        self.__populations = Populations()
        self.__pop_size = pop_size
        self.__num_of_populations = num_of_populations

    def run_optimization(self):
        population = self.get_init_population()
        self.__optimize(population, 1)

    def adjust_q_vector(self):
        pass

    def __optimize(self, population, iteration):
        print(iteration)
        if iteration <= self.__num_of_populations:
            cols = list(population.columns)
            new_population = Population(cols, iteration)
            for index, params in population.iterrows():
                analytical_data = self.__model.calculate_model(params)
                man = dtm.Manipulator(self.__measured_data.copy())

                # data manipulation
                man.set_analytical_data(analytical_data)
                man.get_significant_points()
                man.adjust_q_vector()

                q_vector = man.get_adjusted_q_vector() * params['Q']

                man.move_and_superpose()
                super_data = man.get_superposed_resampled()
                measured_data = man.get_measured_data()

                # fitness calculation
                fitness = self.__calculate_fitness(measured_data, super_data)
                params['fitness'] = fitness
                # TODO: ošetřit sloupce v entitě Population
                params = params.append(q_vector.iloc[0])
                new_population.add_chromosome(params)

            self.__populations.add_population(new_population)
            new_population.write_log()
            new_population.perform_selection()
            new_population.perform_crossover()

            iteration += 1
            return self.__optimize(new_population.get_crossover_product(), iteration)

        # TODO: best solution here
        best_params = self.__populations.get_last_population().get_max_fitness_row()
        best_params.to_csv('logs/best_solution.txt')
        best_analytical_data = self.__model.calculate_model(best_params)

        man = dtm.Manipulator(self.__measured_data.copy())

        # data manipulation
        man.set_analytical_data(best_analytical_data)
        man.get_significant_points()
        man.adjust_q_vector()

        man.move_and_superpose()
        super_data = man.get_superposed_resampled()
        measured_data = man.get_measured_data()

        plotter.plot_deflection_for_ga(measured_data, super_data)

        return None

    def __calculate_fitness(self, measured_data, analytical_data):
        diff = np.sum((measured_data['y_axis'] / 1000 - analytical_data['y_axis'] / 1000) ** 2)
        lmbd = lambda x: 1 if x <= 0 else x
        return lmbd(int(diff ** (-1)))

    def get_init_population(self):
        if self.__model.get_model_type() == 'dynamic_single_winkler':
            params = [['EI', 3e5, 1e9],
                      ['m', 1e1, 1e4],
                      ['c', 1e4, 1e7],
                      ['k', 5e5, 5e9],
                      ['v', 1e1, 1e2],
                      ['Q', 9e2, 3e6]]

            pop = []
            for i in range(self.__pop_size):
                chromosome = []
                for param in params:
                    gene = random.randrange(param[1], param[2])
                    chromosome.append(gene)
                pop.append(chromosome)

            head = list(param[0] for param in params)
            population = pd.DataFrame(pop, columns=head)
            return population


class Chromosome:
    def __init__(self, columns):
        self.__chromosome = pd.DataFrame(columns=columns)

    def add_chromosome(self, chromosome):
        self.__chromosome = self.__chromosome.append(chromosome, ignore_index=True)

    def get_chromosome(self):
        return self.__chromosome

    def get_chromosome_values(self):
        return self.__chromosome.values


class Population:
    def __init__(self, columns, population_id):
        self.__population_id = population_id
        self.__columns = columns
        self.__population = pd.DataFrame(columns=columns)
        self.__selection_product = None
        self.__crossover_product = None

    def add_chromosome(self, chromosome):
        self.__population = self.__population.append(chromosome, ignore_index=True)

    def perform_selection(self):
        weight_cum = np.cumsum(self.__population['fitness'])
        weight_sum = np.sum(self.__population['fitness'])

        indexes = []
        offs = []
        for i in range(self.__population.shape[0]):
            idx = 0
            rand = random.randrange(1, weight_sum + 1)
            for j in weight_cum:
                if j >= rand:
                    break
                idx += 1
            indexes.append(idx)
            offs.append(self.__population.loc[idx].values)
        self.__selection_product = pd.DataFrame(offs, columns=self.__population.columns)

    def perform_crossover(self):
        cross_pop = self.__selection_product.loc[:, self.__selection_product.columns != 'fitness']
        # print(cross_pop)
        crossing_point = int((cross_pop.shape[1] - 1) / 2)

        def cross(pop, c_p, idx):
            item = []
            if not idx % 2:
                item.extend(pop.iloc[idx, :c_p + 1].values)
                item.extend(pop.iloc[idx + 1, c_p + 1:].values)
            else:
                item.extend(pop.iloc[idx, :c_p + 1].values)
                item.extend(pop.iloc[idx - 1, c_p + 1:].values)
            # item.extend([-1])
            return item

        offs = []
        for row in range(0, cross_pop.shape[0], 2):
            chrom_1 = cross(cross_pop, crossing_point, row)
            chrom_2 = cross(cross_pop, crossing_point, row + 1)
            offs.append(chrom_1)
            offs.append(chrom_2)

        self.__crossover_product = pd.DataFrame(offs, columns=cross_pop.columns)

    def get_population(self):
        return self.__population[self.__columns]

    def get_selection_product(self):
        return self.__selection_product[self.__columns]

    def get_crossover_product(self):
        return self.__crossover_product[self.__columns]

    def get_max_fitness_row(self):
        return self.__population.loc[self.__population['fitness'] == np.max(self.__population['fitness']), :].iloc[0]

    def write_log(self):
        self.__population.to_csv(f'logs/population_{self.__population_id}.txt')


class Populations:
    def __init__(self):
        self.__population_id = -1
        self.__populations = []

    def add_population(self, population):
        self.__population_id += 1
        self.__populations.append(population)
        # self.__populations = self.__populations.append({self.__population_id, population.get_population().values},
        #                                                ignore_index=True)

    def get_last_population(self):
        return self.__populations[self.__population_id]

    def get_populations(self):
        return self.__populations

    def get_last_population_id(self):
        return self.__population_id

    def save_report(self):
        self.__populations.to_csv('report.csv')
