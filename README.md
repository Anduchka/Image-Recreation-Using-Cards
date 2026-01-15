# Image Recreation Using Cards

Recreates images by layering playing card sprites and improving the result over generations using an evolutionary / genetic style search.
The fitness score is based on pixel color difference and SSIM (Structural Similarity).

<img width="2560" height="1707" alt="temp_save535" src="https://github.com/user-attachments/assets/5ee72ff1-5de5-4200-8db3-e88ac03b5588" />
[video(8).webm](https://github.com/user-attachments/assets/5257885d-0263-40cf-bf3d-906fa61ae2e7)

## How it works
1. Start with a blank canvas.
2. Create many cards with random position/rotation/scale/tint.
3. Score each card + existing canvas against the target image (color metric + SSIM).
4. Keep the best candidates and generate new variations.
5. Repeat for several generations and get 1 best candidate.
6. Repeat all of the generation loop for n times or untill fitness stopes improving

## Features
- Evolves a card collage to approximate an input image
- Adjustable parameters in a simple UI
- Exports results to image files

## Requirements
- Python 3.9+

### Python packages
- Pillow (`PIL`) — image loading/processing + UI image preview
- numpy — pixel array operations
- scikit-image — SSIM (`skimage.metrics.structural_similarity`)

### Standard library
- tkinter — UI (`tkinter`, `messagebox`, `filedialog`)
- threading — background worker thread
- random — randomness utilities

