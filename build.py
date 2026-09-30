#!/usr/bin/env python3
"""Genera el sitio estático de +MÁQUINAS desde equipos.json.

Uso: python3 build.py  → escribe sitio/index.html, sitio/equipos/<slug>/index.html,
sitemap.xml y robots.txt. Para agregar un equipo: fotos en sitio/img/<slug>-<n>.webp
(y -s.webp la chica) y una entrada nueva en equipos.json.
"""
import json
import os
from html import escape
from urllib.parse import quote

RAIZ = os.path.dirname(os.path.abspath(__file__))
SITIO = os.path.join(RAIZ, "sitio")
DOMINIO = "https://mas-maquinas.cl"

D = json.load(open(os.path.join(RAIZ, "equipos.json"), encoding="utf-8"))
WA = D["whatsapp"]
IG = D["instagram"]
EQUIPOS = D["equipos"]

ICONO_WA = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            '<path d="M3.5 20.5l1.3-4A8.5 8.5 0 1 1 8 19.6z"/>'
            '<path d="M9 9.5c0 3 2.5 5.5 5.5 5.5l1-1.5-2-1-1 .8a4 4 0 0 1-1.8-1.8l.8-1-1-2z" '
            'fill="currentColor" stroke-width="1"/></svg>')

TIPOS_PLURAL = {"Retroexcavadora": "Retroexcavadoras", "Excavadora": "Excavadoras",
                "Camión tolva": "Camiones"}


def wa(msg):
    return f"https://wa.me/{WA}?text={quote(msg)}"


def nombre(e):
    return f'{e["marca"]} {e["modelo"]}'


def nombre_completo(e):
    return f'{nombre(e)} {e["anio"]}' if e["anio"] else nombre(e)


def datos_cortos(e):
    d = []
    if e["anio"]:
        d.append(str(e["anio"]))
    d.append(e["uso"])
    if e.get("ubicacion"):
        d.append(e["ubicacion"])
    return "".join(f"<li>{escape(x)}</li>" for x in d)


def precio_html(e, clase="ficha"):
    if e["precio"]:
        return f'<b>{escape(e["precio"])}<small>{escape(e.get("precio_nota", ""))}</small></b>'
    if clase == "grande":
        return '<b class="consultar">Precio a consultar</b>'
    return '<span class="consultar">Precio a consultar</span>'


def foto(e, n, chica=False):
    return f'img/{e["slug"]}-{n}{"-s" if chica else ""}.webp'


def cabeza(titulo, descripcion, p, canonica, extra=""):
    return f"""<!doctype html>
<html lang="es-CL">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(titulo)}</title>
<meta name="description" content="{escape(descripcion)}">
<link rel="canonical" href="{DOMINIO}{canonica}">
<meta property="og:type" content="website">
<meta property="og:title" content="{escape(titulo)}">
<meta property="og:description" content="{escape(descripcion)}">
<meta property="og:locale" content="es_CL">
<meta name="theme-color" content="#0f0f0e">
<link rel="icon" href="{p}assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Barlow:wght@400;500;600&family=Bebas+Neue&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{p}assets/estilo.css">
{extra}</head>
"""


def cabecera(p):
    return f"""<header class="cabecera">
  <div class="envase">
    <a class="marca" href="{p}index.html" aria-label="+MÁQUINAS, inicio"><img src="{p}assets/logo.svg" alt="+MÁQUINAS" width="112" height="30"></a>
    <nav class="menu" aria-label="Principal">
      <a href="{p}index.html#equipos">Equipos</a>
      <a href="{p}index.html#vender">Vender mi máquina</a>
      <a href="{p}index.html#nosotros">Nosotros</a>
      <a href="{p}index.html#contacto">Contacto</a>
    </nav>
    <a class="boton boton-amarillo" href="{wa('Hola, vengo de la web de +MÁQUINAS.')}" target="_blank" rel="noopener">{ICONO_WA}<span>WhatsApp</span></a>
  </div>
</header>
"""


