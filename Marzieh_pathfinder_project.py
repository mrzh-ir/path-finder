from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from queue import PriorityQueue
from collections import deque
import random
import time
import os
from PIL import Image, ImageTk

root = Tk()
root.title('Pathfinder')
root.maxsize(900, 900)
root.config(bg='#e3decf')

font = ("Helvetica", 11)

WIDTH = 600
HEIGHT = 600
ROWS = 25
COLS = 25
grid = []

node_frame = Frame(root, bg = '#b5e8e8') 
node_frame.grid(row = 0, column = 0, padx = 10, pady = 5)

canvas = Canvas(root, width = WIDTH, height = HEIGHT, bg = 'white')
canvas.grid(row = 0, column = 1, padx = 10, pady = 5)

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

class Node:
    def __init__(self, row, column, width, total_rows):
        
        self.parent = None
        self.neighbors = []
        self.Gcost = float('inf')
        self.heuristic = 0
        self.Fcost = float('inf')
        self.source = False
        self.destination = False
        self.barrier = False
        self.clicked = False
        self.total_rows = total_rows
        self.photo = ''

        self.button = Button(canvas,
                             command = lambda a = row, b = column: self.click(a, b),
                             bg = 'white', bd = 2, relief = RIDGE
                             )

        self.row = row
        self.col = column
        self.width = width

        self.button.place(x = row * width, y = column * width,
                          width = width, height = width)


    source = None
    destination = None

    def set_as_source(self):
        self.button.config(bg = "#b147cc")     
        image = Image.open(os.path.join(__location__, r'icons\placeholder.png'))
        resize_image = image.resize((20, 20))
        self.photo = ImageTk.PhotoImage(resize_image)
        self.button.config(image = self.photo)
        self.source = True
        self.clicked = True
        Node.source = (self.col, self.row)

    def set_as_destination(self):
        self.button.config(bg = "#28de2b")     
        image = Image.open(os.path.join(__location__, r'icons\flag_FILL0_wght400_GRAD0_opsz48.png'))
        resize_image = image.resize((20, 20))
        self.photo = ImageTk.PhotoImage(resize_image)
        self.button.config(image = self.photo)
        self.destination = True
        self.clicked = True
        Node.destination = (self.col, self.row)

    def set_as_barrier(self):
        self.button.config(bg = "black")
        self.barrier = True
        self.clicked = True

    def reset(self):
        self.button.config(bg = "white", image = '')
           
        self.clicked = False

    def set_path(self):
        self.button.config(bg = "#f29b29")    

    def unexplored(self):
        self.button.config(bg = "#9dcbf2")   

    def explored(self):
        self.button.config(bg = "#b0aca2")    

    def disable(self):
        self.button.config(state = DISABLED)

    def enable(self):
        self.button.config(state = NORMAL)

    def click(self, row, col):
        if self.clicked == False:
            if not Node.source:
                self.set_as_source()
            elif not Node.destination:
                self.set_as_destination()
            else:
                self.set_as_barrier()
        else:
            self.reset()
            if self.source == True:
                self.source = False
                Node.source = None
            elif self.destination == True:
                self.destination = False
                Node.destination = None
            else:
                self.barrier = False

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row > 0 and not grid[self.row - 1][self.col].barrier:
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col > 0 and not grid[self.row][self.col - 1].barrier:
            self.neighbors.append(grid[self.row][self.col - 1])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].barrier:
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].barrier:
            self.neighbors.append(grid[self.row + 1][self.col])

#-------------------------------------------------------------------------------------------------------------------
def create_grid(width, rows):
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return grid

# heuristic function : Manhatten distance
def heuristic(a, b):
    return abs(a.row - b.row) + abs(a.col - b.col)


def reconstruct_path(node, tickTime):
    current = node
    while current.source == False:
        parent = current.parent
        parent.set_path()
        root.update_idletasks()
        time.sleep(tickTime)
        current = parent


def Reset():
    global grid
    Node.source = None
    Node.destination = None
    for row in grid:
        for node in row:
            node.reset()
            node.neighbors = []
            node.Gcost = float('inf')
            node.heuristic = 0
            node.Fcost = float('inf')
            node.parent = None
            node.source = False
            node.destination = False
            node.barrier = False
            node.enable()

