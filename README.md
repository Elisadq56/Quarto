# Modèles de rendus numériques Quarto pour le cerema

> Ce site propose un ensemble de fichiers à adapter pour créer des rapports d'étude cerema au format numérique en utilisant [Quarto](https://quarto.org/), un outil de publication scientifique et technique open source.

*Nouveauté juin 2026 : ces modèles, après un travail associant des agents de la DTerNC, un stagiaire (merci Arthur !) et l'aide de personnes ressources du pôle web, font peau neuve pour mieux respecter la charte graphique.*

# Un aperçu des modèles
Les modèles de rendus numériques sont visibles sur
- [Mode book barre de navigation à gauche](https://app-nc.cerema.fr/quarto-website-modele_v2/book/)
- [Mode barre de navigation en haut](https://app-nc.cerema.fr/quarto-website-modele_v2/navbar/)
- [Mode hybrid barre en haut et à gauche](https://app-nc.cerema.fr/quarto-website-modele_v2/hybrid_navbar_sidebar/)

# Comment utiliser ce modèle

Sur le présent lien gitlab [https://gitlab.cerema.fr/normandie-centre/quarto-website-modele](https://gitlab.cerema.fr/normandie-centre/quarto-website-modele), vous avez une bouton `Code` bleu avec menu déroulant qui vous propose télécharger le code source au format zip.

Cliquer sur `Télécharger le zip` puis dézipper le sur votre disque dur, renommer le répertoire avec le nom de votre projet et c'est parti : à vous d'adapter d'adapter le _quarto.yaml et vos pages .qmd.

Prérequis : installer R, un éditeur (Rstudio, Visual Studio Code ou Positron) et se former à Quarto pour savoir écrire un article et construire un projet.

## Adapter le _quarto.yml

3 modèles sont disponibles :
- **Book** (`_quarto_exemple_book.yml`) : barre de navigation sur le côté gauche (sidebar). Ce mode a plusieurs avantages : numérotation automatique, fil d'ariane, navigation de pages en pages avec page précédente / page suivante, facilité de paramétrage du .yml. C'est le modèle qui se rapproche le plus d'un rapport.    
- **Navbar** (`_quarto_exemple_navbar.yml`) : barre de navigation en haut (navbar) avec possibilités de sous-menus.  
- **Hybrid navbar sidebar** (`_quarto_exemple_hybrid_navbar_sidebar.yml`) : ce mode permet d'avoir à la fois d'avoir une barre de navigation en haut pour les grandes parties et une barre de navigation à droite pour les pages. La configuration du .yaml est plus complexe (double niveau de navigation à paramétrer).  

Une fois le dépôt cloné, copier le contenu de l'un des trois modèles dans le `_quarto.yml` puis adapter l'architecture du site à votre projet.

# Migrer un ancien projet

Pour mettre à jour un ancien site avec les améliorations de styles et de menus, deux solutions :
- Cloner le présent dépôt puis ajouter vos .qmd mais également tous vos autres fichiers et répertoires puis adapter le .yml (reprenez la partie avec l'architecture).
- Conserver votre ancien projet et ajouter / remplacer :
    - le répertoire js
    - le répertoires images / logo (surtout pour avoir logo_cerema_rf_fab-vertical_1_10.png)
    - le fichier custom.scss
    - le répertoire css qui contient les polices d'écriture
	- le répertoire _partials (avec le nouveau footer.html)
    - les parties du .yaml qui ne correspondent pas à l'architecture de votre site (notamment pour charger les fichiers .js, le footer html, adapter les tailles des blocs etc...)
- Rendre votre site (quarto render dans le terminal) et vérifier les mises en pages, il faudra peut être adapater quelques lignes dans les .qmd (notamment les schémas mermaid).


# Publier

-   Pour la mise en ligne sur le web, contacter un admin du serveur app-nc.cerema.fr. Si besoin, les sites quarto peuvent être hébergés sur des pages github ou le site quarto publish ou simplement déposer sur l'intra ou internet d'un maître d'ouvrage.
-   Thomas a également travaillé la possibilité d'associer projet git et job jenkins pour un déploiement sur le web quasi automoatique (en cours de test).


# Bonnes pratiques à respecter (impératif)

- Ne **jamais travailler sur box**, box est trop lent pour générer les dizaines de fichiers qui constituent un site web et ralentis les preview et bug régulièrement. Il est nécessaire de travailler en local et mettre en place un projet `Gitlab` pour qu'ils soient sauvegardés (ou sauvegarder votre projet manuellement de temps en temps !).
- La communication et le référencement passe par **Ceremaweb**
- Un pdf doit être généré pour alimenter **CeremDoc**.
- Les systèmes de relecture et de **validation** doivent respecter le circuit d'un rapport classique.
- Tant que le site n'est pas validé, une **limitation des accès par mot de passe** est nécessaire.

# Comment générer des pdf ?

[TODO : à rédiger quand on aura progresser sur ce point !]

Deux possibilités qui n'ont pas encore été suffisament explorée :
-   Clic droit + imprimer dans le navigateur puis compiler les pages pdf en ajoutant une page de garde et une quatrième de couverture (avec pdfsam par exemple), cela permet de garder la mémoire du rendu numérique et de le verser sur ceremadoc.
-   Passer d'abord par un .docx (quarto permet d'exporter en .docx sur la base d'un modèle dans ce format), corriger les mises en page, remettre les illustrations qui ne sont pas bien passées puis générer un pdf.

# Quelques ressources pour apprendre Quarto

-   Rendez-vous sur [la documentation officielle de quarto](https://quarto.org/) pour maîtriser toutes les subtilités de quarto !  
-   Retrouvez nos supports d'atelier module 1 et module 2 (encore en cours d'écriture) : [TODO retrouver les liens !]
https://app-nc.cerema.fr/atelier_quarto/atelier_quarto_module_1/index.html#/title-slide
https://app-nc.cerema.fr/atelier_quarto/atelier_quarto_module_2/index.html#/title-slide