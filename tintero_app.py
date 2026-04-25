# tintero_app.py — CustomTkinter v3
# pip install customtkinter pillow
# python tintero_app.py

import customtkinter as ctk
from tkinter import messagebox
import sqlite3, json, sys, os
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────

# Carpeta donde vive el .exe (o el script en desarrollo)
if getattr(sys, "frozen", False):
    # Ejecutable compilado con PyInstaller
    _EXE_DIR = Path(sys.executable).parent
else:
    # Script en desarrollo
    _EXE_DIR = Path(__file__).parent

# Datos escribibles: junto al .exe si se puede, si no en APPDATA
def _get_data_dir() -> Path:
    """Devuelve una carpeta donde siempre se puede escribir."""
    # Primero intentamos junto al .exe (instalación en carpeta propia, portable)
    candidate = _EXE_DIR
    try:
        candidate.mkdir(parents=True, exist_ok=True)
        test = candidate / ".write_test"
        test.touch()
        test.unlink()
        return candidate
    except OSError:
        pass
    # Fallback: AppData\Roaming\ElTintero  (siempre escribible en Windows)
    appdata = Path(os.environ.get("APPDATA", Path.home())) / "ElTintero"
    appdata.mkdir(parents=True, exist_ok=True)
    return appdata

_DATA_DIR  = _get_data_dir()
DB_PATH    = str(_DATA_DIR / "tintero.db")
CFG_PATH   = _DATA_DIR / "tintero_config.json"

# Assets (solo lectura, siempre junto al .exe)
ASSETS = _EXE_DIR / "assets"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# ── Paleta ────────────────────────────────────
C_NAVY   = "#1C223A"
C_NAVY2  = "#242b47"
C_CARD   = "#2d3657"
C_CARD2  = "#1e2840"
C_GOLD   = "#EDA745"
C_CREAM  = "#F0EADC"
C_MUTED  = "#8892b0"
C_GREEN  = "#4caf82"
C_RED    = "#e05c5c"
C_BLUE   = "#5b9bd5"
C_ORANGE = "#e0903a"
C_LINE   = "#2e3a5c"   # separadores sutiles

# ── Tipografía ────────────────────────────────
# Cormorant Garamond: elegante, literario, serif de alta calidad
# Nunito: redondo, legible, moderno sin ser genérico
# Si no están instaladas, cae en Georgia / Helvetica gracefully
FONT_DISPLAY = "Cormorant Garamond"   # títulos, headings
FONT_BODY    = "Nunito"               # UI general
FONT_MONO    = "Consolas"             # datos numéricos

def F(size, weight="normal", family=FONT_BODY):
    """Shorthand para CTkFont con fallback."""
    return ctk.CTkFont(family=family, size=size,
                       weight="bold" if weight=="bold" else "normal")

def F_title(size=18): return F(size, "bold", FONT_DISPLAY)
def F_body(size=13):  return F(size, "normal", FONT_BODY)
def F_bold(size=13):  return F(size, "bold",   FONT_BODY)
def F_data(size=13):  return F(size, "normal", FONT_MONO)

# ── Config helpers ────────────────────────────
def _load_cfg() -> dict:
    if CFG_PATH.exists():
        try: return json.loads(CFG_PATH.read_text("utf-8"))
        except: pass
    return {}

def _save_cfg(d: dict):
    CFG_PATH.write_text(json.dumps(d, indent=2, ensure_ascii=False), "utf-8")

def get_password() -> str:
    return _load_cfg().get("password", "")

def set_password(pw: str):
    d = _load_cfg(); d["password"] = pw; _save_cfg(d)

def is_first_run() -> bool:
    return get_password() == ""

# ── Color utils ───────────────────────────────
def _dark(h):
    r,g,b=int(h[1:3],16),int(h[3:5],16),int(h[5:7],16)
    return "#{:02x}{:02x}{:02x}".format(max(0,r-28),max(0,g-28),max(0,b-28))

def _alpha_blend(fg, bg, alpha=0.15):
    """Simula color con opacidad sobre fondo."""
    fr,fg2,fb=int(fg[1:3],16),int(fg[3:5],16),int(fg[5:7],16)
    br,bg3,bb=int(bg[1:3],16),int(bg[3:5],16),int(bg[5:7],16)
    return "#{:02x}{:02x}{:02x}".format(
        int(fr*alpha+br*(1-alpha)), int(fg2*alpha+bg3*(1-alpha)), int(fb*alpha+bb*(1-alpha)))

# ──────────────────────────────────────────────
# HELPERS UI
# ──────────────────────────────────────────────
def lbl(p, text, size=13, color=C_CREAM, bold=False, family=FONT_BODY, **kw):
    return ctk.CTkLabel(p, text=text, text_color=color,
                        font=F(size, "bold" if bold else "normal", family), **kw)

def title_lbl(p, text, size=20, color=C_CREAM, **kw):
    """Label con fuente display (Cormorant Garamond)."""
    return ctk.CTkLabel(p, text=text, text_color=color, font=F_title(size), **kw)

def inp(p, ph="", w=220, **kw):
    return ctk.CTkEntry(p, placeholder_text=ph, width=w,
                        fg_color=C_CARD2, border_color=C_LINE,
                        text_color=C_CREAM, placeholder_text_color=C_MUTED,
                        font=F_body(13), **kw)

def combo(p, vals, w=200, **kw):
    return ctk.CTkComboBox(p, values=vals, width=w,
                           fg_color=C_CARD2, border_color=C_LINE,
                           button_color=C_CARD, dropdown_fg_color=C_CARD,
                           text_color=C_CREAM, dropdown_text_color=C_CREAM,
                           font=F_body(13), dropdown_font=F_body(13), **kw)

def pbtn(p, text, cmd, color=C_GOLD, w=160):
    return ctk.CTkButton(p, text=text, command=cmd, width=w,
                         fg_color=color, hover_color=_dark(color),
                         text_color=C_NAVY, corner_radius=8,
                         font=F_bold(13))

def gbtn(p, text, cmd, color=C_MUTED, w=110):
    return ctk.CTkButton(p, text=text, command=cmd, width=w, height=28,
                         fg_color="transparent", hover_color=C_CARD,
                         text_color=color, border_width=1, border_color=color,
                         corner_radius=6, font=F_body(12))

def sep(p):
    return ctk.CTkFrame(p, height=1, fg_color=C_LINE)

def cframe(p, **kw):
    return ctk.CTkFrame(p, fg_color=C_CARD2, corner_radius=10, **kw)

def sframe(p, **kw):
    return ctk.CTkScrollableFrame(p, fg_color="transparent",
                                  scrollbar_button_color=C_CARD,
                                  scrollbar_button_hover_color=C_MUTED, **kw)

def accentbar(p, color=C_GOLD, h=3):
    """Barra decorativa de acento."""
    return ctk.CTkFrame(p, height=h, fg_color=color, corner_radius=2)

def load_logo(fn, sz=(50,50)):
    if not HAS_PIL: return None
    pp = ASSETS / fn
    if not pp.exists(): return None
    try:
        img = Image.open(pp)
        return ctk.CTkImage(light_image=img, dark_image=img, size=sz)
    except: return None

def row(p, **kw):
    return ctk.CTkFrame(p, fg_color="transparent", **kw)

