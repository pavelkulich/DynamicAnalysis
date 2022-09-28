import models as mod
import manipulator as man
import plotter
import random
import numpy as np
import pandas as pd


def init_generator(n):
    params = [['EI_1', 3e6, 1e8],
              ['EI_2', 1, 1e4],
              ['GA', 1e5, 1e6],
              ['k_1', 5e7, 5e8],
              ['k_2', 1e6, 2e8],
              ['c_1', 5e4, 1e6],
              ['c_2', 8e4, 1e6],
              ['Q', 9e3, 3e5]]

    pop = []
    for i in range(n):
        chromosome = []
        for param in params:
            gene = random.randrange(param[1], param[2])
            chromosome.append(gene)
        pop.append(chromosome)

    head = list(param[0] for param in params)
    population = pd.DataFrame(pop, columns=head)
    return population


def mutation_generator(idx):
    params = [['EI_1', 3e6, 1e8],
              ['EI_2', 1, 1e3],
              ['GA', 1e5, 1e6],
              ['k_1', 5e7, 5e8],
              ['k_2', 1e7, 2e8],
              ['c_1', 1e5, 1e6],
              ['c_2', 1e5, 1e6],
              ['Q', 9e4, 3e5]]
    gene = random.randrange(params[idx][1], params[idx][2])
    return gene


# caluclate difference of cumulative distribution
def fitness_cumulative_distribution(measured_data, analytical_data):
    diff = np.sum((measured_data['y_axis'] - analytical_data['y_axis']) ** 2)
    # cumsum_measured = measured_data['y_axis'].cumsum(axis=0)
    # cumsum_analytical = analytical_data['y_axis'].cumsum(axis=0)
    # cumsum_diff = np.max(np.abs(cumsum_measured - cumsum_analytical))
    # print(cumsum_diff)
    # plotter.plot(measured_data['y_axis'], cumsum_measured, analytical_data['y_axis'], cumsum_analytical)
    lmbd = lambda x: 1 if x == 0 else x
    return lmbd(int(100 / diff))


def random_genes_selection(population, num_of_offspring):
    weight_cum = np.cumsum(population['fitness'])
    weight_sum = np.sum(population['fitness'])

    indexes = []
    offs = []
    for i in range(num_of_offspring):
        idx = 0
        rand = random.randrange(1, weight_sum + 1)
        # print(f'rand: {rand}')
        for j in weight_cum:
            if j >= rand:
                break
            idx += 1
        indexes.append(idx)
        offs.append(population.loc[idx].values)
    offspring = pd.DataFrame(offs, columns=population.columns)
    return offspring


def crossover(population):
    # print(population.iloc[:, 0:int((population.shape[1] - 1) / 2)])
    crossing_point = int((population.shape[1] - 1) / 2)

    def cross(pop, c_p, idx):
        item = []
        if not idx % 2:
            item.extend(pop.iloc[idx, :c_p].values)
            item.extend(pop.iloc[idx + 1, c_p:-1].values)
        else:
            item.extend(pop.iloc[idx, :c_p].values)
            item.extend(pop.iloc[idx - 1, c_p:-1].values)
        item.extend([-1])
        return item

    offs = []
    for row in range(0, population.shape[0], 2):
        chrom_1 = cross(population, crossing_point, row)
        chrom_2 = cross(population, crossing_point, row + 1)
        offs.append(chrom_1)
        offs.append(chrom_2)

    return pd.DataFrame(offs, columns=population.columns)


def mutate(population):
    for index, value in population.iterrows():
        if bool(random.getrandbits(1)):
            rand_param = random.randrange(population.shape[1] - 1)
            rand_gene = mutation_generator(rand_param)
            value[rand_param] = rand_gene

    return population


def optimize(measured_data, population, chroms_in_pop, n=1):
    print('*************************************')

    def asses_data(meas_data, pop):
        pop_fitness = []
        for index, row in pop.iterrows():
            print(index)
            # analytical_data = mod.dynamic_double_pasternak()
            analytical_data = mod.dynamic_double_pasternak(row, v=40, m1=60, m2=304)
            meas_data, superposed_data = man.rescale_and_fit(meas_data, analytical_data)
            # plotter.measured_and_superposed(measured_data, superposed_data)
            fitness = fitness_cumulative_distribution(measured_data, superposed_data)
            pop_fitness.append(fitness)

        pop['fitness'] = pop_fitness
        return meas_data, pop

    def print_best_solution(meas_data, pop):
        print(pop)
        sol = pop[pop['fitness'] == pop['fitness'].max()]
        for index, row in sol.iterrows():
            sol = row
            break
        analytical_data = mod.dynamic_double_pasternak(sol, v=40, m1=60, m2=304)
        meas_data, superposed_data = man.rescale_and_fit(meas_data, analytical_data)
        plotter.plot(meas_data, superposed_data)

    while n < 10:
        measured_data, population = asses_data(measured_data, population)
        print_best_solution(measured_data, population)
        offspring = random_genes_selection(population, chroms_in_pop)
        # print(f'offspring: \n {offspring}')
        crossded_pop = crossover(offspring)
        mutated_pop = mutate(crossded_pop)
        n += 1
        return optimize(measured_data, mutated_pop, chroms_in_pop, n)
    else:
        measured_data, population = asses_data(measured_data, population)
        print_best_solution(measured_data, population)
        # return population
        return None


def main():
    measured_data = man.import_data()
    chroms_in_pop = 40  # must be even
    if chroms_in_pop % 2:
        chroms_in_pop -= 1
    population = init_generator(chroms_in_pop)
    optimize(measured_data, population, chroms_in_pop)


main()
