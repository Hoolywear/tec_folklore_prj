# image renaming utilities usate all'importazione di banner per Prenotazioni

import os


def save_rename_promo_banner(instance, filename):
    # recupero l'estensione del file
    old_ext = os.path.splitext(filename)[1]
    os.rename(filename, 'promo_banner_' + str(instance.pk) + old_ext)
    return os.path.join('promozioni/', filename)
