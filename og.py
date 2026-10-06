#!/usr/bin/env python3
"""Genera las imágenes de vista previa (WhatsApp, Facebook, Instagram, etc.).

Uso: python3 og.py   (después de fotos.py y antes de build.py)
Escribe sitio/og/home.jpg y sitio/og/<slug>.jpg (1200x630). Necesita playwright + chromium.
"""
import html
import json
import os
import tempfile

from playwright.sync_api import sync_playwright

RAIZ = os.path.dirname(os.path.abspath(__file__))
SITIO = os.path.join(RAIZ, "sitio")
SALIDA = os.path.join(SITIO, "og")
LOGO = "file://" + os.path.join(SITIO, "assets", "logo.svg")

BASE = """<!doctype html><meta charset="utf-8"><style>
*{box-sizing:border-box;margin:0}
body{width:1200px;height:630px;background:#0f0f0e;color:#fff;overflow:hidden;
 font-family:'DejaVu Sans Condensed','DejaVu Sans',Arial,sans-serif;display:flex}
.txt{flex:1;padding:56px 56px 48px;display:flex;flex-direction:column;min-width:0}
.foto{background-size:cover;background-position:center;flex:none}
.logo{height:62px;width:auto;align-self:flex-start}
.rot{margin-top:auto;color:#F9B80D;font-weight:700;letter-spacing:4px;text-transform:uppercase;font-size:24px}
h1{margin-top:12px;font-size:60px;line-height:1.05;font-weight:700;letter-spacing:-1px}
.dato{margin-top:18px;font-size:30px;color:#cfcdc6}
.precio{margin-top:22px;font-size:54px;font-weight:700;color:#F9B80D}
.precio small{font-size:28px;color:#fff;font-weight:400;margin-left:10px}
.pie{margin-top:26px;font-size:24px;color:#8b8982;letter-spacing:1px}
.barra{height:8px;width:90px;background:#F9B80D;margin-bottom:22px}
</style>"""


def pagina_home(foto):
    return BASE + f"""<body>
<div class="txt"><img class="logo" src="{LOGO}" style="height:96px">
<div class="rot">Compra y venta</div>
<h1 style="font-size:56px">Camiones y maquinaria pesada en Chile</h1>
<div class="dato">Fotos reales · ficha técnica · consulta por WhatsApp</div>
<div class="pie">mas-maquinas.cl</div></div>
<div class="foto" style="width:473px;background-image:url('{foto}')"></div></body>"""


def pagina_equipo(e, foto):
    nombre = f'{e["marca"]} {e["modelo"]}'
    partes = [str(e["anio"])] if e.get("anio") else []
    partes.append(e["uso"])
    if e.get("ubicacion"):
        partes.append(e["ubicacion"])
    if e.get("precio"):
        nota = html.escape(e.get("precio_nota") or "")
        precio = f'{html.escape(e["precio"])}<small>{nota}</small>'
    else:
        precio = '<span style="font-size:40px;color:#fff">Precio a consultar</span>'
    return BASE + f"""<body>
<div class="txt"><img class="logo" src="{LOGO}">
<div class="rot">{html.escape(e["tipo"])} en venta</div>
<h1>{html.escape(nombre)}</h1>
<div class="dato">{html.escape(" · ".join(partes))}</div>
<div class="precio">{precio}</div>
<div class="pie">mas-maquinas.cl</div></div>
<div class="foto" style="width:473px;background-image:url('{foto}')"></div></body>"""


def main():
    with open(os.path.join(RAIZ, "equipos.json"), encoding="utf-8") as f:
        equipos = json.load(f)["equipos"]
    os.makedirs(SALIDA, exist_ok=True)

    def ruta_foto(e):
        return "file://" + os.path.join(SITIO, "img", f'{e["slug"]}-{e["fotos"][0]}.webp')

    trabajos = [("home", pagina_home(ruta_foto(equipos[0])))]
    trabajos += [(e["slug"], pagina_equipo(e, ruta_foto(e))) for e in equipos]

    with sync_playwright() as p:
        nav = p.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or None)
        pg = nav.new_page(viewport={"width": 1200, "height": 630})
        with tempfile.TemporaryDirectory() as tmp:
            for nombre, contenido in trabajos:
                ruta = os.path.join(tmp, nombre + ".html")
                with open(ruta, "w", encoding="utf-8") as f:
                    f.write(contenido)
                pg.goto("file://" + ruta)
                pg.wait_for_timeout(150)
                pg.screenshot(path=os.path.join(SALIDA, nombre + ".jpg"), type="jpeg", quality=82)
        nav.close()
    print("ok ·", len(trabajos), "imágenes en sitio/og/")


if __name__ == "__main__":
    main()
