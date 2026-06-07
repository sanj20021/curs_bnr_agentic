# PLAN DE REFACERE CHATBOT (Interactivitate, Estetică și Memorie)

## 1. Analiza Problemei
În prezent, fluxul de tool-calling este "scurtcircuitat" în frontend. Când AI-ul decide să folosească o unealtă (ex: `get_forecast`), frontend-ul prinde acel JSON și aruncă un text uriaș prestabilit (tot array-ul de 7 zile) direct pe ecranul utilizatorului. 
* **Problema estetică:** Un bloc uriaș de text arată foarte aglomerat și neprietenos într-o bulă mică de chat.
* **Problema logică:** AI-ul nu ajunge niciodată să "citească" datele extrase pentru a formula un răspuns scurt și la obiect (ex: "Pe 10 iunie cursul va fi X"), pentru că frontend-ul îi "fură" răspunsul.

## 2. Soluția: Bucla Agentică Reală (2-Step Process)
Vom implementa un comportament veritabil de agent:
1. **Pasul 1:** Utilizatorul întreabă "Cât e prognoza pe 10?".
2. **Pasul 2:** AI-ul răspunde cu `{"tool": "get_forecast"}`.
3. **Pasul 3 (Silent):** Frontend-ul execută funcția, dar **nu** îi mai afișează utilizatorului datele brute. În schimb, trimite un al doilea request invizibil către AI, conținând datele cerute (ex: `[{"Data": "2026-06-10", "Predictie": 1.2264}]`).
4. **Pasul 4:** AI-ul procesează datele primite și generează un răspuns natural, scurt și estetic pentru utilizator: *"Prognoza pentru data de 10 iunie este 1.2264 RON."*

## 3. Implementarea Memoriei și Butonului de Clear (Frontend)
### 3.1. Memorie Persistență
- Vom modifica starea `messages` din `App.jsx` să se inițializeze din `localStorage`.
- La fiecare mesaj nou, array-ul va fi salvat în `localStorage`. Astfel, la darea unui refresh, conversația nu se pierde.

### 3.2. Buton de Clear Chat
- În header-ul ferestrei de chat (lângă rotița de setări), vom adăuga o iconiță discretă de coș de gunoi (Trash/Clear).
- La apăsare, va șterge conversația din `localStorage` și va reseta array-ul de `messages` la starea inițială (mesajul de salut).

## 4. Pașii exacți de urmat în cod
1. **`frontend/src/App.jsx`**:
   - Import `Trash2` din `lucide-react`.
   - Modificarea `useState`-ului pentru `messages` ca să citească din `localStorage`.
   - Adăugarea funcției `clearChat()`.
   - Rescrierea funcției `handleChatSubmit`: în loc să adauge conținut în UI la un `TOOL CALL`, va adăuga un mesaj invizibil în istoric și va re-apela `fetch('/api/chat')` cu datele injectate, lăsând AI-ul să dea verdictul final.
2. **`src/api/server.py`**:
   - Vom ajusta subtil prompt-ul sistemului pentru a-i spune AI-ului: *"Dacă ai chemat un tool, vei primi datele înapoi. Formulează un răspuns scurt, clar și la obiect pentru utilizator pe baza lor."*

---
*Proiect realizat de: Cristian Antonescu*
