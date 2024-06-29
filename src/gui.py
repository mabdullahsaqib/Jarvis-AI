import tkinter as tk

def show_gui():
    root = tk.Tk()
    root.title("Voice Assistant")
    root.geometry("400x200")
    root.configure(bg="black")

    # Create four colored bars
    bars = [tk.Frame(root, width=50, height=200, bg=color) for color in ["red", "yellow", "green", "blue"]]
    for i, bar in enumerate(bars):
        bar.place(x=i*100, y=0)

    root.after(3000, root.destroy)  # Automatically close the GUI after 3 seconds
    root.mainloop()
