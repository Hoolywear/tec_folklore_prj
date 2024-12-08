from PIL import Image
from PIL.ImageOps import fit


def image_resize(open_path, save_path, width, height):
    try:
        with Image.open(open_path) as img:
            img = fit(img, (width, height))
            img.save(save_path)
    except OSError as e:
        print(f"Errore durante l'apertura dell'immagine! {e}")
