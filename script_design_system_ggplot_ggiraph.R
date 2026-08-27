# design_system Cerema

library(ggplot2)
library(ggiraph)
#library(showtext)
library(sysfonts)
library(glue)

# ── Polices ───────────────────────────────────────────────────────────────────
font_add(
  family = "Marianne",
  regular = "css/fonts/Marianne-Regular.woff2",
  bold    = "css/fonts/Marianne-Bold.woff2"
)

# ── Design system ─────────────────────────────────────────────────────────────
ds <- list(
  colors = list(
    # Couleurs principales
    cerema_orange = "#EF7757",
    cerema_bleu = "#292574",
    cerema_bleu_moyen = "#8E84AE",
    cerema_bleu_clair = "#C6BFD8",
    cerema_bleu_pale = "#E7E4EF",

    # Couleurs domaines
    domaine_a_fonce = "#26216A",
    domaine_a_moyen = "#827AAC",
    domaine_a_pale = "#BDB8D6",

    domaine_b_fonce = "#F7D05C",
    domaine_b_moyen = "#FDEB7D",
    domaine_b_pale = "#FEF3DB",

    domaine_c_fonce = "#EF7757",
    domaine_c_moyen = "#F49D54",
    domaine_c_pale = "#EBE6D6",

    domaine_d_fonce = "#96AB5B",
    domaine_d_moyen = "#B0CC4E",
    domaine_d_pale = "#EDF3D9",

    domaine_e_fonce = "#448D60",
    domaine_e_moyen = "#60B467",
    domaine_e_pale = "#DEEDDC",

    domaine_f_fonce = "#5A71B4",
    domaine_f_moyen = "#7E97CE",
    domaine_f_pale = "#E0E4F4",

    # R&I Carnot
    carnot_bleu_clair = "#5A71B4",
    carnot_bleu_fonce = "#292574",
    carnot_gris_clair = "#C6BFD8",
    carnot_gris = "#818383",

    # Couleur additionnelle
    background_error = "#FDE9E3",

    # Neutres
    blanc = "#FFFFFF",
    noir = "#000000",
    gris_clair = "#F5F4F9",
    gris_moyen = "#DEDBE9",


    # à revoir
    seq       = c("#DBDAFF", "#00005F"),
    cat       = c("#292574", "#EF7757", "#60B467", "#FDEB7D", "pink", "purple", "black", "grey")
  ),
  fonts = list(
    title = "Marianne",
    body  = "Marianne",
    size  = list(title = 13, subtitle = 11, axis = 7, caption = 8)
  )
)

# ── Thème ─────────────────────────────────────────────────────────────────────
theme_ds <- function(grid = "xy", sf = FALSE) {
  theme_minimal(base_family = ds$fonts$body) +
    theme(
      plot.title = element_text(
        family = ds$fonts$title,
        size = ds$fonts$size$title,
        face = "bold",
        color = ds$colors$cerema_bleu,
        margin = margin(b = 6)
      ),
      plot.subtitle = element_text(
        size = ds$fonts$size$subtitle,
        color = ds$colors$cerema_bleu_moyen,
        margin = margin(b = 16)
      ),
      plot.caption = element_text(
        size = ds$fonts$size$caption,
        color = ds$colors$cerema_bleu_moyen,
        hjust = 1,
        margin = margin(t = 12)
      ),
      axis.title = if (!sf) element_text(size = ds$fonts$size$axis, color = ds$colors$cerema_bleu_moyen) else element_blank(),
      axis.text = if (!sf) element_text(size = ds$fonts$size$axis, color = ds$colors$cerema_bleu) else element_blank(),
      axis.ticks.x = if (!sf) element_line() else element_blank(),
      axis.ticks.y = if (!sf) element_line() else element_blank(),
      axis.line.x = if (!sf) element_line(color = ds$colors$cerema_bleu) else element_blank(),
      axis.line.y = if (!sf) element_line(color = ds$colors$cerema_bleu) else element_blank(),

       # Grille : désactivée si sf = TRUE, sinon selon 'grid'
      panel.grid = if (sf) element_blank() else element_line(color = ds$colors$gris_moyen, linewidth = 0.3),
      panel.grid.major = if (sf) element_blank() else element_line(color = ds$colors$gris_moyen, linewidth = 0.3),
      
      panel.grid.major.x = if (!sf && grid %in% c("x", "xy")) element_line(color = ds$colors$gris_moyen, linewidth = 0.3) else element_blank(),
      panel.grid.major.y = if (!sf && grid %in% c("y", "xy")) element_line(color = ds$colors$gris_moyen, linewidth = 0.3) else element_blank(),
      panel.grid.minor = element_blank(),

      plot.background = element_rect(fill = ds$colors$blanc, color = NA),
      panel.background = element_rect(fill = ds$colors$blanc, color = NA),
      legend.position = "top",
      legend.text = element_text(size = ds$fonts$size$axis, color = ds$colors$cerema_bleu),
      legend.title = element_text(size = ds$fonts$size$axis, color = ds$colors$cerema_bleu_moyen),
      legend.key.size = unit(0.8, "lines"),
      plot.margin = margin(20, 24, 16, 20)
    )
}
   

