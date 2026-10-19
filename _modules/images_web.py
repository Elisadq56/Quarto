"""
Préparer des images pour le web : format WebP, taille raisonnable.

Module réutilisable. C'est le seul module de `_modules/` qui a besoin d'une
bibliothèque externe : Pillow (`pip install Pillow`). Sans Pillow, il ne
plante pas : il renvoie l'image d'origine, et PILLOW_DISPONIBLE vaut False
pour que l'appelant puisse le signaler.

Pourquoi WebP ? Pour une capture de carte, un PNG pèse souvent 5 à 10 fois
plus qu'un WebP de qualité 80, sans différence visible à l'écran.

Utilisation type
----------------
    from _modules.images_web import optimiser_image
    chemin_web = optimiser_image("brut/carte.png", "images/web")
    # -> images/web/carte.webp
"""

import shutil
from pathlib import Path

try:
    from PIL import Image
    PILLOW_DISPONIBLE = True
except ImportError:
    PILLOW_DISPONIBLE = False

COTE_MAX = 1600   # pixels sur le plus grand côté : assez pour lire une carte agrandie au clic
QUALITE = 80      # 0 à 100 ; 80 est un bon compromis poids / netteté


def optimiser_image(source, dossier_sortie, cote_max=COTE_MAX, qualite=QUALITE):
    """
    Crée dans `dossier_sortie` une version web de l'image `source` et renvoie son chemin.

    - convertit en WebP (la transparence éventuelle est conservée) ;
    - réduit l'image si son plus grand côté dépasse `cote_max` (jamais d'agrandissement) ;
    - ne refait rien si la version web existe déjà et est plus récente que la source.

    Sans Pillow, l'image d'origine est simplement copiée dans `dossier_sortie`.
    """
    source = Path(source)
    dossier_sortie = Path(dossier_sortie)
    dossier_sortie.mkdir(parents=True, exist_ok=True)

    if not PILLOW_DISPONIBLE:
        copie = dossier_sortie / source.name
        if not copie.exists():
            shutil.copy2(source, copie)
        return copie

    sortie = dossier_sortie / f"{source.stem}.webp"
    if sortie.exists() and sortie.stat().st_mtime >= source.stat().st_mtime:
        return sortie  # déjà à jour

    with Image.open(source) as image:
        # WebP gère RGB et RGBA ; les autres modes (palette, niveaux de gris…) sont convertis
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA" if "transparency" in image.info else "RGB")
        image.thumbnail((cote_max, cote_max), Image.Resampling.LANCZOS)  # réduit en gardant les proportions
        image.save(sortie, format="WEBP", quality=qualite, method=6)     # method=6 : compression la plus poussée
    return sortie
