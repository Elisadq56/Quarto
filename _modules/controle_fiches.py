"""
Contrôler une liste de fiches (dictionnaires) avant de les afficher.

Module réutilisable : il ne connaît ni Grist ni le projet, seulement un
« schéma » qu'on lui fournit, c'est-à-dire la liste des champs attendus et
leurs règles.

Ce qui est vérifié
------------------
1. Publication : si un champ de publication est indiqué, les fiches où il est
   faux sont mises de côté (sans être signalées comme des erreurs).
2. Champs : pour chaque champ du schéma,
   - obligatoire (toujours, ou seulement dans certains cas) -> sinon fiche écartée ;
   - type attendu (entier, texte…)                         -> sinon fiche écartée ;
   - valeurs autorisées (liste fermée)                      -> sinon simple avertissement.
3. Rattachement (facultatif) : quand une fiche peut être rattachée à une
   autre fiche de la même liste (champ « parent »), on vérifie qu'elle ne
   pointe pas vers elle-même, que le parent existe, qu'il est retenu, et
   qu'il n'est pas lui-même rattaché (un seul niveau).

Utilisation type
----------------
    schema = [
        Champ("Titre", obligatoire=True, type_attendu=str),
        Champ("Plus_value", obligatoire=lambda fiche: fiche["Est_carte"]),
        Champ("Type_demandeur", valeurs_autorisees=["Collectivité", "Autre"]),
    ]
    resultat = controler_fiches(fiches, schema, champ_publication="Publie")
    resultat.retenues     # fiches à afficher
    print(resultat.rapport())
"""

from dataclasses import dataclass, field, replace
from typing import Any, Callable, Optional, Union


@dataclass
class Champ:
    """Règles d'un champ.

    obligatoire : True, False, ou une fonction qui reçoit la fiche et renvoie
                  True quand le champ est obligatoire pour cette fiche-là
                  (ex. : lambda fiche: fiche["Est_carte"]).
    type_attendu : type Python (int, str, list…) ou tuple de types, ou None.
    valeurs_autorisees : liste des valeurs admises, ou None. Pour un champ
                  liste (ex. Liste de choix Grist), chaque élément est vérifié.
    """
    nom: str
    obligatoire: Union[bool, Callable[[dict], bool]] = False
    type_attendu: Any = None
    valeurs_autorisees: Optional[list] = None


@dataclass
class Anomalie:
    id_fiche: Any
    titre: str
    message: str
    bloquante: bool  # True : la fiche est écartée ; False : simple avertissement


@dataclass
class ResultatControle:
    lues: int
    non_publiees: int
    retenues: list = field(default_factory=list)
    anomalies: list = field(default_factory=list)

    @property
    def ecartees(self):
        return self.lues - self.non_publiees - len(self.retenues)

    def rapport(self):
        """Texte lisible résumant le contrôle, une ligne par anomalie."""
        lignes = [
            f"Contrôle des fiches : {self.lues} lue(s), {self.non_publiees} non publiée(s), "
            f"{len(self.retenues)} retenue(s), {self.ecartees} écartée(s)."
        ]
        for anomalie in self.anomalies:
            symbole = "✗ ÉCARTÉE" if anomalie.bloquante else "⚠ avertissement"
            lignes.append(f"  {symbole} — fiche #{anomalie.id_fiche} « {anomalie.titre} » : "
                          f"{anomalie.message}")
        if not self.anomalies:
            lignes.append("  Aucune anomalie.")
        return "\n".join(lignes)


def est_vide(valeur):
    """Vrai pour None, texte vide ou fait d'espaces, liste vide."""
    if valeur is None:
        return True
    if isinstance(valeur, str):
        return not valeur.strip()
    if isinstance(valeur, (list, tuple, dict)):
        return len(valeur) == 0
    return False


