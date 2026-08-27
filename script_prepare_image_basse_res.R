library(magick)

# Ce script redimensionne les images si elles dépassent max_dim en largeur ou hauteur
# et écrase les fichiers d'origine avec les versions réduites

# Nb pixels maxi
max_dim <- 1800

# Fonction pour redimensionner une image (en écrasant l'original si nécessaire)
redimensionner_image <- function(fichier) {
  img <- image_read(fichier)
  
  # Récupération des dimensions
  info <- image_info(img)
  largeur <- info$width
  hauteur <- info$height
  
  # Détermination du facteur d'échelle
  facteur <- max_dim / max(largeur, hauteur)
  
  if (facteur < 1) {
    new_largeur <- round(largeur * facteur)
    new_hauteur <- round(hauteur * facteur)
    
    img_redim <- image_resize(img, paste0(new_largeur, "x", new_hauteur))
    
    # Écrase le fichier original avec l'image redimensionnée
    image_write(img_redim, path = fichier, format = tools::file_ext(fichier))
    
    message("Image redimensionnée : ", basename(fichier))
  } else {
    message("Image déjà plus petite que la limite : ", basename(fichier))
  }
}

# Répertoire de base
base_dir <- "./images"

# Lister tous les sous-répertoires (inclus récursivement)
all_dirs <- list.dirs(path = base_dir, recursive = TRUE, full.names = TRUE)

# Parcourir chaque répertoire et traiter les images
for (dir in all_dirs){
  fichiers <- list.files(dir, pattern = "\\.(jpg|jpeg|png|tiff|bmp|gif|webp)$", 
                         full.names = TRUE, ignore.case = TRUE)
  
  fichiers <- fichiers[!grepl("favicon\\.png$", fichiers, ignore.case = TRUE)]
  
  lapply(fichiers, redimensionner_image)
}