def pie(p):
    tel = f"+{WA[:2]} {WA[2]} {WA[3:7]} {WA[7:]}"
    return f"""<footer class="pie" id="contacto">
  <div class="envase">
    <div>
      <img src="{p}assets/logo.svg" alt="+MÁQUINAS" width="112" height="30">
      <p>Camiones y maquinaria pesada en todo Chile.</p>
    </div>
    <div>
      <h4>Contacto</h4>
      <ul>
        <li><a href="{wa('Hola, vengo de la web de +MÁQUINAS.')}" target="_blank" rel="noopener">WhatsApp {tel}</a></li>
        <li><a href="https://www.instagram.com/{IG}/" target="_blank" rel="noopener">Instagram @{IG}</a></li>
      </ul>
    </div>
    <div>
      <h4>Equipos</h4>
      <ul>
        <li><a href="{p}index.html#equipos">Disponibles</a></li>
        <li><a href="{p}index.html#vender">Vender mi máquina</a></li>
      </ul>
    </div>
    <p class="legal"><span>© 2026 +MÁQUINAS</span><span>Stock actualizado al {D["actualizado"]}</span></p>
  </div>
</footer>
"""


def tarjeta(e, p=""):
    tipo = TIPOS_PLURAL.get(e["tipo"], e["tipo"])
    return f"""      <a class="ficha" href="{p}equipos/{e["slug"]}/index.html" data-tipo="{escape(tipo)}">
        <div class="ficha-foto"><img src="{p}{foto(e, e["fotos"][0], True)}" alt="{escape(e["tipo"] + " " + nombre_completo(e))}" loading="lazy" width="640" height="853"></div>
        <div class="ficha-cuerpo">
          <span class="rotulo">{escape(e["tipo"])}</span>
          <h3>{escape(nombre(e))}</h3>
          <ul class="datos">{datos_cortos(e)}</ul>
          <div class="ficha-precio">{precio_html(e)}<span class="ver">Ver ficha</span></div>
        </div>
      </a>
"""


