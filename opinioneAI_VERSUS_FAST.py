import os
import json
import logging
import imaplib
import email
from email.header import decode_header
import re
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Configurazione del sistema di logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("AutomationCore")

# ==========================================
# 1. IL MOTORE DETERMINISTICO (Il Cilindro)
# ==========================================

class CammeIntercambiabile(ABC):
    @abstractmethod
    def esegui(self, contesto: Dict[str, Any]) -> Dict[str, Any]:
        pass


class RegistryCamme:
    def __init__(self):
        self._camme: Dict[str, CammeIntercambiabile] = {}

    def registra(self, nome: str, camma: CammeIntercambiabile):
        self._camme[nome] = camma
        logger.info(f"Camma sincronizzata nel sistema: '{nome}'")

    def ottieni(self, nome: str) -> CammeIntercambiabile:
        if nome not in self._camme:
            raise ValueError(f"Camma '{nome}' non trovata nel registro del sistema.")
        return self._camme[nome]


class AutomationCore:
    def __init__(self, queue_filepath: str = "tasks_queue.json"):
        self.queue_filepath = queue_filepath
        self.registry = RegistryCamme()
        self._inizializza_coda_default()

    def _inizializza_coda_default(self):
        if not os.path.exists(self.queue_filepath):
            coda_iniziale = [
                {
                    "id": "task_email_multipla_01",
                    "modulo": "scanner_email_multipla",
                    "parametri": {
                        "imap_server": "imap.gmail.com",
                        "email_user": "Bettazzifg@gmail.com",
                        "email_pass": "bowvgphnrrkfogmi",
                        "filtro_mittente": "centro di opinione"
                    }
                },
                {
                    "id": "task_flusso_multiplo_01",
                    "modulo": "flusso_continuo_multiplo",
                    "parametri": {
                        "headless": False,
                        "url_login": "https://www.centrodiopinione.it/login",
                        "sito_user": "Bettazzifg@gmail.com",
                        "sito_pass": "08081973Gf@"
                    }
                },
                {
                    "id": "task_report_01",
                    "modulo": "generatore_report",
                    "parametri": {"output_file": "report_giornaliero_centro.json"}
                }
            ]
            with open(self.queue_filepath, "w", encoding="utf-8") as f:
                json.dump(coda_iniziale, f, indent=4)
            logger.info(f"Creato file di coda predefinito: {self.queue_filepath}")

    def registra_camma(self, nome: str, camma: CammeIntercambiabile):
        self.registry.registra(nome, camma)

    def esegui_ciclo(self):
        logger.info("--- AVVIO CICLO DI AUTOMAZIONE MULTIPLA: CENTRO DI OPINIONE ---")
        
        if not os.path.exists(self.queue_filepath):
            logger.error("File della coda dei task non trovato.")
            return

        with open(self.queue_filepath, "r", encoding="utf-8") as f:
            try:
                tasks: List[Dict[str, Any]] = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Errore di decodifica JSON nella coda: {e}")
                return

        contesto_condiviso = {}

        for task in tasks:
            task_id = task.get("id", "sconosciuto")
            nome_modulo = task.get("modulo")
            parametri = task.get("parametri", {})

            parametri.update(contesto_condiviso)

            logger.info(f"Esecuzione task [{task_id}] tramite camma '{nome_modulo}'")

            try:
                camma = self.registry.ottieni(nome_modulo)
                risultato = camma.esegui(parametri)
                
                if isinstance(risultato, dict):
                    contesto_condiviso.update(risultato)

                logger.info(f"Task [{task_id}] completato con successo.")
            except Exception as e:
                logger.error(f"Errore critico durante l'esecuzione del task [{task_id}]: {e}")
                break


# ==========================================
# 2. IMPLEMENTAZIONE DELLE "CAMME" DIGITALI
# ==========================================

