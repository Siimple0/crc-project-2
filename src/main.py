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

    def __init__(self, width, height, empty_ratio, similarity_threshold, neighbour_depth):
        self.model_configure(width, height, empty_ratio, similarity_threshold, neighbour_depth)

        self.cmap = ListedColormap(['white', 'gold', 'limegreen', 'purple', 'red', 'royalblue'])

        self.create_plot()

    
    def model_configure(self, width, height, empty_ratio, similarity_threshold, neighbour_depth, races_ratios=None):
        self.width = width
        self.height = height
        self.empty_ratio = empty_ratio
        self.similarity_threshold = similarity_threshold
        self.neighbour_depth = neighbour_depth

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
        population_size = width * height
        # Generate starting placement
        self.population = np.random.choice([0, 1, 2, 3, 4, 5], size=population_size, p=ratios)
        # Reshape 1D array to 2D
        self.population = np.reshape(self.population, (int(self.height), int(self.width)))


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
                # x_max = min(row + self.neighbour_depth + 1, int(np.sqrt(self.size)))
                x_max = min(row + self.neighbour_depth + 1, self.width)
                y_min = max(col - self.neighbour_depth, 0)
                # y_max = min(col + self.neighbour_depth + 1, int(np.sqrt(self.size)))
                y_max = min(col + self.neighbour_depth + 1, self.height)
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

        self.random = False

        self.title('Schelling\'s Model of Segregation')

        self.left_frame = Frame(self)
        self.left_frame.pack(side=LEFT, fill=BOTH, expand=True)
        self.right_frame = Frame(self)
        self.right_frame.pack(side=RIGHT, padx=10, pady=10, fill=BOTH)

        self.create_and_add_model()

        self.create_text_box_frames()

        self.create_button_row_frame()

        self.configure_components()


    def create_and_add_model(self):
        self.number_iterations = 20
        self.schelling = Schelling(10, 10, 0.5, 0.8, 1)
        self.draw_canvas()
        

    def draw_canvas(self):
        self.canvas = FigureCanvasTkAgg(self.schelling.fig, master=self.left_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=True)


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

        pop_frame_width = Frame(population_frame)
        population_label = Label(pop_frame_width, text="Population Width ")
        population_label.pack(side=LEFT)

        population_width_value = StringVar()
        self.population_width_box = Entry(pop_frame_width, textvariable=population_width_value, width=21) # , validate="focusout")
        self.population_width_box.pack(side=RIGHT)
        pop_frame_width.pack(side=TOP)

        pop_frame_height = Frame(population_frame)
        population_label = Label(pop_frame_height, text="Population Height ")
        population_label.pack(side=LEFT)

        population_height_value = StringVar()
        self.population_height_box = Entry(pop_frame_height, textvariable=population_height_value, width=21) # , validate="focusout")
        self.population_height_box.pack(side=RIGHT)
        pop_frame_height.pack(side=TOP)

        population_frame.pack(side=TOP)

        # create neighbourhood depth
        neighbour_depth_frame = Frame(self.right_frame)

        neighbour_depth_label = Label(neighbour_depth_frame, text="Neighbourhood Depth ")
        neighbour_depth_label.pack(side=LEFT)

        
        neighbour_depth_value = StringVar()
        
        self.neighbour_depth_box = Entry(neighbour_depth_frame, textvariable=neighbour_depth_value, width=15)
        self.neighbour_depth_box.pack(side=LEFT)

        neighbour_depth_frame.pack(side=TOP)

        # create similarity threshold
        similarity_threshold_frame = Frame(self.right_frame)

        similarity_threshold_label = Label(similarity_threshold_frame, text="Similarity Threshold")
        similarity_threshold_label.pack(side=LEFT)

        
        similarity_threshold_value = StringVar()
        
        self.similarity_threshold_box = Entry(similarity_threshold_frame, textvariable=similarity_threshold_value, width=15)
        self.similarity_threshold_box.pack(side=LEFT)

        similarity_threshold_frame.pack(side=TOP)


        # random
        random_frame = Frame(self.right_frame, pady=10)

        self.random_button =  Button(random_frame, text="Toggle Random", width=15)
        self.random_button.pack(side=LEFT)

        self.random_label = Label(random_frame, text="Not random")
        self.random_label.pack(side=LEFT)

        random_frame.pack(side=TOP)


        # create empty ratio
        empty_ratio_frame = Frame(self.right_frame)

        empty_ratio_label = Label(empty_ratio_frame, text="Empty Ratio ")
        empty_ratio_label.pack(side=LEFT)


        empty_ratio_value = StringVar()
        self.empty_ratio_box = Entry(empty_ratio_frame, textvariable=empty_ratio_value, width=15)
        self.empty_ratio_box.pack(side=LEFT)

        empty_ratio_frame.pack(side=TOP)
        
        # create races
        races_frame = Frame(self.right_frame)

        self.races_ratio_boxes = []
        
        for i in range(5):
            race_frame = Frame(races_frame, pady=2)


            race_label_text = "Race " + chr(ord('A') + i) + " Ratio "
            race_label = Label(race_frame, text=race_label_text)
            race_label.pack(side=LEFT)
            
            races_value = StringVar()
            races_box = Entry(race_frame, textvariable=races_value, width=15)
            races_box.pack(side=LEFT)

            self.races_ratio_boxes.append(races_box)

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


    def configure_components(self):
        self.iteration_box.insert(0, self.number_iterations)

        self.population_height_box.insert(0, self.schelling.height)
        self.population_width_box.insert(0, self.schelling.width)

        self.neighbour_depth_box.insert(0, self.schelling.neighbour_depth)
    
        self.similarity_threshold_box.insert(0, self.schelling.similarity_threshold)

        self.empty_ratio_box.insert(0, self.schelling.empty_ratio)
        i = 0
        for x in self.races_ratio_boxes:
            self.races_ratio_boxes[i].insert(0, (1 - float(self.empty_ratio_box.get())) / 5)
            i = i + 1

        self.start_button.configure(command=self.run_graph)
        self.step_button.configure(command=self.run_round)

        self.load_button.configure(command=self.validate_and_update)

        self.random_button.configure(command=self.toggle_random_ratios)
        

    def run_graph(self):
        self.start_button.config(state="disabled")
        if self.number_iterations > 0:
            for i in range(self.number_iterations): 
                if self.run_round():
                    break
                self.simulation_status_label.config(text="Iteration " + str(i + 1))
        else:
            i = 0
            while True:
                if self.run_round():
                    break
                i = i + 1
                self.simulation_status_label.config(text="Iteration " + str(i + 1))
        self.start_button.config(state="normal")
            

    def run_round(self):
        result = self.schelling.run_round()
        self.schelling.update_plot()
        self.canvas.draw()

        return result
    

    def validate_and_update(self):
        if not self.random:
            if self.validate_parameters():
                if self.validate_ratios():
                    self.update()
                    self.simulation_status_label.config(text="Load Complete!")
                else:
                    threading.Thread(target=self.popupmsg, args=("The sum of the Empty Ratio and the Races' Ratios needs to be equal to 1!", )).start()
            else:
                threading.Thread(target=self.popupmsg, args=("There can't be no empty parameters!", )).start()
        else:
            self.generate_random_races_with_random_ratios()
            self.update()
            self.simulation_status_label.config(text="Load Complete!")
        return True


    def generate_random_races_with_random_ratios(self):
        number_races = random.randint(2,5)
        empty_ratio = round(random.uniform(0, 1), 2)
        self.empty_ratio_box.configure(state="normal")
        self.empty_ratio_box.delete(0, END)
        self.empty_ratio_box.insert(0, empty_ratio)
        self.empty_ratio_box.configure(state="disabled")
        ratio_total = empty_ratio
        j = 0
        for _ in range(number_races):
            if j == number_races - 1:
                race_ratio = round(1 - ratio_total, 2)
            else:
                race_ratio = round(random.uniform(0, 1 - ratio_total), 2)
            self.races_ratio_boxes[j].configure(state="normal")
            self.races_ratio_boxes[j].delete(0, END)
            self.races_ratio_boxes[j].insert(0, race_ratio)
            self.races_ratio_boxes[j].configure(state="disabled")
            ratio_total = ratio_total + race_ratio
            j = j + 1
        for i in range(j, 5):
            self.races_ratio_boxes[i].configure(state="normal")
            self.races_ratio_boxes[i].delete(0, END)
            self.races_ratio_boxes[i].insert(0, 0.0)
            self.races_ratio_boxes[i].configure(state="disabled")


    def popupmsg(self, msg):
        popup = Tk()
        popup.resizable(False, False)
        popup.wm_title("Invalid values!")
        label = Label(popup, text=msg)
        label.pack(side="top", fill="x", pady=10)
        B1 = Button(popup, text="Okay", command = popup.destroy)
        B1.pack(pady=10)
        popup.mainloop()


    def validate_parameters(self):
        if self.iteration_box.get() and self.population_height_box.get() and self.population_width_box.get() and self.similarity_threshold_box.get() and self.neighbour_depth_box.get():
            return True
        return False


    def validate_ratios(self):
        ratios = self.get_race_ratios()
        ratios_sum = 0
        for i in ratios:
            if not i:
                return
            ratios_sum += float(i)
        ratios_sum = round(ratios_sum, 3)
        if (ratios_sum + float(self.empty_ratio_box.get())) == 1.0:
            return True
        return False


    def update(self):
        self.number_iterations = int(self.iteration_box.get())

        self.schelling.model_configure(int(self.population_width_box.get()), int(self.population_height_box.get()), float(self.empty_ratio_box.get()), float(self.similarity_threshold_box.get()), int(self.neighbour_depth_box.get()), self.get_race_ratios())

        self.schelling.update_plot()

        self.canvas.get_tk_widget().pack_forget()

        self.draw_canvas()
       

    def get_race_ratios(self):
        return [float(x.get()) if x.get() else None for x in self.races_ratio_boxes] 


    def toggle_random_ratios(self):
        self.random = not self.random
        if self.random:
            self.random_label.config(text="Random")
            self.empty_ratio_box.configure(state="disabled")
            for x in self.races_ratio_boxes:
                x.configure(state="disabled")
        else:
            self.random_label.config(text="Not Random")
            self.empty_ratio_box.configure(state="normal")
            for x in self.races_ratio_boxes:
                x.configure(state="normal")


    def print_values(self):
        print(self.iteration_box.get())
        print(self.population_box.get())

        print(self.schelling.population)

        print(self.empty_ratio_box.get())
        for x in self.races_ratio_boxes:
            print(x.get())
        
        print(self.similarity_threshold_box.get())


    def _quit(self):
        self.quit()
        self.destroy()



app = Application()
app.minsize(1000, 700)
app.protocol("WM_DELETE_WINDOW", app._quit)
app.mainloop()