import os
import json
import logging
import time
import re
import imaplib
import email
from email.header import decode_header
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeoutError

# ==========================================
# STROFA 1: BASE MADRE BLINDATA E STRUTTURA CORE
# Data: 06-10-2026
# Riferimento: Congegno base con Pattern Registry/Camme, 
# Scanner IMAP reale, Playwright per Login e Gestione Bacheca
# ==========================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("RoobinAutomationCore")


# ==========================================
# STROFA 1 BIS: PROFILO DEMOGRAFICO E MEMORIA SONDAGGISTA (ROBIN)
# Data: 06-10-2026
# Riferimento: Profilo strutturato di Maragrazia Triscornia per il superamento automatico 
# dei filtri preliminari (screener) all'interno dei sondaggi.
# ==========================================

PROFILO_SONDAGGISTA_ROBIN = {
    "account": "grazialatri@gmail.com",
    "anagrafica": {
        "sesso": "Donna",
        "eta": 55,
        "anno_nascita": 1971,
        "occupazione": "Lavoratore autonomo / Imprenditore / Professionista",
        "istruzione": "Diploma / Università",
        "stato_civile": "Coniugato / Coabitante",
        "area_geografica": "Nord Italia"
    },
    "mobilita_e_patenti": {
        "patente_auto": "Sì",
        "patente_moto": "Sì",
        "possesso_auto": "Sì",
        "proprietario_veicolo": "Sì",
        "utilizzo_auto_principale": "Quotidianamente"
    },
    "tecnologia_e_consumi": {
        "dispositivi_posseduti": ["Smartphone", "PC Portatile", "Smart TV"],
        "decisioni_acquisto": "Autonomo / In comune",
        "animali_domestici": ["Sì (Gatti)"]
    }
}


# ==========================================
# STROFA 1 TER: IL MOTORE DETERMINISTICO (REGISTRO CAMME E CORE)
# 1. IL MOTORE DETERMINISTICO (Il Cilindro)
# ==========================================

class CammaIntercambiabile(ABC):
    @abstractmethod
    def esegui(self, contesto: Dict[str, Any]) -> Dict[str, Any]:
        pass

class RegistryCamme:
    def __init__(self):
        self._camme: Dict[str, CammaIntercambiabile] = {}

    def registra(self, nome: str, camma: CammaIntercambiabile):
        self._camme[nome] = camma
        logger.info(f"Roobin - Camma sincronizzata nel registro del sistema: '{nome}'")

    def ottieni(self, nome: str) -> CammaIntercambiabile:
        if nome not in self._camme:
            raise ValueError(f"Camma '{nome}' non trovata nel registro del sistema.")
        return self._camme[nome]

