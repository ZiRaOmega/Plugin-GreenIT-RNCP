---
name: video-pitch
description: Produit une vidéo de pitch ou de soutenance à partir des slides, avec narration, sous-titres et voix off optionnelle.
argument-hint: "<deck.pptx> <narration.md> [--audio voice.mp3]"
disable-model-invocation: true
---

# Générer une vidéo de pitch

## Quand l’utiliser

Utiliser ce skill pour un teaser de 60–90 s ou une vidéo de soutenance. La vidéo est silencieuse si aucune voix off n’est fournie ; elle est sous-titrée.

## Commande

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/build_video.py \
  --deck /chemin/mon-projet/dist/soutenance.pptx \
  --narration /chemin/mon-projet/dist/narration.md \
  --out /chemin/mon-projet/dist/teaser.mp4
```

## Exigences

- Convertir le PPTX en PDF, puis en PNG 1920×1080 avec `pdftoppm`.
- 5 s par slide par défaut ; total 60–90 s.
- H.264, 30 fps, `yuv420p`.
- Sous-titres `.srt` générés depuis la narration.
- Audio optionnel : `--audio voice.mp3`, AAC 128 kbps.
- Pas de musique soumise à droits, pas de service cloud.
- `video-report.json` : durée, résolution, codec, nombre de slides.
- Échouer si `ffmpeg` ou `pdftoppm` manque ; ne pas produire de faux MP4.

## Vérification

`ffprobe` doit donner 60–90 s, 1920×1080, h264. Lire la vidéo et vérifier la synchronisation des sous-titres.
