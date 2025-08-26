import random
import streamlit as st

# ---------------- Config de página ----------------
st.set_page_config(page_title="Capitales por Niveles", page_icon="🌍", layout="centered")

# ---------------- Datasets por continente ----------------
# ISO2 en minúsculas para FlagCDN: https://flagcdn.com/w320/{iso2}.png
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
    # Puedes añadir más niveles/continentes aquí:
    # 3: ("Asia", list(ASIA)),
    # 4: ("África", list(AFRICA)),
    # 5: ("Oceanía", list(OCEANIA)),
}

# ---------------- Parámetros del juego ----------------
QUESTIONS_IN_LEVEL = 10
CHOICES_PER_QUESTION = 4

# ---------------- Estado de sesión ----------------
if "level" not in st.session_state:
    st.session_state.level = 1  # Comienza en Europa
if "continent_name" not in st.session_state:
    st.session_state.continent_name = CONTINENTS[st.session_state.level][0]
if "pool" not in st.session_state:
    st.session_state.pool = CONTINENTS[st.session_state.level][1][:]
if "all_capitals" not in st.session_state:
    st.session_state.all_capitals = [cap for (_, cap, __) in st.session_state.pool]
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "question" not in st.session_state:
    st.session_state.question = None
if "locked" not in st.session_state:
    st.session_state.locked = False
if "last_correct" not in st.session_state:
    st.session_state.last_correct = None

def load_level(level: int):
    """Carga datos del nivel/continente indicado."""
    if level not in CONTINENTS:
        # Si no hay más continentes, reinicia al 1
        level = 1
    st.session_state.level = level
    st.session_state.continent_name = CONTINENTS[level][0]
    st.session_state.pool = CONTINENTS[level][1][:]
    st.session_state.all_capitals = [cap for (_, cap, __) in st.session_state.pool]
    st.session_state.current_q = 0
    st.session_state.score = 0
    st.session_state.question = None
    st.session_state.locked = False
    st.session_state.last_correct = None

def new_question():
    """Genera nueva pregunta y opciones para el continente actual."""
    st.session_state.locked = False
    st.session_state.last_correct = None
    country, capital, iso2 = random.choice(st.session_state.pool)

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

# ---------------- Cabecera dinámica ----------------
st.title(f"🌍 Juego de Capitales — Nivel {st.session_state.level} ({st.session_state.continent_name})")
st.caption("Nivel 1: Europa. Acaba el nivel para pasar al siguiente continente. ¡La bandera arriba te da una pista!")

# ---------------- Inicializa primera pregunta ----------------
if st.session_state.question is None:
    new_question()

q = st.session_state.question

# ---------------- UI: bandera + país ----------------
flag_url = f"https://flagcdn.com/w320/{q['iso2']}.png"
st.image(flag_url, width=160)
st.subheader(f"¿Cuál es la capital de **{q['country']}**?")

# ---------------- Opciones como botones ----------------
cols = st.columns(2)
clicked_value = None
for i, opt in enumerate(q["options"]):
    with cols[i % 2]:
        if st.button(opt, disabled=st.session_state.locked, use_container_width=True):
            clicked_value = opt

# ---------------- Resolver respuesta ----------------
if clicked_value and not st.session_state.locked:
    st.session_state.locked = True
    is_correct = (clicked_value == q["capital"])
    st.session_state.last_correct = is_correct
    if is_correct:
        st.success("✅ ¡Correcto!")
        st.session_state.score += 1
    else:
        st.error(f"❌ Incorrecto. La capital de **{q['country']}** es **{q['capital']}**.")

# ---------------- Progreso + controles ----------------
st.progress(st.session_state.current_q / QUESTIONS_IN_LEVEL)
st.info(f"Puntuación: **{st.session_state.score} / {st.session_state.current_q}**")

col_a, col_b, col_c = st.columns(3)
with col_a:
    if st.button("🔁 Reiniciar nivel"):
        load_level(st.session_state.level)
        st.rerun()

with col_b:
    if not st.session_state.locked:
        st.caption("Consejo: usa la bandera como pista 😉")
    else:
        st.caption("Haz clic en **Siguiente** para continuar.")

with col_c:
    next_disabled = not st.session_state.locked
    if st.button("Siguiente ▶️", disabled=next_disabled):
        st.session_state.current_q += 1
        if st.session_state.current_q >= QUESTIONS_IN_LEVEL:
            st.balloons()
            st.success(
                f"🎉 ¡Nivel {st.session_state.level} completado! "
                f"Resultado: {st.session_state.score}/{QUESTIONS_IN_LEVEL}"
            )
            # Avanzar al siguiente continente/nivel
            next_level = st.session_state.level + 1
            load_level(next_level)
        else:
            new_question()
        st.rerun()