def portada():
    dest = EQUIPOS[0]
    conteo = {}
    for e in EQUIPOS:
        t = TIPOS_PLURAL.get(e["tipo"], e["tipo"])
        conteo[t] = conteo.get(t, 0) + 1
    filtros = f'<button type="button" aria-pressed="true" data-filtro="todos">Todos<span>{len(EQUIPOS)}</span></button>'
    filtros += "".join(f'<button type="button" aria-pressed="false" data-filtro="{escape(t)}">{escape(t)}<span>{n}</span></button>'
                       for t, n in conteo.items())
    vendidos = "".join(f"""      <div class="ficha vendido" data-tipo="vendido">
        <div class="ficha-foto"><img src="img/{v["foto"]}" alt="{escape(v["titulo"])}, vendido" loading="lazy" width="640" height="853"><span class="sello">Vendido · {escape(v["cuando"].lower())}</span></div>
        <div class="ficha-cuerpo">
          <span class="rotulo">Minicargador</span>
          <h3>{escape(v["titulo"].replace("Minicargador ", ""))}</h3>
          <ul class="datos"><li>Nuestra primera venta</li></ul>
          <div class="ficha-precio"><span class="consultar">Vendido</span></div>
        </div>
      </div>
""" for v in D["vendidos"])
    tipos_opts = "".join(f"<option>{t}</option>" for t in
                         ["Excavadora", "Retroexcavadora", "Minicargador", "Cargador frontal",
                          "Camión tolva", "Camión", "Grúa", "Bulldozer", "Motoniveladora", "Otro"])
    ld = {"@context": "https://schema.org", "@type": "AutoDealer", "name": "+MÁQUINAS",
          "url": DOMINIO, "telephone": "+" + WA, "areaServed": "CL",
          "sameAs": [f"https://www.instagram.com/{IG}/"]}
    html = cabeza("+MÁQUINAS · Camiones y maquinaria pesada en Chile",
                  "Compra y venta de camiones y maquinaria pesada usada en Chile. Retroexcavadoras, excavadoras y camiones tolva con fotos reales y ficha técnica.",
                  "", "/",
                  f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n')
    html += "<body>\n" + cabecera("") + f"""
<main>
<section class="portada">
  <div class="envase">
    <div class="portada-texto">
      <span class="rotulo">Camiones · Maquinaria pesada · Chile</span>
      <h1>Donde hay trabajo, <em>hay máquinas.</em></h1>
      <p class="bajada">Vendemos camiones y maquinaria pesada en todo Chile. Si tienes un equipo, lo vendemos por ti: fotos profesionales, ficha técnica y difusión a compradores reales.</p>
      <div class="portada-acciones">
        <a class="boton boton-amarillo" href="#equipos">Ver equipos disponibles</a>
        <a class="boton boton-linea" href="#vender">Quiero vender mi máquina</a>
      </div>
    </div>
    <a class="destacado" href="equipos/{dest["slug"]}/index.html">
      <img src="{foto(dest, dest["fotos"][0])}" alt="{escape(dest["tipo"] + " " + nombre_completo(dest))}" width="1086" height="1448">
      <div class="destacado-pie">
        <div><span class="rotulo">Destacado</span><strong>{escape(nombre_completo(dest))}</strong></div>
        <div class="precio">{escape(dest["precio"] or "Precio a consultar")} {escape(dest.get("precio_nota", ""))}<small>{escape(dest["uso"])}</small></div>
      </div>
    </a>
  </div>
</section>

<div class="franja"><div class="envase"><span>{len(EQUIPOS)} equipos disponibles</span><span>Fotos reales de cada equipo</span><span>Visitas coordinadas por WhatsApp</span></div></div>

<section class="seccion" id="equipos">
  <div class="envase">
    <div class="seccion-cabeza">
      <div><span class="rotulo">Stock</span><h2>Equipos disponibles</h2></div>
      <span class="rotulo">Actualizado al {D["actualizado"]}</span>
    </div>
    <div class="filtros" role="group" aria-label="Filtrar por tipo">{filtros}</div>
    <div class="grilla" id="grilla">
{"".join(tarjeta(e) for e in EQUIPOS)}{vendidos}      <a class="ficha ficha-vende" href="#vender" data-tipo="vende">
        <span class="rotulo">¿Tienes un equipo?</span>
        <strong>Tu máquina podría estar aquí.</strong>
        <p>Fotos profesionales, ficha técnica y difusión a compradores de todo Chile.</p>
        <span class="boton boton-amarillo">Quiero vender</span>
      </a>
    </div>
  </div>
</section>

<section class="seccion oscuro vender" id="vender">
  <div class="envase">
    <div>
      <span class="rotulo">Vende con nosotros</span>
      <h2>¿Tienes una máquina para vender?</h2>
      <p class="intro">Nos encargamos de todo lo que hace que un equipo se venda: que se vea bien, que la información esté completa y que llegue a quien lo necesita.</p>
      <ol class="pasos">
        <li><span class="n">01</span><div><b>Vamos a ver tu equipo</b><p>Lo revisamos contigo y tomamos fotos profesionales en terreno.</p></div></li>
        <li><span class="n">02</span><div><b>Armamos la ficha técnica</b><p>Año, horas, mantenciones y todo lo que un comprador pregunta antes de llamar.</p></div></li>
        <li><span class="n">03</span><div><b>Lo mostramos a compradores reales</b><p>Publicación en nuestros canales y contacto directo con empresas del rubro en todo Chile.</p></div></li>
      </ol>
    </div>
    <form class="formulario" id="form-vender" novalidate>
      <h3>Cuéntanos qué tienes</h3>
      <p>Completa lo que sepas. Al enviar se abre WhatsApp con el mensaje listo.</p>
      <div class="campos">
        <div class="campo"><label for="f-tipo">Tipo de equipo</label><select id="f-tipo" name="tipo">{tipos_opts}</select></div>
        <div class="campo"><label for="f-marca">Marca y modelo</label><input id="f-marca" name="marca" placeholder="Ej: Caterpillar 320"></div>
        <div class="campo"><label for="f-anio">Año</label><input id="f-anio" name="anio" inputmode="numeric" placeholder="Ej: 2018"></div>
        <div class="campo"><label for="f-uso">Horas o km</label><input id="f-uso" name="uso" placeholder="Ej: 6.500 h"></div>
        <div class="campo"><label for="f-lugar">Dónde está</label><input id="f-lugar" name="lugar" placeholder="Ciudad o región"></div>
        <div class="campo"><label for="f-nombre">Tu nombre</label><input id="f-nombre" name="nombre" autocomplete="name"></div>
        <div class="campo ancho"><label for="f-nota">Algo más</label><textarea id="f-nota" name="nota" placeholder="Estado, mantenciones, precio que esperas…"></textarea></div>
      </div>
      <button class="boton boton-amarillo" type="submit">{ICONO_WA}Enviar por WhatsApp</button>
      <p class="nota">El mensaje llega directo a nuestro WhatsApp.</p>
    </form>
  </div>
</section>

<section class="seccion historia" id="nosotros">
  <div class="envase">
    <figure><img src="img/{D["vendidos"][0]["foto"]}" alt="Minicargador Bobcat cargado en camión, primera venta de +MÁQUINAS" loading="lazy" width="720" height="1280"></figure>
    <div>
      <span class="rotulo">Agosto 2026</span>
      <h2>Así empezamos.</h2>
      <p>Nuestra primera venta fue un minicargador Bobcat. Salió de la faena arriba del camión, rumbo a un cliente que confió en nosotros para encontrarlo.</p>
      <p>Desde entonces hacemos lo mismo con cada equipo: fotos de verdad, datos completos y trato directo entre quien vende y quien compra.</p>
      <p class="firma">Síguenos en <a href="https://www.instagram.com/{IG}/" target="_blank" rel="noopener">@{IG}</a></p>
    </div>
  </div>
</section>
</main>
""" + pie("") + f"""<a class="flotante" href="{wa('Hola, vengo de la web de +MÁQUINAS.')}" target="_blank" rel="noopener" aria-label="Escríbenos por WhatsApp">{ICONO_WA}</a>
<script>
const WA = "{WA}";
document.querySelectorAll(".filtros button").forEach(b => b.addEventListener("click", () => {{
  const f = b.dataset.filtro;
  document.querySelectorAll(".filtros button").forEach(x => x.setAttribute("aria-pressed", x === b));
  document.querySelectorAll("#grilla .ficha").forEach(c => {{
    c.hidden = !(f === "todos" || c.dataset.tipo === f || c.dataset.tipo === "vende");
  }});
}}));
document.getElementById("form-vender").addEventListener("submit", ev => {{
  ev.preventDefault();
  const v = n => ev.target.elements[n].value.trim();
  const lineas = ["Hola, tengo un equipo para vender:", "• " + v("tipo") + (v("marca") ? " " + v("marca") : "")];
  if (v("anio")) lineas.push("• Año: " + v("anio"));
  if (v("uso")) lineas.push("• Uso: " + v("uso"));
  if (v("lugar")) lineas.push("• Ubicación: " + v("lugar"));
  if (v("nota")) lineas.push("• " + v("nota"));
  if (v("nombre")) lineas.push("", "Soy " + v("nombre") + ".");
  window.open("https://wa.me/" + WA + "?text=" + encodeURIComponent(lineas.join("\\n")), "_blank");
}});
</script>
</body>
</html>
"""
    return html


def pagina_equipo(e):
    p = "../../"
    n = nombre_completo(e)
    fotos = e["fotos"]
    minis = "".join(
        f'<button type="button" data-i="{i}" aria-label="Foto {i + 1}"{" aria-current=\"true\"" if i == 0 else ""}>'
        f'<img src="{p}{foto(e, f, True)}" alt="" loading="lazy" width="160" height="213"></button>'
        for i, f in enumerate(fotos))
    grandes = json.dumps([p + foto(e, f) for f in fotos])
    specs = "".join(f"<dt>{escape(k)}</dt><dd>{escape(v)}</dd>" for k, v in e["specs"])
    msg = f"Hola, me interesa el equipo {e['tipo'].lower()} {n} que vi en la web de +MÁQUINAS."
    msg_visita = f"Hola, quiero coordinar una visita para ver el equipo {n}."
    otros = [x for x in EQUIPOS if x["slug"] != e["slug"]][:3]
    tipo_pl = TIPOS_PLURAL.get(e["tipo"], e["tipo"])
    ld = {"@context": "https://schema.org", "@type": "Product", "name": f'{e["tipo"]} {n}',
          "brand": {"@type": "Brand", "name": e["marca"]}, "description": e["texto"],
          "image": [f"{DOMINIO}/{foto(e, f)}" for f in fotos],
          "itemCondition": "https://schema.org/UsedCondition"}
    if e["precio"]:
        ld["offers"] = {"@type": "Offer", "priceCurrency": "CLP",
                        "price": e["precio"].replace("$", "").replace(".", ""),
                        "availability": "https://schema.org/InStock"}
    html = cabeza(f'{e["tipo"]} {n} en venta · +MÁQUINAS',
                  f'{e["tipo"]} {n}, {e["uso"]}. {e["resumen"]} Fotos reales y ficha técnica.',
                  p, f'/equipos/{e["slug"]}/',
                  f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n')
    html += '<body class="pagina-equipo">\n' + cabecera(p) + f"""
<main class="envase">
  <nav class="miga" aria-label="Ruta"><a href="{p}index.html">Inicio</a><span>/</span><a href="{p}index.html#equipos">{escape(tipo_pl)}</a><span>/</span>{escape(nombre(e))}</nav>
  <div class="detalle">
    <div>
      <div class="galeria-principal">
        <img id="foto-grande" src="{p}{foto(e, fotos[0])}" alt="{escape(e["tipo"] + " " + n)}" width="1086" height="1448">
        <button class="galeria-flecha ant" type="button" aria-label="Foto anterior">←</button>
        <button class="galeria-flecha sig" type="button" aria-label="Foto siguiente">→</button>
        <span class="contador" id="contador">1 / {len(fotos)}</span>
      </div>
      <div class="miniaturas">{minis}</div>
    </div>
    <div class="info">
      <span class="rotulo">{escape(e["tipo"])}</span>
      <h1>{escape(nombre(e))}</h1>
      <ul class="datos">{datos_cortos(e)}</ul>
      <div class="precio-grande"><span class="rotulo">Precio</span>{precio_html(e, "grande")}</div>
      <div class="acciones">
        <a class="boton boton-amarillo" href="{wa(msg)}" target="_blank" rel="noopener">{ICONO_WA}Consultar por WhatsApp</a>
        <a class="boton boton-linea" href="{wa(msg_visita)}" target="_blank" rel="noopener">Coordinar una visita</a>
      </div>
      <div class="tabla"><h2>Ficha técnica</h2><dl>{specs}</dl></div>
      <div class="descripcion"><h2>Descripción</h2><p>{escape(e["texto"])}</p></div>
    </div>
  </div>
</main>
<section class="otros"><div class="envase"><h2>Otros equipos</h2><div class="grilla">
{"".join(tarjeta(x, p) for x in otros)}</div></div></section>
""" + pie(p) + f"""<div class="barra-movil"><a class="boton boton-amarillo" href="{wa(msg)}" target="_blank" rel="noopener">{ICONO_WA}Consultar por WhatsApp</a></div>
<script>
const fotos = {grandes};
let i = 0;
const grande = document.getElementById("foto-grande"), cont = document.getElementById("contador");
const minis = document.querySelectorAll(".miniaturas button");
function ir(n) {{
  i = (n + fotos.length) % fotos.length;
  grande.src = fotos[i];
  cont.textContent = (i + 1) + " / " + fotos.length;
  minis.forEach((m, k) => m.setAttribute("aria-current", k === i));
}}
minis.forEach(m => m.addEventListener("click", () => ir(+m.dataset.i)));
document.querySelector(".galeria-flecha.ant").addEventListener("click", () => ir(i - 1));
document.querySelector(".galeria-flecha.sig").addEventListener("click", () => ir(i + 1));
document.addEventListener("keydown", ev => {{ if (ev.key === "ArrowLeft") ir(i - 1); if (ev.key === "ArrowRight") ir(i + 1); }});
fotos.slice(1).forEach(s => {{ const im = new Image(); im.src = s; }});
</script>
</body>
</html>
"""
    return html


def main():
    open(os.path.join(SITIO, "index.html"), "w", encoding="utf-8").write(portada())
    urls = ["/"]
    for e in EQUIPOS:
        d = os.path.join(SITIO, "equipos", e["slug"])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(pagina_equipo(e))
        urls.append(f'/equipos/{e["slug"]}/')
    open(os.path.join(SITIO, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{DOMINIO}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    open(os.path.join(SITIO, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {DOMINIO}/sitemap.xml\n")
    print(f"ok · {len(urls)} páginas")


if __name__ == "__main__":
    main()