def ajouter_valeurs_autorisees(schema, choix):
    """
    Renvoie une copie du schéma où les valeurs autorisées sont complétées à
    partir d'un dictionnaire {nom_du_champ: [valeurs]} (ex. listes de choix
    lues dans Grist). Les champs absents du dictionnaire sont inchangés.
    """
    return [replace(champ, valeurs_autorisees=choix[champ.nom]) if champ.nom in choix else champ
            for champ in schema]


def controler_fiches(fiches, schema, champ_publication=None, champ_titre="Titre",
                     champ_parent=None):
    """
    Contrôle les fiches selon le schéma et renvoie un ResultatControle.

    fiches : liste de dictionnaires, chacun avec une clé "id".
    schema : liste d'objets Champ.
    champ_publication : nom du champ vrai/faux indiquant si la fiche est publiée.
    champ_titre : champ utilisé pour nommer la fiche dans le rapport.
    champ_parent : nom du champ contenant l'id d'une autre fiche (rattachement).
    """
    resultat = ResultatControle(lues=len(fiches), non_publiees=0)

    def signaler(fiche, message, bloquante=True):
        titre = fiche.get(champ_titre) or "(sans titre)"
        resultat.anomalies.append(Anomalie(fiche.get("id"), titre, message, bloquante))

    # 1. Publication
    publiees = []
    for fiche in fiches:
        if champ_publication and not fiche.get(champ_publication):
            resultat.non_publiees += 1
        else:
            publiees.append(fiche)

    # 2. Règles de chaque champ
    valides = []
    for fiche in publiees:
        ok = True
        for champ in schema:
            valeur = fiche.get(champ.nom)
            obligatoire = champ.obligatoire(fiche) if callable(champ.obligatoire) else champ.obligatoire

            if est_vide(valeur):
                if obligatoire:
                    signaler(fiche, f"champ « {champ.nom} » vide alors qu'il est obligatoire.")
                    ok = False
                continue  # champ vide et facultatif : rien d'autre à vérifier

            if champ.type_attendu and not isinstance(valeur, champ.type_attendu):
                signaler(fiche, f"champ « {champ.nom} » : type inattendu ({type(valeur).__name__}).")
                ok = False
                continue

            if champ.valeurs_autorisees is not None:
                elements = valeur if isinstance(valeur, list) else [valeur]
                inconnues = [v for v in elements if v not in champ.valeurs_autorisees]
                if inconnues:
                    signaler(fiche, f"champ « {champ.nom} » : valeur(s) non prévue(s) {inconnues}.",
                             bloquante=False)
        if ok:
            valides.append(fiche)

    # 3. Rattachements
    if champ_parent:
        valides = _controler_rattachements(fiches, valides, champ_parent, signaler)

    resultat.retenues = valides
    return resultat


def _controler_rattachements(toutes, valides, champ_parent, signaler):
    """Écarte les fiches dont le rattachement est incohérent (voir docstring du module)."""
    toutes_par_id = {fiche["id"]: fiche for fiche in toutes}
    ids_valides = {fiche["id"] for fiche in valides}

    retenues = []
    for fiche in valides:
        parent_id = fiche.get(champ_parent)
        if est_vide(parent_id):
            retenues.append(fiche)  # fiche principale : rien à vérifier
            continue

        parent = toutes_par_id.get(parent_id)
        if parent_id == fiche["id"]:
            signaler(fiche, "rattachée à elle-même.")
        elif parent is None:
            signaler(fiche, f"rattachée à la fiche #{parent_id}, qui n'existe pas.")
        elif not est_vide(parent.get(champ_parent)):
            signaler(fiche, f"rattachée à la fiche #{parent_id}, qui est elle-même rattachée "
                            f"à une autre (un seul niveau autorisé).")
        elif parent_id not in ids_valides:
            signaler(fiche, f"rattachée à la fiche #{parent_id}, qui n'est pas affichée "
                            f"(non publiée ou écartée).")
        else:
            retenues.append(fiche)
    return retenues