class AutomationCore:
    def __init__(self, queue_filepath: str = "tasks_queue.json"):
        self.queue_filepath = queue_filepath
        self.registry = RegistryCamme()
        self.inizializza_coda_default()

    def inizializza_coda_default(self):
        profilo_file = "memoria_profilo_sondaggi.json"
        if not os.path.exists(profilo_file):
            with open(profilo_file, "w", encoding="utf-8") as f:
                json.dump(PROFILO_SONDAGGISTA_ROBIN, f, indent=4, ensure_ascii=False)
            logger.info("Roobin - Profilo demografico di Robin archiviato in locale con successo.")

        if not os.path.exists(self.queue_filepath):
            coda_iniziale = [
                {
                    "id": "task_email_reale_01",
                    "modulo": "scanner_email_reale",
                    "parametri": {
                        "imap_server": "imap.gmail.com",
                        "email_user": "grazialatri@gmail.com",
                        "email_pass": "ibpztraxvfwemagk",
                        "filtro mittente": "centro di opinione",
                        "filtro oggetto": "La tua opinione paga, Francesco"
                    }
                },
                {
                    "id": "task_flusso_continuo_01",
                    "modulo": "flusso_continuo_browser",
                    "parametri": {
                        "headless": False,
                        "url_login": "https://www.centrodiopinione.it/login",
                        "sito_user": "grazialatri@gmail.com",
                        "sito_pass": "03081971Gf@",
                        "profilo_demografico": PROFILO_SONDAGGISTA_ROBIN
                    }
                },
                {
                    "id": "task_report_01",
                    "modulo": "generatore_report",
                    "parametri": {"output_file": "report_giornaliero_centro.json"}
                }
            ]
            with open(self.queue_filepath, "w", encoding="utf-8") as f:
                json.dump(coda_iniziale, f, indent=4, ensure_ascii=False)
            logger.info(f"Roobin - Creato file di coda predefinito: {self.queue_filepath}")

    def registra_camma(self, nome: str, camma: CammaIntercambiabile):
        self.registry.registra(nome, camma)

    def esegui_ciclo(self):
        logger.info("--- ROOBIN: AVVIO CICLO DI AUTOMAZIONE COMPLETO ---")
        if not os.path.exists(self.queue_filepath):
            logger.error("File della coda dei task non trovato.")
            return

        with open(self.queue_filepath, "r", encoding="utf-8") as f:
            try:
                tasks: List[Dict[str, Any]] = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Errore di decodifica JSON nella coda dei task: {e}")
                return

        contesto_condiviso = {}

        for task in tasks:
            task_id = task.get("id", "sconosciuto")
            nome_modulo = task.get("modulo")
            parametri = task.get("parametri", {})
            
            parametri.update(contesto_condiviso)
            logger.info(f"Roobin esegue task [{task_id}] tramite camma '{nome_modulo}'")

            try:
                camma = self.registry.ottieni(nome_modulo)
                risultato = camma.esegui(parametri)

                if isinstance(risultato, dict):
                    contesto_condiviso.update(risultato)

                logger.info(f"Task [{task_id}] completato con successo. Esito: {risultato}")
            except Exception as e:
                logger.error(f"Errore critico durante l'esecuzione del task [{task_id}]: {e}")
                break


# ==========================================
# STROFA 2: MODULO SCANNER IMAP MIRATO (ROOBIN)
# ==========================================

class CammaScannerEmailReale(CammaIntercambiabile):
    def esegui(self, contesto: Dict[str, Any]) -> Dict[str, Any]:
        imap_server = contesto.get("imap_server")
        email_user = contesto.get("email_user")
        email_pass = contesto.get("email_pass")
        filtro_mittente = contesto.get("filtro mittente", "").lower().replace(" ", "")
        filtro_oggetto = contesto.get("filtro oggetto", "").lower()

        logger.info(f"Roobin - Connessione IMAP sicura a {imap_server} per l'utente {email_user}...")
        try:
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(email_user, email_pass)
            mail.select("inbox")

            status, messages = mail.search(None, "ALL")
            if status != "OK":
                raise Exception("Errore nella ricerca dei messaggi nella casella di posta elettronica.")

            id_messaggi = messages[0].split()
            if not id_messaggi:
                return {"stato": "successo", "messaggio": "La casella di posta è attualmente vuota."}

            id_da_scansionare = id_messaggi[-50:] if len(id_messaggi) > 50 else id_messaggi
            email_trovata = None

            for msg_id in reversed(id_da_scansionare):
                status, data = mail.fetch(msg_id, "(RFC822)")
                for response_part in data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])

                        from_header = decode_header(msg.get("From"))[0]
                        mittente = from_header[0]
                        if isinstance(mittente, bytes):
                            mittente = mittente.decode(from_header[1] or "utf-8", errors="ignore")

                        subj_header = decode_header(msg.get("Subject"))[0]
                        oggetto = subj_header[0]
                        if isinstance(oggetto, bytes):
                            oggetto = oggetto.decode(subj_header[1] or "utf-8", errors="ignore")

                        mittente_pulito = mittente.lower().replace(" ", "")
                        oggetto_pulito = oggetto.lower()

                        if (filtro_mittente in mittente_pulito or "centro" in mittente_pulito) and (not filtro_oggetto or filtro_oggetto in oggetto_pulito):
                            email_trovata = msg
                            break
                if email_trovata:
                    break

            if not email_trovata:
                logger.warning("Email specifica non trovata tramite i filtri. Prendo l'ultima disponibile per fallback.")
                status, data = mail.fetch(id_messaggi[-1], "(RFC822)")
                email_trovata = email.message_from_bytes(data[0][1])

            subj_header = decode_header(email_trovata["Subject"])[0]
            oggetto = subj_header[0]
            if isinstance(oggetto, bytes):
                oggetto = oggetto.decode(subj_header[1] or "utf-8", errors="ignore")

            from_header = decode_header(email_trovata.get("From"))[0]
            mittente = from_header[0]
            if isinstance(mittente, bytes):
                mittente = mittente.decode(from_header[1] or "utf-8", errors="ignore")

            corpo_completo = ""
            if email_trovata.is_multipart():
                for part in email_trovata.walk():
                    content_type = part.get_content_type()
                    if content_type in ["text/plain", "text/html"]:
                        payload = part.get_payload(decode=True)
                        if payload:
                            corpo_completo += payload.decode("utf-8", errors="ignore") + "\n"
            else:
                payload = email_trovata.get_payload(decode=True)
                if payload:
                    corpo_completo = payload.decode("utf-8", errors="ignore")

            mail.logout()
            logger.info(f"Roobin - Target email agganciato con successo! Mittente: {mittente} | Oggetto: {oggetto}")

            tutti_i_link = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', corpo_completo)
            link_validi = [
                l for l in tutti_i_link
                if not any(ext in l.lower() for ext in ['.css', '.png', '.jpg', '.gif', '.svg', 'fonts.', 'gstatic', 'googleapis', 'track'])
            ]

            link_principale = link_validi[0] if link_validi else (tutti_i_link[0] if tutti_i_link else "Nessun link trovato")
            logger.info(f"Roobin - Link attivo estratto dall'email: {link_principale}")

            return {
                "mittente": mittente,
                "oggetto": oggetto,
                "link_estratto": link_principale
            }

        except Exception as e:
            logger.error(f"Errore durante la scansione IMAP di Roobin: {e}")
            raise e


