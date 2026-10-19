"""
Lire une table Grist depuis Python, pour l'utiliser dans une page Quarto.

Module réutilisable : il ne dépend que de la bibliothèque standard.

Utilisation type
----------------
    from _modules.grist_connexion import ConnexionGrist, lire_table_avec_secours

    grist = ConnexionGrist("https://grist.numerique.gouv.fr", "identifiant_du_document")
    fiches, avertissement = lire_table_avec_secours(grist, "Ma_table", "_cache/ma_table.json")

Chaque fiche est un dictionnaire Python : {"id": 3, "Titre": "...", "Annee": 2026, ...}.
Les identifiants de colonnes Grist (et non leurs libellés) servent de clés.

La clé d'API
------------
Elle est cherchée, dans l'ordre :
1. dans la variable d'environnement GRIST_API_KEY ;
2. dans un fichier .env, dans le dossier courant ou l'un de ses parents
   (ligne `GRIST_API_KEY=...`).
Ce fichier .env ne doit jamais être commité : vérifiez qu'il figure dans le .gitignore.
"""

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

VARIABLE_CLE = "GRIST_API_KEY"
DELAI_MAX_SECONDES = 30


class ErreurGrist(Exception):
    """Erreur de connexion ou de lecture Grist, avec un message compréhensible."""


# ---------------------------------------------------------------------------
# Clé d'API
# ---------------------------------------------------------------------------

def trouver_fichier_env(depart=None):
    """Remonte les dossiers depuis `depart` jusqu'à trouver un fichier .env (ou None)."""
    dossier = Path(depart or Path.cwd()).resolve()
    for candidat in [dossier, *dossier.parents]:
        if (candidat / ".env").is_file():
            return candidat / ".env"
    return None


def lire_variable(variable, fichier_env=None):
    """
    Renvoie la valeur d'un réglage : variable d'environnement, sinon fichier .env.
    Sert pour la clé d'API, mais aussi pour l'identifiant du document, etc.
    """
    if os.environ.get(variable):
        return os.environ[variable].strip()

    fichier_env = Path(fichier_env) if fichier_env else trouver_fichier_env()
    if fichier_env and fichier_env.is_file():
        for ligne in fichier_env.read_text(encoding="utf-8").splitlines():
            # Lignes attendues : NOM=valeur (guillemets facultatifs)
            nom, signe_egal, valeur = ligne.partition("=")
            if signe_egal and nom.strip() == variable:
                return valeur.strip().strip('"').strip("'")

    raise ErreurGrist(
        f"Réglage introuvable : définissez {variable} dans l'environnement "
        f"ou dans un fichier .env (non commité)."
    )


def lire_cle_api(variable=VARIABLE_CLE, fichier_env=None):
    """Renvoie la clé d'API Grist."""
    return lire_variable(variable, fichier_env)


# ---------------------------------------------------------------------------
# Connexion
# ---------------------------------------------------------------------------

