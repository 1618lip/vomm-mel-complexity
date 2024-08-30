import os
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import shutil

def analyze_song():
    txt_file = txt_file_entry.get()
    mxl_file = mxl_file_entry.get()
    D = d_entry.get()
    W = w_entry.get()

    if not txt_file or not mxl_file or not D or not W:
        messagebox.showerror("Input Error", "Please provide all inputs.")
        return

    mxl_basename = os.path.basename(mxl_file)
    mxl_name, mxl_ext = os.path.splitext(mxl_basename)

    directory_name = mxl_name
    directory_path = os.path.join("examples", directory_name)

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # Define the new paths for the files in the examples/ directory
    new_txt_file = os.path.join(directory_path, f"{mxl_name}" + ".txt")
    new_mxl_file = os.path.join(directory_path, mxl_basename)

    try:
        # Copy the files to the new directory with the new names
        shutil.copy(txt_file, new_txt_file)
        shutil.copy(mxl_file, new_mxl_file)

        # Run the analysis commands using the new file names

        parsechord_command = f'src\\chord_parser.exe {new_txt_file}'
        midi_command = f'python src\\midi_rep.py {new_mxl_file}'
        sliding_window_command = f'python src\\sliding_window.py {D} {W} {os.path.join(directory_path, mxl_name)}_MIDI_representation.txt'
        
        # print(parsechord_command)
        # print(midi_command)
        # print(sliding_window_command)
        subprocess.run(parsechord_command, shell=True, check=True)
        subprocess.run(midi_command, shell=True, check=True)
        subprocess.run(sliding_window_command, shell=True, check=True)
        
        messagebox.showinfo("Running...", "Song analysis completed successfully.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    except FileNotFoundError as e:
        messagebox.showerror("Error", f"File not found: {e}")

def select_txt_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        txt_file_entry.delete(0, tk.END)
        txt_file_entry.insert(0, file_path)

def select_mxl_file():
    file_path = filedialog.askopenfilename(filetypes=[("MusicXML files", "*.mxl")])
    if file_path:
        mxl_file_entry.delete(0, tk.END)
        mxl_file_entry.insert(0, file_path)

# Create the main window
root = tk.Tk()
root.title("Song Analyzer")

# Create and place widgets
tk.Label(root, text="Select .txt File:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
txt_file_entry = tk.Entry(root, width=40)
txt_file_entry.grid(row=0, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=select_txt_file).grid(row=0, column=2, padx=10, pady=5)

tk.Label(root, text="Select .mxl File:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
mxl_file_entry = tk.Entry(root, width=40)
mxl_file_entry.grid(row=1, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=select_mxl_file).grid(row=1, column=2, padx=10, pady=5)

tk.Label(root, text="Context size (D):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
d_entry = tk.Entry(root, width=10)
d_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

tk.Label(root, text="Beats in context (W):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
w_entry = tk.Entry(root, width=10)
w_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")

tk.Button(root, text="Analyze", command=analyze_song).grid(row=4, column=1, padx=10, pady=20)

# Run the main loop
root.mainloop()