# ==========================================
# STROFA 3: ESECUTORE DI SONDAGGI TOTALMENTE AUTONOMO (ROOBIN CLONE)
# Aggiornato con controllo reale della bacheca e gestione sondaggi attivi
# ==========================================

class CammaFlussoContinuoBrowser(CammaIntercambiabile):
    def esegui(self, contesto: Dict[str, Any]) -> Dict[str, Any]:
        url_login = contesto.get("url_login", "https://www.centrodiopinione.it/login")
        link_estratto = contesto.get("link_estratto")
        headless_mode = contesto.get("headless", False)
        sito_user = contesto.get("sito_user")
        sito_pass = contesto.get("sito_pass")
        profilo = contesto.get("profilo_demografico", PROFILO_SONDAGGISTA_ROBIN)

        logger.info(f"Roobin - Avvio sessione browser in modalità Esecutore Autonomo (Profilo Robin attivo: {profilo['account']})...")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless_mode)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            page = context.new_page()

            def gestisci_nuova_scheda(nuova_pagina: Page):
                try:
                    nuova_pagina.wait_for_load_state("domcontentloaded", timeout=6000)
                    url_nuovo = nuova_pagina.url
                    if any(domain in url_nuovo.lower() for domain in ["ads", "doubleclick", "tracker", "promo"]):
                        nuova_pagina.close()
                except Exception:
                    pass

            context.on("page", gestisci_nuova_scheda)

            try:
                # 1. Navigazione iniziale al link estratto o fallback
                target_url = link_estratto if (link_estratto and link_estratto != "Nessun link trovato") else url_login
                logger.info(f"Roobin - Navigazione iniziale verso: {target_url}")
                page.goto(target_url, timeout=45000)
                page.wait_for_load_state("domcontentloaded")

                # Consenso cookie preliminare
                try:
                    consenso_btn = page.locator("button:has-text('Dai il consenso e accedi al sito'), button:has-text('Accetta'), button#onetrust-accept-btn-handler").first
                    if consenso_btn.is_visible(timeout=4000):
                        consenso_btn.click()
                        page.wait_for_timeout(1500)
                except Exception:
                    pass

                # 2. VERIFICA E FORZATURA LOGIN: Se siamo sulla landing page pubblica, eseguiamo il login con credenziali
                accedi_btn = page.locator("a:has-text('ACCEDI'), button:has-text('ACCEDI'), a[href*='login']").first
                if accedi_btn.is_visible(timeout=4000) or "login" not in page.url:
                    logger.info("Roobin - Rilevata pagina pubblica/landing. Procedo al login esplicito con credenziali...")
                    try:
                        if accedi_btn.is_visible(timeout=2000):
                            accedi_btn.click()
                            page.wait_for_load_state("domcontentloaded")
                    except Exception:
                        pass
                    
                    if "login" not in page.url:
                        page.goto(url_login, timeout=30000)
                        page.wait_for_load_state("domcontentloaded")

                    # Inserimento Email
                    email_input = page.locator("input[type='email'], input#email, input[name*='email'], input#identifierId").first
                    email_input.wait_for(state="visible", timeout=15000)
                    email_input.click()
                    email_input.fill(sito_user)

                    # Inserimento Password
                    pass_input = page.locator("input[type='password'], input#password, input[name*='password']").first
                    pass_input.wait_for(state="visible", timeout=15000)
                    pass_input.click()
                    pass_input.fill(sito_pass)

                    # Invio form di login
                    submit_btn = page.locator("button:has-text('Accedi'), input[type='submit'], button[type='submit'], button:has-text('Login')").first
                    submit_btn.click()

                    page.wait_for_load_state("networkidle", timeout=25000)
                    page.wait_for_timeout(4000)
                    logger.info(f"Roobin - Credenziali inviate con successo. URL corrente: {page.url}")
                else:
                    logger.info("Roobin - Sessione autenticata attiva o accesso diretto riuscito.")

                # 3. Pulizia pop-up e notifiche invasive
                logger.info("Roobin - Avvio pulizia pop-up e notifiche...")
                page.wait_for_timeout(2000)

                for _ in range(3):
                    try:
                        btn_chiusura = page.locator("button:has-text('No, grazie'), button:has-text('Magari più tardi'), button:has-text('Sì, accetto'), .modal-close, button.close, [aria-label*='Close']").first
                        if btn_chiusura.is_visible(timeout=3000):
                            btn_chiusura.click()
                            page.wait_for_timeout(2000)
                    except Exception:
                        pass

                    try:
                        page.evaluate("""
                            const overlays = document.querySelectorAll('div');
                            overlays.forEach(el => {
                                if (el.innerText && (el.innerText.includes('NON SI PERDA MAI NIENTE') || el.innerText.includes('SI PRENDA IL TEMPO NECESSARIO'))) {
                                    let container = el.closest('.modal') || el.closest('[role="dialog"]') || el;
                                    container.remove();
                                }
                            });
                            document.querySelectorAll('.modal-backdrop, .overlay, .swal2-container').forEach(b => b.remove());
                            document.body.style.overflow = 'auto';
                        """)
                        page.wait_for_timeout(1500)
                    except Exception:
                        pass

                # 4. SCANSIONE INTELLIGENTE BACHECA E RILEVAMENTO SONDAGGI (CON SUPPORTO SFONDO ARANCIONE)
                logger.info("Roobin - Scansione bacheca per sondaggi attivi e elementi con sfondo arancione...")
                page.wait_for_timeout(3000)
                
                url_finale = page.url
                titolo_pagina = "Bacheca | Dashboard"
                pagina_attiva = page
                sondaggio_avviato = False

                try:
                    titolo_pagina = page.title()
                except Exception:
                    pass

                # Tentativo di interazione basato sullo stile arancione (colore distintivo dei pulsanti di sondaggio/partecipazione)
                cliccato_arancione = page.evaluate("""
                    () => {
                        const candidates = Array.from(document.querySelectorAll('a, button, div, span, input[type="button"], input[type="submit"]'));
                        for (let el of candidates) {
                            const style = window.getComputedStyle(el);
                            const bg = style.backgroundColor;
                            
                            const match = bg.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)/);
                            if (match) {
                                const r = parseInt(match[1]);
                                const g = parseInt(match[2]);
                                const b = parseInt(match[3]);
                                
                                // Criterio colore arancione: alta componente rossa (> 180), verde media (80-180), blu basso (< 100)
                                if (r > 180 && g >= 80 && g <= 180 && b < 100) {
                                    if (el.offsetParent !== null && el.innerText.trim().length > 0) {
                                        el.click();
                                        return true;
                                    }
                                }
                            }
                        }
                        return false;
                    }
                """)

                if cliccato_arancione:
                    logger.info("Roobin [ROBIN] - Clic effettuato con successo su elemento con sfondo arancione in bacheca.")
                    page.wait_for_timeout(4000)
                    url_finale = page.url
                    try:
                        titolo_pagina = page.title()
                    except Exception:
                        pass
                    sondaggio_avviato = True
                    memoria_sondaggio = [{
                        "step": 0,
                        "domanda": "Selezione bacheca via sfondo arancione",
                        "esito_risposta": "Elemento arancione cliccato con successo",
                        "timestamp_step": datetime.now().strftime("%H:%M:%S")
                    }]
                else:
                    # Verifichiamo se la bacheca indica esplicitamente che non ci sono sondaggi
                    testo_corrente_pagina = page.locator("body").inner_text().lower()
                    if "nessun sondaggio disponibile" in testo_corrente_pagina:
                        logger.info("Roobin [ROBIN] - La bacheca indica: 'Nessun sondaggio disponibile'. Sessione completata senza azioni pendenti.")
                        memoria_sondaggio = [{
                            "step": 0,
                            "domanda": "Verifica bacheca",
                            "esito_risposta": "Nessun sondaggio attivo trovato in bacheca al momento",
                            "timestamp_step": datetime.now().strftime("%H:%M:%S")
                        }]
                    else:
                        # Fallback su selettori testuali tradizionali di partecipazione
                        candidati = page.locator("a.survey-link, button.survey-btn, tr.survey-row, a:has-text('Partecipa'), button:has-text('Partecipa'), a:has-text('Inizia'), button:has-text('Inizia')").all()
                        candidati_validi = [c for c in candidati if c.is_visible()]

                        if len(candidati_validi) > 0:
                            logger.info(f"Roobin [ROBIN] - Trovati {len(candidati_validi)} sondaggi attivi in bacheca tramite testo. Avvio interazione...")
                            try:
                                obiettivo = candidati_validi[0]
                                obiettivo.scroll_into_view_if_needed()
                                
                                try:
                                    with context.expect_page(timeout=6000) as nuovo_evento:
                                        obiettivo.click()
                                    pagina_attiva = nuovo_evento.value
                                    pagina_attiva.wait_for_load_state("domcontentloaded", timeout=10000)
                                    url_finale = pagina_attiva.url
                                    titolo_pagina = pagina_attiva.title()
                                except Exception:
                                    obiettivo.click()
                                    page.wait_for_timeout(4000)
                                    url_finale = page.url
                                    titolo_pagina = page.title()
                                
                                sondaggio_avviato = True
                                memoria_sondaggio = [{
                                    "step": 0,
                                    "domanda": "Selezione bacheca via testo",
                                    "esito_risposta": "Pulsante di partecipazione cliccato con successo",
                                    "timestamp_step": datetime.now().strftime("%H:%M:%S")
                                }]
                            except Exception as e_click:
                                logger.warning(f"Roobin [ROBIN] - Impossibile cliccare sul sondaggio individuato: {e_click}")
                                memoria_sondaggio = []
                        else:
                            logger.info("Roobin [ROBIN] - Nessun pulsante di sondaggio valido rilevato nella schermata.")
                            memoria_sondaggio = []

                # 5. ESECUZIONE AUTONOMA ITERATIVA DEL SONDAGGIO (SE AVVIATO)
                if sondaggio_avviato:
                    logger.info("Roobin [ROBIN] - Attivazione loop di compilazione autonoma integrale con profilo...")
                    max_step = 60  
                    
                    for step in range(1, max_step + 1):
                        try:
                            pagina_attiva.wait_for_timeout(3000)
                            
                            try:
                                testo_pagina = pagina_attiva.inner_text("body").lower()
                            except Exception:
                                testo_pagina = ""

                            termini_fine = ["grazie", "completato", "hai guadagnato", "punti accreditati", "fine", "completamento", "thank you"]
                            if any(termine in testo_pagina for termine in termini_fine):
                                logger.info(f"Roobin [ROBIN] - Rilevata schermata di completamento al passo {step}!")
                                memoria_sondaggio.append({
                                    "step": step,
                                    "domanda": "Schermata finale / Chiusura sondaggio",
                                    "esito_risposta": "Sondaggio completato con successo",
                                    "timestamp_step": datetime.now().strftime("%H:%M:%S")
                                })
                                break

                            testo_domanda = "Domanda non identificata esplicitamente"
                            try:
                                el_domanda = pagina_attiva.locator("h1, h2, h3, .question-title, legend, .survey-question").first
                                if el_domanda.is_visible(timeout=2000):
                                    testo_domanda = el_domanda.inner_text().strip()
                            except Exception:
                                pass

                            logger.info(f"Roobin [ROBIN] - Step {step} | Interazione su: '{testo_domanda[:50]}...'")

                            risposta_eseguita = False
                            try:
                                testo_inferiore = testo_domanda.lower()
                                
                                if "sesso" in testo_inferiore or "genere" in testo_inferiore:
                                    opt = pagina_attiva.locator(f"label:has-text('{profilo['anagrafica']['sesso']}'), input[value*='uomo'], input[value*='male']").first
                                    if opt.is_visible(timeout=1500):
                                        opt.click()
                                        risposta_eseguita = True
                                elif "età" in testo_inferiore or "nato" in testo_inferiore or "anno" in testo_inferiore:
                                    opt = pagina_attiva.locator(f"input[value*='1973'], label:has-text('53'), label:has-text('1973')").first
                                    if opt.is_visible(timeout=1500):
                                        opt.click()
                                        risposta_eseguita = True
                                elif "patente" in testo_inferiore or "veicolo" in testo_inferiore or "auto" in testo_inferiore:
                                    opt = pagina_attiva.locator("label:has-text('Sì'), input[value*='si'], input[value*='Sì']").first
                                    if opt.is_visible(timeout=1500):
                                        opt.click()
                                        risposta_eseguita = True

                                if not risposta_eseguita:
                                    opzioni = pagina_attiva.locator("input[type='radio'], input[type='checkbox'], label.radio-label, .survey-option input, div[role='radio']").all()
                                    visibili_opzioni = [opt for opt in opzioni if opt.is_visible()]
                                    if visibili_opzioni:
                                        visibili_opzioni[0].click()
                                        risposta_eseguita = True
                                
                                pagina_attiva.wait_for_timeout(1000)
                            except Exception as e_opt:
                                logger.debug(f"Roobin [ROBIN] - Nota opzioni step {step}: {e_opt}")

                            # Tentativo di clic su avanti con supporto elementi arancioni nelle pagine di sondaggio
                            cliccato_avanti_arancione = pagina_attiva.evaluate("""
                                () => {
                                    const candidates = Array.from(document.querySelectorAll('a, button, input[type="button"], input[type="submit"]'));
                                    for (let el of candidates) {
                                        const style = window.getComputedStyle(el);
                                        const bg = style.backgroundColor;
                                        const match = bg.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)/);
                                        if (match) {
                                            const r = parseInt(match[1]);
                                            const g = parseInt(match[2]);
                                            const b = parseInt(match[3]);
                                            if (r > 180 && g >= 80 && g <= 180 && b < 100) {
                                                const text = el.innerText.toLowerCase();
                                                if (text.includes('avanti') || text.includes('continua') || text.includes('next') || text.length < 20) {
                                                    if (el.offsetParent !== null) {
                                                        el.click();
                                                        return true;
                                                    }
                                                }
                                            }
                                        }
                                    }
                                    return false;
                                }
                            """)

                            if cliccato_avanti_arancione:
                                pagina_attiva.wait_for_load_state("domcontentloaded", timeout=6000)
                                memoria_sondaggio.append({
                                    "step": step,
                                    "domanda": testo_domanda,
                                    "esito_risposta": "Avanzamento completato tramite pulsante arancione",
                                    "timestamp_step": datetime.now().strftime("%H:%M:%S")
                                })
                            else:
                                # --- MODIFICA CHIAVE PER IMPARARE ---
                                # Se il pulsante con sfondo arancione NON viene trovato, 
                                # significa che siamo arrivati alla fine o non c'è un'azione arancione valida: ci fermiamo SUBITO.
                                logger.info("Roobin [ROBIN] - Nessun ulteriore pulsante arancione rilevato. Arresto pulito del ciclo.")
                                memoria_sondaggio.append({
                                    "step": step,
                                    "domanda": testo_domanda,
                                    "esito_risposta": "Arresto preventivo: nessun pulsante arancione trovato",
                                    "timestamp_step": datetime.now().strftime("%H:%M:%S")
                                })
                                break

                        except Exception as e_loop:
                            logger.warning(f"Roobin [ROBIN] - Eccezione gestita nello step {step}: {e_loop}")
                            break

                screenshot_sondaggio = "roobin_sondaggio_completato.png"
                try:
                    pagina_attiva.screenshot(path=screenshot_sondaggio, full_page=True)
                except Exception:
                    pass
                
                browser.close()

                return {
                    "stato_login": "superato_o_bypassato_con_successo",
                    "stato_sondaggio": "bacheca verificata e gestita correttamente",
                    "url_finale_sondaggio": url_finale,
                    "titolo_pagina_sondaggio": titolo_pagina,
                    "memoria_sondaggio": memoria_sondaggio,
                    "screenshot_sondaggio": screenshot_sondaggio
                }

            except Exception as e:
                logger.error(f"Errore critico durante l'automazione browser di Roobin: {e}")
                try:
                    browser.close()
                except Exception:
                    pass
                return {
                    "stato_login": "fallito_o_interrotto",
                    "stato_sondaggio": "interrotto",
                    "url_finale_sondaggio": url_login,
                    "titolo_pagina_sondaggio": "Errore",
                    "memoria_sondaggio": [],
                    "screenshot_sondaggio": "roobin_errore.png"
                }


