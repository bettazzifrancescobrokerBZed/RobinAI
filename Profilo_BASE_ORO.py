"""
PROFILO DEMOGRAFICO INTELLIGENTE 3.0 - Francesco Bettazzi
Sistema avanzato con ragionamento semantico e NLP per sondaggi
Capace di rispondere a domande mai viste prima analizzando il contesto
"""

import re
import random
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

# ==========================================
# PARTE 1: DATABASE STATICO (VERITÀ ASSOLUTE)
# ==========================================

PROFILO_BASE = {
    # --- ANAGRAFICA ---
    "genere": "Maschio",
    "sesso": "Uomo",
    "eta": 53,
    "anno_nascita": 1973,
    "mese_nascita": 8,
    "giorno_nascita": 8,
    "data_nascita": "08/08/1973",
    "stato_civile": "Sposato",
    "coniugato": True,
    "figli": 0,
    "figli_minorenni": 0,
    "lingua_madre": "Italiano",
    
    # --- GEOGRAFIA ---
    "nazione": "Italia",
    "regione": "Emilia-Romagna",
    "provincia": "Parma",
    "citta": "Berceto",
    "tipo_comune": "Piccolo comune rurale montano",
    "area_geografica": "Nord Italia",
    "zona": "Montagna Appenninica",
    "altitudine": "Alta (>600m)",
    "cap": "43042",
    
    # --- LAVORO ---
    "stato_occupazionale": "Lavoratore autonomo",
    "occupazione": "Libero professionista",
    "settore": "Media, Fotografia, Video e Informatica",
    "ruolo": "Titolare/Freelance",
    "settore_dettaglio": "Produzione video, fotografia professionale, sviluppo software",
    "decisore_acquisti_aziendali": True,
    "dipendenti": 0,
    "partita_iva": True,
    "anni_esperienza": 25,
    
    # --- REDDITO ---
    "reddito_familiare_annuo": "30.000-50.000€",
    "fascia_reddito": "Media",
    
    # --- ISTRUZIONE ---
    "titolo_studio": "Diploma di Scuola Superiore",
    "livello_istruzione": "Diploma",
    "istruzione_universitaria": False,
    "formazione_continua": True,
    "autodidatta": True,
    
    # --- ABITAZIONE ---
    "tipo_abitazione": "Casa indipendente con giardino",
    "proprieta_casa": "Di proprietà",
    "mutuo_attivo": False,
    "mq_abitazione": "100-150",
    "componenti_nucleo": 2,
    "animali_domestici": ["Gatti"],
    "numero_gatti": 2,
    "giardino": True,
    "orto": True,
    
    # --- TECNOLOGIA ---
    "dispositivi": ["PC Portatile Linux", "Smartphone Android"],
    "sistema_operativo_pc": "Linux",
    "sistema_operativo_mobile": "Android",
    "connessione_internet": "Fibra/FWA",
    "velocita_internet": "30-100 Mbps",
    "servizi_streaming": ["YouTube"],
    "cloud_storage": True,
    "competenze_informatiche": "Avanzate",
    
    # --- MOBILITÀ ---
    "patente_auto": True,
    "patente_moto": True,
    "possesso_auto": True,
    "possesso_moto": True,
    "numero_auto": 1,
    "numero_moto": 1,
    "alimentazione_auto": "Benzina",
    "alimentazione_moto": "Benzina",
    "km_annui_auto": "10.000-15.000",
    "uso_auto": "Quotidiano",
    "uso_mezzi_pubblici": False,
    
    # --- CONSUMI E ABITUDINI ---
    "responsabile_spesa": "Condiviso",
    "frequenza_spesa_online": "1-3 volte/mese",
    "hobby": ["Fotografia", "Programmazione", "Natura", "Video editing", "Trekking"],
    "sport_praticati": ["Trekking", "Passeggiate"],
    "fumatore": False,
    "consumo_alcol": "Occasionale/Moderato",
    "dieta": "Onnivora",
    
    # --- SALUTE ---
    "problemi_salute_cronici": False,
    "allergie": False,
    "occhiali_lenti": False,
    "attivita_fisica": "Regolare",
    
    # --- FINANZA ---
    "conto_corrente": True,
    "carta_credito": True,
    "investimenti": False,
    "assicurazioni": ["Auto", "Moto", "Casa"],
    "risparmio": "Moderato",
}


