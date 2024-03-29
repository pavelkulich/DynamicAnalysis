import pandas as pd
import numpy as np
import random
import models
import manipulator as dtm
import plotter
import config
import os
import csv


class GA:
    def __init__(self, model, measured_data, pop_size, num_of_populations):
        self.__model: models.Model = model
        self.__measured_data = measured_data
        self.__populations = Populations()
        self.__pop_size = pop_size
        self.__num_of_populations = num_of_populations

    def run_optimization(self, round=""):
        population = self.get_init_population()
        self.__optimize(population, 1, True, round)

    def adjust_q_vector(self):
        pass

    def __optimize(self, population, iteration, mutation, round):
        if iteration <= self.__num_of_populations:
            cols = list(population.columns)
            new_population = Population(cols, iteration, self.__model)
            for index, params in population.iterrows():
                print(f'population {iteration}, chromosome {index}')
                analytical_data = self.__model.calculate_model(params)
                man = dtm.Manipulator(self.__measured_data.copy()) # mozno vyhodit ze smycky

                # data manipulation
                man.set_analytical_data(analytical_data)
                man.get_significant_points() # mozno vyhodit ze smycky
                man.adjust_q_vector(params)

                q_vector = man.get_adjusted_q_vector() * params['Q']

                man.move_and_superpose()
                super_data = man.get_superposed_resampled()
                measured_data = man.get_measured_data()

                # fitness calculation
                fitness = self.__calculate_fitness(measured_data, super_data)
                params['fitness'] = fitness
                params = params.append(q_vector.iloc[0])
                new_population.add_chromosome(params)

            self.__populations.add_population(new_population)
            # new_population.write_log()
            new_population.perform_selection()
            new_population.perform_crossover()
            iteration += 1

            # plt.plot(measured_data['x_axis'], measured_data['y_axis'])
            # plt.plot(super_data['x_axis'], super_data['y_axis'])
            # plt.grid(True)
            # plt.savefig(f'plots/iteration_{iteration}.png')
            # plt.close()

            if mutation:
                new_population.perform_mutation()
                return self.__optimize(new_population.get_mutation_product(), iteration, mutation, round)

            return self.__optimize(new_population.get_crossover_product(), iteration, mutation)

        best_params = self.__populations.get_last_population().get_max_fitness_row()
        best_analytical_data = self.__model.calculate_model(best_params)
        best_params['vcr'] = 3.6 * np.power((best_params['k'] / (4 * best_params['EI'])), 0.25) / np.sqrt(
            best_params['m'] / best_params['EI'])

        if os.path.exists("logs/best_solutions.csv"):
            with open('logs/best_solutions.csv', 'a', newline='') as csvfile:
                fieldnames = best_params.index
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writerow(best_params.to_dict())
        else:
            with open('logs/best_solutions.csv', 'w', newline='') as csvfile:
                fieldnames = best_params.index
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                writer.writerow(best_params.to_dict())

        man = dtm.Manipulator(self.__measured_data.copy())

        # data manipulation
        man.set_analytical_data(best_analytical_data)
        man.get_significant_points()
        man.adjust_q_vector(best_params)

        man.move_and_superpose()
        super_data = man.get_superposed_resampled()
        measured_data = man.get_measured_data()
        print(best_params)
        plotter.plot_deflection_for_ga(measured_data, super_data, iter_round=round)

        return None

    def __calculate_fitness(self, measured_data, analytical_data):
        diff = np.sum((measured_data['y_axis'] - analytical_data['y_axis']) ** 2)
        sim = (diff / 10000) ** (-2)
        lmbd = lambda x: 1 if x <= 0 else x
        return lmbd(int(sim))

    # def __calculate_fitness(self, measured_data, analytical_data):
    #     result = 1 - spatial.distance.cosine(measured_data['y_axis'], analytical_data['y_axis'])
    #     return int(result * 10000)

    def get_init_population(self):
        if self.__model.get_model_type() == 'dynamic_single_winkler':
            params = config.DYNAMIC_SINGLE_WINKLER

        elif self.__model.get_model_type() == 'dynamic_double_pasternak':
            params = config.DYNAMIC_DOUBLE_PASTERNAK

        elif self.__model.get_model_type() == 'dynamic_single_winkler_moment':
            params = config.DYNAMIC_SINGLE_WINKLER

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
    def __init__(self, columns, population_id, model):
        self.__population_id = population_id
        self.__columns = columns
        self.__population = pd.DataFrame(columns=columns)
        self.__selection_product = None
        self.__crossover_product = None
        self.__mutation_product = None
        self.__model = model

    def add_chromosome(self, chromosome):
        self.__population = self.__population.append(chromosome, ignore_index=True)

    def perform_selection(self):
        weight_cum = np.cumsum(self.__population['fitness'])
        weight_sum = np.sum(self.__population['fitness'])
        # print(weight_cum) # odstranit
        # print(weight_sum) # odstranit

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
        cross_pop = self.__selection_product[self.__columns]
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

    def perform_mutation(self):
        mut_pop = self.__crossover_product[self.__columns]

        def mutate(chromosome):
            new_chromosome = self.get_randomized_populatuion(chromosome)
            return new_chromosome

        offs = []
        for row in range(0, mut_pop.shape[0]):
            if row % 2:
                mut_row = mutate(mut_pop.iloc[row])
                offs.append(mut_row)
                continue
            offs.append(mut_pop.iloc[row])

        self.__mutation_product = pd.DataFrame(offs, columns=mut_pop.columns)

    def get_randomized_populatuion(self, chromosome):
        if self.__model.get_model_type() == 'dynamic_single_winkler':
            params = config.DYNAMIC_SINGLE_WINKLER

        elif self.__model.get_model_type() == 'dynamic_double_pasternak':
            params = config.DYNAMIC_DOUBLE_PASTERNAK

        elif self.__model.get_model_type() == 'dynamic_single_winkler_moment':
            params = config.DYNAMIC_SINGLE_WINKLER

        if params:
            param = random.choice(params)
            gene = random.randrange(param[1], param[2])
            return chromosome.replace(to_replace=chromosome[param[0]], value=gene)

        else:
            print('Cannot randomize population. Model not implemented')
            return chromosome

    def get_population(self):
        return self.__population[self.__columns]

    def get_selection_product(self):
        return self.__selection_product[self.__columns]

    def get_crossover_product(self):
        return self.__crossover_product[self.__columns]

    def get_mutation_product(self):
        return self.__mutation_product[self.__columns]

    def get_max_fitness_row(self):
        return self.__population.loc[self.__population['fitness'] == np.max(self.__population['fitness']), :].iloc[0]

    def write_log(self):
        int_population = self.__population.astype(int, errors='ignore')
        int_population.to_csv(f'logs/population_{self.__population_id}.txt')


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
