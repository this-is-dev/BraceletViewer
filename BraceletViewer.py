import os
import pickle
import tkinter as tk
from tkinter import *
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk
from pathlib import Path

base_directory = Path(__file__).parent

saveFile = "saved_data.pickle"
data_dump = {"initial_y": 0, "overlay_increment": 0, "y_coordinate": 0, "user_file_path": "", "overlay_file_path": ""}


## Handle Loading
if os.path.exists(saveFile):
    with open('saved_data.pickle', 'rb') as f:
        data_dump = pickle.load(f)
    initial_y = data_dump["initial_y"]
    y_coordinate = data_dump["y_coordinate"]
    overlay_increment = data_dump["overlay_increment"]
    user_file_path = data_dump["user_file_path"]
    overlay_file_path = data_dump["overlay_file_path"]
else:
    initial_y = 238 #e33: 238 Phai: 197
    overlay_increment = 93.7
    y_coordinate = initial_y
    user_file_path = askopenfilename(
        title="Select the bracelet file",
        filetypes=(
            ("Image files", "*.jpg;*.jpeg;*.png;*.gif;*.bmp"),
            ("All files", "*.*")
        )
    )
    overlay_file_path = os.getcwd() + "/overlays/overlay-yellow.png"

x_coordinate = 0

root = tk.Tk()
root.title('Bracelet Viewer')
root.configure(bg="grey")
root.geometry("1280x1000")



# Open the background image
pil_background = Image.open(user_file_path)
img_width = pil_background.width
img_height = pil_background.height
background_img = ImageTk.PhotoImage(pil_background)

# Open the image to overlay
overlay_img = ImageTk.PhotoImage(Image.open(overlay_file_path)) # This image should have an alpha channel

# Stores all persistent data to the data_dump file and saves it
def saveData():
    global initial_y, overlay_increment, y_coordinate, user_file_path, overlay_file_path, data_dump
    data_dump["initial_y"] = initial_y
    data_dump["overlay_increment"] = overlay_increment
    data_dump["y_coordinate"] = y_coordinate
    data_dump["user_file_path"] = user_file_path
    data_dump["overlay_file_path"] = overlay_file_path
    with open(saveFile, 'wb') as f:
        pickle.dump(data_dump, f)

# Configures the scrollbar
def onConfigure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

# Update the bracelet image on the canvas
def selectImage():
    global background_label, background_img, user_file_path, pil_background, canvas, img_width, img_height, scrollbar, overlay_img, x_coordinate, y_coordinate

    user_file_path = askopenfilename(
        title="Select the bracelet file",
        filetypes=(
            ("Image files", "*.jpg;*.jpeg;*.png;*.gif;*.bmp"),
            ("All files", "*.*")
        )
    )

    canvas.delete("bracelet")
    canvas.delete("overlay")

    pil_background = Image.open(user_file_path)
    background_img = ImageTk.PhotoImage(pil_background)
    img_width = pil_background.width
    img_height = pil_background.height

    canvas.create_image(0,0, image=background_img, anchor=tk.NW, tags="bracelet")
    canvas.create_image(x_coordinate, y_coordinate, image=overlay_img, anchor=tk.NW, tags="overlay")
    canvas.background = background_img
    canvas.overlay = overlay_img

    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.config(command=canvas.yview)
    canvas.configure(scrollregion=canvas.bbox("all"))

    saveData()

# Handles key presses (Specifically the bound Up key and Down key)
def onKeyEvent(event):
    updateOverlay(event.keysym)

# Handles scroll wheel events (Allows us to scroll through the longer images)
def onMouseWheel(event):
    if event.num == 5 or event.delta < 0:
        canvas.yview_scroll(1, "units")
    elif event.num == 4 or event.delta > 0:
        canvas.yview_scroll(-1, "units")

# Update overlay position when moved up or down using the buttons on screen or the key presses
def updateOverlay(direction):
    global background_img, pil_background, canvas, overlay_img, x_coordinate, y_coordinate
    canvas.delete("overlay")
    if direction == "Up":
        y_coordinate = y_coordinate - overlay_increment
    if direction == "Down":
        y_coordinate = y_coordinate + overlay_increment
    canvas.create_image(x_coordinate, y_coordinate, image=overlay_img, anchor=tk.NW, tags="overlay")

    canvas.overlay = overlay_img

    saveData()

# Set the overlay back to it's initial position at the top row
def resetOverlay(event):
    global canvas, overlay_img, x_coordinate, y_coordinate
    canvas.delete("overlay")
    y_coordinate = initial_y
    canvas.create_image(x_coordinate, y_coordinate, image=overlay_img, anchor=tk.NW, tags="overlay")

    canvas.overlay = overlay_img

    saveData()

