import random
import threading
import numpy as np
import matplotlib.pyplot as plt

from tkinter import *
# from tkinter import ttk
from time import sleep
from matplotlib.colors import ListedColormap
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure


class Schelling:

    # Only with 2 races for now, later it will be possible to send an array with tuples for each race
    def __init__(self, size, empty_ratio, similarity_threshold, neighbour_depth):
        self.model_configure(size, empty_ratio, similarity_threshold, neighbour_depth)

        self.cmap = ListedColormap(['white', 'gold', 'limegreen', 'purple', 'red', 'royalblue'])

        self.create_plot()

    
    def model_configure(self, size, empty_ratio, similarity_threshold, neighbour_depth, races_ratios=None):
        self.size = size
        self.empty_ratio = empty_ratio
        self.similarity_threshold = similarity_threshold
        self.neighbour_depth = neighbour_depth

        # Ratios for races and empty
        # ratios = [(1 - empty_ratio) / 2, (1 - empty_ratio) / 2, empty_ratio]
        
        if races_ratios:
            ratios = races_ratios
            ratios.insert(0, empty_ratio)
        else: 
            ratios = [
                empty_ratio,
                (1 - empty_ratio) / 5, 
                (1 - empty_ratio) / 5,
                (1 - empty_ratio) / 5,
                (1 - empty_ratio) / 5,
                (1 - empty_ratio) / 5
            ]

        print(ratios)

        # Actual size of population
        population_size = int(np.sqrt(self.size)) ** 2
        # Generate starting placement
        self.population = np.random.choice([0, 1, 2, 3, 4, 5], size=population_size, p=ratios)
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
                    
                    if similarity_ratio < self.similarity_threshold: # unhappy
                        try:
                            empty_entities = list(zip(np.where(self.population == 0)[0], np.where(self.population == 0)[1]))    
                            random_empty_entity = random.choice(empty_entities)
                            self.population[random_empty_entity] = race
                            self.population[row, col] = 0
                        except IndexError:
                            pass


    def create_plot(self):
        plt.style.use("ggplot")

        self.fig, self.ax = plt.subplots()
        
        self.update_plot()

    def update_plot(self):
        self.ax.clear()
        self.ax.axis('off')
        
        self.ax.pcolormesh(self.population, cmap=self.cmap, edgecolors='w', linewidths=1, vmin=0, vmax=5)
        self.fig.canvas.draw()


