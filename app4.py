import random
import time
import streamlit as st

st.set_page_config(page_title="Capitales — Niveles con Eventos", page_icon="🌍", layout="centered")

# ================= Datasets por continente =================
# Formato: (pais, capital, iso2). Usa iso2 minúscula para FlagCDN: https://flagcdn.com/w320/{iso2}.png
EUROPE = {
    ("España", "Madrid", "es"),
    ("Francia", "París", "fr"),
    ("Alemania", "Berlín", "de"),
    ("Italia", "Roma", "it"),
    ("Portugal", "Lisboa", "pt"),
    ("Países Bajos", "Ámsterdam", "nl"),
    ("Bélgica", "Bruselas", "be"),
    ("Suiza", "Berna", "ch"),
    ("Austria", "Viena", "at"),
    ("Polonia", "Varsovia", "pl"),
    ("Hungría", "Budapest", "hu"),
    ("Chequia", "Praga", "cz"),
    ("Grecia", "Atenas", "gr"),
    ("Suecia", "Estocolmo", "se"),
    ("Noruega", "Oslo", "no"),
    ("Finlandia", "Helsinki", "fi"),
    ("Dinamarca", "Copenhague", "dk"),
    ("Irlanda", "Dublín", "ie"),
    ("Reino Unido", "Londres", "gb"),
    ("Rumanía", "Bucarest", "ro"),
    ("Bulgaria", "Sofía", "bg"),
    ("Croacia", "Zagreb", "hr"),
    ("Serbia", "Belgrado", "rs"),
    ("Eslovaquia", "Bratislava", "sk"),
    ("Eslovenia", "Liubliana", "si"),
    ("Bosnia y Herzegovina", "Sarajevo", "ba"),
    ("Albania", "Tirana", "al"),
    ("Andorra", "Andorra la Vieja", "ad"),
    ("Mónaco", "Mónaco", "mc"),
    ("Liechtenstein", "Vaduz", "li"),
    ("Luxemburgo", "Luxemburgo", "lu"),
    ("Malta", "La Valeta", "mt"),
    ("Moldavia", "Chisináu", "md"),
    ("Montenegro", "Podgorica", "me"),
    ("Macedonia del Norte", "Skopie", "mk"),
    ("Estonia", "Tallin", "ee"),
    ("Letonia", "Riga", "lv"),
    ("Lituania", "Vilna", "lt"),
    ("Islandia", "Reikiavik", "is"),
    ("San Marino", "San Marino", "sm"),
    ("Ciudad del Vaticano", "Ciudad del Vaticano", "va"),
    ("Chipre", "Nicosia", "cy"),
    ("Ucrania", "Kiev", "ua"),
    ("Bielorrusia", "Minsk", "by"),
    ("Rusia", "Moscú", "ru"),
    ("Turquía", "Ankara", "tr"),
}

AMERICAS = {
    ("Estados Unidos", "Washington D.C.", "us"),
    ("Canadá", "Ottawa", "ca"),
    ("México", "Ciudad de México", "mx"),
    ("Argentina", "Buenos Aires", "ar"),
    ("Brasil", "Brasilia", "br"),
    ("Chile", "Santiago", "cl"),
    ("Perú", "Lima", "pe"),
    ("Colombia", "Bogotá", "co"),
    ("Uruguay", "Montevideo", "uy"),
    ("Paraguay", "Asunción", "py"),
    ("Bolivia", "Sucre", "bo"),
    ("Ecuador", "Quito", "ec"),
    ("Venezuela", "Caracas", "ve"),
    ("Cuba", "La Habana", "cu"),
    ("República Dominicana", "Santo Domingo", "do"),
    ("Guatemala", "Ciudad de Guatemala", "gt"),
    ("Honduras", "Tegucigalpa", "hn"),
    ("El Salvador", "San Salvador", "sv"),
    ("Nicaragua", "Managua", "ni"),
    ("Costa Rica", "San José", "cr"),
    ("Panamá", "Ciudad de Panamá", "pa"),
}

CONTINENTS = {
    1: ("Europa", list(EUROPE)),
    2: ("América", list(AMERICAS)),
    # 3: ("Asia", list(ASIA)), ...
}

# ================= Parámetros del juego =================
CHOICES_PER_QUESTION = 4
EVENT_PROB = 0.25  # prob. de lanzar evento tras una pregunta
STREAK_CHEST_STEPS = {3, 5, 8}  # en estas rachas se abre cofre

