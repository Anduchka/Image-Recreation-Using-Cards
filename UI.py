import tkinter as tk
from tkinter import messagebox, filedialog
import threading

import Main

stop_event = threading.Event()

def start():
    def chooseFile():
        path = filedialog.askopenfilename(
            title="Select target image",
            filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")])
        if path:
            target_path_def.set(path)
    
    def onRun():
        if not target_path_def.get():
            messagebox.showerror("Error", "Select target image")
            return
        
        try:
            loops = int(loops_def.get())
            generations_per_loop = int(generations_per_loop_def.get())
            image_simplification = int(image_simplification_def.get())
            weight_color = int(weight_color_def.get()) / 100.0
            weight_ssim = int(weight_ssim_def.get()) / 100.0
        except ValueError:
            messagebox.showerror("Error", "All values must be integers")
            return
        
        stop_event.clear()
        run_button.config(state="disabled")
        stop_button.config(state="normal")
        progress_def.set("Running...")
        
        t = threading.Thread(target=runEvolution, args=(loops, generations_per_loop, image_simplification, weight_color, weight_ssim, target_path_def.get()))
        t.daemon = True
        t.start()
    
    def onStop():
        stop_event.set()
        run_button.config(state="normal")
        stop_button.config(state="disabled")
    
    def runEvolution(loops, generations_per_loop, image_simplification, weight_color, weight_ssim, target_path):
        current_fitness = 0.0
        
        def progressCallback(loop, generation, best_fitness):
            nonlocal current_fitness
            
            if best_fitness != -1:
                current_fitness = best_fitness
            
            def updateLabel():
                progress_def.set("Loop: " + str(loop) + " | Generation: " + str(generation) + " | Fitness: " + str(current_fitness))
            
            root.after(0, updateLabel)
        
        try:
            Main.runEvolution(
                loops=loops,
                generations_per_loop=generations_per_loop,
                image_simplification=image_simplification,
                weight_color=weight_color,
                weight_ssim=weight_ssim,
                target_path=target_path,
                progress_callback=progressCallback,
                stop_event=stop_event)
        except Exception as e:
            msg = str(e)
            root.after(0, lambda: messagebox.showerror("Error", msg))
        finally:
            root.after(0, lambda: run_button.config(state="normal"))
            stop_button.config(state="disabled")
            
    def onClose():
        stop_event.set()
        root.destroy()
    
    root = tk.Tk()
    root.title("Card Evolution")
    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", onClose)
    
    loops_def = tk.StringVar(value=str(Main.MAX_LOOP_COUNT))
    generations_per_loop_def = tk.StringVar(value=str(Main.GENERATIONS_PER_LOOP))
    image_simplification_def = tk.StringVar(value=str(Main.IMAGE_SIMPLIFICATION))
    target_path_def = tk.StringVar(value=str(Main.TARGET_PATH))
    weight_ssim_def = tk.StringVar(value=str(int(Main.WEIGHT_SSIM * 100)))
    weight_color_def = tk.StringVar(value=str(int(Main.WEIGHT_COLOR * 100)))
    progress_def = tk.StringVar(value="None")
    
    row = 0
    tk.Label(root, text="Target image:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
    tk.Entry(root, textvariable=target_path_def, width=10).grid(row=row, column=1, padx=5, pady=5)
    tk.Button(root, text="Browse...", command=chooseFile).grid(row=row, column=2, padx=5, pady=5)
    
    row+=1
    tk.Label(root, text="Loop count:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
    tk.Entry(root, textvariable=loops_def, width=10).grid(row=row, column=1, padx=5, pady=5)
    
    row += 1
    tk.Label(root, text="Generations per loop:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
    tk.Entry(root, textvariable=generations_per_loop_def, width=10).grid(row=row, column=1, padx=5, pady=5)
    
    row += 1
    tk.Label(root, text="Simplification ammount:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
    tk.Entry(root, textvariable=image_simplification_def, width=10).grid(row=row, column=1, padx=5, pady=5)
    
    row += 1
    tk.Label(root, text="Color weight:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
    tk.Entry(root, textvariable=weight_color_def, width=10).grid(row=row, column=1, padx=5, pady=5)
    tk.Label(root, text="%").grid(row=row, column=1, sticky="e", padx=5, pady=5)
    
    row += 1
    tk.Label(root, text="SSIM weight:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
    tk.Entry(root, textvariable=weight_ssim_def, width=10).grid(row=row, column=1, padx=5, pady=5)
    tk.Label(root, text="%").grid(row=row, column=1, sticky="e", padx=5, pady=5)
    
    row+=1
    run_button = tk.Button(root, text="Run simulation", command=onRun)
    run_button.grid(row=row, column=0, columnspan=3, pady=10)
    
    row+=1
    stop_button = tk.Button(root, text="Stop simulation", command=onStop)
    stop_button.grid(row=row, column=0, columnspan=3, pady=10)
    stop_button.config(state="disabled")
    
    row+=1
    tk.Label(root, textvariable=progress_def).grid(row=row, column=0, columnspan=3, pady=5)
    
    root.mainloop()
    
if __name__ == "__main__":
    start()