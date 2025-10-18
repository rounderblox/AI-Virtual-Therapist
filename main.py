# main.py
import time
import streamlit as st
import cv2
from deepface import DeepFace
import tempfile
from llm_interface import get_therapist_response
from session_storage import init_session, add_message, get_chat_history
from risk_alert import check_for_risk, send_risk_email

st.set_page_config(page_title="AI Therapist", layout="centered")
st.title("🌸 Personal AI Therapist")

st.markdown(
    """
    <style>
        /* Entire App Background and Text */
        .stApp {
            background-color: #2271b1 !important;
            color: #000000 !important;
        }

        html, body, [class^="css"] {
            background-color: #2271b1 !important;
            color: #000000 !important;
        }

        /* Override all markdown and text elements */
        .stMarkdown, .stTextElement, .stText, .css-1cpxqw2, .css-10trblm {
            color: #00131c !important;
        }

        /* Text input fields, textarea */
        textarea, input, .stTextInput > div > div > input {
            background-color: #ffffff !important;
            color: #00131c !important;
            border: 1px solid #007acc !important;
            caret-color: #000000 !important;
        }

        /* Buttons */
        .stButton>button {
            background-color: #000000 !important;
            color: #000000 !important;
            font-weight: bold;
            border-radius: 6px;
            border: 1px solid #007acc;
            padding: 0.5em 1em;
        }

        .stButton>button:hover {
            background-color: #2271b1 !important;
        }

        /* Checkboxes and labels */
        .stCheckbox > label {
            color: #000000 !important;
        }

        /* Radio, selectbox, form labels */
        label, .stSelectbox label, .stRadio label {
            color: #000000 !important;
        }

        /* Chat bubbles / message markdown */
        .css-1kyxreq, .css-1v0mbdj {
            color: #000000 !important;
        }

        /* Make the label white */
        label[for="input"] {
            color: #ffffff !important;
            font-weight: bold;
        }

        /* Make the conversation text white */
        div[data-testid="stMarkdownContainer"] p {
            color: #ffffff !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

init_session()

# --- Emotion Detection ---


def detect_emotion():
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            return "Unknown"

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            cv2.imwrite(tmp.name, frame)
            analysis = DeepFace.analyze(img_path=tmp.name, actions=[
                                        "emotion"], enforce_detection=False)
            return analysis[0]["dominant_emotion"]
    except Exception:
        return "Unknown"


# --- Chat UI ---
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_area(
        "How are you feeling today?", key="input", height=100)
    detect_face = st.checkbox("Use facial emotion detection")
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    # Step 1: Emotion detection
    emotion = detect_emotion() if detect_face else None

    # Step 2: Risk detection and alert
    if check_for_risk(user_input):
        send_risk_email(user_input)
        st.warning(
            "⚠️ Risk-related content detected. The therapist has been alerted.")

    # Step 3: Store user message
    add_message("user", user_input)

    # Step 4: Get LLM response
    with st.spinner("Therapist is thinking..."):
        response = get_therapist_response(user_input, emotion)

    # Step 5: Store and display response
    add_message("assistant", response)

# --- Display Chat History ---
for msg in get_chat_history():
    if msg["role"] == "user":
        st.markdown(f"🧑‍💬 **You** ({msg['time']}): {msg['content']}")
    else:
        st.markdown(f"🤖 **Therapist** ({msg['time']}): {msg['content']}")

# --- Live Webcam View ---
show_cam = st.checkbox("📷 Show Live Webcam")

if show_cam:
    FRAME_WINDOW = st.image([])
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        st.warning("Webcam not accessible.")
    else:
        for _ in range(30):
            ret, frame = cap.read()
            if not ret:
                st.error("Failed to capture video frame.")
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            FRAME_WINDOW.image(frame)
        cap.release()


# --- Journaling Section ---
st.markdown("---")
with st.expander("📓 Journaling (Private Notes)"):
    st.markdown(
        "Write down your thoughts, reflections, or anything else you'd like to note.")

    # Daily Prompt
    st.markdown("### 🌅 Daily Guided Prompt")
    st.markdown(
        "> *\"What emotions did I experience today, and what might have caused them? How did I respond to those feelings?\"*")

    # Initialize journal state
    if "journal_entries" not in st.session_state:
        st.session_state.journal_entries = []

    if "clear_journal_input" not in st.session_state:
        st.session_state.clear_journal_input = False

    if st.session_state.clear_journal_input:
        journal_input = st.text_area(
            "Your Journal Entry", height=150, key="journal_input_temp")
    else:
        journal_input = st.text_area(
            "Your Journal Entry", height=150, key="journal_input")

    if st.button("Save Journal Entry"):
        if journal_input.strip():
            st.session_state.journal_entries.append(journal_input.strip())
            st.session_state.clear_journal_input = True
            st.experimental_rerun()

    if st.session_state.clear_journal_input:

        st.session_state.clear_journal_input = False

    if st.session_state.journal_entries:
        st.markdown("### 📝 Your Journal")
        for idx, entry in enumerate(reversed(st.session_state.journal_entries), 1):
            st.markdown(f"**Entry {idx}:**\n\n{entry}\n---")

# --- Breathing Exercise Section ---

st.markdown("---")
with st.expander("🧘‍♂️ Guided Breathing Exercise"):
    st.markdown("Take a moment to relax with this short breathing exercise.")

    duration = st.slider("⏱️ Select duration (seconds per step)", 2, 6, 4)
    cycles = st.slider("🔄 Number of breaths", 1, 5, 3)

    if st.button("Start Breathing"):
        st.empty()
        for i in range(cycles):
            st.markdown(f"### 🌬️ Inhale")
            time.sleep(duration)
            st.markdown(f"### 🫁 Hold")
            time.sleep(duration)
            st.markdown(f"### 😮‍💨 Exhale")
            time.sleep(duration)
            st.markdown("---")
        st.success("✨ Great job! You completed the breathing cycle.")
