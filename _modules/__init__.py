"""
Modules réutilisables pour les sites Quarto.

Chaque module est indépendant et n'utilise que la bibliothèque standard de
Python, sauf images_web qui a besoin de Pillow. Pour les réutiliser dans un
autre projet Quarto, il suffit de copier le dossier `_modules/` (le « _ »
initial indique à Quarto de ne pas le traiter comme une page du site).

- grist_connexion : lire une table Grist (avec copie de secours locale)
- controle_fiches : vérifier des fiches selon un schéma, produire un rapport
- galerie_cartes  : transformer des fiches en galerie de cartes Quarto
  (+ galerie_cartes.scss pour le style)
- images_web      : convertir une image en WebP de taille raisonnable (Pillow)
"""
