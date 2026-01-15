# UI module for Image Recreation Using Cards
# Provides the Tkinter interface to select input images, set parameters,
# start/stop the evolution loop, and display progress/previews.

import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import threading
import Main

stop_event = threading.Event()

def start():
    def chooseFile(): #choosing target image
        path = filedialog.askopenfilename(
            title="Select target image",
            filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")])
        if path:
            target_path_var.set(path)
    
    def makeLetterboxed(pil: Image.Image, box_w: int, box_h: int) -> Image.Image: #placing/resizing progress image 
        pil = pil.convert("RGB")
        
        img = pil.copy()
        img.thumbnail((box_w, box_h), Image.Resampling.LANCZOS)
        
        bg = Image.new("RGB", (box_w, box_h), (255, 255, 255))
        x = (box_w - img.width) // 2
        y = (box_h - img.height) // 2
        
        bg.paste(img, (x, y))
        
        return bg
    
    def setPreviewImage(path: str | None): #setting image preview
        nonlocal _preview_photo_ref
        
        if not path:
            preview_label.config(image="", text="No image was generated")
            _preview_photo_ref = None
            return
        
        pil = Image.open(path)
        pil = makeLetterboxed(pil, PREVIEW_W, PREVIEW_H)
        
        _preview_photo_ref = ImageTk.PhotoImage(pil)
        preview_label.config(image=_preview_photo_ref, text="")
    
    def changeSSIMPower(*args): #on value change for ssim power
        weight_ssim = 0
        
        try:
            weight_ssim = int(weight_ssim_var.get())
        except ValueError:
            pass
        
        weight_color = max(0, min(100 - weight_ssim, 100))
        
        weight_color_var.set(weight_color)
        
    def changeColorPower(*args): #on value change for color power
        weight_color = 0
        
        try:
            weight_color = int(weight_color_var.get())
        except ValueError:
            pass
        
        weight_ssim = max(0, min(100 - weight_color, 100))
        
        weight_ssim_var.set(weight_ssim)
    
    def onRun(): #start of recreation thread
        if not target_path_var.get():
            messagebox.showerror("Error", "Select target image")
            return
        
        try: #get values from input fields
            loops = int(loops_var.get())
            generations_per_loop = int(generations_per_loop_var.get())
            image_simplification = int(image_simplification_var.get())
            use_color = use_color_var.get()
            weight_color = int(weight_color_var.get()) / 100.0
            use_ssim = use_ssim_var.get()
            weight_ssim = int(weight_ssim_var.get()) / 100.0
        except ValueError:
            messagebox.showerror("Error", "All values must be integers")
            return
        
        if use_color and not use_ssim:
            weight_color = 1
        elif use_ssim and not use_color:
            weight_ssim = 1
        
        stop_event.clear() #configure buttons and progress bar
        run_button.config(state="disabled")
        stop_button.config(state="normal")
        progress_var.set("Running...")
        setPreviewImage(None)
        
        t = threading.Thread(target=runEvolution,
                             args=(loops, generations_per_loop, image_simplification, use_color, weight_color,
                                   use_ssim, weight_ssim, target_path_var.get()))
        t.daemon = True
        t.start() #thread start
    
    def onStop(): #stoping generation
        stop_event.set()
        run_button.config(state="normal")
        stop_button.config(state="disabled")
    
    def runEvolution(loops, generations_per_loop, image_simplification, use_color, weight_color, use_ssim, weight_ssim, target_path):
        current_fitness = 0.0
        
        def progressCallback(loop, generation, best_fitness, path=None): #callback to get loop/generation/fitness/progress
            nonlocal current_fitness
            
            if best_fitness != -1:
                current_fitness = best_fitness
            
            def updateUI():
                progress_var.set("Loop: " + str(loop) + " | Generation: " + str(generation) + " | Fitness: " + f"{current_fitness:.5f}")
                
                if path is not None:
                    setPreviewImage(path) #setting preview image
                
            root.after(0, updateUI)
        
        try: #running main evolution with curent values
            Main.runEvolution(
                loops=loops,
                generations_per_loop=generations_per_loop,
                image_simplification=image_simplification,
                use_color=use_color,
                weight_color=weight_color,
                use_ssim=use_ssim,
                weight_ssim=weight_ssim,
                target_path=target_path,
                progress_callback=progressCallback,
                stop_event=stop_event)
        except Exception as e:
            msg = str(e)
            root.after(0, lambda: messagebox.showerror("Error", msg))
        finally:#configure after finish
            root.after(0, lambda: run_button.config(state="normal"))
            stop_button.config(state="disabled")
            
    def onClose():
        stop_event.set()
        root.destroy()
    
    #preiew values
    PREVIEW_W = 480
    PREVIEW_H = 480
    _preview_photo_ref = None 
    
    #window setup
    root = tk.Tk()
    root.title("Card Evolution")
    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", onClose)
    img = tk.PhotoImage(file="icon.png")
    root.iconphoto(True, img) 
    
    #seperation of window to left and right
    root.grid_columnconfigure(0, weight=0)
    root.grid_columnconfigure(1, weight=0)
    
    left = tk.Frame(root)
    left.grid(row=0, column=0, sticky="n", padx=10, pady=10)
    
    right = tk.Frame(root, bg="white")
    right.grid(row=0, column=1, sticky="n", padx=(0, 10), pady=10)
    
    #variables of input fields
    loops_var = tk.StringVar(value=str(Main.MAX_LOOP_COUNT))
    generations_per_loop_var = tk.StringVar(value=str(Main.GENERATIONS_PER_LOOP))
    image_simplification_var = tk.StringVar(value=str(Main.IMAGE_SIMPLIFICATION))
    target_path_var = tk.StringVar(value=str(Main.TARGET_PATH))
    use_ssim_var = tk.BooleanVar(value=Main.USE_SSIM)
    weight_ssim_var = tk.StringVar(value=str(int(Main.WEIGHT_SSIM * 100)))
    use_color_var = tk.BooleanVar(value=Main.USE_COLOR)
    weight_color_var = tk.StringVar(value=str(int(Main.WEIGHT_COLOR * 100)))
    progress_var = tk.StringVar(value="None")
    
    #window layout
    row = 0
    tk.Label(left, text="Target image:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
    tk.Entry(left, textvariable=target_path_var, width=10).grid(row=row, column=1, padx=5, pady=5)
    tk.Button(left, text="Browse...", command=chooseFile).grid(row=row, column=2, padx=5, pady=5)
    
    row+=1
    tk.Label(left, text="Loop count:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
    tk.Entry(left, textvariable=loops_var, width=10).grid(row=row, column=1, padx=5, pady=5)
    
    row += 1
    tk.Label(left, text="Generations per loop:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
    tk.Entry(left, textvariable=generations_per_loop_var, width=10).grid(row=row, column=1, padx=5, pady=5)
    
    row += 1
    tk.Label(left, text="Simplification ammount:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
    tk.Entry(left, textvariable=image_simplification_var, width=10).grid(row=row, column=1, padx=5, pady=5)
    
    row += 1
    tk.Label(left, text="Use color:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
    tk.Checkbutton(left, variable=use_color_var).grid(row=row, column=1, sticky="w", pady=5)
    
    row += 1
    tk.Label(left, text="Color weight:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
    tk.Entry(left, textvariable=weight_color_var, width=10).grid(row=row, column=1, padx=5, pady=5)
    tk.Label(left, text="%").grid(row=row, column=1, sticky="e", padx=5, pady=5)
    weight_color_var.trace_add("write", changeColorPower)
    
    row += 1
    tk.Label(left, text="Use SSIM:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
    tk.Checkbutton(left, variable=use_ssim_var).grid(row=row, column=1, sticky="w", pady=5)
    
    row += 1
    tk.Label(left, text="SSIM weight:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
    tk.Entry(left, textvariable=weight_ssim_var, width=10).grid(row=row, column=1, padx=5, pady=5)
    tk.Label(left, text="%").grid(row=row, column=1, sticky="e", padx=5, pady=5)
    weight_ssim_var.trace_add("write", changeSSIMPower)
    
    row+=1
    run_button = tk.Button(left, text="Run simulation", command=onRun)
    run_button.grid(row=row, column=0, columnspan=3, pady=10)
    
    row+=1
    stop_button = tk.Button(left, text="Stop simulation", command=onStop)
    stop_button.grid(row=row, column=0, columnspan=3, pady=10)
    stop_button.config(state="disabled")
    
    row+=1
    tk.Label(left, textvariable=progress_var).grid(row=row, column=0, columnspan=3, pady=5)
    
    preview_box = tk.Frame(right, width=PREVIEW_W, height=PREVIEW_H, bg="white")
    preview_box.pack()
    preview_box.pack_propagate(False)
    
    preview_label = tk.Label(preview_box, text="No image was generated", bg="white")
    preview_label.pack(fill="both", expand=True)

    root.mainloop()
    
if __name__ == "__main__":
    start()