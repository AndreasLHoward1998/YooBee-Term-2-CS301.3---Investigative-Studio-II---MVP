import tkinter as tk

# Function to open a new screen with a specific background color
def open_screen(bg_color="#1d5899"):
    # Hide the main screen buttons
    main_screen.pack_forget()
    
    # Create a new frame for the selected screen
    screen = tk.Frame(root, bg=bg_color)
    screen.pack(fill="both", expand=True)
    
    # Back button to return to the main menu
    back_button = tk.Button(screen, text="Back", command=lambda: show_main_screen(screen))
    back_button.place(relx=0.5, rely=0.1, anchor="n")
    
    # Black rectangle below the "Back" button
    canvas = tk.Canvas(screen, width=200, height=100, bg="black", highlightthickness=0)
    canvas.place(relx=0.5, rely=0.25, anchor="n")

# Function to return to the main menu
def show_main_screen(screen):
    screen.pack_forget()  # Hide the current screen
    main_screen.pack(fill="both", expand=True)  # Show the main screen

# Set up the main application window
root = tk.Tk()
root.title("Multi-Screen Display")
root.geometry("400x600")

# Create the main screen with a blue background
main_screen = tk.Frame(root, bg="#1d5899")
main_screen.pack(fill="both", expand=True)

# Button configurations for different screens
button_configs = [
    ("Current User/Guest", "#1d5899"),
    ("Start Session", "#1d5899"),
    ("Progress", "#1d5899"),
    ("Feedback", "#1d5899"),
    ("Settings", "#1d5899"),
]

# Standard size for all main screen buttons
button_width = 20
button_height = 2

# Create buttons for each screen
for idx, (text, color) in enumerate(button_configs):
    button = tk.Button(main_screen, text=text, width=button_width, height=button_height, command=lambda color=color: open_screen(color))
    button.pack(pady=10)

# Add an "Exit" button below the five main buttons, with the same size
exit_button = tk.Button(main_screen, text="Exit", width=button_width, height=button_height, command=root.quit)
exit_button.pack(pady=20)

# Start the main loop
root.mainloop()
