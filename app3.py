import random
import streamlit as st

st.set_page_config(page_title="Capitales por Niveles", page_icon="🌍", layout="centered")

# ================= Datasets por continente =================
# Usa (pais, capital, iso2) con iso2 en minúsculas para FlagCDN: https://flagcdn.com/w320/{iso2}.png
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

# ================= Parámetros =================
CHOICES_PER_QUESTION = 4  # opción múltiple con N opciones

# ================= Estado =================
if "level" not in st.session_state:
    st.session_state.level = 1  # Arranca en Europa

# Variables de sesión del juego
for key, default in [
    ("continent_name", None),
    ("pool", []),
    ("all_capitals", []),
    ("phase", "all_first"),           # all_first -> failed_review -> final_mastery
    ("remaining", []),                # preguntas pendientes en la fase
    ("phase_total", 0),               # tamaño total de la fase
    ("failed_buffer", []),            # fallos de la fase actual
    ("question", None),
    ("locked", False),
    ("answered_in_phase", 0),         # cuantas respondidas en fase actual
]:
    if key not in st.session_state:
        st.session_state[key] = default

def load_level(level: int):
    """Carga continente (nivel) y arranca en fase all_first."""
    if level not in CONTINENTS or not CONTINENTS[level][1]:
        # Si no existe o no tiene datos, reinicia al 1 si existe; si no, muestra aviso
        if 1 in CONTINENTS and CONTINENTS[1][1]:
            level = 1
        else:
            st.error("No hay datos en los continentes definidos. Rellena EUROPE/AMERICAS.")
            return
    st.session_state.level = level
    st.session_state.continent_name = CONTINENTS[level][0]
    st.session_state.pool = CONTINENTS[level][1][:]
    st.session_state.all_capitals = [cap for (_, cap, __) in st.session_state.pool]
    start_phase("all_first")

def start_phase(phase: str, seed_items=None):
    """Inicia una fase con su cola de 'remaining'."""
    st.session_state.phase = phase
    if phase == "all_first":
        remaining = st.session_state.pool[:]
        random.shuffle(remaining)
    elif phase == "failed_review":
        # Usamos los fallos de la fase previa (seed_items)
        remaining = list(dict.fromkeys(seed_items or []))  # único preservando orden
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
            return False  # no hay más en la fase
        # Saca el primero de la cola
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
        st.session_state.question = {
            "country": country,
            "capital": capital,
            "iso2": iso2,
            "options": options,
        }
    return True

def answer_and_advance(clicked_value):
    """Procesa respuesta y habilita siguiente."""
    st.session_state.locked = True
    q = st.session_state.question
    is_correct = (clicked_value == q["capital"])
    if is_correct:
        st.success("✅ ¡Correcto!")
    else:
        st.error(f"❌ Incorrecto. La capital de **{q['country']}** es **{q['capital']}**.")
        st.session_state.failed_buffer.append((q["country"], q["capital"], q["iso2"]))

def go_next():
    """Avanza en la cola de la fase o transiciona de fase/continente."""
    # Retira la pregunta actual de 'remaining'
    if st.session_state.remaining:
        st.session_state.remaining.pop(0)
    st.session_state.answered_in_phase += 1
    st.session_state.question = None
    st.session_state.locked = False

    # Si aún hay pendientes en la fase, seguimos
    if st.session_state.remaining:
        return

    # Si se acabó la fase, decide transición:
    phase = st.session_state.phase
    fails = st.session_state.failed_buffer

    if phase == "all_first":
        if fails:
            # pasar a ronda de fallados
            start_phase("failed_review", seed_items=fails)
        else:
            # si no fallaste ninguna, pasa a mastery
            start_phase("final_mastery")
    elif phase == "failed_review":
        # Tras repasar fallos, siempre hacemos mastery
        start_phase("final_mastery")
    elif phase == "final_mastery":
        if fails:
            # Si fallas en mastery, vuelves a fallados con estos nuevos fallos
            start_phase("failed_review", seed_items=fails)
        else:
            # Mastery perfecto -> siguiente continente (nivel)
            st.balloons()
            st.success(f"🎉 ¡Dominaste {st.session_state.continent_name}! Pasando al siguiente continente…")
            load_level(st.session_state.level + 1)

# ================ Carga inicial del nivel ================
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

# Si no hay datos en el continente actual
if not st.session_state.pool:
    st.warning("Este continente no tiene países cargados todavía. Añade entradas a EUROPE/AMERICAS.")
    st.stop()

# Saca o prepara la pregunta actual
has_question = pick_question()
if not has_question:
    # No quedan preguntas en esta fase (la transición se hace en go_next, pero por si acaso)
    st.info("Fase completada. Preparando transición…")
    st.rerun()

q = st.session_state.question
flag_url = f"https://flagcdn.com/w320/{q['iso2']}.png"
st.image(flag_url, width=160)
st.subheader(f"¿Cuál es la capital de **{q['country']}**?")

cols = st.columns(2)
clicked_value = None
for i, opt in enumerate(q["options"]):
    with cols[i % 2]:
        if st.button(opt, disabled=st.session_state.locked, use_container_width=True, key=f"opt_{i}_{opt}"):
            clicked_value = opt

if clicked_value and not st.session_state.locked:
    answer_and_advance(clicked_value)

# Progreso de la fase actual
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