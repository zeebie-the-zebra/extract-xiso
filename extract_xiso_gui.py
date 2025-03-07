#!/usr/bin/env python3
import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading


class ExtractXisoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Extract-XISO GUI")
        self.root.geometry("600x400")
        self.root.resizable(True, True)

        # Variables
        self.input_folder_var = tk.StringVar()
        self.output_file_var = tk.StringVar()
        self.extract_xiso_path = tk.StringVar(value=os.path.join(os.getcwd(), "extract-xiso"))  # Set relative path based on current working directory
        self.status_var = tk.StringVar(value="Ready")
        self.is_running = False

        # Create the GUI layout
        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Extract-XISO path
        ttk.Label(main_frame, text="Extract-XISO Path:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.extract_xiso_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_extract_xiso).grid(row=0, column=2, padx=5, pady=5)

        # Input folder selection
        ttk.Label(main_frame, text="Input Folder:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_folder_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_input_folder).grid(row=1, column=2, padx=5, pady=5)

        # Output ISO file selection
        ttk.Label(main_frame, text="Output ISO File:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_file_var, width=50).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_output_file).grid(row=2, column=2, padx=5, pady=5)

        # Run button
        run_button = ttk.Button(main_frame, text="Create ISO", command=self.run_extract_xiso)
        run_button.grid(row=3, column=0, columnspan=3, pady=20)

        # Status bar
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT, padx=5)
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT, padx=5)

        # Output console
        console_frame = ttk.LabelFrame(main_frame, text="Output")
        console_frame.grid(row=4, column=0, columnspan=3, sticky=tk.NSEW, pady=10)
        main_frame.grid_rowconfigure(4, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        self.console = tk.Text(console_frame, height=10, width=70, wrap=tk.WORD)
        self.console.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar for console
        scrollbar = ttk.Scrollbar(self.console, command=self.console.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.console.config(yscrollcommand=scrollbar.set)
        
        # Make the console read-only
        self.console.config(state=tk.DISABLED)

    def browse_extract_xiso(self):
        file_path = filedialog.askopenfilename(
            title="Select extract-xiso executable",
            filetypes=[("All files", "*.*")]
        )
        if file_path:
            self.extract_xiso_path.set(file_path)

    def browse_input_folder(self):
        folder_path = filedialog.askdirectory(title="Select Input Folder")
        if folder_path:
            self.input_folder_var.set(folder_path)
            # Suggest a default output filename based on the input folder name
            folder_name = os.path.basename(folder_path)
            if folder_name and not self.output_file_var.get():
                self.output_file_var.set(f"{folder_name}.iso")

    def browse_output_file(self):
        file_path = filedialog.asksaveasfilename(
            title="Select Output ISO File",
            defaultextension=".iso",
            filetypes=[("ISO files", "*.iso"), ("All files", "*.*")]
        )
        if file_path:
            self.output_file_var.set(file_path)

    def update_console(self, text):
        """Update the console with the given text."""
        self.console.config(state=tk.NORMAL)
        self.console.insert(tk.END, f"{text}\n")
        self.console.see(tk.END)  # Scroll to the end
        self.console.config(state=tk.DISABLED)

    def run_extract_xiso(self):
        # Get the input values
        input_folder = self.input_folder_var.get().strip()
        output_file = self.output_file_var.get().strip()
        extract_xiso_path = self.extract_xiso_path.get().strip()

        # Validate inputs
        if not input_folder:
            messagebox.showerror("Error", "Please select an input folder.")
            return

        if not output_file:
            messagebox.showerror("Error", "Please specify an output ISO file.")
            return

        if not extract_xiso_path:
            messagebox.showerror("Error", "Please specify the path to extract-xiso.")
            return

        # Check if the input folder exists
        if not os.path.isdir(input_folder):
            messagebox.showerror("Error", f"Input folder '{input_folder}' does not exist.")
            return

        # Prevent running multiple operations simultaneously
        if self.is_running:
            messagebox.showinfo("Info", "A process is already running. Please wait.")
            return

        # Start the operation in a separate thread to avoid freezing the GUI
        self.is_running = True
        self.status_var.set("Running...")
        
        self.update_console(f"Starting extract-xiso to create ISO from: {input_folder}")
        self.update_console(f"Output will be saved to: {output_file}")
        
        thread = threading.Thread(target=self.run_extract_xiso_thread, 
                                 args=(extract_xiso_path, input_folder, output_file))
        thread.daemon = True
        thread.start()

    def run_extract_xiso_thread(self, extract_xiso_path, input_folder, output_file):
        try:
            # Construct the command
            command = [extract_xiso_path, "-c", input_folder]
            
            # If the output file is not in the current directory, cd to the right directory first
            output_dir = os.path.dirname(output_file)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                current_dir = os.getcwd()
                os.chdir(output_dir)
                
                # Update the command to use the relative folder path if needed
                input_folder_abs = os.path.abspath(input_folder)
                command = [extract_xiso_path, "-c", input_folder_abs]
                
                # Set the output file name without path (extract-xiso will create it in the current directory)
                output_basename = os.path.basename(output_file)
                if output_basename != os.path.basename(input_folder) + ".iso":
                    # If a different name is specified, we need to rename after creation
                    default_output = os.path.basename(input_folder) + ".iso"
                    need_rename = True
                else:
                    need_rename = False
            else:
                need_rename = False
                
            self.update_console(f"Executing command: {' '.join(command)}")
            
            # Run the command
            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Read and display the output
            for line in process.stdout:
                self.root.after(0, self.update_console, line.strip())
            
            # Wait for the process to complete
            process.wait()
            
            # Check if we need to rename the output
            if need_rename:
                default_output = os.path.basename(input_folder) + ".iso"
                output_basename = os.path.basename(output_file)
                if os.path.exists(default_output):
                    self.update_console(f"Renaming {default_output} to {output_basename}")
                    os.rename(default_output, output_basename)
            
            # Change back to the original directory if we changed it
            if output_dir:
                os.chdir(current_dir)
            
            # Check the return code
            if process.returncode == 0:
                self.root.after(0, lambda: self.status_var.set("Completed successfully"))
                self.root.after(0, lambda: messagebox.showinfo("Success", "ISO file created successfully."))
                self.update_console("ISO file created successfully.")
            else:
                self.root.after(0, lambda: self.status_var.set("Failed"))
                self.root.after(0, lambda: messagebox.showerror("Error", f"extract-xiso failed with return code {process.returncode}"))
                self.update_console(f"extract-xiso failed with return code {process.returncode}")
                
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set("Error"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.update_console(f"Error: {str(e)}")
        finally:
            self.is_running = False


if __name__ == "__main__":
    root = tk.Tk()
    app = ExtractXisoGUI(root)
    root.mainloop()

