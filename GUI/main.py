from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk

root = Tk()
root.title("Scotland Yard Agents in London")
root.geometry("1200x1000")

content = ttk.Frame(root)
content.pack(fill=BOTH, expand=True)

# Load and resize the image
img = Image.open('./map.png')
img = img.resize((1100, 900), Image.Resampling.LANCZOS)  # Resize to fit window
imgobj = ImageTk.PhotoImage(img)

# Create label with resized image
image = ttk.Label(content, image=imgobj)
image.image = imgobj  # Keep a reference to prevent garbage collection
image.pack()




root.mainloop()