class ConnexionGrist:
    """Accès en lecture à un document Grist."""

    def __init__(self, serveur, document, cle=None):
        self.serveur = serveur.rstrip("/")
        self.document = document
        self.cle = cle or lire_cle_api()
        self.base = f"{self.serveur}/api/docs/{document}"

    def _requete(self, chemin, brut=False):
        """Envoie une requête GET à l'API et renvoie le JSON décodé (ou les octets si brut=True)."""
        requete = urllib.request.Request(
            self.base + chemin,
            headers={"Authorization": f"Bearer {self.cle}"},
        )
        try:
            with urllib.request.urlopen(requete, timeout=DELAI_MAX_SECONDES) as reponse:
                contenu = reponse.read()
        except urllib.error.HTTPError as erreur:
            if erreur.code in (401, 403):
                raise ErreurGrist("Accès refusé par Grist : clé d'API invalide ou droits insuffisants "
                                  "sur le document.") from erreur
            if erreur.code == 404:
                raise ErreurGrist(f"Introuvable dans Grist : {chemin} "
                                  f"(identifiant du document ou nom de table erroné ?).") from erreur
            raise ErreurGrist(f"Erreur Grist {erreur.code} sur {chemin}.") from erreur
        except (urllib.error.URLError, TimeoutError) as erreur:
            raise ErreurGrist(f"Serveur Grist injoignable ({self.serveur}) : {erreur}") from erreur
        return contenu if brut else json.loads(contenu)

    def colonnes(self, table):
        """Renvoie la description des colonnes : {identifiant: propriétés Grist (type, options…)}."""
        reponse = self._requete(f"/tables/{urllib.parse.quote(table)}/columns")
        return {colonne["id"]: colonne["fields"] for colonne in reponse["columns"]}

    def types_colonnes(self, table):
        """Renvoie {identifiant_colonne: type_grist}, par exemple {"Annee": "Int", "Cas_similaire_de": "Ref:Cas_usage"}."""
        return {nom: proprietes["type"] for nom, proprietes in self.colonnes(table).items()}

    def choix_colonnes(self, table):
        """
        Renvoie les listes de choix définies dans Grist, pour les colonnes
        « Choix » et « Liste de choix » : {"Type_demandeur": ["Collectivité", ...]}.
        Permet de contrôler les valeurs sans recopier ces listes dans le code.
        """
        choix = {}
        for nom, proprietes in self.colonnes(table).items():
            # Seules les colonnes Choix / Liste de choix comptent : une colonne convertie
            # (ex. Choix -> Référence) garde son ancienne liste dans ses options.
            if proprietes["type"] not in ("Choice", "ChoiceList"):
                continue
            options = json.loads(proprietes.get("widgetOptions") or "{}")
            if options.get("choices"):
                choix[nom] = options["choices"]
        return choix

    def lire_table(self, table, references_a_resoudre=()):
        """
        Renvoie toutes les lignes de la table, sous forme de liste de dictionnaires.

        Une colonne Référence contient le numéro de la ligne visée (ex. 2).
        Pour les colonnes listées dans `references_a_resoudre`, ce numéro est
        remplacé par la valeur affichée dans Grist (ex. "Bordeaux"). Les autres
        références gardent leur numéro, utile pour relier des lignes entre elles.
        """
        colonnes = self.colonnes(table)
        libelles = {nom: self._libelles_reference(colonnes[nom])
                    for nom in references_a_resoudre if nom in colonnes}

        reponse = self._requete(f"/tables/{urllib.parse.quote(table)}/records")
        fiches = []
        for ligne in reponse["records"]:
            fiche = {"id": ligne["id"]}
            for colonne, valeur in ligne["fields"].items():
                valeur = _normaliser(valeur, colonnes.get(colonne, {}).get("type", ""))
                if colonne in libelles:
                    valeur = _remplacer_par_libelles(valeur, libelles[colonne])
                fiche[colonne] = valeur
            fiches.append(fiche)
        return fiches

    def _libelles_reference(self, proprietes):
        """
        Pour une colonne Référence, renvoie {numéro de ligne: valeur affichée}
        en lisant la table visée et sa « colonne visible » (réglage Grist
        « Afficher la colonne »).
        """
        type_grist = proprietes["type"]
        if not type_grist.startswith(("Ref:", "RefList:")):
            raise ErreurGrist(f"La colonne de type {type_grist} n'est pas une référence.")
        table_visee = type_grist.split(":", 1)[1]

        colonnes_visees = self.colonnes(table_visee)
        visible = next((nom for nom, p in colonnes_visees.items()
                        if p.get("colRef") == proprietes.get("visibleCol")), None)
        lignes = self._requete(f"/tables/{urllib.parse.quote(table_visee)}/records")["records"]
        # Sans colonne visible définie, Grist affiche le numéro de ligne : on fait pareil
        return {ligne["id"]: (ligne["fields"].get(visible) if visible else ligne["id"])
                for ligne in lignes}

    def telecharger_piece_jointe(self, id_piece, dossier):
        """
        Télécharge une pièce jointe dans `dossier` et renvoie son chemin.

        Le fichier est nommé « <id>_<nom d'origine> ». Une pièce jointe Grist ne
        change jamais de contenu : si le fichier existe déjà, il n'est pas
        retéléchargé (ce qui permet aussi de travailler hors connexion).
        """
        dossier = Path(dossier)
        deja_la = sorted(dossier.glob(f"{id_piece}_*"))
        if deja_la:
            return deja_la[0]

        infos = self._requete(f"/attachments/{id_piece}")
        nom = _nom_de_fichier_sur(infos.get("fileName", "fichier"))
        contenu = self._requete(f"/attachments/{id_piece}/download", brut=True)
        dossier.mkdir(parents=True, exist_ok=True)
        chemin = dossier / f"{id_piece}_{nom}"
        chemin.write_bytes(contenu)
        return chemin


def _normaliser(valeur, type_grist):
    """
    Convertit les valeurs « codées » de Grist en valeurs Python simples :
    - listes (Liste de choix, Pièces jointes, Référence multiple) : ["L", a, b] -> [a, b]
    - référence vide : 0 -> None
    """
    if isinstance(valeur, list) and valeur and valeur[0] == "L":
        return valeur[1:]
    if type_grist.startswith("Ref:") and valeur == 0:
        return None
    if type_grist.startswith(("ChoiceList", "Attachments", "RefList:")) and valeur is None:
        return []
    return valeur


def _remplacer_par_libelles(valeur, libelles):
    """Remplace un numéro de ligne (ou une liste de numéros) par la ou les valeurs affichées."""
    if isinstance(valeur, list):
        return [libelles.get(numero, numero) for numero in valeur]
    return libelles.get(valeur, valeur) if valeur is not None else None


def _nom_de_fichier_sur(nom):
    """Remplace les caractères gênants dans un nom de fichier (espaces, accents conservés)."""
    return re.sub(r"[^\w.\-]+", "_", nom).strip("_") or "fichier"


# ---------------------------------------------------------------------------
# Lecture avec copie de secours
# ---------------------------------------------------------------------------

def lire_table_avec_secours(connexion, table, fichier_cache, references_a_resoudre=()):
    """
    Lit la table et enregistre une copie locale (JSON) de ce qui a été lu.
    (references_a_resoudre : voir ConnexionGrist.lire_table.)

    Si Grist est injoignable, renvoie la dernière copie locale à la place.
    Renvoie un couple (fiches, avertissement) : l'avertissement vaut None si la
    lecture Grist a réussi, sinon il explique d'où viennent les données.

    Attention : la copie locale contient toutes les colonnes, y compris celles
    qui ne sont pas publiées ; elle doit être ignorée par Git.
    """
    fichier_cache = Path(fichier_cache)
    try:
        fiches = connexion.lire_table(table, references_a_resoudre)
    except ErreurGrist as erreur:
        if not fichier_cache.is_file():
            raise ErreurGrist(f"{erreur}\nAucune copie locale disponible ({fichier_cache}).") from erreur
        sauvegarde = json.loads(fichier_cache.read_text(encoding="utf-8"))
        return sauvegarde["fiches"], (f"{erreur}\nDonnées issues de la copie locale "
                                      f"du {sauvegarde['lu_le']}.")

    fichier_cache.parent.mkdir(parents=True, exist_ok=True)
    fichier_cache.write_text(
        json.dumps({"lu_le": datetime.now().strftime("%Y-%m-%d %H:%M"), "fiches": fiches},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return fiches, None
