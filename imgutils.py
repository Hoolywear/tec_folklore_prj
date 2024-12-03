from PIL import Image


def image_resize(path, width, height):
    try:
        with Image.open(path) as img:
            img.thumbnail((width, height))
            img.save(path)
    except OSError as e:
        print(f"Errore durante l'apertura dell'immagine! {e}")
