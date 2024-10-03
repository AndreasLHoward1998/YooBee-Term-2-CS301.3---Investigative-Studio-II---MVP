import pandas as pd
import numpy as np
import mne
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk

def preprocess_eeg_data(file_path):
    df = pd.read_csv(file_path)
    # Drop columns if they exist
    columns_to_drop = ['TimeStamp (ms)', 'Test Label:Stimulus']
    existing_columns_to_drop = [col for col in columns_to_drop if col in df.columns]
    if existing_columns_to_drop:
        df.drop(columns=existing_columns_to_drop, inplace=True)
    data = df.values.T
    info = mne.create_info(ch_names=df.columns.tolist(), sfreq=256, ch_types='eeg')
    raw = mne.io.RawArray(data, info)
    raw.filter(l_freq=1, h_freq=40)
    return raw.get_data().T

def prepare_data(data, time_steps=10):
    X, y = [], []
    for i in range(len(data) - time_steps):
        X.append(data[i:(i + time_steps)])
        y.append(data[i + time_steps])
    return np.array(X), np.array(y)

def create_model(input_shape, output_shape):
    model = Sequential([
        Input(shape=input_shape),
        LSTM(64, return_sequences=True),
        LSTM(32, return_sequences=False),
        Dense(output_shape)
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

def main(file_path):
    data = preprocess_eeg_data(file_path)
    X, y = prepare_data(data)
    model = create_model((X.shape[1], X.shape[2]), y.shape[1])
    model.fit(X, y, epochs=10, batch_size=32, validation_split=0.2)
    predictions = model.predict(X)
    
    # Adjust this list based on the actual number of columns in predictions
    column_names = [
        'EEG Channel Value: CP3', 'EEG Channel Value: C3', 'EEG Channel Value: F5',
        'EEG Channel Value: PO3', 'EEG Channel Value: PO4', 'EEG Channel Value: F6',
        'EEG Channel Value: C4', 'EEG Channel Value: CP4', 'EEG Channel 9', 'EEG Channel 10', 'EEG Channel 11'
    ]
    predicted_df = pd.DataFrame(predictions, columns=column_names[:predictions.shape[1]])
    return predicted_df

def update_display(predicted_df, root):
    concentration = np.mean(predicted_df[['EEG Channel Value: F5', 'EEG Channel Value: F6']])
    if concentration > 0.5:
        text_color = 'blue'
        bg_color = 'lightgreen'
    else:
        text_color = 'red'
        bg_color = 'lightpink'

    text_widget.config(fg=text_color, bg=bg_color)
    root.after(1000, lambda: update_display(predicted_df, root))

def display_interface(predicted_df):
    root = tk.Tk()
    root.title("Educational Material Display")

    global text_widget
    text_widget = tk.Text(root, font=("Helvetica", 16), wrap="word")
    text_widget.pack(expand=1, fill="both")
    text_widget.insert("1.0", "This is the educational material to be displayed...")

    update_display(predicted_df, root)
    root.mainloop()

# Execute the workflow
file_path = 'Prototype Dataset 1.csv'
predicted_df = main(file_path)
display_interface(predicted_df)
