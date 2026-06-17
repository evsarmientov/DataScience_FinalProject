"""
Scraper de "Requisitos" de paginas de hospitales publicos peruanos
(INEN, EsSalud / Rebagliati).

Estrategia: estas paginas son WordPress estatico (sin JS de por medio),
asi que buscamos cualquier encabezado/texto en negrita que contenga la
palabra "requisito" y extraemos la lista (ul/ol) que viene justo despues.
Esto es mas robusto que depender de una clase CSS especifica, porque
funciona igual en INEN y en EsSalud aunque su HTML no sea identico.
"""
import re

from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; MédiRutaBot/0.1; "
    "+https://github.com/tu-usuario/tu-repo)"
}


def extraer_requisitos(html: str) -> list[dict]:
    """Devuelve bloques {titulo, items} encontrados en el HTML."""
    soup = BeautifulSoup(html, "html.parser")
    bloques = []

    # Solo encabezados/texto-en-negrita, no parrafos sueltos (un parrafo
    # introductorio que solo *menciona* la palabra "requisitos" no cuenta
    # como seccion real, y nos daria falsos positivos).
    candidatos = soup.find_all(
        lambda tag: tag.name in ("h2", "h3", "h4", "strong", "b")
        and tag.get_text()
        and len(tag.get_text(strip=True)) < 120
        and re.search(r"requisito", tag.get_text(), re.IGNORECASE)
    )

    def texto_limpio(elemento) -> str:
        """Texto sin el problema clasico de BeautifulSoup: si la pagina
        mete un espacio en su propio <span> separado (comun en paginas
        .gob.pe hechas con editores visuales), get_text(strip=True) a
        secas borra ese espacio y pega las palabras ('DNI)o carnet').
        Usamos un separador explicito y luego colapsamos espacios
        repetidos para que quede 'DNI) o carnet' en vez de eso."""
        crudo = elemento.get_text(separator=" ", strip=True)
        return re.sub(r"\s+", " ", crudo).strip()

    vistos = set()
    for tag in candidatos:
        titulo = texto_limpio(tag)
        siguiente_lista = tag.find_next(["ul", "ol"])
        if siguiente_lista is None:
            continue
        items = tuple(texto_limpio(li) for li in siguiente_lista.find_all("li"))
        if not items:
            continue
        clave = (titulo, items)
        if clave in vistos:
            continue
        vistos.add(clave)
        bloques.append({"titulo": titulo, "items": list(items)})

    return bloques


def _sesion_con_reintentos():
    """Sesion de requests con reintentos automaticos (3 intentos, con
    espera creciente) para tolerar hiccups puntuales del servidor."""
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    sesion = requests.Session()
    reintentos = Retry(
        total=3,
        backoff_factor=2,  # espera 2s, 4s, 8s entre intentos
        status_forcelist=[429, 500, 502, 503, 504],
    )
    sesion.mount("https://", HTTPAdapter(max_retries=reintentos))
    return sesion


def scrapear_url(url: str, timeout: int = 30, verbose: bool = True) -> list[dict]:
    """Para usar en tu propio entorno (Streamlit Cloud, tu laptop, etc.),
    donde si hay salida de red hacia dominios .gob.pe."""
    import time

    sesion = _sesion_con_reintentos()
    inicio = time.time()
    resp = sesion.get(url, headers=HEADERS, timeout=timeout)
    if verbose:
        print(f"  [status={resp.status_code}  tiempo={time.time() - inicio:.1f}s]")
    resp.raise_for_status()
    return extraer_requisitos(resp.text)


if __name__ == "__main__":
    URLS = {
        "INEN - admision pacientes nuevos": "https://portal.inen.sld.pe/procedimiento-de-atencion-2/",
        "Rebagliati - salud mental": "https://www.essalud.gob.pe/servicio-de-salud-mental/",
    }
    for nombre, url in URLS.items():
        print(f"\n=== {nombre} ===")
        try:
            bloques = scrapear_url(url)
        except Exception as e:
            print(f"  FALLO: {type(e).__name__}: {e}")
            continue
        for bloque in bloques:
            print(f"- {bloque['titulo']}")
            for item in bloque["items"]:
                print(f"   . {item}")
