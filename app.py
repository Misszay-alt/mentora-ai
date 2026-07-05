import streamlit as st
import google.generativeai as genai
import PyPDF2
import os
import tempfile
from pypdf import PdfReader
from docx import Document

def load_preloaded_files():
    all_text = ""
    files_to_load = ["ROBOTICS UPDATED.pdf", "BASIC PUBLISHER UPDATED.pdf"]

    for filename in files_to_load:
        if os.path.exists(filename):
            try:
                reader = PyPDF2.PdfReader(filename)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        all_text += text + "\n"
            except:
                all_text += f"\n[Could not read {filename}]\n"
        else:
            all_text += f"\n[Warning: {filename} not found]\n"

    return all_text
# Load materials automatically
if "materials" not in st.session_state:
    st.session_state.materials = load_preloaded_files()

st.set_page_config(page_title="Mentora AI", layout="wide")
st.title("🎓 Mentora AI")
st.caption("Your Personal AI Tutor. Your teacher's notes are already uploaded. Just ask questions.")

# 1. CONFIGURE API KEY SAFELY
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = st.text_input("Enter your Google AI API Key", type="password")

if not api_key:
    st.warning("Please enter your API key to start Mentora AI")
    st.stop()

genai.configure(api_key=api_key)
# 2. CHAT INTERFACE
st.header("2. Ask Mentora")
st.info("Your notes are already loaded by your teacher.")

# Step 1: Ask for name first
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if st.session_state.user_name == "":
    name = st.text_input("What's your name?")
    if st.button("Start Chatting"):
        if name:
            st.session_state.user_name = name
            st.rerun()
        else:
            st.warning("Please enter your name")
else:
    st.success(f"Hi {st.session_state.user_name}! Mentora is ready for your questions.")

    # Step 2: Show chat box after we have name
    user_question = st.chat_input("Ask a question about your materials...")

    if user_question:
        with st.spinner("Mentora is thinking..."):
            materials_snippet = st.session_state.materials[:90000] if st.session_state.materials else "No materials loaded yet."

            prompt = f"""You are Mentora, a friendly tutor.
Answer ONLY using the LEARNING MATERIAL below.
If the answer is not in the material, say "I couldn't find that in your notes."

LEARNING MATERIAL:
{materials_snippet}

--------------------------
Student's question: {user_question}
Answer:"""

            # Call Gemini to get the real answer
            response = model.generate_content(prompt)
            answer = response.text

            st.chat_message("user").write(user_question)
            st.chat_message("assistant").write(answer)
.
Answer ONLY using the LEARNING MATERIAL below.
If the answer is not in the material, say "I couldn't find that in your notes."

LEARNING MATERIAL:
{materials_snippet}

Student's question: {user_question}
Answer:"""

        # Call Gemini to get the real answer
        response = model.generate_content(prompt)
        answer = response.text

        st.chat_message("user").write(user_question)
        st.chat_message("assistant").write(answer)  # <- 8 spaces
def load_materials():
    folder_path = "materials"
    materials_text = []
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        try:
            if filename.endswith(".txt"):
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()
            elif filename.endswith(".pdf"):
                reader = PyPDF2.PdfReader(filepath)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            elif filename.endswith(".docx"):
                doc = Document(filepath)
                text = ""
                for para in doc.paragraphs:
                    text += para.text + "\n"
            else:
                text = ""

            materials_text.append(f"\n\n--- START OF {filename} ---\n\n{text}\n\n--- END OF {filename} ---\n")
        except Exception as e:
            materials_text.append(f"\nError reading {filename}: {e}")

    all_text = "\n\n".join(materials_text)
    return all_text if all_text else "No documents loaded."

st.header("1. Course Materials")
st.info("Your notes are already loaded by your teacher.")
st.success("Mentora is ready! Ask me anything.")
st.session_state.ready = True
material_count = len(st.session_state.materials) if st.session_state.materials else 0
st.write(f"Materials loaded: {material_count} characters")
with st.spinner("Mentora AI is studying your materials..."):
    materials_text = st.session_state.materials

    system_prompt = f"""
    You are Mentora AI, a helpful AI Tutor for students in Accra, Ghana.
    Your ONLY job is to answer questions using the learning material and video provided.
    If the answer is not in the material, say "That's not in the documents or video you gave me."
    Always be clear, simple, encouraging, and give examples. Cite which document the answer came from.
    Sign your answers as "- Mentora AI"

    LEARNING MATERIAL:
    {materials_text[:900000]}
    """

# 5. CHAT INTERFACE
if "chat" not in st.session_state:
    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_prompt)
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask Mentora AI anything about your notes..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Mentora AI is thinking..."):
            response = st.session_state.chat.send_message(prompt)
            st.markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})
