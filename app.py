import random
import streamlit as st

# -------- Configuración de la página --------
st.set_page_config(page_title="Capitales - Nivel 1", page_icon="🌍", layout="centered")
st.title("🌍 Juego de Capitales — Nivel 1 (opción múltiple)")
st.caption("Adivina la capital. Elige entre varias opciones. ¡La bandera arriba te da una pista!")
# -------- Dataset (Europa): País -> Capital + ISO2 para la bandera --------
# (ISO2 en minúsculas para usar FlagCDN: https://flagcdn.com/w320/{iso2}.png)
COUNTRIES = {
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

ALL = list(COUNTRIES)
ALL_CAPITALS = [cap for (_, cap, __) in ALL]

# -------- Parámetros del nivel --------
QUESTIONS_IN_LEVEL = 10     # cuántas preguntas tiene el nivel
CHOICES_PER_QUESTION = 4    # opciones por pregunta

# -------- Estado de sesión --------
if "pool" not in st.session_state:
    st.session_state.pool = random.sample(ALL, k=min(len(ALL), 50))  # subconjunto aleatorio (opcional)
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "question" not in st.session_state:
    st.session_state.question = None
if "locked" not in st.session_state:
    st.session_state.locked = False   # bloquea opciones tras responder
if "last_correct" not in st.session_state:
    st.session_state.last_correct = None

def new_question():
    """Genera nueva pregunta y opciones."""
    st.session_state.locked = False
    st.session_state.last_correct = None
    country, capital, iso2 = random.choice(st.session_state.pool)

    # Generar opciones
    options = {capital}
    distractors = [c for c in ALL_CAPITALS if c != capital]
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
        "options": options
    }

# Inicializa la primera pregunta
if st.session_state.question is None:
    new_question()

q = st.session_state.question

# -------- UI: bandera + país --------
flag_url = f"https://flagcdn.com/w320/{q['iso2']}.png"
st.image(flag_url, width=160)  # bandera
st.subheader(f"¿Cuál es la capital de **{q['country']}**?")

# -------- Opciones como botones --------
cols = st.columns(2)
clicked_value = None

for i, opt in enumerate(q["options"]):
    with cols[i % 2]:
        if st.button(opt, disabled=st.session_state.locked, use_container_width=True):
            clicked_value = opt

# -------- Resolver respuesta --------
if clicked_value and not st.session_state.locked:
    st.session_state.locked = True
    is_correct = (clicked_value == q["capital"])
    st.session_state.last_correct = is_correct
    if is_correct:
        st.success("✅ ¡Correcto!")
        st.session_state.score += 1
    else:
        st.error(f"❌ Incorrecto. La capital de **{q['country']}** es **{q['capital']}**.")

# -------- Barra inferior: progreso y controles --------
st.progress((st.session_state.current_q) / QUESTIONS_IN_LEVEL)
st.info(f"Puntuación: **{st.session_state.score} / {st.session_state.current_q}**")

col_a, col_b, col_c = st.columns(3)
with col_a:
    if st.button("🔁 Reiniciar nivel"):
        st.session_state.current_q = 0
        st.session_state.score = 0
        st.session_state.question = None
        st.session_state.locked = False
        st.session_state.last_correct = None
        st.rerun()

with col_b:
    # Mostrar solución si aún no se ha respondido
    if not st.session_state.locked:
        st.caption("Consejo: puedes usar la bandera como pista 😉")
    else:
        st.caption("Haz clic en **Siguiente** para continuar.")

with col_c:
    next_disabled = not st.session_state.locked
    if st.button("Siguiente ▶️", disabled=next_disabled):
        st.session_state.current_q += 1
        if st.session_state.current_q >= QUESTIONS_IN_LEVEL:
            st.balloons()
            st.success(f"🎉 ¡Nivel completado! Resultado final: {st.session_state.score}/{QUESTIONS_IN_LEVEL}")
            # Preparar siguiente vuelta del nivel
            st.session_state.current_q = 0
            st.session_state.score = 0
        new_question()
        st.rerun()