# ── Scales ────────────────────────────────────────────────────────────────────
# à revoir
scale_color_ds <- function(...) scale_color_manual(values = ds$colors$cat, ...)
scale_fill_ds  <- function(...) scale_fill_manual(values = ds$colors$cat, ...)

scale_fill_ds_seq <- function(n = NULL, ...) {
  if (is.null(n)) scale_fill_gradientn(colors = ds$colors$seq, ...)
  else scale_fill_manual(values = colorRampPalette(ds$colors$seq)(n), ...)
}
scale_color_ds_seq <- function(n = NULL, ...) {
  if (is.null(n)) scale_color_gradientn(colors = ds$colors$seq, ...)
  else scale_color_manual(values = colorRampPalette(ds$colors$seq)(n), ...)
}

# ── Render ggiraph ────────────────────────────────────────────────────────────
render_ds <- function(gg, width_svg = 8, height_svg = 5, tooltip_css = NULL) {
  css_default <- glue("
    background: {ds$colors$cerema_bleu };
    color: {ds$colors$cerema_bleu_pale };
    font-family: {ds$fonts$body};
    font-size: 12px;
    padding: 8px 12px;
    border-radius: 6px;
    border: 1px solid {ds$colors$cerema_bleu_pale };
  ")
  girafe(
    ggobj      = gg,
    width_svg = width_svg,
    height_svg = height_svg,
    options = list(
      opts_tooltip(css = tooltip_css %||% css_default, use_fill = FALSE),
      opts_hover(css = "opacity: 0.85; cursor: pointer;"),
      opts_hover_inv(css = "opacity: 0.3;"),
      opts_sizing(rescale = TRUE)
    )
  )
}



# ── TEST AVANT DE METTRE DANS LE QUARTO ────────────────────────────────────────────────────────────
# ça va plus vite là qu'en chunck et ça permet d'avoir tout sous la main...
# A COMMENTER UNE FOIS LE TEST FINI

# packages <- c(
#   "dplyr",   # manipulation de données
#   "ggplot2", # graphiques
#   "ggiraph", # transformer un ggplot en graphe interactif
#   "plotly",  # graphiques interactifs
#   "DT",      # tableaux HTML (fonction datatable)
#   "sf",      # données géographiques
#   "leaflet",  # cartes interactives
#   "glue", # utilitaire sympa pour insérer des variables dans des chaînes de character
#   "sysfonts" # pour la gestion de la mariane
# )

# # Installation des packages manquants
# packages_to_install <- packages[!(packages %in% installed.packages()[, "Package"])]
# if (length(packages_to_install) > 0) {
#   install.packages(packages_to_install, dependencies = TRUE)
# }

# # Chargement des packages
# invisible(lapply(packages, library, character.only = TRUE))





# prepa données avec geom simplifié et clockforce etc...
# library(dplyr)
# library(sf)
# library(rmapshaper)
# geojson_communes_mrn_v3 <- st_read("data/exemple_communes_mrn_v2.geojson") |> 
#   ms_simplify() |> 
#   select(
#     "insee_com",
#     "nom",
#     "secteur_proximite",
#     "population_2013" = "p13_pop",
#     "population_2014" ="p14_pop",
#     "population_2015" ="p15_pop",
#     "population_2016" ="p16_pop",
#     "population_2017" ="p17_pop",
#     "population_2018" ="p18_pop",
#     "population_2019" ="p19_pop",
#     "population_2020" ="p20_pop",
#     "population_2021" ="p21_pop",
#     "population_2022" ="p22_pop",
#     "population_2023" ="p23_pop",
#     "surface_ha",
#     "geometry" 
#   )

# names(geojson_communes_mrn_v3)

# st_write(geojson_communes_mrn_v3,"data/exemple_communes_mrn_v3.geojson", driver = "GeoJSON", quiet = TRUE)