# ----------------------------------------------------------------------
def a_star(grid, tickTime):
    count = 0
    source = grid[Node.source[1]][Node.source[0]]
    destination = grid[Node.destination[1]][Node.destination[0]]
    open_set = PriorityQueue()
    open_set.put((0, count, source))
    source.Gcost = 0
    source.Fcost = heuristic(source, destination)
    open_set_hash = {source}

    while not open_set.empty():
        current = open_set.get()[2]
        open_set_hash.remove(current)
        if current == destination:
            reconstruct_path(destination, tickTime)
            destination.set_as_destination()
            source.set_as_source()
            for child in node_frame.winfo_children():
                child.configure(state='normal')
            return True
        for neighbor in current.neighbors:
            temp_g_score = current.Gcost + 1
            if temp_g_score < neighbor.Gcost:
                neighbor.parent = current
                neighbor.Gcost = temp_g_score
                neighbor.Fcost = temp_g_score + heuristic(neighbor, destination)

                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((neighbor.Fcost, count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.unexplored()

        root.update_idletasks()
        time.sleep(tickTime)

        if current != source:
            current.explored()

    messagebox.showinfo("No Solution", "There was no solution")

    return False

def dijkstra_search(grid, tickTime):

    count = 0
    source = grid[Node.source[1]][Node.source[0]]
    destination = grid[Node.destination[1]][Node.destination[0]]
    open_set = PriorityQueue()
    open_set.put((0, count, source))
    source.Gcost = 0
    source.Fcost = 0
    open_set_hash = {source}
    while not open_set.empty():
        current = open_set.get()[2]        
        open_set_hash.remove(current)
        if current == destination:
            reconstruct_path(destination, tickTime)
            destination.set_as_destination()
            source.set_as_source()
            for child in node_frame.winfo_children():
                child.configure(state='normal')
            return True
        for neighbor in current.neighbors:
            temp_g_score = current.Gcost + 1
            if temp_g_score < neighbor.Gcost:
                neighbor.parent = current
                neighbor.Gcost = temp_g_score
                neighbor.Fcost = temp_g_score + 0
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((neighbor.Fcost, count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.unexplored()
        root.update_idletasks()
        time.sleep(tickTime)
        if current != source:
            current.explored()
    messagebox.showinfo("No Solution", "There was no solution")

    return False
def bfs(grid, tickTime):
    source = grid[Node.source[1]][Node.source[0]]
    destination = grid[Node.destination[1]][Node.destination[0]]
    queue = deque()
    queue.append(source)
    visited = {source}
    while queue:
        current = queue.popleft()
        if current == destination:
            reconstruct_path(destination, tickTime)
            destination.set_as_destination()
            source.set_as_source()
            return
        for neighbor in current.neighbors:
            if neighbor not in visited:
                neighbor.parent = current
                visited.add(neighbor)
                queue.append(neighbor)
                neighbor.unexplored()
        root.update_idletasks()
        time.sleep(tickTime)
        if current != source:
            current.explored()
    messagebox.showinfo("No Solution", "There was no solution")
    return False

def start_algorithm():
    global grid
    if not grid:
        return
    if not Node.source or not Node.destination:
        messagebox.showinfo("No source/destination", "Place sourceing and destination points")
        return
    for row in grid:
        for node in row:
            node.neighbors = []
            node.Gcost = float('inf')
            node.heuristic = 0
            node.Fcost = float('inf')
            node.parent = None
            node.update_neighbors(grid)
            if node.clicked == False:
                node.reset()
            node.disable()  
    for child in node_frame.winfo_children():
        child.configure(state='disable')
    if algorithm_menu.get() == 'A-star':
        a_star(grid, delay_scale.get())         
    elif algorithm_menu.get() == 'Breadth-First-Search':
        bfs(grid, delay_scale.get())
    elif algorithm_menu.get() == 'Dijkstra':
        dijkstra_search(grid, delay_scale.get())
    else:
        messagebox.showinfo("No algorithm", "Select algorithm")
    for row in grid:
        for node in row:
            node.enable()

    for child in node_frame.winfo_children():
        child.configure(state='normal')  

def random_walls():
    global grid
    if not grid:
        return

    for row in grid:
        for node in row:
            node.disable() 

    for child in node_frame.winfo_children():
        child.configure(state='disable')

    if not Node.source:
        current = grid[random.randint(
            0, ROWS - 1)][random.randint(0, COLS - 1)]
        if current.destination == False:
            current.set_as_source()

    if not Node.destination:
        current = grid[random.randint(
            0, ROWS - 1)][random.randint(0, COLS - 1)]
        if current.source == False:
            current.set_as_destination()

    source = grid[Node.source[1]][Node.source[0]]
    destination = grid[Node.destination[1]][Node.destination[0]]

    for row in grid:
        for node in row:
            if node != source and node != destination:
                node.reset()
                node.barrier = False
                node.clicked = False
                if random.randint(0, 100) < 10:  # assumed 10 for density of obstacles
                    node.set_as_barrier()

    root.update_idletasks()

    for row in grid:
        for node in row:
            node.enable()

    for child in node_frame.winfo_children():
        child.configure(state='normal')  
#----------------------------------------------------------------------------------------------
sel_algorithm = StringVar()
text_var = StringVar()
label = Label(node_frame, textvariable = text_var, bg = "#b5e8e8", font = font)

text_var.set("First click on the grid is Start Node \n"
"Second click is End Node \n" 
"Third click and after are barriers \n"
"Or you can generate random walls")

label.grid(padx = 5, pady = (10, 20))

Button(node_frame, text = 'generate random walls', command = random_walls, font = font,
       bg = '#71f5c7').grid(row = 2, column = 0, padx = 5, pady = (10, 20))

algorithm_menu = ttk.Combobox(node_frame, textvariable = sel_algorithm,
                              values = ['select algorithm','A-star', 'Breadth-First-Search', 'Dijkstra'], font = font)
algorithm_menu.grid(row = 3, column = 0, padx = 5, pady = (20, 5))
algorithm_menu.current(0)
delay_scale = Scale(node_frame, from_= 0.1, to = 1, digits = 2, resolution = 0.05,
                    orient = HORIZONTAL, label = 'Delay', font = font, length = 180, cursor='fleur')
delay_scale.grid(row = 4, column = 0, padx = 5, pady = (5, 5))
Button(node_frame, text = 'Start Searching', command = start_algorithm, font = ('Helvetica 10 bold'),
       bg = '#f0a692').grid(row = 5, column = 0, padx = 5, pady = (10, 10))

Button(node_frame, text = 'Reset', command = Reset, font = ('Helvetica 10'),
       bg = 'gold').grid(row = 6, column = 0, padx = 5, pady = (10, 10))

Button(node_frame, text = 'EXIT', command = root.destroy, font = ('Helvetica 10'),
       bg = 'white').grid(row = 7, column = 0, padx = 5, pady = (10, 10))

grid = create_grid(WIDTH, ROWS)

root.mainloop()