class CammaScannerEmailMultipla(CammeIntercambiabile):
    def esegui(self, contesto: Dict[str, Any]) -> Dict[str, Any]:
        imap_server = contesto.get("imap_server")
        email_user = contesto.get("email_user")
        email_pass = contesto.get("email_pass")
        filtro_mittente = contesto.get("filtro_mittente", "").lower().replace(" ", "")

        logger.info(f"Connessione IMAP al server {imap_server}...")
        
        try:
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(email_user, email_pass)
            mail.select("inbox")

            status, messages = mail.search(None, "ALL")
            if status != "OK":
                raise Exception("Errore nella ricerca dei messaggi.")

            id_messaggi = messages[0].split()
            if not id_messaggi:
                return {"stato": "successo", "lista_link_sondaggi": []}

            id_da_scansionare = id_messaggi[-30:] if len(id_messaggi) > 30 else id_messaggi
            lista_link_sondaggi = []

            for msg_id in reversed(id_da_scansionare):
                status, data = mail.fetch(msg_id, "(RFC822)")
                for response_part in data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        from_header = decode_header(msg.get("From"))[0]
                        mittente = str(from_header[0], from_header[1] or "utf-8", errors="ignore") if isinstance(from_header[0], bytes) else str(from_header[0])
                        
                        subj_header = decode_header(msg["Subject"])[0]
                        oggetto = str(subj_header[0], subj_header[1] or "utf-8", errors="ignore") if isinstance(subj_header[0], bytes) else str(subj_header[0])

                        if filtro_mittente in mittente.lower().replace(" ", "") or "centro" in mittente.lower():
                            corpo = ""
                            if msg.is_multipart():
                                for part in msg.walk():
                                    if part.get_content_type() in ["text/plain", "text/html"]:
                                        p = part.get_payload(decode=True)
                                        if p: corpo += p.decode("utf-8", errors="ignore") + "\n"
                            else:
                                p = msg.get_payload(decode=True)
                                if p: corpo = p.decode("utf-8", errors="ignore")

                            tutti_i_link = re.findall(r'https?://[^\s<>"\']+|www\.[^\s<>"\']+', corpo)
                            
                            # Filtro rigoroso: accetta SOLO link del dominio centrodiopinione.it (inclusi i domini di tracciamento come t.centrodiopinione.it)
                            link_validi = [
                                l for l in tutti_i_link 
                                if "centrodiopinione.it" in l.lower() and not any(ext in l.lower() for ext in ['.css', '.png', '.jpg', '.gif', 'fonts.', 'gstatic', 'googleapis', 'unsub'])
                            ]

                            if link_validi:
                                link_scelto = link_validi[0]
                                if link_scelto not in lista_link_sondaggi:
                                    lista_link_sondaggi.append(link_scelto)
                                    logger.info(f"Trovato link utile -> Oggetto: {oggetto} | Link: {link_scelto}")

            mail.logout()
            return {"lista_link_sondaggi": lista_link_sondaggi, "totale_sondaggi": len(lista_link_sondaggi)}

        except Exception as e:
            logger.error(f"Errore scansione email: {e}")
            raise e


