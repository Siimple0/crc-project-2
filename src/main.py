import random
import numpy as np
import matplotlib.pyplot as plt

from tkinter import *
from time import sleep
from matplotlib.colors import ListedColormap
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure


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
        print('Population size: ' +str(population_size))
        # Generate starting placement
        self.population = np.random.choice([-1, 1, 0], size=population_size, p=ratios)
        # Reshape 1D array to 2D
        self.population = np.reshape(self.population, (int(np.sqrt(self.size)), int(np.sqrt(self.size))))

    def printToConsole(self):
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
schelling = Schelling(100, 0.5, 0.9, 1)

# print('---------> Round 0')
# schelling.printBoard()

number_iterations = 50

# for i in range(number_iterations):
#     print('---------> Round ' + str(i + 1))
#     schelling.run_round()
#     schelling.printBoard()




root = Tk()
root.title('Schelling\'s Model of Segregation')
#root.geometry("1200x800")~
root.bind("<Configure>", resize)

left_frame = Frame(root)
left_frame.pack(side=LEFT)
right_frame = Frame(root)
right_frame.pack(side=RIGHT)


plt.style.use("ggplot")
cmap = ListedColormap(['red', 'white', 'royalblue'])

fig, ax = plt.subplots()

ax.axis('off')
ax.pcolor(schelling.population, cmap=cmap, edgecolors='w', linewidths=1) 

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=True)

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)




def run_graph():
    for i in range(number_iterations): 
        schelling.run_round()
        ax.pcolor(schelling.population, cmap=cmap, edgecolors='w', linewidths=1)
        canvas.draw()

my_button1 = Button(right_frame, text='Start!', command=run_graph)
my_button1.pack()


root.mainloop()

            

# refs
# https://www.binpress.com/simulating-segregation-with-python/
# https://ytliu0.github.io/schelling/
# https://docs.python.org/3/library/tkinter.html
# https://matplotlib.org/3.3.3/contents.html