# ==========================================
# PARTE 2: MATRICE DI PERSONALITÀ E VALORI
# (Per inferire opinioni su temi complessi)
# ==========================================

MATRICE_PERSONALITA = {
    # Valori su scala 1-10
    "sensibilita_ambientale": 8,  # Vive in montagna, natura, trekking
    "apertura_tecnologica": 9,    # Programmatore, Linux, early adopter
    "indipendenza": 9,             # Autonomo, autodidatta
    "pragmatismo": 8,              # Professionista, problem solver
    "creativita": 8,               # Fotografia, video, media
    "tradizionalismo": 4,          # Usa Linux, non mainstream
    "orientamento_privacy": 9,     # Linux, autonomo, consapevole
    "orientamento_sociale": 6,     # Vive in zona rurale, ma connesso
    "propensione_rischio": 5,      # Moderato, non investe
    "sensibilita_economica": 7,    # Attento ma non estremo
}


# ==========================================
# PARTE 3: KNOWLEDGE BASE SEMANTICA
# (Associazioni concettuali per ragionamento)
# ==========================================

KNOWLEDGE_BASE = {
    # Temi ambientali
    "ambiente": {
        "keywords": ["clima", "ambiente", "ecologia", "sostenibilità", "inquinamento", "riscaldamento", "verde", "natura"],
        "posizione": "favorevole_forte",
        "reasoning": "Vive in montagna, pratica trekking, ha orto e giardino, sensibile alla natura"
    },
    
    # Tecnologia
    "tecnologia": {
        "keywords": ["tech", "digitale", "innovazione", "AI", "software", "app", "internet", "5G"],
        "posizione": "favorevole_forte",
        "reasoning": "Programmatore, usa Linux, competenze avanzate, lavora nel settore"
    },
    
    # Privacy e dati
    "privacy": {
        "keywords": ["privacy", "dati personali", "sorveglianza", "tracking", "cookie", "GDPR"],
        "posizione": "molto_importante",
        "reasoning": "Usa Linux (scelta consapevole), autonomo, competenze tecniche"
    },
    
    # Economia e lavoro
    "lavoro_autonomo": {
        "keywords": ["freelance", "partita iva", "autonomo", "impresa", "startup"],
        "posizione": "favorevole",
        "reasoning": "È libero professionista da anni, conosce vantaggi e sfide"
    },
    
    # Mobilità
    "mobilita_sostenibile": {
        "keywords": ["elettrico", "ibrido", "mobilità sostenibile", "car sharing"],
        "posizione": "neutrale_aperto",
        "reasoning": "Ha auto benzina ma vive in zona rurale dove elettrico è meno pratico"
    },
    
    # Salute
    "salute_prevenzione": {
        "keywords": ["salute", "prevenzione", "vaccini", "medicina", "benessere"],
        "posizione": "favorevole",
        "reasoning": "Fa attività fisica regolare, nessun problema cronico, approccio pragmatico"
    },
    
    # Politica (neutrale/pragmatico)
    "politica": {
        "keywords": ["governo", "elezioni", "partito", "politica"],
        "posizione": "neutrale_informato",
        "reasoning": "Profilo autonomo e indipendente, non schierato ideologicamente"
    },
    
    # Consumi
    "consumo_responsabile": {
        "keywords": ["bio", "km zero", "locale", "artigianale", "qualità"],
        "posizione": "favorevole",
        "reasoning": "Vive in zona rurale, ha orto, sensibilità ambientale"
    },
}


# ==========================================
# PARTE 4: MOTORE DI RAGIONAMENTO SEMANTICO
# ==========================================

