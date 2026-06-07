"""
model_utils.py – Agent BNR cu Tool Calling local

Demonstrează cum o funcție Python locală poate fi înregistrată ca
"tool" pe care modelul Gemini îl apelează automat atunci când consideră
necesar pentru a rezolva o sarcină.

Flux agentic (ReAct-style):
  1. Utilizatorul trimite un mesaj natural (ex: "Care e cursul actual USD?")
  2. Modelul decide → emite un FunctionCall (nu text direct)
  3. Codul local execută funcția corespunzătoare
  4. Rezultatul e trimis înapoi ca FunctionResponse
  5. Modelul formulează răspunsul final în limbaj natural
  Pașii 2-4 se repetă până modelul nu mai cere niciun tool.

Rulare rapidă (demo):
    python -m curs_bnr.model_utils

Setare cheie API:
    $env:GEMINI_API_KEY = "cheia_ta"   # PowerShell
    export GEMINI_API_KEY="cheia_ta"   # bash
"""

from __future__ import annotations

import json
import os
from typing import Any

import requests

# ── Configurare ──────────────────────────────────────────────────────────────
BACKEND_URL = os.getenv("BNR_BACKEND_URL", "http://localhost:7772")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ═════════════════════════════════════════════════════════════════════════════
# SECȚIUNEA 1: Funcțiile locale (viitoarele "tools")
# Acestea sunt funcții Python obișnuite – pot accesa DB, API, fișiere etc.
# ═════════════════════════════════════════════════════════════════════════════

def get_latest_exchange_rate() -> dict[str, Any]:
    """
    Returnează cel mai recent curs USD/RON din baza de date locală.
    Tool folosit când utilizatorul întreabă despre cursul curent.
    """
    try:
        r = requests.get(f"{BACKEND_URL}/api/rates", timeout=10)
        r.raise_for_status()
        rates = r.json()
        if rates:
            latest = rates[-1]
            return {
                "success": True,
                "date": latest["date"],
                "value": latest["value"],
                "currency": "USD/RON",
            }
        return {"success": False, "error": "Nu există date în baza de date."}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def get_forecast_summary() -> dict[str, Any]:
    """
    Returnează prognoza curentă și modelul câștigător (cel cu MAE minim).
    Tool folosit când utilizatorul întreabă despre prognoze viitoare.
    """
    try:
        r = requests.get(f"{BACKEND_URL}/api/forecast/latest", timeout=10)
        r.raise_for_status()
        data = r.json()
        if not data:
            return {"success": False, "error": "Nu există prognoze disponibile."}

        forecasts = data.get("forecasts", [])
        preview = forecasts[:3] if forecasts else []  # primele 3 zile

        return {
            "success": True,
            "winner_model": data.get("winner_model"),
            "winner_mae": round(data.get("winner_mae", 0), 4),
            "next_days_preview": [
                {"date": f["forecast_date"], "predicted": round(f["predicted_value"], 4)}
                for f in preview
            ],
        }
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def get_model_metrics() -> dict[str, Any]:
    """
    Returnează metricile (MAE, RMSE, MAPE) pentru toate modelele din ultima rulare.
    Tool folosit când utilizatorul compară performanța modelelor.
    """
    try:
        r = requests.get(f"{BACKEND_URL}/api/runs?limit=1", timeout=10)
        r.raise_for_status()
        runs = r.json()
        if not runs:
            return {"success": False, "error": "Nu există rulări de antrenare."}

        latest = runs[0]
        return {
            "success": True,
            "run_date": latest.get("run_at", "")[:19].replace("T", " "),
            "method": latest.get("method"),
            "winner": latest.get("winner_model"),
            "models": [
                {
                    "name": res["model_name"],
                    "mae": round(res["mae"], 4),
                    "rmse": round(res["rmse"], 4),
                    "mape_pct": round(res["mape"], 2),
                }
                for res in sorted(latest.get("results", []), key=lambda x: x["mae"])
            ],
        }
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def trigger_scrape(currency_code: str = "USD", start_date: str = "22/02/2020") -> dict[str, Any]:
    """
    Declanșează scraping-ul datelor BNR pentru a actualiza cursurile istorice.
    Tool folosit când utilizatorul cere actualizarea datelor.

    Args:
        currency_code: Codul valutei (ex: "USD", "EUR").
        start_date: Data de start în format DD/MM/YYYY.
    """
    try:
        r = requests.post(
            f"{BACKEND_URL}/api/scrape",
            json={"currency_code": currency_code, "start_date": start_date},
            timeout=60,
        )
        r.raise_for_status()
        return {"success": True, "message": r.json().get("message", "Scraping complet.")}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


