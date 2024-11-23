import tkinter as tk
from neurosity import NeurositySDK
from dotenv import load_dotenv
import os
import csv
import time
from datetime import datetime

# Load environment variables
load_dotenv()

class NeurosityDataCollector:
    def __init__(self):
        self.neurosity = NeurositySDK({
            "device_id": os.getenv("NEUROSITY_DEVICE_ID")
        })
        self.neurosity.login({
            "email": os.getenv("NEUROSITY_EMAIL"),
            "password": os.getenv("NEUROSITY_PASSWORD")
        })
        self.data = []
        self.session_active = False

    def start_session(self):
        """Starts data collection"""
        if not self.session_active:
            self.session_active = True
            self.data = []
            self.unsubscribe = self.neurosity.brainwaves_raw(self.collect_data)
            print("Data collection started.")

    def collect_data(self, data):
        """Collects incoming data into a list"""
        if self.session_active:
            self.data.append(data)

    def stop_session(self):
        """Stops data collection and saves to a CSV file"""
        if self.session_active:
            self.unsubscribe()  # Stop data collection
            self.session_active = False
            filename = f"Data_Collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["timestamp", "brainwave_data"])  # Adjust columns as needed
                for entry in self.data:
                    writer.writerow([entry['timestamp'], entry['value']])  # Adjust data keys as needed
            print(f"Data saved to {filename}")
            self.data = []  # Clear the data after saving

# Initialize data collector instance
data_collector = NeurosityDataCollector()

# Tkinter setup
root = tk.Tk()
root.title("Multi-Screen Display")
root.geometry("400x600")

# Main screen with a blue background
main_screen = tk.Frame(root, bg="#1d5899")
main_screen.pack(fill="both", expand=True)

# Function to open a new screen
def open_screen(bg_color="#1d5899", start_session=False):
    main_screen.pack_forget()
    screen = tk.Frame(root, bg=bg_color)
    screen.pack(fill="both", expand=True)

    back_button = tk.Button(screen, text="Back", command=lambda: show_main_screen(screen))
    back_button.place(relx=0.5, rely=0.1, anchor="n")

    if start_session:
        data_collector.start_session()

def show_main_screen(screen):
    screen.pack_forget()
    data_collector.stop_session()  # Stop session and save data
    main_screen.pack(fill="both", expand=True)

# Configure buttons for different screens
button_configs = [
    ("Current User/Guest", "#1d5899"),
    ("Start Session", "#1d5899", True),
    ("Progress", "#1d5899"),
    ("Feedback", "#1d5899"),
    ("Settings", "#1d5899"),
]

# Button setup
for idx, (text, color, *args) in enumerate(button_configs):
    start_session = args[0] if args else False
    button = tk.Button(main_screen, text=text, width=20, height=2,
                       command=lambda color=color, start_session=start_session: open_screen(color, start_session))
    button.pack(pady=10)

# Add "Exit" button
exit_button = tk.Button(main_screen, text="Exit", width=20, height=2, command=root.quit)
exit_button.pack(pady=20)

# Run the application
root.mainloop()
