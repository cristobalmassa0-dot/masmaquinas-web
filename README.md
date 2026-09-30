# +MÁQUINAS — web (mas-maquinas.cl)

Sitio estático. Netlify publica la carpeta `sitio/` en cada push a `main` (sin comando de build).

## Actualizar
1. Fotos nuevas: `python3 fotos.py <slug> foto1.jpg foto2.jpg ...`
2. Editar `equipos.json` (agregar/editar equipo, o moverlo a "vendidos").
3. `python3 build.py` (Python 3.12+) → regenera `sitio/`.
4. `git commit` + `git push` → Netlify publica solo en ~1 minuto.
