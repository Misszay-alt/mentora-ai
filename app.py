import streamlit as st
import google.generativeai as genai
import os
import tempfile
from pypdf import PdfReader
from docx import Document

st.set_page_config(page_title="Mentora AI", layout="wide")
st.title("🎓 Mentora AI")
st.caption("Your Personal AI Tutor. Upload notes, PDFs, DOCX, or Videos. Then ask questions.")

# 1. CONFIGURE API KEY SAFELY
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = st.text_input("Enter your Google AI API Key", type="password")

if not api_key:
    st.warning("Please enter your API key to start Mentora AI")
    st.stop()

genai.configure(api_key=api_key)

# 2. FUNCTION TO LOAD ALL DOCUMENTS FROM FOLDER
@st.cache_data
def load_materials(folder_path="materials"):
    """Loads all txt, pdf, docx from a materials folder"""
    all_text = ""
    if not os.path.exists(folder_path):
        return "No materials folder found."

    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        text = ""
        try:
            if filename.endswith(".txt"):
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()

            elif filename.endswith(".pdf"):
                reader = PdfReader(filepath)
                for page in reader.pages:
                    text += page.extract_text() + "\n"

            elif filename.endswith(".docx"):
                doc = Document(filepath)
                for para in doc.paragraphs:
                    text += para.text + "\n"

            all_text += f"\n\n--- START OF {filename} ---\n{text}\n--- END OF {filename} ---\n"
        except Exception as e:
            all_text += f"\nError reading {filename}: {e}"
    return all_text if all_text else "No documents loaded."

# 3. SIDEBAR: UPLOAD FILES + VIDEO
with st.sidebar:
    st.header("1. Add Materials to Mentora")

    uploaded_docs = st.file_uploader(
        "Upload Notes",
        type=["txt", "pdf", "docx"],
        accept_multiple_files=True
    )

    st.info("Or put files in a 'materials' folder next to app.py")

    uploaded_video = st.file_uploader("Upload Lecture Video", type=["mp4", "mov", "avi"])

    if st.button("Load Materials & Start Mentora"):
        st.session_state.ready = True

# 4. BUILD MENTORA AI
if "ready" not in st.session_state:
    st.info("Upload documents or videos in the sidebar, then click 'Load Materials & Start Mentora'")
    st.stop()

with st.spinner("Mentora AI is studying your materials..."):
    materials_text = load_materials()

    for doc in uploaded_docs:
        materials_text += f"\n\n--- START OF UPLOADED {doc.name} ---\n"
        if doc.name.endswith(".txt"):
            materials_text += doc.read().decode("utf-8")
        elif doc.name.endswith(".pdf"):
            reader = PdfReader(doc)
            for page in reader.pages:
                materials_text += page.extract_text() + "\n"
        elif doc.name.endswith(".docx"):
            doc_file = Document(doc)
            for para in doc_file.paragraphs:
                materials_text += para.text + "\n"
        materials_text += f"\n--- END OF {doc.name} ---\n"

    video_file = None
    if uploaded_video:
        st.video(uploaded_video)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(uploaded_video.read())
            video_path = tmp.name
        video_file = genai.upload_file(path=video_path)
        st.success(f"Video '{uploaded_video.name}' uploaded to Mentora AI")

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

if prompt := st.chat_input("Ask Mentora AI anything about your notes or video..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Mentora AI is thinking..."):
            if video_file:
                response = st.session_state.chat.send_message([video_file, prompt])
            else:
                response = st.session_state.chat.send_message(prompt)

            st.markdown(response.text)

    st.session_state.messages.append({"role": "assistant", "content": response.text})