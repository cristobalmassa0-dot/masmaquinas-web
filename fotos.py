#!/usr/bin/env python3
"""Convierte fotos originales (jpg/png/heic/webp) al formato de la web.

Uso: python3 fotos.py <slug> foto1.jpg foto2.jpg ...
Escribe sitio/img/<slug>-<n>.webp (lado mayor 1448 px) y <slug>-<n>-s.webp (lado mayor 853 px),
numerando desde 2 (la 1 queda libre, igual que los equipos actuales). Imprime la lista
de números para pegar en "fotos" de equipos.json.
"""
import os
import sys
from PIL import Image, ImageOps

RAIZ = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(RAIZ, "sitio", "img")


def guardar(im, destino, lado):
    im = im.copy()
    im.thumbnail((lado, lado))
    im.save(destino, "WEBP", quality=80, method=6)


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    slug, archivos = sys.argv[1], sys.argv[2:]
    numeros = []
    for i, ruta in enumerate(archivos, start=2):
        im = ImageOps.exif_transpose(Image.open(ruta)).convert("RGB")
        guardar(im, os.path.join(IMG, f"{slug}-{i}.webp"), 1448)
        guardar(im, os.path.join(IMG, f"{slug}-{i}-s.webp"), 853)
        numeros.append(i)
    print("fotos:", numeros)


if __name__ == "__main__":
    main()
