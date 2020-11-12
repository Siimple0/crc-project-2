import random
from time import sleep
import numpy as np
import matplotlib as plt

class Schelling:

    # Only with 2 races for now, later it will be possible to send an array with tuples for each race
    def __init__(self, size, empty_ratio, neighbours_race_threshold, neighbour_depth, race1_ratio=None, race2_ratio=None):
        self.size = size
        self.empty_ratio = empty_ratio
        self.neighbours_race_threshold = neighbours_race_threshold
        self.neighbour_depth = neighbour_depth

        # Ratios for race1, race2 and empty
        ratios = [(1 - empty_ratio) / 2, (1 - empty_ratio) / 2, empty_ratio]
        # Actual size of population
        population_size = int(np.sqrt(self.size)) ** 2
        # Generate starting placement
        self.population = np.random.choice([-1, 1, 0], size=population_size, p=ratios)
        # Reshape 1D array to 2D
        self.population = np.reshape(self.population, (int(np.sqrt(self.size)), int(np.sqrt(self.size))))

    def printBoard(self):
        print('-' * (len(self.population) * 2 + 2))
        for x in self.population:
            row_str = "| "
            for y in x:
                if y == -1:
                    row_str += "# "
                elif y == 1:
                    row_str += "O "
                else:
                    row_str += "  "
            row_str = row_str[:-1] + "|" 
            print(row_str)
        print('-' * (len(self.population) * 2 + 2))


    def run_round(self):
        for (row, col), value in np.ndenumerate(self.population):
            race = self.population[row, col]
            if race != 0: # not empty
                x_min = max(row - self.neighbour_depth, 0)
                x_max = min(row + self.neighbour_depth + 1, int(np.sqrt(self.size)))
                y_min = max(col - self.neighbour_depth, 0)
                y_max = min(col + self.neighbour_depth + 1, int(np.sqrt(self.size)))
                neighbourhood = self.population[x_min:x_max, y_min:y_max]

                # print("Row : " + str(row) + ", Col : " + str(col))
                # print("x_min : " + str(x_min) + ", x_max : " + str(x_max) + ", y_min : " + str(y_min) + ", y_max : " + str(y_max))
                # print(neighbourhood)

                neighbourhood_size = np.size(neighbourhood)
                number_empty_entities = len(np.where(neighbourhood == 0)[0]) # number of empty entities on the neighbourhood
                if neighbourhood_size != number_empty_entities + 1: # plus the current node
                    number_similar = len(np.where(neighbourhood == race)[0]) - 1
                    similarity_ratio = number_similar / (neighbourhood_size - number_empty_entities - 1) 
                    if similarity_ratio < self.neighbours_race_threshold: # unhappy
                        empty_entities = list(zip(np.where(self.population == 0)[0], np.where(self.population == 0)[1]))
                        random_empty_entity = random.choice(empty_entities)
                        self.population[random_empty_entity] = race
                        self.population[row, col] = 0

            

round = 0
schelling = Schelling(500, 0.3, 0.4, 1)
print('---------> Round 0')
schelling.printBoard()

number_iterations = 100

for i in range(number_iterations):
    print('---------> Round ' + str(i + 1))
    schelling.run_round()
    schelling.printBoard()
