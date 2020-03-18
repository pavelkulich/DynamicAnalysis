import data_manipulator as man
import pandas as pd


class GenAlgs:
    data = 1

    def __init__(self, model, pop_size):
        self.__init_population = man.import_data()
        self.__model: str = model
        self.__pop_size: int = pop_size

    def get_init_population(self):
        return self.__init_population


    def work(self):
        pass
