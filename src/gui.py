import tkinter as tk


class VoiceAssistantGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("JARVIS")
        self.root.geometry("400x200")
        self.root.configure(bg="black")

        # Create four colored bars
        self.bars = [tk.Frame(self.root, width=50, height=200, bg=color) for color in ["red", "yellow", "green", "blue"]]
        for i, bar in enumerate(self.bars):
            bar.place(x=i*100, y=0)

        self.is_listening = False
        self.is_speaking = False

    def show(self):
        self.root.deiconify()
        self.animate()

    def hide(self):
        self.root.withdraw()

    def animate(self):
        if self.is_listening:
            self.animate_listening()
        elif self.is_speaking:
            self.animate_speaking()
        self.root.after(100, self.animate)

    def animate_listening(self):
        for bar in self.bars:
            for width in range(50, 100, 10):
                bar.config(width=width)
                self.root.update_idletasks()
                self.root.update()
            for width in range(100, 50, -10):
                bar.config(width=width)
                self.root.update_idletasks()
                self.root.update()

    def animate_speaking(self):
        for bar in self.bars:
            for height in range(200, 100, -10):
                bar.config(height=height)
                self.root.update_idletasks()
                self.root.update()
            for height in range(100, 200, 10):
                bar.config(height=height)
                self.root.update_idletasks()
                self.root.update()

    def set_listening(self):
        self.is_listening = True
        self.is_speaking = False

    def set_speaking(self):
        self.is_listening = False
        self.is_speaking = True

    def stop_animation(self):
        self.is_listening = False
        self.is_speaking = False

    def run(self):
        self.root.mainloop()


# Global instance of the GUI
voice_assistant_gui = VoiceAssistantGUI()