# Prompts user to swap their overlay image
def swapOverlay():
    global canvas, overlay_img, x_coordinate, y_coordinate, overlay_file_path
    canvas.delete("overlay")
    overlay_file_path = askopenfilename(
        title="Select the bracelet file",
        initialdir= f"{base_directory}\overlays",
        filetypes=(
            ("Image files", "*.jpg;*.jpeg;*.png;*.gif;*.bmp"),
            ("All files", "*.*")
        )
    )
    overlay_img = ImageTk.PhotoImage(Image.open(overlay_file_path))
    canvas.create_image(x_coordinate, y_coordinate, image=overlay_img, anchor=tk.NW, tags="overlay")

    saveData()

# Updates the increment amount based on the entry field
def updateIncrement():
    global overlay_increment
    user_input = increment_entry.get()
    try:
        overlay_increment = float(user_input)
    except ValueError:
        print("ERR: Increment amount tried to be set to something that's not number")
        return
    saveData()

# Updates the initial position of the overlay
def updateInitialPosition():
    global initial_y
    user_input = initialPosition_entry.get()
    try:
        initial_y = float(user_input)
    except ValueError:
        print("ERR: Initial position tried to be set to something that's not number")
        return
    saveData()

# Setup button column
button_frame = tk.Frame(root)
button_frame.pack(side="left", padx=10)

initialPosition_frame = tk.Frame(button_frame)
increment_frame = tk.Frame(button_frame)
arrow_frame = tk.Frame(button_frame)

# Setup input fields
tk.Label(button_frame, text="Initial position:").pack()
initialPosition_entry = tk.Entry(initialPosition_frame, width=10)
button_initialPosition = Button(initialPosition_frame, text=">>", command=lambda: updateInitialPosition())
initialPosition_frame.pack(pady=10)
initialPosition_entry.pack(side=LEFT)
initialPosition_entry.insert(0, str(initial_y))
button_initialPosition.pack(side=LEFT, padx=5)

tk.Label(button_frame, text="Increment amount:").pack()
increment_entry = tk.Entry(increment_frame, width=10)
button_increment = Button(increment_frame, text=">>", command=lambda: updateIncrement())
increment_frame.pack(pady=10)
increment_entry.pack(side=LEFT)
increment_entry.insert(0, str(overlay_increment))
button_increment.pack(side=LEFT, padx=5)


# Setup buttons
button_selectImage = Button(button_frame, text="Change Image", command=lambda: selectImage())
button_toggleColor = Button(button_frame, text="Swap Overlay", command=lambda: swapOverlay())
button_exit = Button(button_frame, text="Close", command=root.quit)
button_up = Button(arrow_frame, text="↑", command=lambda: updateOverlay("Up"))
button_reset = Button(arrow_frame, text="Reset", command=lambda: resetOverlay(None))
button_down = Button(arrow_frame, text="↓", command=lambda: updateOverlay("Down"))

button_selectImage.pack(pady=10)
button_toggleColor.pack(pady=10)

arrow_frame.pack(pady=10)
button_up.pack(side=LEFT)
button_reset.pack(side=LEFT, padx=5)
button_down.pack(side=LEFT)

button_exit.pack(pady=10)

# Setup Container
container = tk.Frame(root)
container.pack(fill="both", expand=True)
container.configure(bg="gray")

canvas = tk.Canvas(container)
scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set, bg="gray")

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

canvas.create_image(0,0, image=background_img, anchor=tk.NW, tags="bracelet")
canvas.create_image(x_coordinate,y_coordinate, image=overlay_img, anchor=tk.NW, tags="overlay")

canvas.background = background_img
canvas.overlay = overlay_img

# Setup scrollbar
scrollbar = tk.Scrollbar(canvas, orient=tk.VERTICAL)
scrollbar.config(command=canvas.yview)

saveData()

# Canvas binding and configuration events
canvas.bind_all("<MouseWheel>", onMouseWheel)
canvas.bind_all("<Button-4>", onMouseWheel) # Scroll up on Linux
canvas.bind_all("<Button-5>", onMouseWheel) # Scroll down on Linux
canvas.bind('<Configure>', onConfigure)

# Key binding
root.focus_force()
root.bind('<Up>', onKeyEvent)
root.bind("<Key-Down>", onKeyEvent)
root.bind("<space>", resetOverlay)

# Start the application
root.mainloop()