# ================= Estado =================
def init_state_if_needed():
    defaults = {
        "level": 1,
        "continent_name": None,
        "pool": [],
        "all_capitals": [],
        "phase": "all_first",        # all_first -> failed_review -> final_mastery
        "remaining": [],
        "phase_total": 0,
        "failed_buffer": [],
        "answered_in_phase": 0,
        "question": None,
        "locked": False,

        # Gamificación
        "score": 0,
        "streak": 0,
        "lives": 3,
        "active_event": None,        # {"type": "...", "expires_at_q": int}
        "last_event_info": None,     # texto del último evento lanzado (UI)
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def load_level(level: int):
    """Carga continente (nivel) y arranca en fase all_first."""
    if level not in CONTINENTS or not CONTINENTS[level][1]:
        # Si no hay más continentes o no tienen datos, vuelve al 1 si existe
        if 1 in CONTINENTS and CONTINENTS[1][1]:
            level = 1
        else:
            st.error("No hay datos en los continentes. Rellena EUROPE/AMERICAS.")
            return
    st.session_state.level = level
    st.session_state.continent_name = CONTINENTS[level][0]
    st.session_state.pool = CONTINENTS[level][1][:]
    st.session_state.all_capitals = [cap for (_, cap, __) in st.session_state.pool]

    # Reset de meta-juego por continente
    st.session_state.score = 0
    st.session_state.streak = 0
    st.session_state.lives = 3
    st.session_state.active_event = None
    st.session_state.last_event_info = None

    start_phase("all_first")

def start_phase(phase: str, seed_items=None):
    """Inicia una fase con su cola de 'remaining'."""
    st.session_state.phase = phase
    if phase == "all_first":
        remaining = st.session_state.pool[:]
        random.shuffle(remaining)
    elif phase == "failed_review":
        remaining = list(dict.fromkeys(seed_items or []))
        random.shuffle(remaining)
    elif phase == "final_mastery":
        remaining = st.session_state.pool[:]
        random.shuffle(remaining)
    else:
        remaining = []

    st.session_state.remaining = remaining
    st.session_state.phase_total = len(remaining)
    st.session_state.failed_buffer = []
    st.session_state.answered_in_phase = 0
    st.session_state.question = None
    st.session_state.locked = False

def pick_question():
    """Selecciona la siguiente pregunta si no hay una activa."""
    if not st.session_state.question:
        if not st.session_state.remaining:
            return False
        country, capital, iso2 = st.session_state.remaining[0]

        # Prepara opciones
        options = {capital}
        distractors = [c for c in st.session_state.all_capitals if c != capital]
        random.shuffle(distractors)
        for d in distractors:
            if len(options) >= CHOICES_PER_QUESTION:
                break
            options.add(d)
        options = list(options)
        random.shuffle(options)

        # Si hay evento 50/50 y aplica a esta pregunta: reducir opciones
        if st.session_state.active_event and st.session_state.active_event["type"] == "50_50":
            if len(options) > 2:
                # asegurar capital correcta + 1 distractor
                correct = capital
                distract_only = [o for o in options if o != correct]
                random.shuffle(distract_only)
                options = [correct, distract_only[0]]
                random.shuffle(options)

        st.session_state.question = {
            "country": country,
            "capital": capital,
            "iso2": iso2,
            "options": options,
        }
    return True

def apply_event_rewards(is_correct: bool) -> int:
    """Calcula puntos según evento activo y efecto en vidas/racha."""
    base_points = 1 if is_correct else 0
    ev = st.session_state.active_event

    if ev:
        etype = ev["type"]
        # Doble o nada
        if etype == "double_or_nothing":
            if is_correct:
                base_points = 2
            else:
                # pierdes 1 vida si fallas
                st.session_state.lives = max(0, st.session_state.lives - 1)
                base_points = 0
        # Doble puntos
        elif etype == "double_points":
            if is_correct:
                base_points *= 2
        # 50/50 no afecta puntos, solo opciones
        # Expiración del evento al final de la pregunta:
        if st.session_state.answered_in_phase + 1 >= ev["expires_at_q"]:
            st.session_state.active_event = None
    return base_points

def maybe_trigger_event():
    """Lanza eventos sorpresa con probabilidad, y cofres por racha."""
    # Cofre por racha
    if st.session_state.streak in STREAK_CHEST_STEPS:
        power = random.choice(["double_points", "50_50", "double_or_nothing"])
        st.session_state.active_event = {"type": power, "expires_at_q": st.session_state.answered_in_phase + 1}
        pretty = {"double_points": "✨ Doble Puntos", "50_50": "🎲 50/50", "double_or_nothing": "💣 Doble o Nada"}[power]
        st.session_state.last_event_info = f"🎁 ¡Cofre de racha! Has obtenido: **{pretty}**"
        return

    # Evento aleatorio
    if random.random() < EVENT_PROB:
        power = random.choice(["double_points", "50_50", "double_or_nothing"])
        st.session_state.active_event = {"type": power, "expires_at_q": st.session_state.answered_in_phase + 1}
        pretty = {"double_points": "✨ Doble Puntos", "50_50": "🎲 50/50", "double_or_nothing": "💣 Doble o Nada"}[power]
        st.session_state.last_event_info = f"⚡ Evento sorpresa: **{pretty}** (solo esta pregunta)"
    else:
        st.session_state.last_event_info = None

def answer_and_advance(clicked_value):
    """Procesa respuesta y pinta feedback."""
    st.session_state.locked = True
    q = st.session_state.question
    is_correct = (clicked_value == q["capital"])
    # Racha / vidas
    if is_correct:
        st.session_state.streak += 1
        st.success(f"✅ ¡Correcto! (🔥 racha {st.session_state.streak})")
    else:
        st.session_state.streak = 0
        st.error(f"❌ Incorrecto. La capital de **{q['country']}** es **{q['capital']}**.")
        st.session_state.failed_buffer.append((q["country"], q["capital"], q["iso2"]))

    # Puntos con evento
    gained = apply_event_rewards(is_correct)
    st.session_state.score += gained

def go_next():
    """Avanza en la cola de la fase o transiciona de fase/continente."""
    # Retira la pregunta actual
    if st.session_state.remaining:
        st.session_state.remaining.pop(0)
    st.session_state.answered_in_phase += 1
    st.session_state.question = None
    st.session_state.locked = False

    # Check game over (sin vidas)
    if st.session_state.lives <= 0:
        st.error("💀 Te quedaste sin vidas. Reiniciando continente…")
        load_level(st.session_state.level)
        return

    # Si aún hay, quizá lanzar evento para la siguiente
    if st.session_state.remaining:
        maybe_trigger_event()
        return

    # Fase completada → decidir transición
    phase = st.session_state.phase
    fails = st.session_state.failed_buffer

    if phase == "all_first":
        start_phase("failed_review", seed_items=fails) if fails else start_phase("final_mastery")
    elif phase == "failed_review":
        start_phase("final_mastery")
    elif phase == "final_mastery":
        if fails:
            # si fallas algo en mastery, repasa esos y vuelve a intentar mastery
            start_phase("failed_review", seed_items=fails)
        else:
            st.balloons()
            st.success(f"🎉 ¡Dominaste {st.session_state.continent_name}! Pasando al siguiente continente…")
            load_level(st.session_state.level + 1)

# ================ Inicio ================
init_state_if_needed()
if not st.session_state.pool:
    load_level(st.session_state.level)

# ================ UI ================
st.title(f"🌍 Capitales — Nivel {st.session_state.level} ({st.session_state.continent_name or '—'})")

fase_txt = {
    "all_first": "Ronda 1: todos los países del continente",
    "failed_review": "Ronda 2: repaso de fallos",
    "final_mastery": "Ronda 3: dominio total (todos de nuevo)",
}.get(st.session_state.phase, st.session_state.phase)
st.caption(fase_txt)

# Barra superior: vidas, racha, score
lives = "❤" * st.session_state.lives + "🤍" * (3 - st.session_state.lives)
st.markdown(f"**Vidas:** {lives} &nbsp;&nbsp; **🔥 Racha:** {st.session_state.streak} &nbsp;&nbsp; **⭐ Puntos:** {st.session_state.score}")

# Evento activo / último evento
if st.session_state.active_event:
    pretty = {"double_points": "✨ Doble Puntos", "50_50": "🎲 50/50", "double_or_nothing": "💣 Doble o Nada"}[st.session_state.active_event["type"]]
    st.info(f"Evento activo: **{pretty}** (solo esta pregunta)")
elif st.session_state.last_event_info:
    st.info(st.session_state.last_event_info)

# Saca la pregunta
has_question = pick_question()
if not has_question:
    st.info("Fase completada. Preparando transición…")
    st.rerun()

q = st.session_state.question
flag_url = f"https://flagcdn.com/w320/{q['iso2']}.png"
st.image(flag_url, width=160)
st.subheader(f"¿Cuál es la capital de **{q['country']}**?")

# Opciones
cols = st.columns(2)
clicked_value = None
for i, opt in enumerate(q["options"]):
    with cols[i % 2]:
        if st.button(opt, disabled=st.session_state.locked, use_container_width=True, key=f"opt_{i}_{opt}"):
            clicked_value = opt

if clicked_value and not st.session_state.locked:
    answer_and_advance(clicked_value)

# Progreso de fase
total = max(1, st.session_state.phase_total)
done = st.session_state.answered_in_phase
st.progress(min(done / total, 1.0))
st.info(f"Progreso fase: **{done} / {total}** — Fase: **{fase_txt}**")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🔁 Reiniciar fase"):
        start_phase(st.session_state.phase)
        st.rerun()
with col2:
    if st.button("🔄 Reiniciar continente"):
        load_level(st.session_state.level)
        st.rerun()
with col3:
    next_disabled = not st.session_state.locked
    if st.button("Siguiente ▶️", disabled=next_disabled):
        go_next()
        st.rerun()