class Application(Tk):

    def __init__(self):
        Tk.__init__(self)

        self.title('Schelling\'s Model of Segregation')

        self.left_frame = Frame(self)
        self.left_frame.pack(side=LEFT, fill=BOTH, expand=True)
        self.right_frame = Frame(self)
        self.right_frame.pack(side=RIGHT, padx=10, pady=10, fill=BOTH)

        self.create_and_add_model()

        self.create_text_box_frames()

        self.create_button_row_frame()

        self.configure_components()

    def run_thread(self):
        x = threading.Thread(target=self.run_graph, args=(), daemon=True)
        x.start()

    def run_graph(self):
        for i in range(self.number_iterations): 
            self.run_round()

    def run_round(self):
        self.schelling.run_round()
        self.schelling.update_plot()
        self.canvas.draw()

    # TODO: initialize every component with the correct values and so on
    def configure_components(self):
        self.iteration_box.insert(0, self.number_iterations)

        self.population_box.insert(0, self.schelling.size)
        self.population_box.configure(validatecommand=self.update_test)
    
        self.empty_ratio_box.set(self.schelling.empty_ratio)
        self.similarity_threshold_box.set(self.schelling.similarity_threshold)

        i = 0
        for x in self.races_ratio_boxes:
        # for (x, y) in self.races_ratio_boxes:
            if i == 0 or i == 1:
                x.set(0.5)
            # y.current(i)
            i += 1

        self.start_button.configure(command=self.run_graph)
        self.reset_button.configure(command=self.print_values)
        # self.stop_button.configure()
        self.step_button.configure(command=self.run_round)
        
    
    def create_and_add_model(self):
        self.number_iterations = 20
        self.schelling = Schelling(100, 0.5, 0.8, 1)
        self.draw_canvas()
        

    def draw_canvas(self):
        self.canvas = FigureCanvasTkAgg(self.schelling.fig, master=self.left_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=True)

    def update_test(self):
        self.number_iterations = int(self.iteration_box.get())

        ratios =  [float(x.get()) for x in self.races_ratio_boxes] 

        self.schelling.model_configure(int(self.population_box.get()), float(self.empty_ratio_box.get()), float(self.similarity_threshold_box.get()), 1, ratios)

        self.schelling.update_plot()

        self.canvas.get_tk_widget().pack_forget()

        self.draw_canvas()
       
        return True


    def create_text_box_frames(self):
        # create iteration frame
        iteration_frame = Frame(self.right_frame)

        iteration_label = Label(iteration_frame, text="Number of Iterations ")
        iteration_label.pack(side=LEFT)

        iteration_value = StringVar()
        self.iteration_box = Entry(iteration_frame, textvariable=iteration_value)
        self.iteration_box.pack(side=LEFT)

        iteration_frame.pack(side=TOP)


        # create population frame
        population_frame = Frame(self.right_frame)

        population_label = Label(population_frame, text="Population Size ")
        population_label.pack(side=LEFT)

        population_value = StringVar()
        self.population_box = Entry(population_frame, textvariable=population_value, validate="focusout")
        self.population_box.pack(side=LEFT)

        population_frame.pack(side=TOP)


        # create empty ratio
        empty_ratio_frame = Frame(self.right_frame)

        empty_ratio_label = Label(empty_ratio_frame, text="Empty Ratio ")
        empty_ratio_label.pack(side=LEFT)

        self.empty_ratio_box = Scale(empty_ratio_frame, from_=0.00, to=1.00, digits=3, resolution=0.01, orient=HORIZONTAL, length=150)
        self.empty_ratio_box.pack(side=LEFT)

        empty_ratio_frame.pack(side=TOP)

        # create similarity threshold
        similarity_threshold_frame = Frame(self.right_frame)

        similarity_threshold_label = Label(similarity_threshold_frame, text="Similarity Threshold ")
        similarity_threshold_label.pack(side=LEFT)

        self.similarity_threshold_box = Scale(similarity_threshold_frame, from_=0.00, to=1.00, digits=3, resolution=0.01, orient=HORIZONTAL)
        self.similarity_threshold_box.pack(side=LEFT)

        similarity_threshold_frame.pack(side=TOP)

        # create races
        races_frame = Frame(self.right_frame)

        self.races_ratio_boxes = []
        
        for i in range(5):
            race_frame = Frame(races_frame)

            race_label_text = "Race " + str(i + 1) + " "
            race_label = Label(race_frame, text=race_label_text)
            race_label.pack(side=LEFT)
            
            races_scale = Scale(race_frame, from_=0.00, to=1.00, digits=3, resolution=0.01, orient=HORIZONTAL)
            races_scale.pack(side=LEFT)

            # races_colors = ('royalblue', 'red', 'gold', 'limegreen', 'purple')
            # races_color_value = StringVar()
            # races_color_combobox = ttk.Combobox(race_frame, textvariable=races_color_value, state="readonly", values=races_colors)
            # races_color_combobox.pack(side=LEFT)

            # self.races_ratio_boxes.append((races_scale, races_color_combobox))
            self.races_ratio_boxes.append(races_scale)

            race_frame.pack(side=TOP)
        
        races_frame.pack(side=TOP)


    def create_button_row_frame(self):
        self.button_row_frame = Frame(self.right_frame)
        self.button_row_frame.pack(side=BOTTOM, pady=20)

        self.start_button = Button(self.button_row_frame, text='Start', bg="red1", fg="white")
        self.start_button.pack(side=LEFT)
        self.stop_button = Button(self.button_row_frame, text='Stop')
        self.stop_button.pack(side=LEFT)
        self.reset_button = Button(self.button_row_frame, text='Reset')
        self.reset_button.pack(side=LEFT)
        self.step_button = Button(self.button_row_frame, text='Step')
        self.step_button.pack(side=LEFT)


    def print_values(self):
        print(self.iteration_box.get())
        print(self.population_box.get())

        print(self.schelling.population)

        print(self.empty_ratio_box.get())
        # for (x, y) in self.races_ratio_boxes:
        for x in self.races_ratio_boxes:
            print(x.get())
            # print(y.get())
        
        print(self.similarity_threshold_box.get())


    def _quit():
        self.quit()  
        self.destroy()


app = Application()
app.mainloop()

# Key handler
# def on_key_press(event):
#     print("you pressed {}".format(event.key))
#     key_press_handler(event, canvas)
# canvas.mpl_connect("key_press_event", on_key_press)


#TODO: Load button or dynamic loading?
#TODO: Button commands