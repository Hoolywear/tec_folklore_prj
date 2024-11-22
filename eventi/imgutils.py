# image renaming utilities usate all'importazione di thumbnails per Eventi e Luoghi

import os


def save_rename_luogo_img(instance, filename):
    old_ext = os.path.splitext(filename)[1]
    os.rename(filename, 'luogo_thumb_' + str(instance.pk) + old_ext)
    return os.path.join('thumbnails/luoghi', filename)


def save_rename_evento_img(instance, filename):
    old_ext = os.path.splitext(filename)[1]
    return os.path.join('thumbnails/eventi', 'evento_thumb_' + str(instance.pk) + old_ext)