# ──────────────────────────────────────────────
# DATABASE
# ──────────────────────────────────────────────
SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL, email TEXT, phone TEXT, notes TEXT,
    active INTEGER DEFAULT 1, student_type TEXT DEFAULT 'taller',
    skill_writing INTEGER DEFAULT 0,
    skill_redaction INTEGER DEFAULT 0,
    skill_plot INTEGER DEFAULT 0,
    skill_correction INTEGER DEFAULT 0,
    enfoque_scores TEXT DEFAULT '{}',
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL, date TEXT NOT NULL,
    concept TEXT NOT NULL, amount REAL NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('ingreso','egreso')),
    FOREIGN KEY(student_id) REFERENCES students(id)
);
CREATE TABLE IF NOT EXISTS stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL, title TEXT NOT NULL,
    genre TEXT, status TEXT DEFAULT 'borrador', feedback TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(student_id) REFERENCES students(id)
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL, date TEXT NOT NULL, time TEXT,
    location TEXT, description TEXT, event_type TEXT DEFAULT 'evento'
);
CREATE TABLE IF NOT EXISTS copy_clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL, email TEXT, phone TEXT, company TEXT,
    notes TEXT, active INTEGER DEFAULT 1, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS copy_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER, title TEXT NOT NULL, description TEXT,
    status TEXT DEFAULT 'pendiente', due_date TEXT, created_at TEXT NOT NULL,
    FOREIGN KEY(client_id) REFERENCES copy_clients(id)
);
"""

MIGRATE_SQL = [
    "ALTER TABLE students ADD COLUMN student_type TEXT DEFAULT 'taller'",
    "ALTER TABLE students ADD COLUMN skill_writing INTEGER DEFAULT 0",
    "ALTER TABLE students ADD COLUMN skill_redaction INTEGER DEFAULT 0",
    "ALTER TABLE students ADD COLUMN skill_plot INTEGER DEFAULT 0",
    "ALTER TABLE students ADD COLUMN skill_correction INTEGER DEFAULT 0",
    "ALTER TABLE students ADD COLUMN enfoque_scores TEXT DEFAULT '{}'",
]

class DB:
    def __init__(self):
        with sqlite3.connect(DB_PATH) as c:
            c.executescript(SCHEMA)
        # safe migrations
        with sqlite3.connect(DB_PATH) as c:
            for sql in MIGRATE_SQL:
                try: c.execute(sql)
                except: pass

    def q(self, sql, p=()):
        with sqlite3.connect(DB_PATH) as c:
            c.row_factory = sqlite3.Row
            return c.execute(sql, p).fetchall()

    def run(self, sql, p=()):
        with sqlite3.connect(DB_PATH) as c:
            c.execute(sql, p)

    # ── Students ──────────────────────────────
    def list_students(self, stype=None):
        if stype:
            return self.q("SELECT * FROM students WHERE student_type=? ORDER BY name", (stype,))
        return self.q("SELECT * FROM students ORDER BY name")

    def add_student(self, name, email, phone, notes, active, stype="taller"):
        self.run(
            "INSERT INTO students(name,email,phone,notes,active,student_type,created_at) VALUES(?,?,?,?,?,?,?)",
            (name,email,phone,notes,int(active),stype,datetime.utcnow().isoformat()))

    def update_student(self, sid, name, email, phone, notes, active):
        self.run("UPDATE students SET name=?,email=?,phone=?,notes=?,active=? WHERE id=?",
                 (name,email,phone,notes,int(active),sid))

    def delete_student(self, sid):
        self.run("DELETE FROM students WHERE id=?", (sid,))

    def update_skills(self, sid, writing, redaction, plot, correction):
        self.run("UPDATE students SET skill_writing=?,skill_redaction=?,skill_plot=?,skill_correction=? WHERE id=?",
                 (writing,redaction,plot,correction,sid))

    def update_enfoque(self, sid, scores: dict):
        self.run("UPDATE students SET enfoque_scores=? WHERE id=?",
                 (json.dumps(scores), sid))

    def get_student(self, sid):
        rows = self.q("SELECT * FROM students WHERE id=?", (sid,))
        return rows[0] if rows else None

    # ── Accounts ──────────────────────────────
    def list_accounts(self, student_id):
        return self.q("SELECT * FROM accounts WHERE student_id=? ORDER BY date DESC", (student_id,))

    def add_account(self, student_id, date, concept, amount, atype):
        self.run("INSERT INTO accounts(student_id,date,concept,amount,type) VALUES(?,?,?,?,?)",
                 (student_id,date,concept,amount,atype))

    def balance(self, student_id):
        rows = self.list_accounts(student_id)
        return sum(r["amount"]*(1 if r["type"]=="ingreso" else -1) for r in rows)

    # ── Stories ───────────────────────────────
    def list_stories(self, student_id=None):
        base = ("SELECT s.*,st.name as student_name FROM stories s "
                "JOIN students st ON s.student_id=st.id")
        if student_id:
            return self.q(base+" WHERE s.student_id=? ORDER BY s.created_at DESC",(student_id,))
        return self.q(base+" ORDER BY s.created_at DESC")

    def add_story(self, student_id, title, genre, status, feedback):
        self.run("INSERT INTO stories(student_id,title,genre,status,feedback,created_at) VALUES(?,?,?,?,?,?)",
                 (student_id,title,genre,status,feedback,datetime.utcnow().isoformat()))

    def update_story(self, sid, title, genre, status, feedback):
        self.run("UPDATE stories SET title=?,genre=?,status=?,feedback=? WHERE id=?",
                 (title,genre,status,feedback,sid))

    def delete_story(self, sid):
        self.run("DELETE FROM stories WHERE id=?", (sid,))

    # ── Events ────────────────────────────────
    def list_events(self):
        return self.q("SELECT * FROM events ORDER BY date ASC, time ASC")

    def add_event(self, title, date, time, location, desc, etype):
        self.run("INSERT INTO events(title,date,time,location,description,event_type) VALUES(?,?,?,?,?,?)",
                 (title,date,time,location,desc,etype))

    def delete_event(self, eid):
        self.run("DELETE FROM events WHERE id=?", (eid,))

    # ── Copy clients ──────────────────────────
    def list_copy_clients(self):
        return self.q("SELECT * FROM copy_clients ORDER BY name")

    def add_copy_client(self, name, email, phone, company, notes):
        self.run("INSERT INTO copy_clients(name,email,phone,company,notes,active,created_at) VALUES(?,?,?,?,?,1,?)",
                 (name,email,phone,company,notes,datetime.utcnow().isoformat()))

    def update_copy_client(self, cid, name, email, phone, company, notes, active):
        self.run("UPDATE copy_clients SET name=?,email=?,phone=?,company=?,notes=?,active=? WHERE id=?",
                 (name,email,phone,company,notes,int(active),cid))

    # ── Copy tasks ────────────────────────────
    def list_copy_tasks(self):
        return self.q("SELECT t.*,c.name as client_name FROM copy_tasks t "
                      "LEFT JOIN copy_clients c ON t.client_id=c.id ORDER BY t.due_date ASC")

    def add_copy_task(self, client_id, title, desc, status, due_date):
        self.run("INSERT INTO copy_tasks(client_id,title,description,status,due_date,created_at) VALUES(?,?,?,?,?,?)",
                 (client_id or None,title,desc,status,due_date,datetime.utcnow().isoformat()))

    def set_task_status(self, tid, status):
        self.run("UPDATE copy_tasks SET status=? WHERE id=?", (status,tid))

    def delete_copy_task(self, tid):
        self.run("DELETE FROM copy_tasks WHERE id=?", (tid,))


# ══════════════════════════════════════════════
# MODAL BASE
# ══════════════════════════════════════════════
class Modal(ctk.CTkToplevel):
    def __init__(self, parent, title, w=440, h=520):
        super().__init__(parent)
        self.title(title)
        self.geometry(f"{w}x{h}")
        self.configure(fg_color=C_NAVY2)
        self.grab_set(); self.resizable(False,False)
        self.body = sframe(self)
        self.body.pack(fill="both", expand=True, padx=14, pady=14)


# ══════════════════════════════════════════════
# TEST DE LOS 6 ENFOQUES (basado en Di Marco)
# ══════════════════════════════════════════════
# Las preguntas están inspiradas en los conceptos del Taller de corte y corrección:
# claridad expresiva, imagen, musicalidad, análisis, argumentación, reflexión.
ENFOQUE_QUESTIONS = [
    {
        "q": "Cuando leés literatura, ¿qué es lo que más te atrapa?",
        "opts": [
            ("La historia y lo que les pasa a los personajes",        {"narrativa": 2}),
            ("Los ritmos, las palabras elegidas, la musicalidad",     {"estetica": 2}),
            ("Las ideas que el autor desarrolla y defiende",          {"ensayo": 1, "persuasion": 1}),
            ("Los datos curiosos o la forma en que explica el mundo", {"erudicion": 2}),
        ]
    },
    {
        "q": "Hemingway decía: 'Escribir es sobre todo corregir'. Para vos, corregir es...",
        "opts": [
            ("Ajustar la trama para que fluya mejor",           {"narrativa": 2}),
            ("Pulir cada frase hasta que suene perfecta",        {"estetica": 2}),
            ("Fortalecer el argumento y la lógica del texto",    {"ensayo": 1, "persuasion": 1}),
            ("Verificar que los hechos y referencias sean exactos", {"erudicion": 2}),
        ]
    },
    {
        "q": "Di Marco insiste en 'escribir todos los días'. ¿Sobre qué escribirías hoy?",
        "opts": [
            ("Un personaje que conocí y me resultó fascinante",    {"narrativa": 2}),
            ("Una imagen o sensación que me quedó grabada",        {"estetica": 2}),
            ("Mi opinión sobre algo que me parece injusto",        {"persuasion": 2}),
            ("Algo que aprendí recientemente y quiero registrar",  {"erudicion": 2}),
        ]
    },
    {
        "q": "Di Marco propone: 'Ver, ver, ver'. ¿Qué tipo de observación hacés naturalmente?",
        "opts": [
            ("Noto los gestos y comportamientos de la gente",      {"narrativa": 2}),
            ("Me detengo en colores, formas, luces",               {"estetica": 2}),
            ("Analizo por qué las cosas funcionan de cierta forma",{"ensayo": 1, "erudicion": 1}),
            ("Busco causas y consecuencias de lo que observo",     {"persuasion": 1, "reflexion": 1}),
        ]
    },
    {
        "q": "Al escribir un texto, ¿cuándo sentís que 'funcionó'?",
        "opts": [
            ("Cuando el lector quiere saber qué pasa después",     {"narrativa": 2}),
            ("Cuando cada frase tiene su propio sonido y belleza",  {"estetica": 2}),
            ("Cuando logré convencer al lector de mi punto",        {"persuasion": 2}),
            ("Cuando transmití algo verdadero e iluminador",        {"reflexion": 2}),
        ]
    },
    {
        "q": "Para Borges el genio era 'hacer fácil lo difícil'. ¿Cómo lo intentás vos?",
        "opts": [
            ("Creando situaciones que hablen por sí solas",           {"narrativa": 2}),
            ("Eligiendo la metáfora exacta",                          {"estetica": 2}),
            ("Ordenando las ideas de lo simple a lo complejo",        {"ensayo": 2}),
            ("Apoyándome en ejemplos concretos y referencias",        {"erudicion": 2}),
        ]
    },
    {
        "q": "¿Con qué tipo de escritores te identificás más?",
        "opts": [
            ("Narradores: Borges, Quiroga, Cortázar",                 {"narrativa": 3}),
            ("Poetas: Neruda, Storni, Girondo",                       {"estetica": 3}),
            ("Ensayistas: Sábato, Martínez Estrada, Piglia",          {"ensayo": 2, "reflexion": 1}),
            ("Divulgadores: Sagan, Asimov, Gombrowicz",               {"erudicion": 3}),
        ]
    },
    {
        "q": "Di Marco habla de 'limpiar el texto de ripios'. ¿Cuál es tu mayor tentación al escribir?",
        "opts": [
            ("Agregar más escenas o situaciones a la historia",       {"narrativa": 2}),
            ("Quedarse en la belleza de una frase aunque no aporte",  {"estetica": 2}),
            ("Añadir demasiados argumentos o citas",                  {"ensayo": 1, "erudicion": 1}),
            ("Reflexionar demasiado y perder el hilo",                {"reflexion": 2}),
        ]
    },
    {
        "q": "Si tuvieras que elegir, tu texto ideal sería...",
        "opts": [
            ("Un cuento con personajes memorables y giro final",       {"narrativa": 3}),
            ("Un poema o prosa poética que perdure en la memoria",     {"estetica": 3}),
            ("Un ensayo que cambie la manera de ver algo",             {"ensayo": 2, "reflexion": 1}),
            ("Un artículo de divulgación riguroso y apasionante",      {"erudicion": 3}),
        ]
    },
    {
        "q": "Cuando algo te genera una emoción fuerte, ¿cómo lo procesás escribiendo?",
        "opts": [
            ("Lo convierto en ficción, en un personaje o situación",  {"narrativa": 2}),
            ("Lo transformo en imagen o fragmento poético",           {"estetica": 2}),
            ("Escribo mis opiniones y trato de entenderlo",           {"persuasion": 1, "reflexion": 1}),
            ("Busco información, lo contrasto con otros casos",       {"erudicion": 2}),
        ]
    },
]

ENFOQUES = {
    "narrativa":   ("Narrativa",              C_GOLD),
    "estetica":    ("Estética / Poesía",       C_BLUE),
    "ensayo":      ("Ensayo / Opinión",        C_GREEN),
    "erudicion":   ("Erudición / Divulgación", C_ORANGE),
    "persuasion":  ("Persuasión / Retórica",   "#c47fc4"),
    "reflexion":   ("Reflexión",               C_MUTED),
}

class TestEnfoque(Modal):
    """Test de los 6 enfoques basado en la metodología de Di Marco."""
    def __init__(self, parent, db: DB, student_id: int, on_done=None):
        super().__init__(parent, "Test de Enfoques — Di Marco", w=560, h=580)
        self.db = db
        self.student_id = student_id
        self.on_done = on_done
        self.scores = {k: 0 for k in ENFOQUES}
        self.current = 0
        self._build()
        self._show_q()

    def _build(self):
        r = self.db.get_student(self.student_id)
        lbl(self.body, f"Alumno: {r['name']}", bold=True, size=15, color=C_GOLD).pack(anchor="w", pady=(0,4))
        lbl(self.body,
            "Respondé con honestidad. No hay respuestas correctas o incorrectas.\n"
            "El test revela hacia qué tipo de escritura te inclinás naturalmente.",
            color=C_MUTED, size=12, wraplength=510).pack(anchor="w", pady=(0,10))
        sep(self.body).pack(fill="x", pady=4)

        self.progress_lbl = lbl(self.body, "", color=C_MUTED, size=12)
        self.progress_lbl.pack(anchor="e")
        self.progress_bar = ctk.CTkProgressBar(self.body, width=510,
                                               fg_color=C_CARD, progress_color=C_GOLD)
        self.progress_bar.set(0); self.progress_bar.pack(pady=(2,10))

        self.q_lbl = lbl(self.body, "", bold=True, size=14, wraplength=510)
        self.q_lbl.pack(anchor="w", pady=(0,10))

        self.opts_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        self.opts_frame.pack(fill="x")

    def _show_q(self):
        for w in self.opts_frame.winfo_children(): w.destroy()
        if self.current >= len(ENFOQUE_QUESTIONS):
            self._show_results(); return
        q = ENFOQUE_QUESTIONS[self.current]
        total = len(ENFOQUE_QUESTIONS)
        self.progress_lbl.configure(text=f"Pregunta {self.current+1} de {total}")
        self.progress_bar.set((self.current)/total)
        self.q_lbl.configure(text=q["q"])
        for i, (text, pts) in enumerate(q["opts"]):
            def pick(p=pts):
                for k,v in p.items(): self.scores[k] = self.scores.get(k,0)+v
                self.current += 1
                self._show_q()
            f = cframe(self.opts_frame); f.pack(fill="x", pady=3)
            btn_row = ctk.CTkFrame(f, fg_color="transparent"); btn_row.pack(fill="x", padx=10, pady=6)
            lbl(btn_row, f"{chr(65+i)}. {text}", color=C_CREAM, size=13, wraplength=460).pack(side="left", expand=True, anchor="w")
            gbtn(btn_row, "Elegir", pick, color=C_GOLD, w=80).pack(side="right")

    def _show_results(self):
        self.progress_bar.set(1)
        self.progress_lbl.configure(text="¡Completado!")
        self.q_lbl.configure(text="Tu perfil de escritura según Di Marco:")
        for w in self.opts_frame.winfo_children(): w.destroy()

        total = sum(self.scores.values()) or 1
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        top_key, top_val = sorted_scores[0]

        for key, val in sorted_scores:
            name, color = ENFOQUES[key]
            pct = val/total
            f = ctk.CTkFrame(self.opts_frame, fg_color="transparent"); f.pack(fill="x", pady=2)
            lbl(f, name, color=color, size=12, bold=(key==top_key)).pack(side="left", anchor="w")
            bar = ctk.CTkProgressBar(f, width=260, height=12,
                                     fg_color=C_CARD, progress_color=color)
            bar.set(pct); bar.pack(side="right", padx=4)
            lbl(f, f"{int(pct*100)}%", color=C_MUTED, size=11).pack(side="right")

        top_name = ENFOQUES[top_key][0]
        lbl(self.opts_frame,
            f"\n✦ Tu enfoque dominante es: {top_name}",
            color=C_GOLD, bold=True, size=13).pack(anchor="w", pady=(8,0))

        # guardar en DB
        self.db.update_enfoque(self.student_id, self.scores)
        pbtn(self.opts_frame, "Cerrar", self.destroy).pack(pady=10)
        if self.on_done: self.on_done()


# ══════════════════════════════════════════════
# ALUMNOS TAB
# ══════════════════════════════════════════════
SKILL_LABELS = [
    ("skill_writing",    "Hábito de escritura"),
    ("skill_redaction",  "Redacción congruente"),
    ("skill_plot",       "Construcción de trama"),
    ("skill_correction", "Corrección / Publicación"),
]

class StudentsTab(ctk.CTkFrame):
    def __init__(self, parent, db:DB, stype="taller", accent=C_GOLD, on_change=None):
        super().__init__(parent, fg_color="transparent")
        self.db=db; self.stype=stype; self.accent=accent; self.on_change=on_change
        self._build(); self.reload()

    def _build(self):
        type_label = "Nuevo alumno" if self.stype=="taller" else "Nuevo alumno de edición"
        form = cframe(self); form.pack(fill="x", padx=10, pady=(10,4))
        lbl(form, type_label, size=14, bold=True, color=self.accent).pack(anchor="w", padx=12, pady=(10,4))

        r1=row(form); r1.pack(fill="x", padx=12, pady=2)
        self.e_name  = inp(r1,"Nombre *",200); self.e_name.pack(side="left",padx=(0,8))
        self.e_phone = inp(r1,"Teléfono",150); self.e_phone.pack(side="left")
        r2=row(form); r2.pack(fill="x", padx=12, pady=2)
        self.e_email = inp(r2,"Email",360); self.e_email.pack(side="left")
        r3=row(form); r3.pack(fill="x", padx=12, pady=2)
        self.e_notes = inp(r3,"Notas",360); self.e_notes.pack(side="left")
        r4=row(form); r4.pack(fill="x", padx=12, pady=(4,10))
        self.sw = ctk.CTkSwitch(r4, text="Activo", progress_color=self.accent, text_color=C_CREAM)
        self.sw.select(); self.sw.pack(side="left")
        pbtn(r4, "Guardar", self.save, color=self.accent).pack(side="right")

        sep(self).pack(fill="x", padx=10, pady=4)
        self.list_frame = sframe(self)
        self.list_frame.pack(fill="both", expand=True, padx=8, pady=4)

    def reload(self):
        for w in self.list_frame.winfo_children(): w.destroy()
        for r in self.db.list_students(self.stype):
            bal = self.db.balance(r["id"])
            f = cframe(self.list_frame); f.pack(fill="x", pady=3, padx=4)
            top=row(f); top.pack(fill="x", padx=10, pady=(8,2))
            lbl(top, r["name"], bold=True).pack(side="left")
            lbl(top, "Activo" if r["active"] else "Inactivo",
                color=C_GREEN if r["active"] else C_MUTED, size=11).pack(side="right")
            mid=row(f); mid.pack(fill="x", padx=10, pady=1)
            lbl(mid, r["email"] or "", color=C_MUTED, size=12).pack(side="left")
            lbl(mid, r["phone"] or "", color=C_MUTED, size=12).pack(side="left", padx=6)
            bc = C_GREEN if bal>=0 else C_RED
            lbl(mid, f"Saldo: ${bal:.2f}", color=bc, bold=True, size=12).pack(side="right")

            # Skills bar (solo taller)
            if self.stype == "taller":
                skill_row=row(f); skill_row.pack(fill="x", padx=10, pady=(2,0))
                skills = [r["skill_writing"],r["skill_redaction"],r["skill_plot"],r["skill_correction"]]
                for sk, (_, sk_lbl) in zip(skills, SKILL_LABELS):
                    dot_color = C_GREEN if sk else C_CARD
                    dot = ctk.CTkFrame(skill_row, width=10, height=10,
                                       fg_color=dot_color, corner_radius=5)
                    dot.pack(side="left", padx=2)
                lbl(skill_row, "  habilidades", color=C_MUTED, size=11).pack(side="left")

                # Enfoque dominante
                try:
                    scores = json.loads(r["enfoque_scores"] or "{}")
                    if scores:
                        top_k = max(scores, key=scores.get)
                        top_name, top_color = ENFOQUES[top_k]
                        lbl(skill_row, f"  ✦ {top_name}", color=top_color, size=11).pack(side="left", padx=4)
                except: pass

            btns=row(f); btns.pack(fill="x", padx=10, pady=(2,8))
            rid=r["id"]
            gbtn(btns,"Editar",   lambda rid=rid:self._edit(rid),  color=self.accent).pack(side="left",padx=(0,4))
            gbtn(btns,"Eliminar", lambda rid=rid:self._delete(rid)).pack(side="left", padx=(0,4))
            if self.stype=="taller":
                gbtn(btns,"Habilidades", lambda rid=rid:self._skills(rid), color=C_BLUE).pack(side="left",padx=(0,4))
                gbtn(btns,"Test Enfoques", lambda rid=rid:TestEnfoque(self,self.db,rid,self.reload),
                     color=C_GOLD).pack(side="left")

    def save(self):
        name=self.e_name.get().strip()
        if not name: messagebox.showwarning("Error","Nombre obligatorio"); return
        self.db.add_student(name,self.e_email.get(),self.e_phone.get(),
                            self.e_notes.get(),self.sw.get(),self.stype)
        for e in [self.e_name,self.e_email,self.e_phone,self.e_notes]: e.delete(0,"end")
        self.reload()
        if self.on_change: self.on_change()

    def _edit(self, sid):
        r=self.db.get_student(sid)
        if not r: return
        m=Modal(self,"Editar",w=420,h=400)
        lbl(m.body,"Nombre",size=12,color=C_MUTED).pack(anchor="w")
        en=inp(m.body,w=380); en.pack(pady=(0,6)); en.insert(0,r["name"])
        lbl(m.body,"Email",size=12,color=C_MUTED).pack(anchor="w")
        ee=inp(m.body,w=380); ee.pack(pady=(0,6)); ee.insert(0,r["email"] or "")
        lbl(m.body,"Teléfono",size=12,color=C_MUTED).pack(anchor="w")
        ep=inp(m.body,w=380); ep.pack(pady=(0,6)); ep.insert(0,r["phone"] or "")
        lbl(m.body,"Notas",size=12,color=C_MUTED).pack(anchor="w")
        eno=inp(m.body,w=380); eno.pack(pady=(0,6)); eno.insert(0,r["notes"] or "")
        sw=ctk.CTkSwitch(m.body, text="Activo", progress_color=self.accent, text_color=C_CREAM)
        if r["active"]: sw.select()
        sw.pack(anchor="w",pady=4)
        def ok():
            nm=en.get().strip()
            if not nm: messagebox.showwarning("Error","Nombre requerido"); return
            self.db.update_student(sid,nm,ee.get(),ep.get(),eno.get(),sw.get())
            m.destroy(); self.reload()
            if self.on_change: self.on_change()
        pbtn(m.body,"Actualizar",ok,color=self.accent).pack(pady=8)

    def _delete(self, sid):
        if messagebox.askyesno("Confirmar","¿Eliminar alumno?"):
            self.db.delete_student(sid); self.reload()
            if self.on_change: self.on_change()

    def _skills(self, sid):
        r=self.db.get_student(sid)
        if not r: return
        m=Modal(self,f"Habilidades — {r['name']}",w=400,h=420)
        lbl(m.body,"Nivel de habilidad (Pendiente / Logrado)",
            size=13,bold=True,color=C_GOLD).pack(anchor="w",pady=(0,10))
        lbl(m.body,
            "Basado en la metodología de Di Marco:\ncada habilidad se marca como lograda\ncuando el alumno demuestra dominio consistente.",
            color=C_MUTED,size=12,wraplength=360).pack(anchor="w",pady=(0,10))
        sep(m.body).pack(fill="x",pady=4)
        switches=[]
        for db_col, label in SKILL_LABELS:
            rw=row(m.body); rw.pack(fill="x",pady=4)
            sw=ctk.CTkSwitch(rw, text=label, progress_color=C_GREEN, text_color=C_CREAM,
                             font=ctk.CTkFont(size=13))
            if r[db_col]: sw.select()
            sw.pack(side="left")
            switches.append((db_col,sw))
        def ok():
            vals=[int(sw.get()) for _,sw in switches]
            self.db.update_skills(sid,*vals)
            m.destroy(); self.reload()
        pbtn(m.body,"Guardar",ok,color=C_GREEN).pack(pady=12)


# ══════════════════════════════════════════════
# CUENTAS CORRIENTES
# ══════════════════════════════════════════════
class AccountsTab(ctk.CTkFrame):
    def __init__(self, parent, db:DB, stype="taller"):
        super().__init__(parent, fg_color="transparent")
        self.db=db; self.stype=stype; self.sel_id=None; self._smap={}
        self._build()

    def _build(self):
        top=cframe(self); top.pack(fill="x",padx=10,pady=(10,4))
        title_lbl(top, "Cuenta corriente", size=15, color=C_GOLD).pack(anchor="w",padx=12,pady=(10,4))

        r1=row(top); r1.pack(fill="x",padx=12,pady=2)
        lbl(r1,"Alumno:",size=12,color=C_MUTED).pack(side="left")
        self.dd=combo(r1,[],w=240,command=self._on_sel)
        self.dd.pack(side="left",padx=8)
        self.lbl_bal=lbl(r1,"",color=C_GREEN,bold=True,size=14)
        self.lbl_bal.pack(side="right",padx=12)

        r2=row(top); r2.pack(fill="x",padx=12,pady=2)
        self.e_date=inp(r2,"Fecha (YYYY-MM-DD)",160)
        self.e_date.insert(0,datetime.today().strftime("%Y-%m-%d"))
        self.e_date.pack(side="left",padx=(0,6))
        self.e_concept=inp(r2,"Concepto",190); self.e_concept.pack(side="left",padx=(0,6))
        self.e_amount=inp(r2,"Monto",100);     self.e_amount.pack(side="left",padx=(0,6))
        self.dd_type=combo(r2,["ingreso 💰","egreso 📤"],w=140)
        self.dd_type.set("ingreso 💰"); self.dd_type.pack(side="left")

        r3=row(top); r3.pack(fill="x",padx=12,pady=(4,10))
        pbtn(r3,"Registrar",self.add).pack(side="right")

        sep(self).pack(fill="x",padx=10,pady=4)
        self.list_frame=sframe(self)
        self.list_frame.pack(fill="both",expand=True,padx=8,pady=4)
        self.refresh()

    def refresh(self):
        rows=self.db.list_students(self.stype)
        names=[r["name"] for r in rows]
        self._smap={r["name"]:r["id"] for r in rows}
        self.dd.configure(values=names if names else [""])
        if names:
            self.dd.set(names[0]); self._on_sel(names[0])

    def _on_sel(self, val):
        self.sel_id=self._smap.get(val); self._reload()

    def _reload(self):
        for w in self.list_frame.winfo_children(): w.destroy()
        if not self.sel_id: return
        bal=self.db.balance(self.sel_id)
        bc=C_GREEN if bal>=0 else C_RED
        self.lbl_bal.configure(text=f"Saldo: ${bal:.2f}", text_color=bc)
        for r in self.db.list_accounts(self.sel_id):
            f=cframe(self.list_frame); f.pack(fill="x",pady=2,padx=4)
            rw=row(f); rw.pack(fill="x",padx=10,pady=6)
            lbl(rw,r["concept"],bold=True).pack(side="left")
            lbl(rw,r["date"],color=C_MUTED,size=11).pack(side="left",padx=8)
            sign="+" if r["type"]=="ingreso" else "-"
            c=C_GREEN if r["type"]=="ingreso" else C_RED
            lbl(rw,f"{sign}${r['amount']:.2f}",color=c,bold=True,size=14).pack(side="right")

    def add(self):
        if not self.sel_id: messagebox.showwarning("Error","Seleccioná un alumno"); return
        try: amount=float(self.e_amount.get())
        except: messagebox.showwarning("Error","Monto inválido"); return
        atype="ingreso" if "ingreso" in self.dd_type.get() else "egreso"
        self.db.add_account(self.sel_id,self.e_date.get(),self.e_concept.get(),amount,atype)
        self.e_concept.delete(0,"end"); self.e_amount.delete(0,"end")
        self._reload()  # refresh list + balance immediately


# ══════════════════════════════════════════════
# CUENTOS
# ══════════════════════════════════════════════
class StoriesTab(ctk.CTkFrame):
    STATUSES={"borrador ✏️":"borrador","en revisión 🔍":"en_revision",
              "finalizado ✅":"finalizado","publicado 🌟":"publicado"}
    SC={"borrador":C_MUTED,"en_revision":C_ORANGE,"finalizado":C_GREEN,"publicado":"#c47fc4"}
    SREV={v:k for k,v in STATUSES.items()}

    def __init__(self,parent,db:DB):
        super().__init__(parent,fg_color="transparent")
        self.db=db; self._smap={}; self._build(); self.reload()

    def _build(self):
        form=cframe(self); form.pack(fill="x",padx=10,pady=(10,4))
        title_lbl(form, "Registrar cuento", size=15, color=C_GOLD).pack(anchor="w",padx=12,pady=(10,4))
        r1=row(form); r1.pack(fill="x",padx=12,pady=2)
        lbl(r1,"Alumno:",size=12,color=C_MUTED).pack(side="left")
        self.dd_s=combo(r1,[],w=220); self.dd_s.pack(side="left",padx=8)
        r2=row(form); r2.pack(fill="x",padx=12,pady=2)
        self.e_title=inp(r2,"Título *",220); self.e_title.pack(side="left",padx=(0,8))
        self.e_genre=inp(r2,"Género",160);  self.e_genre.pack(side="left")
        r3=row(form); r3.pack(fill="x",padx=12,pady=2)
        lbl(r3,"Estado:",size=12,color=C_MUTED).pack(side="left")
        self.dd_st=combo(r3,list(self.STATUSES.keys()),w=210)
        self.dd_st.set("borrador ✏️"); self.dd_st.pack(side="left",padx=8)
        r4=row(form); r4.pack(fill="x",padx=12,pady=2)
        self.e_fb=inp(r4,"Devolución / feedback",360); self.e_fb.pack(side="left")
        r5=row(form); r5.pack(fill="x",padx=12,pady=(4,10))
        pbtn(r5,"Guardar cuento",self.save).pack(side="right")

        sep(self).pack(fill="x",padx=10,pady=4)
        fr=row(self); fr.pack(fill="x",padx=10)
        lbl(fr,"Filtrar:",size=12,color=C_MUTED).pack(side="left")
        self.dd_f=combo(fr,["Todos"],w=200,command=lambda v:self.reload())
        self.dd_f.set("Todos"); self.dd_f.pack(side="left",padx=8)

        self.lf=sframe(self); self.lf.pack(fill="both",expand=True,padx=8,pady=4)
        self._refresh_students()

    def _refresh_students(self):
        rows=self.db.list_students("taller")
        names=[r["name"] for r in rows]
        self._smap={r["name"]:r["id"] for r in rows}
        self.dd_s.configure(values=names if names else [""])
        if names: self.dd_s.set(names[0])
        self.dd_f.configure(values=["Todos"]+names)

    def refresh_students(self): self._refresh_students()

    def reload(self):
        for w in self.lf.winfo_children(): w.destroy()
        fval=self.dd_f.get(); fid=self._smap.get(fval) if fval!="Todos" else None
        for r in self.db.list_stories(fid):
            sc=self.SC.get(r["status"],C_MUTED)
            f=cframe(self.lf); f.pack(fill="x",pady=3,padx=4)
            rw=row(f); rw.pack(fill="x",padx=10,pady=(8,2))
            lbl(rw,r["title"],bold=True).pack(side="left")
            lbl(rw,r["status"].replace("_"," "),color=sc,size=12).pack(side="right")
            mid=row(f); mid.pack(fill="x",padx=10,pady=1)
            lbl(mid,f"✍ {r['student_name']}  |  {r['genre'] or '—'}",color=C_MUTED,size=12).pack(side="left")
            if r["feedback"]: lbl(f,r["feedback"],color=C_MUTED,size=12).pack(anchor="w",padx=10)
            btns=row(f); btns.pack(fill="x",padx=10,pady=(2,8))
            rid=r["id"]
            gbtn(btns,"Editar",  lambda rid=rid:self._edit(rid),color=C_GOLD).pack(side="left",padx=(0,4))
            gbtn(btns,"Eliminar",lambda rid=rid:self._del(rid)).pack(side="left")

    def save(self):
        sid=self._smap.get(self.dd_s.get())
        if not sid or not self.e_title.get().strip():
            messagebox.showwarning("Error","Alumno y título obligatorios"); return
        self.db.add_story(sid,self.e_title.get(),self.e_genre.get(),
                          self.STATUSES.get(self.dd_st.get(),"borrador"),self.e_fb.get())
        for e in [self.e_title,self.e_genre,self.e_fb]: e.delete(0,"end")
        self.reload()

    def _edit(self,sid):
        rows=self.db.list_stories(); r=next((x for x in rows if x["id"]==sid),None)
        if not r: return
        m=Modal(self,"Editar cuento",h=400)
        for label,val in [("Título",r["title"]),("Género",r["genre"] or ""),("Feedback",r["feedback"] or "")]:
            lbl(m.body,label,size=12,color=C_MUTED).pack(anchor="w")
            e=inp(m.body,w=380); e.pack(pady=(0,6)); e.insert(0,val)
            setattr(self,f"_edit_{label.lower()}",e)
        lbl(m.body,"Estado",size=12,color=C_MUTED).pack(anchor="w")
        es=combo(m.body,list(self.STATUSES.keys()),w=280); es.pack(pady=(0,6))
        es.set(self.SREV.get(r["status"],"borrador ✏️"))
        et=self._edit_título; eg=self._edit_género; ef=self._edit_feedback
        def ok():
            self.db.update_story(sid,et.get(),eg.get(),self.STATUSES.get(es.get(),"borrador"),ef.get())
            m.destroy(); self.reload()
        pbtn(m.body,"Actualizar",ok).pack(pady=8)

    def _del(self,sid):
        if messagebox.askyesno("Confirmar","¿Eliminar cuento?"):
            self.db.delete_story(sid); self.reload()


# ══════════════════════════════════════════════
# AGENDA
# ══════════════════════════════════════════════
class EventsTab(ctk.CTkFrame):
    TYPES={"evento 🎉":"evento","curso 📚":"curso","charla 🎤":"charla","taller 🖊":"taller"}
    EMOJI={"evento":"🎉","curso":"📚","charla":"🎤","taller":"🖊"}

    def __init__(self,parent,db:DB):
        super().__init__(parent,fg_color="transparent")
        self.db=db; self._build(); self.reload()

    def _build(self):
        form=cframe(self); form.pack(fill="x",padx=10,pady=(10,4))
        title_lbl(form, "Nuevo evento", size=15, color=C_GOLD).pack(anchor="w",padx=12,pady=(10,4))
        r1=row(form); r1.pack(fill="x",padx=12,pady=2)
        self.e_title=inp(r1,"Título *",260); self.e_title.pack(side="left",padx=(0,8))
        self.dd_type=combo(r1,list(self.TYPES.keys()),w=160)
        self.dd_type.set("evento 🎉"); self.dd_type.pack(side="left")
        r2=row(form); r2.pack(fill="x",padx=12,pady=2)
        self.e_date=inp(r2,"Fecha (YYYY-MM-DD) *",180); self.e_date.pack(side="left",padx=(0,8))
        self.e_time=inp(r2,"Hora (ej: 19:00)",130);     self.e_time.pack(side="left",padx=(0,8))
        self.e_loc =inp(r2,"Lugar",160);                self.e_loc.pack(side="left")
        r3=row(form); r3.pack(fill="x",padx=12,pady=2)
        self.e_desc=inp(r3,"Descripción",360); self.e_desc.pack(side="left")
        r4=row(form); r4.pack(fill="x",padx=12,pady=(4,10))
        pbtn(r4,"Agregar evento",self.add).pack(side="right")

        sep(self).pack(fill="x",padx=10,pady=4)
        self.lf=sframe(self); self.lf.pack(fill="both",expand=True,padx=8,pady=4)

    def reload(self):
        for w in self.lf.winfo_children(): w.destroy()
        today=datetime.today().strftime("%Y-%m-%d")
        for r in self.db.list_events():
            past=r["date"]<today
            f=cframe(self.lf); f.pack(fill="x",pady=3,padx=4)
            rw=row(f); rw.pack(fill="x",padx=10,pady=(8,2))
            em=self.EMOJI.get(r["event_type"],"📅")
            lbl(rw,f"{em} {r['title']}",bold=True,
                color=C_MUTED if past else C_CREAM).pack(side="left")
            lbl(rw,r["date"],color=C_MUTED if past else C_GOLD,size=12).pack(side="right")
            mid=row(f); mid.pack(fill="x",padx=10)
            lbl(mid,f"🕐 {r['time'] or '—'}  |  📍 {r['location'] or '—'}",
                color=C_MUTED,size=12).pack(side="left")
            if r["description"]: lbl(f,r["description"],color=C_MUTED,size=12).pack(anchor="w",padx=10)
            eid=r["id"]
            btns=row(f); btns.pack(fill="x",padx=10,pady=(2,8))
            gbtn(btns,"Eliminar",lambda eid=eid:self._del(eid)).pack(side="left")

    def add(self):
        title=self.e_title.get().strip(); date=self.e_date.get().strip()
        if not title or not date:
            messagebox.showwarning("Error","Título y fecha obligatorios"); return
        self.db.add_event(title,date,self.e_time.get(),self.e_loc.get(),
                          self.e_desc.get(),self.TYPES.get(self.dd_type.get(),"evento"))
        for e in [self.e_title,self.e_date,self.e_time,self.e_loc,self.e_desc]: e.delete(0,"end")
        self.reload()

    def _del(self,eid):
        if messagebox.askyesno("Confirmar","¿Eliminar evento?"):
            self.db.delete_event(eid); self.reload()


# ══════════════════════════════════════════════
# CLIENTES COPY
# ══════════════════════════════════════════════
class CopyClientsTab(ctk.CTkFrame):
    def __init__(self,parent,db:DB,on_change=None):
        super().__init__(parent,fg_color="transparent")
        self.db=db; self.on_change=on_change; self._build(); self.reload()

    def _build(self):
        form=cframe(self); form.pack(fill="x",padx=10,pady=(10,4))
        title_lbl(form, "Nuevo cliente", size=15, color=C_GOLD).pack(anchor="w",padx=12,pady=(10,4))
        r1=row(form); r1.pack(fill="x",padx=12,pady=2)
        self.e_name=inp(r1,"Nombre *",200); self.e_name.pack(side="left",padx=(0,8))
        self.e_co=inp(r1,"Empresa",170); self.e_co.pack(side="left")
        r2=row(form); r2.pack(fill="x",padx=12,pady=2)
        self.e_email=inp(r2,"Email",200); self.e_email.pack(side="left",padx=(0,8))
        self.e_phone=inp(r2,"Teléfono",160); self.e_phone.pack(side="left")
        r3=row(form); r3.pack(fill="x",padx=12,pady=2)
        self.e_notes=inp(r3,"Notas",360); self.e_notes.pack(side="left")
        r4=row(form); r4.pack(fill="x",padx=12,pady=(4,10))
        pbtn(r4,"Guardar cliente",self.save).pack(side="right")
        sep(self).pack(fill="x",padx=10,pady=4)
        self.lf=sframe(self); self.lf.pack(fill="both",expand=True,padx=8,pady=4)

    def reload(self):
        for w in self.lf.winfo_children(): w.destroy()
        for r in self.db.list_copy_clients():
            f=cframe(self.lf); f.pack(fill="x",pady=3,padx=4)
            rw=row(f); rw.pack(fill="x",padx=10,pady=(8,2))
            lbl(rw,r["name"],bold=True).pack(side="left")
            lbl(rw,r["company"] or "",color=C_MUTED,size=12).pack(side="left",padx=8)
            lbl(rw,"Activo" if r["active"] else "Inactivo",
                color=C_GREEN if r["active"] else C_MUTED,size=11).pack(side="right")
            lbl(f,r["email"] or "",color=C_MUTED,size=12).pack(anchor="w",padx=10)
            btns=row(f); btns.pack(fill="x",padx=10,pady=(2,8))
            cid=r["id"]
            gbtn(btns,"Editar",lambda cid=cid:self._edit(cid),color=C_GOLD).pack(side="left")

    def save(self):
        name=self.e_name.get().strip()
        if not name: messagebox.showwarning("Error","Nombre obligatorio"); return
        self.db.add_copy_client(name,self.e_email.get(),self.e_phone.get(),
                                self.e_co.get(),self.e_notes.get())
        for e in [self.e_name,self.e_email,self.e_phone,self.e_co,self.e_notes]: e.delete(0,"end")
        self.reload()
        if self.on_change: self.on_change()

    def _edit(self,cid):
        rows=self.db.list_copy_clients(); r=next((x for x in rows if x["id"]==cid),None)
        if not r: return
        m=Modal(self,"Editar cliente",h=460)
        fields_data=[("Nombre",r["name"]),("Empresa",r["company"] or ""),
                     ("Email",r["email"] or ""),("Teléfono",r["phone"] or ""),("Notas",r["notes"] or "")]
        efs=[]
        for lbl_text,val in fields_data:
            lbl(m.body,lbl_text,size=12,color=C_MUTED).pack(anchor="w")
            e=inp(m.body,w=380); e.pack(pady=(0,6)); e.insert(0,val); efs.append(e)
        sw=ctk.CTkSwitch(m.body, text="Activo", progress_color=C_GOLD, text_color=C_CREAM)
        if r["active"]: sw.select()
        sw.pack(anchor="w",pady=4)
        def ok():
            nm=efs[0].get().strip()
            if not nm: messagebox.showwarning("Error","Nombre requerido"); return
            self.db.update_copy_client(cid,nm,efs[2].get(),efs[3].get(),efs[1].get(),efs[4].get(),sw.get())
            m.destroy(); self.reload()
            if self.on_change: self.on_change()
        pbtn(m.body,"Actualizar",ok).pack(pady=8)


# ══════════════════════════════════════════════
# TAREAS COPY
# ══════════════════════════════════════════════
class CopyTasksTab(ctk.CTkFrame):
    STATUSES={"pendiente ⏳":"pendiente","en progreso 🔄":"en_progreso",
              "completada ✅":"completada","cancelada ❌":"cancelada"}
    SC={"pendiente":C_ORANGE,"en_progreso":C_BLUE,"completada":C_GREEN,"cancelada":C_MUTED}

    def __init__(self,parent,db:DB):
        super().__init__(parent,fg_color="transparent")
        self.db=db; self._cmap={}; self._build(); self.reload()

    def _build(self):
        form=cframe(self); form.pack(fill="x",padx=10,pady=(10,4))
        title_lbl(form, "Nueva tarea", size=15, color=C_GOLD).pack(anchor="w",padx=12,pady=(10,4))
        r1=row(form); r1.pack(fill="x",padx=12,pady=2)
        lbl(r1,"Cliente:",size=12,color=C_MUTED).pack(side="left")
        self.dd_c=combo(r1,["Sin cliente"],w=220); self.dd_c.set("Sin cliente"); self.dd_c.pack(side="left",padx=8)
        r2=row(form); r2.pack(fill="x",padx=12,pady=2)
        self.e_title=inp(r2,"Título *",240); self.e_title.pack(side="left",padx=(0,8))
        self.e_due=inp(r2,"Fecha límite (YYYY-MM-DD)",200); self.e_due.pack(side="left")
        r3=row(form); r3.pack(fill="x",padx=12,pady=2)
        self.e_desc=inp(r3,"Descripción",270); self.e_desc.pack(side="left",padx=(0,8))
        self.dd_st=combo(r3,list(self.STATUSES.keys()),w=190)
        self.dd_st.set("pendiente ⏳"); self.dd_st.pack(side="left")
        r4=row(form); r4.pack(fill="x",padx=12,pady=(4,10))
        pbtn(r4,"Agregar tarea",self.add).pack(side="right")
        sep(self).pack(fill="x",padx=10,pady=4)
        self.lf=sframe(self); self.lf.pack(fill="both",expand=True,padx=8,pady=4)
        self.refresh_clients()

    def refresh_clients(self):
        clients=self.db.list_copy_clients()
        self._cmap={c["name"]:c["id"] for c in clients}
        self.dd_c.configure(values=["Sin cliente"]+list(self._cmap.keys()))

    def reload(self):
        for w in self.lf.winfo_children(): w.destroy()
        today=datetime.today().strftime("%Y-%m-%d")
        for r in self.db.list_copy_tasks():
            sc=self.SC.get(r["status"],C_MUTED)
            overdue=(r["due_date"] and r["due_date"]<today
                     and r["status"] not in ("completada","cancelada"))
            f=cframe(self.lf); f.pack(fill="x",pady=3,padx=4)
            rw=row(f); rw.pack(fill="x",padx=10,pady=(8,2))
            lbl(rw,r["title"],bold=True).pack(side="left")
            lbl(rw,r["status"].replace("_"," "),color=sc,size=12).pack(side="right")
            mid=row(f); mid.pack(fill="x",padx=10)
            dc=C_RED if overdue else C_MUTED
            lbl(mid,f"Cliente: {r['client_name'] or '—'}  |  📅 {r['due_date'] or '—'}",
                color=dc,size=12).pack(side="left")
            if r["description"]: lbl(f,r["description"],color=C_MUTED,size=12).pack(anchor="w",padx=10)
            btns=row(f); btns.pack(fill="x",padx=10,pady=(2,8))
            tid=r["id"]
            gbtn(btns,"✅ Completar",lambda tid=tid:self._set(tid,"completada"),color=C_GREEN).pack(side="left",padx=(0,4))
            gbtn(btns,"🔄 Progreso", lambda tid=tid:self._set(tid,"en_progreso"),color=C_BLUE).pack(side="left",padx=(0,4))
            gbtn(btns,"Eliminar",   lambda tid=tid:self._del(tid)).pack(side="left")

    def add(self):
        title=self.e_title.get().strip()
        if not title: messagebox.showwarning("Error","Título obligatorio"); return
        cv=self.dd_c.get(); cid=self._cmap.get(cv) if cv!="Sin cliente" else None
        self.db.add_copy_task(cid,title,self.e_desc.get(),
                              self.STATUSES.get(self.dd_st.get(),"pendiente"),self.e_due.get())
        for e in [self.e_title,self.e_desc,self.e_due]: e.delete(0,"end")
        self.reload()

    def _set(self,tid,status): self.db.set_task_status(tid,status); self.reload()

    def _del(self,tid):
        if messagebox.askyesno("Confirmar","¿Eliminar tarea?"):
            self.db.delete_copy_task(tid); self.reload()


# ══════════════════════════════════════════════
# APP SHELL + LOGIN
# ══════════════════════════════════════════════
def make_subtabs(parent, tabs_config, sel_color=C_GOLD):
    sub = ctk.CTkTabview(parent, fg_color=C_NAVY,
                         segmented_button_selected_color=sel_color,
                         segmented_button_selected_hover_color=_dark(sel_color),
                         segmented_button_unselected_color=C_CARD,
                         segmented_button_unselected_hover_color=C_CARD2,
                         text_color=C_CREAM)
    sub.pack(fill="both", expand=True)
    widgets = {}
    for name, cls, kwargs in tabs_config:
        t = sub.add(name); t.configure(fg_color=C_NAVY)
        w = cls(t, **kwargs); w.pack(fill="both", expand=True)
        widgets[name] = w
    return sub, widgets


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("El Tintero & Norte Copywriting")
        self.minsize(860, 580)
        self.configure(fg_color=C_NAVY)
        self._center_window(1060, 720)
        self.db = DB()
        if is_first_run():
            self._show_first_run()
        else:
            self._show_login()

    def _center_window(self, w, h):
        """Centra la ventana en el monitor activo, respetando DPI."""
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 2 - 30)   # -30 para compensar barra de tareas
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ══════════════════════════════════════════
    # PRIMER USO
    # ══════════════════════════════════════════
    def _show_first_run(self):
        self._lf = ctk.CTkFrame(self, fg_color=C_NAVY)
        self._lf.place(relx=0, rely=0, relwidth=1, relheight=1)

        center = ctk.CTkFrame(self._lf, fg_color=C_CARD, corner_radius=20)
        center.place(relx=0.5, rely=0.5, anchor="center")

        logo = load_logo("Logo_El_Tintero.png", (100,100))
        if logo:
            ctk.CTkLabel(center, image=logo, text="").pack(pady=(28,6))

        title_lbl(center, "El Tintero", size=28, color=C_CREAM).pack()
        lbl(center, "Taller Literario", size=13, color=C_GOLD).pack(pady=(2,4))
        accentbar(center, C_GOLD).pack(fill="x", padx=40, pady=(0,16))

        lbl(center, "Primera configuración", size=15, bold=True, color=C_CREAM).pack()
        lbl(center, "Creá tu contraseña de acceso", size=12, color=C_MUTED).pack(pady=(2,14))

        self._fr_pw1 = ctk.CTkEntry(center, placeholder_text="Nueva contraseña", show="●",
                                     width=300, fg_color=C_CARD2, border_color=C_LINE,
                                     text_color=C_CREAM, placeholder_text_color=C_MUTED,
                                     font=F_body(13))
        self._fr_pw1.pack(pady=(0,8))
        self._fr_pw2 = ctk.CTkEntry(center, placeholder_text="Repetir contraseña", show="●",
                                     width=300, fg_color=C_CARD2, border_color=C_LINE,
                                     text_color=C_CREAM, placeholder_text_color=C_MUTED,
                                     font=F_body(13))
        self._fr_pw2.pack(pady=(0,6))
        self._fr_err = lbl(center, "", color=C_RED, size=12); self._fr_err.pack()
        pbtn(center, "Crear contraseña y entrar", self._do_first_run, w=260).pack(pady=(8,28))

    def _do_first_run(self):
        p1 = self._fr_pw1.get()
        p2 = self._fr_pw2.get()
        if len(p1) < 4:
            self._fr_err.configure(text="Mínimo 4 caracteres"); return
        if p1 != p2:
            self._fr_err.configure(text="Las contraseñas no coinciden"); return
        set_password(p1)
        self._lf.destroy()
        self._build()

    # ══════════════════════════════════════════
    # LOGIN
    # ══════════════════════════════════════════
    def _show_login(self):
        self._lf = ctk.CTkFrame(self, fg_color=C_NAVY)
        self._lf.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Panel central con borde dorado sutil
        center = ctk.CTkFrame(self._lf, fg_color=C_CARD, corner_radius=20,
                              border_width=1, border_color=C_LINE)
        center.place(relx=0.5, rely=0.5, anchor="center")

        logo = load_logo("Logo_El_Tintero.png", (100,100))
        if logo:
            ctk.CTkLabel(center, image=logo, text="").pack(pady=(28,6))

        title_lbl(center, "El Tintero", size=28, color=C_CREAM).pack()
        lbl(center, "Taller Literario", size=13, color=C_GOLD).pack(pady=(2,0))
        accentbar(center, C_GOLD).pack(fill="x", padx=40, pady=(6,20))

        self._pw = ctk.CTkEntry(center, placeholder_text="Contraseña de acceso",
                                show="●", width=300,
                                fg_color=C_CARD2, border_color=C_LINE,
                                text_color=C_CREAM, placeholder_text_color=C_MUTED,
                                font=F_body(13))
        self._pw.pack(pady=(0,6))
        self._pw.bind("<Return>", lambda e: self._login())
        self._pw.focus_set()
        self._err = lbl(center, "", color=C_RED, size=12); self._err.pack()
        pbtn(center, "Ingresar", self._login, w=240).pack(pady=(8,28))

    def _login(self):
        if self._pw.get() == get_password():
            self._lf.destroy()
            self._build()
        else:
            self._err.configure(text="Contraseña incorrecta")
            self._pw.delete(0, "end")

    # ══════════════════════════════════════════
    # APP PRINCIPAL
    # ══════════════════════════════════════════
    def _build(self):
        tabs = ctk.CTkTabview(self, fg_color=C_NAVY2,
                              segmented_button_selected_color=C_GOLD,
                              segmented_button_selected_hover_color=_dark(C_GOLD),
                              segmented_button_unselected_color=C_CARD,
                              segmented_button_unselected_hover_color=C_CARD2,
                              text_color=C_CREAM, border_color=C_LINE,
                              segmented_button_fg_color=C_CARD)
        tabs.pack(fill="both", expand=True, padx=8, pady=8)

        # ── EL TINTERO ──────────────────────
        t1 = tabs.add("  🖊  El Tintero  "); t1.configure(fg_color=C_NAVY)
        self._hdr(t1, "Logo_El_Tintero.png",
                  "El Tintero", "Taller Literario", C_CREAM)

        sub1 = ctk.CTkTabview(t1, fg_color=C_NAVY,
                              segmented_button_selected_color=C_GOLD,
                              segmented_button_selected_hover_color=_dark(C_GOLD),
                              segmented_button_unselected_color=C_CARD,
                              segmented_button_unselected_hover_color=C_CARD2,
                              text_color=C_CREAM,
                              segmented_button_fg_color=C_CARD2)
        sub1.pack(fill="both", expand=True)

        def on_sc():
            self._acc_t.refresh()
            self._acc_e.refresh()
            self._sto.refresh_students()

        t_at = sub1.add("Alumnos Taller");   t_at.configure(fg_color=C_NAVY)
        self._st = StudentsTab(t_at, self.db, "taller", C_GOLD, on_change=on_sc)
        self._st.pack(fill="both", expand=True)

        t_ae = sub1.add("Alumnos Edición");  t_ae.configure(fg_color=C_NAVY)
        self._se = StudentsTab(t_ae, self.db, "edicion", C_BLUE, on_change=on_sc)
        self._se.pack(fill="both", expand=True)

        t_ct = sub1.add("Cuentas Taller");   t_ct.configure(fg_color=C_NAVY)
        self._acc_t = AccountsTab(t_ct, self.db, "taller")
        self._acc_t.pack(fill="both", expand=True)

        t_ce = sub1.add("Cuentas Edición");  t_ce.configure(fg_color=C_NAVY)
        self._acc_e = AccountsTab(t_ce, self.db, "edicion")
        self._acc_e.pack(fill="both", expand=True)

        t_co = sub1.add("Cuentos");          t_co.configure(fg_color=C_NAVY)
        self._sto = StoriesTab(t_co, self.db)
        self._sto.pack(fill="both", expand=True)

        t_ag = sub1.add("Agenda");           t_ag.configure(fg_color=C_NAVY)
        self._ev = EventsTab(t_ag, self.db)
        self._ev.pack(fill="both", expand=True)

        # ── NORTE COPY ──────────────────────
        t2 = tabs.add("  🧭  Norte Copy  "); t2.configure(fg_color=C_NAVY)
        self._hdr(t2, "NorteCopywritingSolutions.png",
                  "Norte", "Copywriting Solutions", C_GOLD)

        sub2 = ctk.CTkTabview(t2, fg_color=C_NAVY,
                              segmented_button_selected_color=C_GOLD,
                              segmented_button_selected_hover_color=_dark(C_GOLD),
                              segmented_button_unselected_color=C_CARD,
                              segmented_button_unselected_hover_color=C_CARD2,
                              text_color=C_CREAM,
                              segmented_button_fg_color=C_CARD2)
        sub2.pack(fill="both", expand=True)

        def on_cc():
            self._tasks.refresh_clients()

        t_cl = sub2.add("Clientes"); t_cl.configure(fg_color=C_NAVY)
        self._cli = CopyClientsTab(t_cl, self.db, on_change=on_cc)
        self._cli.pack(fill="both", expand=True)

        t_ta = sub2.add("Tareas");   t_ta.configure(fg_color=C_NAVY)
        self._tasks = CopyTasksTab(t_ta, self.db)
        self._tasks.pack(fill="both", expand=True)

        # ── CONFIGURACIÓN ───────────────────
        t3 = tabs.add("  ⚙  Config  "); t3.configure(fg_color=C_NAVY)
        self._cfg_panel = ConfigPanel(t3, on_logout=self._logout)
        self._cfg_panel.pack(fill="both", expand=True)

    # ══════════════════════════════════════════
    # HEADER REUTILIZABLE
    # ══════════════════════════════════════════
    def _hdr(self, parent, logo_file, title, subtitle, tc):
        h = ctk.CTkFrame(parent, fg_color=C_CARD2, corner_radius=0, height=58)
        h.pack(fill="x", side="top"); h.pack_propagate(False)
        # Barra de acento izquierda
        ctk.CTkFrame(h, width=4, fg_color=C_GOLD, corner_radius=0).pack(side="left", fill="y")
        logo = load_logo(logo_file, (40, 40))
        if logo:
            ctk.CTkLabel(h, image=logo, text="").pack(side="left", padx=(12,10), pady=9)
        vline = ctk.CTkFrame(h, width=1, fg_color=C_LINE); vline.pack(side="left", fill="y", pady=10)
        col = ctk.CTkFrame(h, fg_color="transparent"); col.pack(side="left", padx=12, pady=6)
        title_lbl(col, title, size=17, color=tc).pack(anchor="w")
        lbl(col, subtitle, size=11, color=C_MUTED).pack(anchor="w")

    # ══════════════════════════════════════════
    # LOGOUT / CERRAR SESIÓN
    # ══════════════════════════════════════════
    def _logout(self):
        for w in self.winfo_children(): w.destroy()
        self._show_login()


# ══════════════════════════════════════════════
# PANEL DE CONFIGURACIÓN
# ══════════════════════════════════════════════
class ConfigPanel(ctk.CTkFrame):
    def __init__(self, parent, on_logout=None):
        super().__init__(parent, fg_color="transparent")
        self.on_logout = on_logout
        self._build()

    def _build(self):
        # Scroll container
        sf = sframe(self); sf.pack(fill="both", expand=True, padx=16, pady=16)

        # ── Título ──
        title_lbl(sf, "Configuración", size=22, color=C_CREAM).pack(anchor="w", pady=(0,2))
        lbl(sf, "Ajustes del sistema y cuenta", size=12, color=C_MUTED).pack(anchor="w")
        accentbar(sf, C_GOLD).pack(fill="x", pady=(8,20))

        # ── Cambiar contraseña ──
        pw_card = cframe(sf); pw_card.pack(fill="x", pady=(0,12))
        accentbar(pw_card, C_GOLD, 3).pack(fill="x")
        body = ctk.CTkFrame(pw_card, fg_color="transparent"); body.pack(fill="x", padx=16, pady=14)
        title_lbl(body, "Contraseña de acceso", size=15, color=C_CREAM).pack(anchor="w")
        lbl(body, "Modificá la contraseña con la que ingresás al sistema.", size=12, color=C_MUTED).pack(anchor="w", pady=(2,12))

        r1 = ctk.CTkFrame(body, fg_color="transparent"); r1.pack(fill="x", pady=2)
        lbl(r1, "Contraseña actual", size=12, color=C_MUTED).pack(anchor="w")
        self.e_cur = ctk.CTkEntry(r1, show="●", width=320, fg_color=C_CARD2,
                                  border_color=C_LINE, text_color=C_CREAM,
                                  placeholder_text_color=C_MUTED, font=F_body(13))
        self.e_cur.pack(anchor="w", pady=(2,8))
        lbl(r1, "Nueva contraseña", size=12, color=C_MUTED).pack(anchor="w")
        self.e_new = ctk.CTkEntry(r1, show="●", width=320, fg_color=C_CARD2,
                                  border_color=C_LINE, text_color=C_CREAM,
                                  placeholder_text_color=C_MUTED, font=F_body(13))
        self.e_new.pack(anchor="w", pady=(2,8))
        lbl(r1, "Repetir nueva contraseña", size=12, color=C_MUTED).pack(anchor="w")
        self.e_rep = ctk.CTkEntry(r1, show="●", width=320, fg_color=C_CARD2,
                                  border_color=C_LINE, text_color=C_CREAM,
                                  placeholder_text_color=C_MUTED, font=F_body(13))
        self.e_rep.pack(anchor="w", pady=(2,8))
        self.pw_msg = lbl(r1, "", color=C_RED, size=12); self.pw_msg.pack(anchor="w")
        pbtn(r1, "Cambiar contraseña", self._change_pw, color=C_GOLD).pack(anchor="w", pady=(6,0))

        # ── Acerca del sistema ──
        sep(sf).pack(fill="x", pady=16)
        info_card = cframe(sf); info_card.pack(fill="x", pady=(0,12))
        accentbar(info_card, C_BLUE, 3).pack(fill="x")
        info_body = ctk.CTkFrame(info_card, fg_color="transparent"); info_body.pack(fill="x", padx=16, pady=14)
        title_lbl(info_body, "Acerca del sistema", size=15, color=C_CREAM).pack(anchor="w")
        for line in [
            "El Tintero — Sistema de gestión para talleres literarios",
            "Desarrollado con Python 3 + CustomTkinter",
            "Base de datos local SQLite · Sin dependencias en la nube",
        ]:
            lbl(info_body, line, size=12, color=C_MUTED).pack(anchor="w", pady=1)

        # ── Cerrar sesión ──
        sep(sf).pack(fill="x", pady=16)
        logout_card = cframe(sf); logout_card.pack(fill="x", pady=(0,12))
        accentbar(logout_card, C_RED, 3).pack(fill="x")
        lo_body = ctk.CTkFrame(logout_card, fg_color="transparent"); lo_body.pack(fill="x", padx=16, pady=14)
        title_lbl(lo_body, "Cerrar sesión", size=15, color=C_CREAM).pack(anchor="w")
        lbl(lo_body, "Volvés a la pantalla de inicio de sesión.", size=12, color=C_MUTED).pack(anchor="w", pady=(2,10))
        pbtn(lo_body, "Cerrar sesión", self._logout, color=C_RED, w=180).pack(anchor="w")

    def _change_pw(self):
        cur = self.e_cur.get()
        new = self.e_new.get()
        rep = self.e_rep.get()
        if cur != get_password():
            self.pw_msg.configure(text="La contraseña actual es incorrecta", text_color=C_RED); return
        if len(new) < 4:
            self.pw_msg.configure(text="Mínimo 4 caracteres", text_color=C_RED); return
        if new != rep:
            self.pw_msg.configure(text="Las contraseñas no coinciden", text_color=C_RED); return
        set_password(new)
        for e in [self.e_cur, self.e_new, self.e_rep]: e.delete(0, "end")
        self.pw_msg.configure(text="✓  Contraseña actualizada correctamente", text_color=C_GREEN)

    def _logout(self):
        if self.on_logout: self.on_logout()


if __name__=="__main__":
    app=App(); app.mainloop()