# ═════════════════════════════════════════════════════════════════════════════
# SECȚIUNEA 2: Registrul de tools
# Mapare nume_tool → funcție locală + schemă pentru model
# ═════════════════════════════════════════════════════════════════════════════

# Dicționar: numele tool-ului → funcția Python locală
TOOL_REGISTRY: dict[str, callable] = {
    "get_latest_exchange_rate": get_latest_exchange_rate,
    "get_forecast_summary": get_forecast_summary,
    "get_model_metrics": get_model_metrics,
    "trigger_scrape": trigger_scrape,
}

# Schema JSON pe care o primește modelul (ce tools are disponibile și cum să le apeleze)
TOOLS_SCHEMA = [
    {
        "name": "get_latest_exchange_rate",
        "description": (
            "Returnează cel mai recent curs USD/RON disponibil în baza de date locală. "
            "Folosește acest tool când utilizatorul întreabă despre cursul curent sau ultimul curs disponibil."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_forecast_summary",
        "description": (
            "Returnează prognoza cursului USD/RON pentru zilele următoare, "
            "inclusiv modelul cu cea mai mică eroare (MAE). "
            "Folosește acest tool când utilizatorul întreabă despre predicții sau evoluție viitoare."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_model_metrics",
        "description": (
            "Returnează metricile de performanță (MAE, RMSE, MAPE) pentru toate modelele "
            "din ultima rulare de antrenare. "
            "Folosește când utilizatorul compară modele sau întreabă despre acuratețe."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "trigger_scrape",
        "description": (
            "Declanșează actualizarea datelor istorice BNR prin scraping. "
            "Folosește când utilizatorul cere date noi sau actualizarea bazei de date."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "currency_code": {
                    "type": "string",
                    "description": "Codul valutei de scrapat (ex: 'USD', 'EUR'). Default: 'USD'.",
                },
                "start_date": {
                    "type": "string",
                    "description": "Data de start în format DD/MM/YYYY. Default: '22/02/2020'.",
                },
            },
            "required": [],
        },
    },
]


# ═════════════════════════════════════════════════════════════════════════════
# SECȚIUNEA 3: Executorul de tool calls
# Primește cererea modelului, execută funcția locală, returnează rezultatul
# ═════════════════════════════════════════════════════════════════════════════

def execute_tool_call(tool_name: str, tool_args: dict[str, Any]) -> str:
    """
    Execută funcția locală corespunzătoare tool_name cu argumentele primite.

    Args:
        tool_name: Numele tool-ului cerut de model.
        tool_args: Dicționarul de argumente extras din cererea modelului.

    Returns:
        String JSON cu rezultatul – acesta va fi trimis înapoi modelului.
    """
    func = TOOL_REGISTRY.get(tool_name)
    if func is None:
        result = {"error": f"Tool necunoscut: '{tool_name}'"}
    else:
        try:
            result = func(**tool_args)
        except TypeError as exc:
            result = {"error": f"Argumente invalide pentru '{tool_name}': {exc}"}
        except Exception as exc:
            result = {"error": f"Eroare la execuția '{tool_name}': {exc}"}

    return json.dumps(result, ensure_ascii=False)


# ═════════════════════════════════════════════════════════════════════════════
# SECȚIUNEA 4: Agentic Loop – Gemini cu Function Calling
# ═════════════════════════════════════════════════════════════════════════════

def run_bnr_agent(user_message: str, verbose: bool = True) -> str:
    """
    Rulează un agent Gemini care poate apela tools locale pentru a răspunde.

    Fluxul (ReAct-style):
        User message
          └─► Model gândește → FunctionCall?
                ├─ DA  → execută funcția locală → trimite FunctionResponse → repetă
                └─ NU  → returnează textul final

    Args:
        user_message: Întrebarea sau sarcina utilizatorului în limbaj natural.
        verbose: Dacă True, afișează pașii intermediari (gândire + tool calls).

    Returns:
        Răspunsul final al agentului în limbaj natural.

    Raises:
        ImportError: Dacă pachetul google-generativeai nu este instalat.
        ValueError: Dacă GEMINI_API_KEY nu este setat.
    """
    try:
        import google.generativeai as genai
        from google.generativeai.types import FunctionDeclaration, Tool
    except ImportError as exc:
        raise ImportError(
            "Instalează pachetul: pip install google-generativeai"
        ) from exc

    if not GEMINI_API_KEY:
        raise ValueError(
            "Setează variabila de mediu GEMINI_API_KEY înainte de a rula agentul."
        )

    # ── Configurare model ────────────────────────────────────────────────────
    genai.configure(api_key=GEMINI_API_KEY)

    # Construiește declarațiile de funcții din schema noastră
    function_declarations = [
        FunctionDeclaration(
            name=tool["name"],
            description=tool["description"],
            parameters=tool["parameters"],
        )
        for tool in TOOLS_SCHEMA
    ]

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        tools=[Tool(function_declarations=function_declarations)],
        system_instruction=(
            "Ești un asistent specializat în analiza cursului valutar USD/RON "
            "furnizat de Banca Națională a României (BNR). "
            "Folosești tools disponibile pentru a obține date reale din sistem "
            "înainte de a formula răspunsuri. "
            "Răspunde concis, în română, cu date concrete."
        ),
    )

    # ── Agentic Loop ─────────────────────────────────────────────────────────
    chat = model.start_chat(enable_automatic_function_calling=False)
    messages = [user_message]

    # Trimitere mesaj inițial
    response = chat.send_message(user_message)
    iteration = 0
    MAX_ITERATIONS = 5  # protecție anti-buclă infinită

    while iteration < MAX_ITERATIONS:
        iteration += 1
        candidate = response.candidates[0]
        content = candidate.content

        # Verifică dacă există FunctionCall-uri în răspuns
        function_calls = [
            part.function_call
            for part in content.parts
            if hasattr(part, "function_call") and part.function_call.name
        ]

        if not function_calls:
            # Modelul nu mai cere niciun tool → răspuns final
            final_text = "".join(
                part.text for part in content.parts if hasattr(part, "text")
            )
            if verbose:
                print(f"\n✅ Răspuns final după {iteration - 1} tool call(uri).")
            return final_text.strip()

        # Procesează fiecare FunctionCall cerut de model
        function_responses = []
        for fc in function_calls:
            tool_name = fc.name
            tool_args = dict(fc.args)  # proto MapComposite → dict

            if verbose:
                print(f"\n🔧 Model apelează tool: '{tool_name}' cu args: {tool_args}")

            # ← EXECUȚIE LOCALĂ a funcției Python
            result_json = execute_tool_call(tool_name, tool_args)

            if verbose:
                print(f"   └─ Rezultat: {result_json[:200]}...")

            function_responses.append(
                genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=tool_name,
                        response={"result": json.loads(result_json)},
                    )
                )
            )

        # Trimite toate rezultatele înapoi la model
        response = chat.send_message(function_responses)

    return "⚠️ Agentul a depășit numărul maxim de iterații fără un răspuns final."


# ═════════════════════════════════════════════════════════════════════════════
# SECȚIUNEA 5: Demo CLI
# python -m curs_bnr.model_utils
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("  BNR Agent – Demo Tool Calling")
    print("=" * 60)

    # Exemple de întrebări – modelul decide singur ce tool să apeleze
    demo_questions = [
        "Care este cursul USD/RON de azi?",
        "Ce model face cea mai bună prognoză și care e eroarea lui?",
        "Compară performanța tuturor modelelor antrenate.",
    ]

    for question in demo_questions:
        print(f"\n{'─' * 60}")
        print(f"👤 Utilizator: {question}")
        print(f"{'─' * 60}")
        try:
            answer = run_bnr_agent(question, verbose=True)
            print(f"\n🤖 Agent: {answer}")
        except (ImportError, ValueError) as e:
            print(f"⚠️  Configurare necesară: {e}")
            break
