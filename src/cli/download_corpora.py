import argparse
import os
import time
import zipfile
import io

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://talkbank.org"
INDEX_URL       = f"{BASE_URL}/childes/access/Eng-NA/"
PHON_INDEX_URL  = f"{BASE_URL}/phon/access/Eng-NA/"
DEFAULT_OUTPUT_DIR = "Corpora"


def _build_chrome(headless=True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    return webdriver.Chrome(options=opts)


def login_and_get_cookies(email, password, headless=True):
    """Opens a real Chrome session, logs in via TalkBank's JS auth modal, returns cookies."""
    from selenium.common.exceptions import StaleElementReferenceException

    print("Abriendo navegador para autenticar en TalkBank...")
    driver = _build_chrome(headless=headless)
    try:
        driver.get(f"{INDEX_URL}Brent.html")

        short = WebDriverWait(driver, 10)
        long  = WebDriverWait(driver, 30)

        # Open the login modal
        short.until(EC.element_to_be_clickable((By.ID, "authModals_loginLogoutBtn"))).click()

        # Fill credentials
        email_field = short.until(EC.visibility_of_element_located((By.ID, "authModals_userName")))
        email_field.clear()
        email_field.send_keys(email)
        driver.find_element(By.ID, "authModals_pswd").send_keys(password)

        # Grab a sentinel to detect the page reload that happens on success
        sentinel = driver.find_element(By.TAG_NAME, "html")

        driver.find_element(By.ID, "authModals_loginBtn").click()

        # Wait for either an error message or the page to reload (sentinel goes stale)
        def _outcome(d):
            # Error message present → raise immediately
            for el in d.find_elements(By.CSS_SELECTOR, ".authModals_messageFail"):
                text = el.text.strip()
                if text:
                    raise ValueError(text)
            # Page reloaded → sentinel is stale
            try:
                sentinel.tag_name   # access any property; raises if stale
                return False        # still on same page, keep waiting
            except StaleElementReferenceException:
                return True         # page reloaded = login succeeded

        try:
            long.until(_outcome)
        except ValueError as exc:
            raise PermissionError(f"Error de autenticación: {exc}") from None

        # Wait for the new page to finish loading
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        selenium_cookies = driver.get_cookies()
    finally:
        driver.quit()

    cookies = {c["name"]: c["value"] for c in selenium_cookies}
    print(f"Autenticación correcta ({len(cookies)} cookies obtenidas).\n")
    return cookies


def _corpus_names_from_index(session, index_url):
    response = session.get(index_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    return [
        a["href"][:-5]
        for a in soup.find_all("a", href=True)
        if a["href"].endswith(".html") and "/" not in a["href"]
    ]


def fetch_corpus_names(session):
    childes = _corpus_names_from_index(session, INDEX_URL)
    phon    = _corpus_names_from_index(session, PHON_INDEX_URL)

    # Merge: CHILDES first, then PhonBank corpora not already present
    seen = {c.casefold() for c in childes}
    extra = [c for c in phon if c.casefold() not in seen]
    return childes + extra


def _zip_links_from_page(session, page_url):
    """Returns list of (link_text, full_url) for every ?f=zip anchor on the page."""
    try:
        response = session.get(page_url)
        if response.status_code != 200:
            return []
        response.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "?f=zip" in href:
            full = href if href.startswith("http") else f"{BASE_URL}{href}"
            links.append((a.get_text(strip=True).lower(), full))
    return links


def fetch_download_url(session, corpus_name):
    # 1. Try CHILDES
    links = _zip_links_from_page(session, f"{INDEX_URL}{corpus_name}.html")
    if links:
        return links[0][1]

    # 2. Fall back to PhonBank — prefer the CHAT data link (path contains Eng-NA)
    links = _zip_links_from_page(session, f"{PHON_INDEX_URL}{corpus_name}.html")
    if not links:
        return None
    chat = [url for _, url in links if "/Eng-NA/" in url]
    return chat[0] if chat else links[0][1]


def _download_stream(session, url):
    """Descarga url en memoria con detección de velocidad mínima. Devuelve bytes."""
    CONNECT_TIMEOUT = 20
    READ_TIMEOUT    = 30        # segundos sin recibir datos → timeout
    MIN_SPEED_BPS   = 50 * 1024 # 50 KB/s mínimo
    SPEED_CHECK_S   = 15        # intervalo de comprobación de velocidad
    REPORT_EVERY    = 5 * 1024 * 1024

    response = session.get(url, stream=True, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
    response.raise_for_status()

    content_type = response.headers.get("content-type", "")
    if "text/html" in content_type:
        raise PermissionError(
            "El servidor devolvió HTML en lugar del ZIP. "
            "La sesión puede haber expirado o tu cuenta no tiene acceso a este corpus."
        )

    total = int(response.headers.get("content-length", 0))
    chunks = []
    downloaded = 0
    last_reported = 0
    t_speed_check = time.monotonic()
    bytes_at_last_check = 0

    for chunk in response.iter_content(chunk_size=65536):
        chunks.append(chunk)
        downloaded += len(chunk)

        now = time.monotonic()
        elapsed = now - t_speed_check
        if elapsed >= SPEED_CHECK_S:
            speed = (downloaded - bytes_at_last_check) / elapsed
            if speed < MIN_SPEED_BPS:
                raise TimeoutError(
                    f"Descarga demasiado lenta ({speed / 1024:.1f} KB/s < 50 KB/s)."
                )
            t_speed_check = now
            bytes_at_last_check = downloaded

        if downloaded - last_reported >= REPORT_EVERY:
            last_reported = downloaded
            if total:
                pct = downloaded * 100 // total
                print(f"    {pct}% ({downloaded // 1024 // 1024} MB / {total // 1024 // 1024} MB)", flush=True)
            else:
                print(f"    {downloaded // 1024 // 1024} MB descargados...", flush=True)

    return b"".join(chunks)


def download_corpus(session, corpus_name, output_dir, force, retries=2):
    corpus_dir = os.path.join(output_dir, corpus_name)

    if os.path.exists(corpus_dir) and not force:
        print(f"  [{corpus_name}] Ya existe, omitiendo (usa --force para sobreescribir).")
        return False

    download_url = fetch_download_url(session, corpus_name)
    if download_url is None:
        print(f"  [{corpus_name}] No se encontró enlace de descarga.")
        return False

    print(f"  [{corpus_name}] Descargando desde {download_url} ...", flush=True)

    last_error = None
    for attempt in range(1, retries + 2):  # retries + el intento inicial
        try:
            zip_bytes = _download_stream(session, download_url)
            break
        except Exception as e:
            last_error = e
            if attempt <= retries:
                wait = 5 * attempt
                print(f"    Intento {attempt} fallido ({e}). Reintentando en {wait} s...", flush=True)
                time.sleep(wait)
            else:
                raise last_error from None

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        top_entries = {n.split("/")[0] for n in zf.namelist() if n}
        if len(top_entries) == 1 and top_entries.pop().casefold() == corpus_name.casefold():
            zf.extractall(output_dir)
        else:
            os.makedirs(corpus_dir, exist_ok=True)
            zf.extractall(corpus_dir)

    print(f"  [{corpus_name}] Extraído en {corpus_dir}")
    return True


def run(email, password, corpora_filter, output_dir, force, headless=True):
    os.makedirs(output_dir, exist_ok=True)

    try:
        cookies = login_and_get_cookies(email, password, headless=headless)
    except PermissionError as exc:
        print(f"ERROR: {exc}")
        return

    session = requests.Session()
    session.cookies.update(cookies)

    print("Obteniendo lista de corpus de TalkBank...")
    all_corpora = fetch_corpus_names(session)
    print(f"Corpus encontrados: {', '.join(all_corpora)}\n")

    if corpora_filter:
        normalized_filter = {c.casefold() for c in corpora_filter}
        selected = [c for c in all_corpora if c.casefold() in normalized_filter]
        missing = normalized_filter - {c.casefold() for c in selected}
        if missing:
            print(f"Advertencia: estos corpus no existen en TalkBank: {', '.join(missing)}")
    else:
        selected = all_corpora

    print(f"Descargando {len(selected)} corpus en '{output_dir}'...\n")
    ok = 0
    skipped = 0
    failed = 0
    for corpus in selected:
        try:
            result = download_corpus(session, corpus, output_dir, force)
            if result:
                ok += 1
            else:
                skipped += 1
        except PermissionError as e:
            print(f"  [{corpus}] ERROR DE ACCESO: {e}")
            failed += 1
        except Exception as e:
            print(f"  [{corpus}] ERROR: {e}")
            failed += 1

    print(f"\nResumen: {ok} descargados, {skipped} omitidos, {failed} con error.")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Descarga corpus de TalkBank CHILDES Eng-NA en la carpeta Corpora/."
    )
    parser.add_argument(
        "--user", required=True, metavar="EMAIL",
        help="Email de la cuenta TalkBank (ej: usuario@ejemplo.com).",
    )
    parser.add_argument("--password", required=True, help="Contraseña de TalkBank.")
    parser.add_argument(
        "--corpora",
        nargs="+",
        default=None,
        help="Corpus a descargar (por defecto todos). Ej: --corpora Brent Bloom",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Carpeta de destino (por defecto: {DEFAULT_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Sobreescribe corpus que ya existan en la carpeta de destino.",
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Muestra el navegador durante el login (útil para depurar).",
    )

    args = parser.parse_args(argv)
    run(
        email=args.user,
        password=args.password,
        corpora_filter=args.corpora,
        output_dir=args.output_dir,
        force=args.force,
        headless=not args.no_headless,
    )


if __name__ == "__main__":
    main()
