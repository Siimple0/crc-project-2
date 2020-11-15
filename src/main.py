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
        self.model_configure(size, empty_ratio, neighbours_race_threshold, neighbour_depth)

        self.cmap = ListedColormap(['red', 'white', 'royalblue'])

        self.create_plot()

    
    def model_configure(self, size, empty_ratio, neighbours_race_threshold, neighbour_depth):
        self.size = size
        self.empty_ratio = empty_ratio
        self.neighbours_race_threshold = neighbours_race_threshold
        self.neighbour_depth = neighbour_depth

        # Ratios for race1, race2 and empty
        ratios = [(1 - empty_ratio) / 2, (1 - empty_ratio) / 2, empty_ratio]
        # Actual size of population
        population_size = int(np.sqrt(self.size)) ** 2
        print('Population size: ' + str(population_size))
        # Generate starting placement
        self.population = np.random.choice([-1, 1, 0], size=population_size, p=ratios)
        # Reshape 1D array to 2D
        self.population = np.reshape(self.population, (int(np.sqrt(self.size)), int(np.sqrt(self.size))))


    def print_to_console(self):
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


    def create_plot(self):
        plt.style.use("ggplot")

        self.fig, self.ax = plt.subplots()

        self.ax.axis('off')
        self.ax.pcolor(self.population, cmap=self.cmap, edgecolors='w', linewidths=1) 


class Application(Tk):

    def __init__(self):
        Tk.__init__(self)

        self.title('Schelling\'s Model of Segregation')

        self.left_frame = Frame(self)
        self.left_frame.pack(side=LEFT, fill=BOTH, expand=True)
        self.right_frame = Frame(self)
        self.right_frame.pack(side=RIGHT, padx=10, pady=10, fill=BOTH)

        self.create_text_box_frames()

        self.create_button_row_frame()

    def create_text_box_frames(self):
        # create iteration frame
        iteration_frame = Frame(self.right_frame)

        iteration_label = Label(iteration_frame, text="Number of Iterations ")
        iteration_label.pack(side=LEFT)

        iteration_value = IntVar()
        self.iteration_box = Entry(iteration_frame, textvariable=iteration_value)
        self.iteration_box.pack(side=LEFT)

        iteration_frame.pack(side=TOP)


        # create population frame
        population_frame = Frame(self.right_frame)

        population_label = Label(population_frame, text="Population Size ")
        population_label.pack(side=LEFT)

        population_value = IntVar()
        self.population_box = Entry(population_frame, textvariable=population_value)
        self.population_box.pack(side=LEFT)

        population_frame.pack(side=TOP)


        # create empty ratio
        empty_ratio_frame = Frame(self.right_frame)

        empty_ratio_label = Label(empty_ratio_frame, text="Empty Ratio ")
        empty_ratio_label.pack(side=LEFT)

        self.empty_ratio_box = Scale(empty_ratio_frame, from_=0.00, to=1.00, digits=3, resolution=0.01, orient=HORIZONTAL)
        self.empty_ratio_box.pack(side=LEFT)

        empty_ratio_frame.pack(side=TOP)

        # create races
        races_frame = Frame(self.right_frame)

        race1_frame = Frame(races_frame)
        race1_label = Label(race1_frame, text="Race 1 ")
        race1_label.pack(side=LEFT)
        self.race1_ratio_box = Scale(race1_frame, from_=0.00, to=1.00, digits=3, resolution=0.01, orient=HORIZONTAL)
        self.race1_ratio_box.pack(side=LEFT)
        race1_frame.pack(side=TOP)

        race2_frame = Frame(races_frame)
        race2_label = Label(race2_frame, text="Race 2 ")
        race2_label.pack(side=LEFT)
        self.race2_ratio_box = Scale(race2_frame, from_=0.00, to=1.00, digits=3, resolution=0.01, orient=HORIZONTAL)
        self.race2_ratio_box.pack(side=LEFT)
        race2_frame.pack(side=TOP)

        race3_frame = Frame(races_frame)
        race3_label = Label(race3_frame, text="Race 3 ")
        race3_label.pack(side=LEFT)
        self.race3_ratio_box = Scale(race3_frame, from_=0.00, to=1.00, digits=3, resolution=0.01, orient=HORIZONTAL)
        self.race3_ratio_box.pack(side=LEFT)
        race3_frame.pack(side=TOP)

        race4_frame = Frame(races_frame)
        race4_label = Label(race4_frame, text="Race 4 ")
        race4_label.pack(side=LEFT)
        self.race4_ratio_box = Scale(race4_frame, from_=0.00, to=1.00, digits=3, resolution=0.01, orient=HORIZONTAL)
        self.race4_ratio_box.pack(side=LEFT)
        race4_frame.pack(side=TOP)

        race5_frame = Frame(races_frame)
        race5_label = Label(race5_frame, text="Race 5 ")
        race5_label.pack(side=LEFT)
        self.race5_ratio_box = Scale(race5_frame, from_=0.00, to=1.00, digits=3, resolution=0.01, orient=HORIZONTAL)
        self.race5_ratio_box.pack(side=LEFT)
        race5_frame.pack(side=TOP)
        
        races_frame.pack(side=TOP)

        # create similarity threshold
        similarity_threshold_frame = Frame(self.right_frame)

        similarity_threshold_label = Label(similarity_threshold_frame, text="Similarity Threshold ")
        similarity_threshold_label.pack(side=LEFT)

        self.similarity_threshold_box = Scale(similarity_threshold_frame, from_=0.00, to=1.00, digits=3, resolution=0.01, orient=HORIZONTAL)
        self.similarity_threshold_box.pack(side=LEFT)

        similarity_threshold_frame.pack(side=TOP)
    
        

    def create_button_row_frame(self):
        self.button_row_frame = Frame(self.right_frame)
        self.button_row_frame.pack(side=BOTTOM, pady=20)

        self.start_button = Button(self.button_row_frame, text='Start')
        self.start_button.pack(side=LEFT)
        self.stop_button = Button(self.button_row_frame, text='Stop')
        self.stop_button.pack(side=LEFT)
        self.reset_button = Button(self.button_row_frame, text='Reset')
        self.reset_button.pack(side=LEFT)
        self.step_button = Button(self.button_row_frame, text='Step')
        self.step_button.pack(side=LEFT)

    def _quit():
        self.quit()  
        self.destroy()


number_iterations = 20

schelling = Schelling(100, 0.4, 0.8, 1)


app = Application()

canvas = FigureCanvasTkAgg(schelling.fig, master=app.left_frame)
canvas.draw()
canvas.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=True)

# Key handler
# def on_key_press(event):
#     print("you pressed {}".format(event.key))
#     key_press_handler(event, canvas)
# canvas.mpl_connect("key_press_event", on_key_press)

def run_graph():
    for i in range(number_iterations): 
        schelling.run_round()
        schelling.ax.pcolor(schelling.population, cmap=schelling.cmap, edgecolors='w', linewidths=1)
        canvas.draw()

def print_values():
    print("xd")
    print(app.population_box.get())
    print(app.iteration_box.get())

app.start_button.configure(command=run_graph)
app.step_button.configure(command=print_values)

app.mainloop()
