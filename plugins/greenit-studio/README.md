# GreenIT Studio

GreenIT Studio produit les livrables documentaires d’un audit Green IT : rapports DOCX et PDF, diaporamas PPTX, vidéos de pitch, figures PNG et analyses de codebase. Le plugin expose cinq skills autonomes et des scripts Python reproductibles.

## Installation

```text
/plugin install greenit-studio --marketplace <owner>/<repo>
```

## Usage

Utiliser `docx-report` pour convertir un rapport Markdown, `pptx-deck` pour une soutenance, `video-pitch` pour un teaser, `images-charts` pour les figures et `codebase-analysis` pour le diagnostic statique et web.

## Prérequis

Python 3.10+, `python-docx`, `python-pptx`, `matplotlib`, `Pillow`, LibreOffice et `ffmpeg`. Les chemins sont relatifs au plugin et aucun code n’est envoyé à un service externe.
