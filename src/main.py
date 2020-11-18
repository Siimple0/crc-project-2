import random
import threading
import numpy as np
import matplotlib.pyplot as plt

from tkinter import *
from time import sleep
from matplotlib.colors import ListedColormap
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure


class Schelling:

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
        number_unhappy = 0
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
                        number_unhappy = number_unhappy + 1
                        try:
                            empty_entities = list(zip(np.where(self.population == 0)[0], np.where(self.population == 0)[1]))    
                            random_empty_entity = random.choice(empty_entities)
                            self.population[random_empty_entity] = race
                            self.population[row, col] = 0
                        except IndexError:
                            pass
        if number_unhappy == 0:
            return True
        return False


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


    def run_graph(self):
        if self.number_iterations > 0:
            for i in range(self.number_iterations): 
                if self.run_round():
                    break
                self.simulation_status_label.config(text="Iteration " + str(i))
        else:
            i = 0
            while True:
                if self.run_round():
                    break
                i = i + 1
                self.simulation_status_label.config(text="Iteration " + str(i))
        self.simulation_status_label.config(text=self.simulation_status_label.cget("text") + "\nDone!")
            


    def run_round(self):
        result = self.schelling.run_round()
        self.schelling.update_plot()
        self.canvas.draw()

        return result


    def configure_components(self):
        self.iteration_box.insert(0, self.number_iterations)

        self.population_box.insert(0, self.schelling.size)
        # self.population_box.configure(validatecommand=self.validate_and_update)
    
        self.empty_ratio_box.set(self.schelling.empty_ratio)
        self.similarity_threshold_box.set(self.schelling.similarity_threshold)

        i = 0
        for x in self.races_ratio_boxes:
            self.races_ratio_boxes[i].set((1 - self.empty_ratio_box.get()) / 5)
            i = i + 1

        self.start_button.configure(command=self.run_graph)
        self.step_button.configure(command=self.run_round)

        self.load_button.configure(command=self.validate_and_update)
        
    
    def create_and_add_model(self):
        self.number_iterations = 20
        self.schelling = Schelling(100, 0.5, 0.8, 1)
        self.draw_canvas()
        

    def draw_canvas(self):
        self.canvas = FigureCanvasTkAgg(self.schelling.fig, master=self.left_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=True)


    def validate_and_update(self):
        if self.validate_probabilities():
            self.update()
            self.simulation_status_label.config(text="")
        else:
            threading.Thread(target=self.popupmsg, args=("The sum of the Empty Ratio and the Races' Ratios needs to be equal to 1!", )).start()
        return True


    def popupmsg(self, msg):
        popup = Tk()
        popup.resizable(False, False)
        popup.wm_title("Invalid values!")
        label = Label(popup, text=msg)
        label.pack(side="top", fill="x", pady=10)
        B1 = Button(popup, text="Okay", command = popup.destroy)
        B1.pack(pady=10)
        popup.mainloop()


    def validate_probabilities(self):
        ratios = self.get_race_ratios()
        if (sum(ratios) + float(self.empty_ratio_box.get())) == 1.0:
            return True
        return False


    def update(self):
        self.number_iterations = int(self.iteration_box.get())

        ratios = self.get_race_ratios()

        self.schelling.model_configure(int(self.population_box.get()), float(self.empty_ratio_box.get()), float(self.similarity_threshold_box.get()), 1, ratios)

        self.schelling.update_plot()

        self.canvas.get_tk_widget().pack_forget()

        self.draw_canvas()
       

    def create_text_box_frames(self):
        # create parameters label
        parameters_label = Label(self.right_frame, text="Model Parameters", font=("Verdana",16))
        parameters_label.pack(side=TOP)

        # create iteration frame
        iteration_frame = Frame(self.right_frame)

        iteration_label = Label(iteration_frame, text="Number of Iterations ")
        iteration_label.pack(side=LEFT)

        iteration_value = StringVar()
        self.iteration_box = Entry(iteration_frame, textvariable=iteration_value, width=16)
        self.iteration_box.pack(side=LEFT)

        iteration_frame.pack(side=TOP)


        # create population frame
        population_frame = Frame(self.right_frame)

        population_label = Label(population_frame, text="Population Size ")
        population_label.pack(side=LEFT)

        population_value = StringVar()
        self.population_box = Entry(population_frame, textvariable=population_value, width=21) # , validate="focusout")
        self.population_box.pack(side=RIGHT)

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

        similarity_threshold_label = Label(similarity_threshold_frame, text="Similarity Threshold")
        similarity_threshold_label.pack(side=LEFT)

        self.similarity_threshold_box = Scale(similarity_threshold_frame, from_=0.00, to=1.00, digits=3, resolution=0.01, orient=HORIZONTAL, length=110)
        self.similarity_threshold_box.pack(side=LEFT)

        similarity_threshold_frame.pack(side=TOP)

        # create races
        races_frame = Frame(self.right_frame)

        self.races_ratio_boxes = []
        
        for i in range(5):
            race_frame = Frame(races_frame)


            race_label_text = "Race " + chr(ord('A') + i) + " Ratio "
            race_label = Label(race_frame, text=race_label_text)
            race_label.pack(side=LEFT)
            
            races_scale = Scale(race_frame, from_=0.00, to=1.00, digits=3, resolution=0.01, orient=HORIZONTAL, length=148)
            races_scale.pack(side=LEFT)

            self.races_ratio_boxes.append(races_scale)

            race_frame.pack(side=TOP)

        
        races_frame.pack(side=TOP)

        # create status label
        self.simulation_status_label = Label(self.right_frame, text="")
        self.simulation_status_label.pack(side=BOTTOM)


    def create_button_row_frame(self):
        self.button_row_frame = Frame(self.right_frame)
        self.button_row_frame.pack(side=BOTTOM, pady=20)

        self.start_button = Button(self.button_row_frame, text='Start', width=15, bg='red3', fg='white')
        self.start_button.pack(side=LEFT)
        self.step_button = Button(self.button_row_frame, text='Step', width=15, bg='black', fg='white')
        self.step_button.pack(side=LEFT)


        self.button_bottom_row_frame = Frame(self.right_frame)
        self.button_bottom_row_frame.pack(side=BOTTOM, pady=0)
        
        self.load_button = Button(self.button_bottom_row_frame, text='LOAD', bg="royalblue3", fg="white", width=30)
        self.load_button.pack(side=BOTTOM)


    def get_race_ratios(self):
        return [float(x.get()) for x in self.races_ratio_boxes] 


    def print_values(self):
        print(self.iteration_box.get())
        print(self.population_box.get())

        print(self.schelling.population)

        print(self.empty_ratio_box.get())
        for x in self.races_ratio_boxes:
            print(x.get())
        
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


# TODO: Iterations infitnet