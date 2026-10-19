"""
Transformer des fiches (dictionnaires) en contenu Quarto : cartes ou pages de détail.

Module réutilisable : il ne connaît pas le contenu des fiches, seulement un
« modèle » qui dit quel champ afficher dans quelle zone.

Deux usages possibles
---------------------
1. Galerie de cartes complètes sur une seule page : generer_galerie().
   Le Markdown produit s'affiche depuis une cellule Python `output: asis` :

       ```{python}
       #| output: asis
       print(generer_galerie(fiches, modele))
       ```

2. Une page .qmd par fiche : generer_page_detail(). Les pages sont écrites
   dans un dossier, et une page « galerie » les liste avec un listing Quarto
   (vignettes image + titre qui mènent à chaque page). Voir cas_usage_otv.py.

Les textes des fiches sont du Markdown : **gras**, *italique* et
[liens](https://...) sont interprétés.

Le style est dans galerie_cartes.scss, à ajouter au thème dans _quarto.yml.

Zones affichées (de haut en bas)
--------------------------------
    ┌───────────────────────────────┐
    │ image (facultative)           │
    │ Titre (carte uniquement ;     │
    │   sur une page, c'est le titre│
    │   de la page)                 │
    │ [pastille] [pastille]         │
    │ Introduction (contexte)       │
    │ « citation »                  │
    │ Bloc (libellé + texte)        │
    │ Bloc mis en avant (encadré)   │
    │ pied : libellé : a · b · c    │
    └───────────────────────────────┘
"""

import json
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Bloc:
    """Un paragraphe titré. mis_en_avant=True l'affiche dans un encadré coloré."""
    libelle: str
    champ: str
    mis_en_avant: bool = False


@dataclass
class ModeleCarte:
    """Correspondance entre les zones et les champs des fiches.

    titre       : champ du titre (obligatoire).
    pastilles   : champs affichés en pastilles ; un champ liste donne une pastille par élément.
    introduction: champ affiché en paragraphe d'introduction, sans libellé (contexte).
    citation    : champ affiché en citation.
    blocs       : liste de Bloc, dans l'ordre d'affichage.
    image       : champ contenant le chemin d'une image (ou une liste de chemins : seule la
                  première est utilisée).
    pied        : champ contenant une liste de textes courts, affichés en bas.
    pied_libelle: texte placé devant cette liste.
    """
    titre: str
    pastilles: list = field(default_factory=list)
    introduction: Optional[str] = None
    citation: Optional[str] = None
    blocs: list = field(default_factory=list)
    image: Optional[str] = None
    pied: Optional[str] = None
    pied_libelle: str = ""


# ---------------------------------------------------------------------------
# Outils
# ---------------------------------------------------------------------------

def _vide(valeur):
    return valeur is None or valeur == "" or valeur == [] or (isinstance(valeur, str) and not valeur.strip())


def _en_liste(valeur):
    """Renvoie toujours une liste : [] si vide, [valeur] si valeur simple."""
    if _vide(valeur):
        return []
    return list(valeur) if isinstance(valeur, (list, tuple)) else [valeur]


def premiere_image(fiche, modele):
    """Chemin de l'image de la fiche (avec des / même sous Windows), ou None."""
    images = _en_liste(fiche.get(modele.image)) if modele.image else []
    return str(images[0]).replace("\\", "/") if images else None


# ---------------------------------------------------------------------------
# Zones
# ---------------------------------------------------------------------------

def _markdown_image(chemin, texte_alternatif, classe="carte-image"):
    alt = str(texte_alternatif).replace('"', "'")
    return f'![]({chemin}){{.{classe} fig-alt="{alt}"}}'