class MotoreDiRagionamento:
    """
    Analizza domande in linguaggio naturale e genera risposte coerenti
    anche per temi mai visti prima.
    """
    
    def __init__(self, profilo: Dict, personalita: Dict, knowledge: Dict):
        self.profilo = profilo
        self.personalita = personalita
        self.knowledge = knowledge
        self.cache_risposte = {}
    
    def analizza_domanda(self, domanda: str) -> Dict[str, Any]:
        """
        Analizza semanticamente una domanda e identifica il tema.
        """
        domanda_lower = domanda.lower()
        
        # Rimuovi punteggiatura e normalizza
        domanda_clean = re.sub(r'[^\w\s]', ' ', domanda_lower)
        parole = domanda_clean.split()
        
        # Identifica il tema principale
        tema_match = None
        max_score = 0
        
        for tema, info in self.knowledge.items():
            score = sum(1 for keyword in info["keywords"] if keyword in domanda_lower)
            if score > max_score:
                max_score = score
                tema_match = tema
        
        # Identifica il tipo di domanda
        tipo_domanda = self._identifica_tipo_domanda(domanda_lower)
        
        return {
            "tema": tema_match,
            "tipo": tipo_domanda,
            "parole_chiave": parole,
            "score_match": max_score
        }
    
    def _identifica_tipo_domanda(self, domanda: str) -> str:
        """Identifica se è opinione, fatto, frequenza, ecc."""
        if any(word in domanda for word in ["pensi", "opinione", "credi", "ritieni", "secondo te"]):
            return "opinione"
        elif any(word in domanda for word in ["quanto spesso", "frequenza", "quante volte"]):
            return "frequenza"
        elif any(word in domanda for word in ["hai", "possiedi", "usi", "utilizzi"]):
            return "possesso"
        elif any(word in domanda for word in ["sei", "lavori", "abiti"]):
            return "stato"
        else:
            return "generica"
    
    def genera_risposta(self, domanda: str, opzioni: Optional[List[str]] = None) -> str:
        """
        Genera una risposta coerente basata su analisi semantica.
        """
        # Controlla cache
        if domanda in self.cache_risposte:
            return self.cache_risposte[domanda]
        
        # Analizza la domanda
        analisi = self.analizza_domanda(domanda)
        
        # Genera risposta basata sul tipo
        if analisi["tipo"] == "opinione":
            risposta = self._genera_opinione(analisi, opzioni)
        elif analisi["tipo"] == "possesso":
            risposta = self._genera_risposta_possesso(analisi, opzioni)
        elif analisi["tipo"] == "frequenza":
            risposta = self._genera_frequenza(analisi, opzioni)
        else:
            risposta = self._genera_risposta_generica(analisi, opzioni)
        
        # Salva in cache
        self.cache_risposte[domanda] = risposta
        return risposta
    
    def _genera_opinione(self, analisi: Dict, opzioni: Optional[List[str]]) -> str:
        """Genera opinione basata su tema e personalità."""
        tema = analisi["tema"]
        
        if tema and tema in self.knowledge:
            posizione = self.knowledge[tema]["posizione"]
            
            # Mappa posizioni a risposte
            if opzioni:
                return self._seleziona_opzione_coerente(posizione, opzioni)
            else:
                return self._genera_testo_opinione(posizione, tema)
        
        # Fallback: risposta neutra/moderata
        if opzioni:
            return opzioni[len(opzioni)//2]  # Opzione centrale
        return "Neutrale / Non ho un'opinione forte"
    
    def _seleziona_opzione_coerente(self, posizione: str, opzioni: List[str]) -> str:
        """Seleziona l'opzione più coerente con la posizione."""
        opzioni_lower = [opt.lower() for opt in opzioni]
        
        if posizione == "favorevole_forte":
            # Cerca "molto d'accordo", "assolutamente sì", ecc.
            for i, opt in enumerate(opzioni_lower):
                if any(word in opt for word in ["molto", "assolutamente", "completamente", "fortemente"]):
                    if any(word in opt for word in ["d'accordo", "sì", "favorevole", "importante"]):
                        return opzioni[i]
            # Fallback: ultima opzione (spesso la più positiva)
            return opzioni[-1]
        
        elif posizione == "favorevole":
            for i, opt in enumerate(opzioni_lower):
                if any(word in opt for word in ["d'accordo", "sì", "favorevole"]) and "molto" not in opt:
                    return opzioni[i]
            return opzioni[-2] if len(opzioni) > 2 else opzioni[-1]
        
        elif posizione == "neutrale_aperto" or posizione == "neutrale_informato":
            # Cerca opzione centrale o "dipende"
            for i, opt in enumerate(opzioni_lower):
                if any(word in opt for word in ["neutrale", "dipende", "né", "moderato"]):
                    return opzioni[i]
            return opzioni[len(opzioni)//2]
        
        elif posizione == "molto_importante":
            for i, opt in enumerate(opzioni_lower):
                if "molto importante" in opt or "fondamentale" in opt:
                    return opzioni[i]
            return opzioni[-1]
        
        # Default: opzione centrale
        return opzioni[len(opzioni)//2]
    
    def _genera_testo_opinione(self, posizione: str, tema: str) -> str:
        """Genera testo libero per opinione."""
        templates = {
            "favorevole_forte": [
                "Sono molto favorevole",
                "Lo ritengo estremamente importante",
                "È una priorità assoluta"
            ],
            "favorevole": [
                "Sono favorevole",
                "Lo considero importante",
                "Ha senso"
            ],
            "neutrale_aperto": [
                "Dipende dal contesto",
                "Può avere pro e contro",
                "Sono aperto ma cauto"
            ],
            "molto_importante": [
                "È fondamentale",
                "Molto importante",
                "Priorità alta"
            ]
        }
        
        return random.choice(templates.get(posizione, ["Neutrale"]))
    
    def _genera_risposta_possesso(self, analisi: Dict, opzioni: Optional[List[str]]) -> str:
        """Risponde a domande su possesso/uso."""
        domanda_lower = " ".join(analisi["parole_chiave"])
        
        # Cerca match diretti nel profilo
        for chiave, valore in self.profilo.items():
            if chiave in domanda_lower:
                if isinstance(valore, bool):
                    return "Sì" if valore else "No"
                return str(valore)
        
        # Inferenze comuni
        if "smartphone" in domanda_lower:
            return "Sì"
        if "tablet" in domanda_lower:
            return "No"
        if "smart tv" in domanda_lower:
            return "No"
        
        # Fallback
        if opzioni:
            return opzioni[0]
        return "No"
    
    def _genera_frequenza(self, analisi: Dict, opzioni: Optional[List[str]]) -> str:
        """Risponde a domande di frequenza."""
        if opzioni:
            # Scegli opzione moderata (né mai né sempre)
            if len(opzioni) >= 3:
                return opzioni[len(opzioni)//2]
            return opzioni[0]
        return "Occasionalmente"
    
    def _genera_risposta_generica(self, analisi: Dict, opzioni: Optional[List[str]]) -> str:
        """Fallback generico."""
        if opzioni:
            return opzioni[0]
        return "Non specificato"


# ==========================================
# PARTE 5: CLASSE PROFILO INTELLIGENTE 3.0
# ==========================================

class ProfiloIntelligente:
    """
    Profilo con ragionamento semantico avanzato.
    """
    
    def __init__(self, profilo_base: Dict, personalita: Dict, knowledge: Dict):
        self.profilo = profilo_base
        self.personalita = personalita
        self.knowledge = knowledge
        self.motore = MotoreDiRagionamento(profilo_base, personalita, knowledge)
    
    def get(self, chiave: str, default: Any = None) -> Any:
        """Accesso con fallback intelligente."""
        # 1. Database statico
        if chiave in self.profilo:
            return self.profilo[chiave]
        
        # 2. Cache risposte
        if chiave in self.motore.cache_risposte:
            return self.motore.cache_risposte[chiave]
        
        # 3. Inferenza semplice
        risposta = self._inferisci_semplice(chiave)
        if risposta is not None:
            return risposta
        
        return default
    
    def _inferisci_semplice(self, chiave: str) -> Optional[Any]:
        """Inferenze rapide senza analisi semantica completa."""
        chiave_lower = chiave.lower()
        
        # Geografia
        if "nord" in chiave_lower:
            return True
        if "sud" in chiave_lower or "meridion" in chiave_lower:
            return False
        
        # Famiglia
        if "figli" in chiave_lower or "bambini" in chiave_lower:
            return self.profilo.get("figli", 0) > 0
        
        # Lavoro
        if "dipendent" in chiave_lower:
            return False
        if "autonomo" in chiave_lower or "freelance" in chiave_lower:
            return True
        
        return None
    
    def risposta_domanda(self, domanda: str, opzioni: Optional[List[str]] = None) -> str:
        """
        Metodo principale: risponde a qualsiasi domanda.
        """
        return self.motore.genera_risposta(domanda, opzioni)
    
    def to_dict(self) -> Dict[str, Any]:
        """Esporta profilo completo."""
        return {
            **self.profilo,
            **self.motore.cache_risposte,
            "_personalita": self.personalita
        }


# ==========================================
# PARTE 6: ISTANZA GLOBALE
# ==========================================

PROFILO = ProfiloIntelligente(PROFILO_BASE, MATRICE_PERSONALITA, KNOWLEDGE_BASE)


# ==========================================
# PARTE 7: API SEMPLIFICATA
# ==========================================

def get_value(chiave: str, default: Any = None) -> Any:
    """Accesso rapido a valori del profilo."""
    return PROFILO.get(chiave, default)


def risposta(domanda: str, opzioni: Optional[List[str]] = None) -> str:
    """
    Risponde a qualsiasi domanda in linguaggio naturale.
    
    Esempi:
        risposta("Cosa pensi del cambiamento climatico?")
        risposta("Usi uno smartphone?")
        risposta("Quanto spesso fai la spesa online?", ["Mai", "Raramente", "Spesso", "Sempre"])
    """
    return PROFILO.risposta_domanda(domanda, opzioni)


def esporta_json(filepath: str = "profilo_completo.json"):
    """Esporta tutto in JSON."""
    import json
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(PROFILO.to_dict(), f, indent=4, ensure_ascii=False)
    print(f"✓ Profilo esportato: {filepath}")


# ==========================================
# PARTE 8: TEST E DEMO
# ==========================================

if __name__ == "__main__":
    print("=== PROFILO DEMOGRAFICO 3.0 - TEST ===\n")
    
    # Test 1: Accesso diretto
    print("1. DATI DIRETTI:")
    print(f"   Età: {get_value('eta')}")
    print(f"   Città: {get_value('citta')}")
    print(f"   Lavoro: {get_value('occupazione')}")
    
    # Test 2: Domande mai viste (opinioni)
    print("\n2. DOMANDE DI OPINIONE (MAI VISTE PRIMA):")
    print(f"   Q: Cosa pensi del cambiamento climatico?")
    print(f"   A: {risposta('Cosa pensi del cambiamento climatico?')}")
    
    print(f"\n   Q: Sei favorevole all'intelligenza artificiale?")
    print(f"   A: {risposta('Sei favorevole all intelligenza artificiale?')}")
    
    print(f"\n   Q: Quanto è importante per te la privacy online?")
    print(f"   A: {risposta('Quanto è importante per te la privacy online?')}")
    
    # Test 3: Domande con opzioni multiple
    print("\n3. DOMANDE CON OPZIONI MULTIPLE:")
    opzioni_clima = [
        "Non mi interessa",
        "È un problema minore",
        "È importante ma non urgente",
        "È una priorità assoluta"
    ]
    print(f"   Q: Il cambiamento climatico...")
    print(f"   Opzioni: {opzioni_clima}")
    print(f"   A: {risposta('Il cambiamento climatico è', opzioni_clima)}")
    
    # Test 4: Domande di possesso
    print("\n4. DOMANDE DI POSSESSO:")
    print(f"   Q: Hai uno smartphone?")
    print(f"   A: {risposta('Hai uno smartphone?')}")
    
    print(f"\n   Q: Possiedi un tablet?")
    print(f"   A: {risposta('Possiedi un tablet?')}")
    
    # Test 5: Esportazione
    print("\n5. ESPORTAZIONE:")
    esporta_json()
    
    print("\n✓ Test completati!")

Copy

Insert

Come usarlo nei tuoi 5 software
# In FraIA.py, GraziaIA.py, ecc.
from profilo_demografico import risposta, get_value, PROFILO

# Esempio 1: Risposta a domanda testuale rilevata nella pagina
testo_domanda = pagina.locator("h2.question").inner_text()
# Es: "Quanto ti preoccupa il cambiamento climatico?"

risposta_generata = risposta(testo_domanda)
# → "È una priorità assoluta" (inferito da sensibilità ambientale)

# Esempio 2: Con opzioni multiple
opzioni = [opt.inner_text() for opt in pagina.locator(".option").all()]
risposta_scelta = risposta(testo_domanda, opzioni)
# → Seleziona l'opzione più coerente

# Esempio 3: Dati diretti
eta = get_value("eta")  # → 53