import pandas as pd
import numpy as np
import tkinter as tk
import random

# Load EEG data
def load_eeg_data(file_path):
    # Assume the data has columns: 'timestamp', 'alpha', 'beta', 'gamma', etc.
    return pd.read_csv(file_path)

# Preprocessing function
def preprocess_eeg_data(data):
    # Normalization: scale EEG signals between 0 and 1
    normalized_data = (data - data.min()) / (data.max() - data.min())
    
    # Drop unnecessary columns, if any
    cleaned_data = normalized_data.drop(columns=['timestamp'])  # Assuming 'timestamp' is not needed
    
    return cleaned_data

class AdaptiveUI:
    def __init__(self, root, eeg_data):
        self.root = root
        self.root.title("Adaptive Learning Interface")
        self.root.geometry("600x400")
        self.eeg_data = eeg_data
        self.current_row = 0
        
        # UI elements
        self.label = tk.Label(self.root, text="Focus Level", font=("Arial", 20))
        self.label.pack(pady=20)
        
        self.text = tk.Text(self.root, height=10, width=40)
        self.text.insert(tk.END, "Here is some educational content...\nStay focused!")
        self.text.pack(pady=20)
        
        self.update_button = tk.Button(self.root, text="Next EEG Data", command=self.update_ui)
        self.update_button.pack(pady=10)

    def update_ui(self):
        # Simulate reading the next row of EEG data
        if self.current_row < len(self.eeg_data):
            focus_level = self.eeg_data.iloc[self.current_row]['alpha']  # Assume 'alpha' is the focus signal
            self.current_row += 1
        else:
            focus_level = random.uniform(0, 1)  # Fallback if no more data
        
        # Change background color based on focus level
        if focus_level > 0.7:
            self.root.config(bg="green")
            self.label.config(text="Focus Level: High", bg="green")
        elif 0.4 < focus_level <= 0.7:
            self.root.config(bg="yellow")
            self.label.config(text="Focus Level: Medium", bg="yellow")
        else:
            self.root.config(bg="red")
            self.label.config(text="Focus Level: Low", bg="red")

if __name__ == "__main__":
    # Load your EEG data
    file_path = 'data/processed_eeg_data.csv'  # Replace with the actual path to your file
    eeg_data = preprocess_eeg_data(load_eeg_data(file_path))

    # Start the adaptive UI
    root = tk.Tk()
    app = AdaptiveUI(root, eeg_data)
    root.mainloop()