class CammaFlussoContinuoMultiplo(CammeIntercambiabile):
    def esegui(self, contesto: Dict[str, Any]) -> Dict[str, Any]:
        url_login = contesto.get("url_login", "https://www.centrodiopinione.it/login")
        lista_link = contesto.get("lista_link_sondaggi", [])
        headless_mode = contesto.get("headless", False)
        sito_user = contesto.get("sito_user")
        sito_pass = contesto.get("sito_pass")

        logger.info(f"Avvio browser ottimizzato (Sondaggi in coda: {len(lista_link)}) via Playwright...")

        risultati_sequenza = []

        with sync_playwright() as p:
            # Configurazione argomenti per prevenire blocchi anti-bot
            browser = p.chromium.launch(
                headless=headless_mode,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-dev-shm-usage"]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            page = context.new_page()

            try:
                # Navigazione robusta con timeout esteso a 60 secondi
                logger.info(f"Accesso alla pagina di login: {url_login}")
                page.goto(url_login, timeout=60000, wait_until="commit")
                page.wait_for_load_state("domcontentloaded", timeout=20000)
                
                try:
                    page.locator("button:has-text('Dai il consenso'), button:has-text('Accetta')").first.click(timeout=4000)
                except Exception:
                    pass

                logger.info("Inserimento credenziali...")
                page.locator("input[type='email'], input#email").first.fill(sito_user)
                page.locator("input[type='password'], input#password").first.fill(sito_pass)
                page.locator("button:has-text('Accedi'), button[type='submit']").first.click()
                
                page.wait_for_url("**/auth/dashboard", timeout=30000)
                logger.info("Login completato con successo sulla dashboard.")

                try:
                    page.locator("button:has-text('No, grazie'), button:has-text('Magari più tardi')").first.click(timeout=3000)
                except Exception:
                    pass

                if not lista_link:
                    lista_link = ["https://www.centrodiopinione.it/auth/dashboard"]

                for indice, link_sondaggio in enumerate(lista_link, start=1):
                    logger.info(f"--- ESECUZIONE SONDAGGIO SEQUENZIALE {indice}/{len(lista_link)} ---")
                    
                    pagina_lavoro = page
                    sondaggio_avviato = False

                    try:
                        page.goto(link_sondaggio, timeout=40000, wait_until="domcontentloaded")
                        page.wait_for_timeout(2000)

                        pulsanti_avvio = page.locator("button:visible, a:visible, [role='button']:visible").filter(
                            has_text=re.compile(r"(inizia|partecipa|survey|rispondi|vai)", re.IGNORECASE)
                        )

                        if pulsanti_avvio.count() > 0:
                            btn = pulsanti_avvio.first
                            btn.scroll_into_view_if_needed()
                            
                            try:
                                with context.expect_page(timeout=6000) as nuova_scheda:
                                    btn.click()
                                pagina_lavoro = nuova_scheda.value
                                pagina_lavoro.wait_for_load_state("domcontentloaded", timeout=8000)
                                logger.info(f"Sondaggio {indice} aperto in nuova scheda.")
                            except Exception:
                                logger.info(f"Sondaggio {indice} avviato nella pagina corrente.")

                            sondaggio_avviato = True

                        try:
                            btn_interno = pagina_lavoro.locator("button:visible, a:visible").filter(has_text=re.compile(r"inizia|continua", re.IGNORECASE)).first
                            if btn_interno.is_visible(timeout=3000):
                                btn_interno.click()
                                logger.info("Cliccato pulsante interno di conferma.")
                        except Exception:
                            pass

                        screenshot_nome = f"sondaggio_seq_{indice}_esito.png"
                        pagina_lavoro.screenshot(path=screenshot_nome)
                        
                        risultati_sequenza.append({
                            "indice": indice,
                            "link_origine": link_sondaggio,
                            "url_finale": pagina_lavoro.url,
                            "stato": "avviato_con_successo" if sondaggio_avviato else "raggiunto_da_verificare",
                            "screenshot": screenshot_nome
                        })

                    except Exception as err_seq:
                        logger.error(f"Errore nel sondaggio {indice}: {err_seq}")
                        risultati_sequenza.append({"indice": indice, "stato": f"errore: {str(err_seq)}"})

                browser.close()
                return {"stato_login": "completato_con_successo", "risultati_sequenza_sondaggi": risultati_sequenza}

            except Exception as e:
                logger.error(f"Errore critico browser: {e}")
                browser.close()
                raise e


class CammaGeneratoreReport(CammeIntercambiabile):
    def esegui(self, contesto: Dict[str, Any]) -> Dict[str, Any]:
        output_file = contesto.get("output_file", "report_giornaliero_centro.json")
        report_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "stato_login": contesto.get("stato_login", "non_eseguito"),
            "totale_sondaggi_processati": contesto.get("totale_sondaggi", 0),
            "risultati_sequenza_sondaggi": contesto.get("risultati_sequenza_sondaggi", []),
            "stato_sistema": "operativo_multiplo_ottimizzato"
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=4, ensure_ascii=False)

        logger.info(f"Report salvato in: {output_file}")
        return report_data


# ==========================================
# 3. PUNTO DI ACCENSIONE DEL CONGEGNO
# ==========================================

if __name__ == "__main__":
    if os.path.exists("tasks_queue.json"):
        os.remove("tasks_queue.json")
        
    core = AutomationCore(queue_filepath="tasks_queue.json")
    core.registra_camma("scanner_email_multipla", CammaScannerEmailMultipla())
    core.registra_camma("flusso_continuo_multiplo", CammaFlussoContinuoMultiplo())
    core.registra_camma("generatore_report", CammaGeneratoreReport())
    
    core.esegui_ciclo()
    logger.info("--- CICLO CORRETTO TERMINATO ---")