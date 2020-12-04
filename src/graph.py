from schelling import *
import configparser
import sys
import random
import numpy as np
import matplotlib.pyplot as plt

class BigGraph:

    def __init__(self, confFile):
        self.threshold = 1
        
        self.read_properties(confFile)
        
        self.values = [[0.0 for y in range(self.simulations)] for x in range(100)]


        self.schelling = Schelling(self.width, self.height, self.emptyratio, self.threshold, self.ndepth, self.races)
    

    def read_properties(self, confFile):
        config = configparser.ConfigParser()
        config.read(confFile)
        

        self.simulations = config['DEFAULT'].getint('nsimulations')
        self.maxiterations = config['DEFAULT'].getint('maxniterations')
        self.width = config['DEFAULT'].getint('popwidth')
        self.height = config['DEFAULT'].getint('popheight')
        self.ndepth = config['DEFAULT'].getint('ndepth')
        self.random = config['DEFAULT'].getboolean('random')
        self.numberraces = config['DEFAULT'].getint('numberraces')
        self.emptyratio = config['DEFAULT'].getfloat('emptyratio')
        self.races = [
            config['DEFAULT'].getfloat('raratio'),
            config['DEFAULT'].getfloat('rbratio'),
            config['DEFAULT'].getfloat('rcratio'),
            config['DEFAULT'].getfloat('rdratio'),
            config['DEFAULT'].getfloat('reratio')
        ]

        print(self.maxiterations, self.width, self.height, self.ndepth, self.threshold, self.emptyratio, self.races)


    def compute(self):
        while self.threshold <= 100:
            number_of_simulation_in_threshold = 0

            while number_of_simulation_in_threshold < self.simulations:
                number_iterations = 0
                eff_threshold = self.threshold / 100
                self.schelling.model_configure(self.width, self.height, self.emptyratio, eff_threshold, self.ndepth, self.races)

                while not self.schelling.run_round() and number_iterations < self.maxiterations:
                    number_iterations += 1
                
                self.values[self.threshold - 1][number_of_simulation_in_threshold] = self.compute_neighbourhood_numbers()
                number_of_simulation_in_threshold += 1

            print(self.threshold)
            self.threshold += 1

        return self.values

    def compute_random(self):
        while self.threshold <= 100:
            number_of_simulation_in_threshold = 0

            while number_of_simulation_in_threshold < self.simulations:
                number_iterations = 0
                eff_threshold = self.threshold / 100
                self.emptyratio = round(random.uniform(0, 1), 2)
                ratio_total = self.emptyratio
                races = [0, 0, 0, 0, 0]
                for i in range(self.numberraces):
                    if i == self.numberraces - 1:
                        races[i] = round(1 - ratio_total, 2)
                    else:
                        races[i] = round(random.uniform(0, 1 - ratio_total), 2)
                    ratio_total = ratio_total + races[i]
                self.races = races
                self.schelling.model_configure(self.width, self.height, self.emptyratio, eff_threshold, self.ndepth, self.races)

                while not self.schelling.run_round() and number_iterations < self.maxiterations:
                    number_iterations += 1
                
                self.values[self.threshold - 1][number_of_simulation_in_threshold] = self.compute_neighbourhood_numbers()
                number_of_simulation_in_threshold += 1

            print(self.threshold)
            self.threshold += 1

        return self.values



    def compute_neighbourhood_numbers(self):
        neigh_sum = 0
        number_of_ind = 0
        for (row, col), value in np.ndenumerate(self.schelling.population):
            if self.schelling.get_race(row,col) != 0:
                neigh_sum += self.schelling.get_ratio_of_individuals_same_race_in_neighbourhood(row, col)
                number_of_ind += 1
        if number_of_ind == 0:
            return 1
        return neigh_sum / number_of_ind


    def compute_average(self, matrix):
        result = [0.0 for y in range(100)]
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                result[i] += matrix[i][j]
            result[i] /= self.simulations
        return result
        

    def get_min(self, matrix):
        result = [0.0 for y in range(100)]
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                result[i] = min(matrix[i])
        return result
    
    def get_max(self, matrix):
        result = [0.0 for y in range(100)]
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                result[i] = max(matrix[i])
        return result

if len(sys.argv) != 1:
    path = sys.argv[1]
    bg = BigGraph(path)
    if not bg.random:
        values = bg.compute()
    else: 
        values = bg.compute_random()

    min_values = bg.get_min(values)
    average_values = bg.compute_average(values)
    max_values = bg.get_max(values)

    x_coords = [x / 100 for x in range(1, 101)]
    plt.plot(x_coords, min_values, label='Min')
    plt.plot(x_coords, average_values, label='Average')
    plt.plot(x_coords, max_values, label='Max')
    plt.xlabel('Similarity Threshold')
    plt.ylabel('Number of neighbours of the same color')
    plt.legend()
    plt.show()

else:
    print('Usage: python graph.py configFilePath')