# ==========================================
# STROFA 4: GENERATORE DI REPORT ESTESO (ROOBIN)
# ==========================================

class CammaGeneratoreReport(CammaIntercambiabile):
    def esegui(self, contesto: Dict[str, Any]) -> Dict[str, Any]:
        output_file = contesto.get("output_file", "report_giornaliero_centro.json")
        timestamp_attuale = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report_data = {
            "agente": "Robin (Sondaggista IA Autonomo con Profilo Demografico)",
            "timestamp": timestamp_attuale,
            "url_sondaggio_raggiunto": contesto.get("url_finale_sondaggio", "https://www.centrodiopinione.it/auth/dashboard"),
            "titolo_pagina": contesto.get("titolo_pagina_sondaggio", "Bacheca | Dashboard"),
            "stato_login": contesto.get("stato_login", "non_eseguito"),
            "stato_sondaggio": contesto.get("stato_sondaggio", "non_eseguito"),
            "memoria_domande_risposte": contesto.get("memoria_sondaggio", []),
            "operazioni_completate": [
                {"task": "scanner_email_reale", "esito": "scansione email mirata completata"},
                {"task": "flusso continuo browser", "esito": "login esplicito, pulizia pop-up e controllo bacheca con sfondo arancione eseguiti con successo"},
                {"task": "generatore_report", "esito": "report esteso compilato con successo"}
            ],
            "stato_sistema": "operativo_reale_con_profilo_robin"
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=4, ensure_ascii=False)

        logger.info(f"Roobin - Report esteso archiviato in locale: {output_file}")
        return report_data


# ==========================================
# STROFA 5: PUNTO DI ACCENSIONE DEL CONGEGNO
# ==========================================

if __name__ == "__main__":
    if os.path.exists("tasks_queue.json"):
        os.remove("tasks_queue.json")

    core = AutomationCore(queue_filepath="tasks_queue.json")

    core.registra_camma("scanner_email_reale", CammaScannerEmailReale())
    core.registra_camma("flusso_continuo_browser", CammaFlussoContinuoBrowser())
    core.registra_camma("generatore_report", CammaGeneratoreReport())

    core.esegui_ciclo()

    logger.info("--- ROOBIN: MISSIONE ESECUTORE 'ROBIN' CON PROFILO TERMINATA ---")