def generer_zones(fiche, modele, avec_titre=True, avec_image=True):
    """
    Renvoie la liste des morceaux de Markdown (un par zone), dans l'ordre d'affichage.
    avec_titre / avec_image permettent de les omettre quand la page les affiche déjà.
    """
    morceaux = []

    image = premiere_image(fiche, modele)
    if avec_image and image:
        morceaux.append(_markdown_image(image, fiche.get(modele.titre, "")))

    if avec_titre:
        morceaux.append(f"### {fiche.get(modele.titre, '(sans titre)')} {{#carte-{fiche.get('id', '')}}}")

    pastilles = [f"[{p}]{{.carte-pastille}}"
                 for champ in modele.pastilles for p in _en_liste(fiche.get(champ))]
    if pastilles:
        morceaux.append(" ".join(pastilles))

    if modele.introduction and not _vide(fiche.get(modele.introduction)):
        morceaux.append(f"::: {{.carte-introduction}}\n{str(fiche[modele.introduction]).strip()}\n:::")

    if modele.citation and not _vide(fiche.get(modele.citation)):
        # Chaque ligne de la citation doit commencer par « > »
        lignes = str(fiche[modele.citation]).strip().splitlines()
        morceaux.append("\n".join(f"> {ligne}" for ligne in lignes))

    for bloc in modele.blocs:
        texte = fiche.get(bloc.champ)
        if _vide(texte):
            continue
        classes = ".carte-bloc .carte-bloc-accent" if bloc.mis_en_avant else ".carte-bloc"
        morceaux.append(f"::: {{{classes}}}\n"
                        f"[{bloc.libelle}]{{.carte-bloc-titre}}\n\n"
                        f"{str(texte).strip()}\n"
                        f":::")

    elements_pied = _en_liste(fiche.get(modele.pied)) if modele.pied else []
    if elements_pied:
        morceaux.append(f"::: {{.carte-pied}}\n"
                        f"**{modele.pied_libelle}** {' · '.join(map(str, elements_pied))}\n"
                        f":::")
    return morceaux


# ---------------------------------------------------------------------------
# Usage 1 : galerie de cartes complètes sur une page
# ---------------------------------------------------------------------------

def generer_carte(fiche, modele):
    """Renvoie le Markdown d'une carte complète (toutes les zones)."""
    contenu = "\n\n".join(generer_zones(fiche, modele))
    return f":::: {{.g-col-12 .g-col-md-6 .carte-galerie}}\n{contenu}\n::::"


def generer_galerie(fiches, modele):
    """Renvoie le Markdown de la galerie complète (grille responsive : 2 colonnes, 1 sur mobile)."""
    if not fiches:
        return "*Aucun élément à afficher pour le moment.*"
    cartes = "\n\n".join(generer_carte(fiche, modele) for fiche in fiches)
    return f"::::: {{.grid .galerie-cartes}}\n\n{cartes}\n\n:::::\n"


# ---------------------------------------------------------------------------
# Usage 2 : une page .qmd par fiche
# ---------------------------------------------------------------------------

def _yaml(valeur):
    """Écrit une valeur en YAML sûr (le JSON est du YAML valide ; gère guillemets et accents)."""
    return json.dumps(valeur, ensure_ascii=False)


def generer_page_detail(fiche, modele, entete=None, lien_retour=None):
    """
    Renvoie le contenu complet d'un fichier .qmd présentant une fiche.

    entete      : dictionnaire d'options YAML supplémentaires (ex. {"lang": "fr",
                  "categories": [...]}) ; titre et image sont ajoutés automatiquement.
    lien_retour : couple (texte, cible), ex. ("← Tous les cas d'usage", "../Cas_usage.qmd").

    L'image est déclarée dans l'en-tête (champ `image`) : c'est elle qu'un listing
    Quarto affiche en vignette. Elle est aussi affichée en haut de la page.
    """
    options = {"title": fiche.get(modele.titre, "(sans titre)")}
    image = premiere_image(fiche, modele)
    if image:
        options["image"] = image
    options.update(entete or {})

    lignes_entete = "\n".join(f"{cle}: {_yaml(valeur)}" for cle, valeur in options.items())
    corps = "\n\n".join(generer_zones(fiche, modele, avec_titre=False))
    retour = f"\n\n[{lien_retour[0]}]({lien_retour[1]}){{.fiche-retour}}" if lien_retour else ""

    return (f"---\n{lignes_entete}\n---\n\n"
            f"<!-- Page générée automatiquement : ne pas modifier à la main. -->\n\n"
            f":::: {{.fiche-detail}}\n{corps}\n::::{retour}\n")
