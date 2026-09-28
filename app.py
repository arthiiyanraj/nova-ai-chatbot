import asyncio
import hashlib
import os
import tempfile
import wave
import io

import streamlit as st

from datetime import datetime
from zoneinfo import ZoneInfo


# ============================================================
# BACKEND IMPORTS
# ============================================================

from backend.auth import (
    create_users_table,
    register_user,
    login_user,
)

from backend.llm import (
    get_llm,
)

from backend.prompts import (
    create_chat_prompt,
)

from backend.memory import (
    create_memory_table,
    save_memory,
    get_memories,
    build_chat_history,
    detect_memory,
)

from backend.session import (
    initialize_session,
    login,
    logout,
)

from backend.pdf_manager import (
    process_pdf,
)

from backend.pdf_qa import (
    ask_pdf,
)

from backend.web_qa import (
    ask_web,
)

from backend.router import (
    route_question,
)

from backend.chat_history import (
    create_chat_tables,
    create_chat_session,
    get_chat_sessions,
    get_chat_messages,
    save_chat_message,
    update_chat_title,
)

from backend.pdf_database import (
    create_pdf_table,
    save_pdf_document,
    get_user_pdfs,
    delete_pdf_document,
)

from backend.vectorstore import (
    delete_vector_store,
)

from backend.response_utils import (
    get_response_text,
)

from backend.voice.orchestrator import (
    process_voice,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="NOVA AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PROFESSIONAL UI STYLING
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 7rem;
    }

    section[data-testid="stSidebar"] {
        padding-top: 1rem;
    }

    div[data-testid="stChatMessage"] {
        padding-top: 0.75rem;
        padding-bottom: 0.75rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

create_users_table()
create_memory_table()
create_chat_tables()
create_pdf_table()


# ============================================================
# STREAMLIT SESSION INITIALIZATION
# ============================================================

initialize_session()


if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = None


if "pdf_documents" not in st.session_state:
    st.session_state.pdf_documents = []


if "active_pdf_id" not in st.session_state:
    st.session_state.active_pdf_id = None


if "pdf_loaded_for_user" not in st.session_state:
    st.session_state.pdf_loaded_for_user = None


if "last_voice_hash" not in st.session_state:
    st.session_state.last_voice_hash = None


# ============================================================
# CURRENT DATE
# ============================================================

def get_current_date():
    """
    Return current date in Indian Standard Time.
    """

    now = datetime.now(
        ZoneInfo("Asia/Kolkata")
    )

    return now.strftime(
        "%A, %B %d, %Y"
    ).replace(
        " 0",
        " ",
    )


def is_date_question(question):
    """
    Detect common questions asking for today's date.
    """

    text = question.lower().strip()

    date_patterns = [
        "what is today's date",
        "what is todays date",
        "what's today's date",
        "what's todays date",
        "what is the date today",
        "what date is it",
        "today's date",
        "todays date",
        "current date",
        "date today",
        "what day is today",
        "what is today",
    ]

    return any(
        pattern in text
        for pattern in date_patterns
    )


# ============================================================
# LOGIN / REGISTER
# ============================================================

if not st.session_state.logged_in:

    st.title("NOVA AI")

    st.caption(
        "Your general-purpose AI assistant"
    )

    st.divider()

    login_tab, register_tab = st.tabs(
        [
            "Login",
            "Create Account",
        ]
    )

    # ========================================================
    # LOGIN
    # ========================================================

    with login_tab:

        st.subheader(
            "Welcome back"
        )

        username = st.text_input(
            "Username",
            key="login_username",
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password",
        )

        if st.button(
            "Login",
            use_container_width=True,
        ):

            username = username.strip()

            if not username or not password:

                st.warning(
                    "Please enter username and password."
                )

            else:

                user = login_user(
                    username,
                    password,
                )

                if user:

                    login(user)

                    st.session_state.pdf_loaded_for_user = None
                    st.session_state.pdf_documents = []
                    st.session_state.active_pdf_id = None
                    st.session_state.active_chat_id = None
                    st.session_state.last_voice_hash = None

                    st.rerun()

                else:

                    st.error(
                        "Invalid username or password."
                    )

    # ========================================================
    # REGISTER
    # ========================================================

    with register_tab:

        st.subheader(
            "Create your NOVA account"
        )

        new_username = st.text_input(
            "Username",
            key="register_username",
        )

        new_password = st.text_input(
            "Password",
            type="password",
            key="register_password",
        )

        if st.button(
            "Create Account",
            use_container_width=True,
        ):

            new_username = new_username.strip()

            if not new_username or not new_password:

                st.warning(
                    "Please enter username and password."
                )

            elif len(new_username) < 3:

                st.warning(
                    "Username must contain at least 3 characters."
                )

            elif len(new_password) < 6:

                st.warning(
                    "Password must contain at least 6 characters."
                )

            else:

                created = register_user(
                    new_username,
                    new_password,
                )

                if created:

                    st.success(
                        "Account created successfully."
                    )

                else:

                    st.error(
                        "That username already exists."
                    )

    st.stop()


# ============================================================
# CURRENT USER
# ============================================================

user = st.session_state.user


# ============================================================
# LOAD USER DOCUMENTS
# ============================================================

if (
    st.session_state.pdf_loaded_for_user
    != user["id"]
):

    st.session_state.pdf_documents = (
        get_user_pdfs(
            user["id"]
        )
    )

    st.session_state.pdf_loaded_for_user = (
        user["id"]
    )

    if st.session_state.pdf_documents:

        if not st.session_state.active_pdf_id:

            st.session_state.active_pdf_id = (
                st.session_state.pdf_documents[0][
                    "document_id"
                ]
            )


# ============================================================
# LOAD CHAT SESSIONS
# ============================================================

chat_sessions = get_chat_sessions(
    user["id"]
)


# ============================================================
# CREATE FIRST CHAT
# ============================================================

if (
    not chat_sessions
    and st.session_state.active_chat_id is None
):

    chat_id = create_chat_session(
        user["id"],
        "New Chat",
    )

    st.session_state.active_chat_id = chat_id
    st.session_state.messages = []

    st.rerun()


# ============================================================
# LOAD EXISTING CHAT
# ============================================================

if (
    st.session_state.active_chat_id is None
    and chat_sessions
):

    latest_chat_id = chat_sessions[0][0]

    st.session_state.active_chat_id = (
        latest_chat_id
    )

    st.session_state.messages = (
        get_chat_messages(
            latest_chat_id
        )
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # ========================================================
    # BRAND
    # ========================================================

    st.title("NOVA AI")

    st.caption(
        "Your personal AI assistant"
    )

    st.divider()

    # ========================================================
    # USER
    # ========================================================

    st.write(
        f"**{user['username']}**"
    )

    # ========================================================
    # NEW CHAT
    # ========================================================

    if st.button(
        "＋ New chat",
        use_container_width=True,
    ):

        chat_id = create_chat_session(
            user["id"],
            "New Chat",
        )

        st.session_state.active_chat_id = (
            chat_id
        )

        st.session_state.messages = []

        st.session_state.last_voice_hash = None

        st.rerun()

    st.divider()

    # ========================================================
    # CHAT HISTORY
    # ========================================================

    st.caption(
        "Chats"
    )

    chat_sessions = get_chat_sessions(
        user["id"]
    )

    for chat in chat_sessions:

        chat_id = chat[0]
        chat_title = chat[1]

        if (
            chat_id
            == st.session_state.active_chat_id
        ):

            label = f"● {chat_title}"

        else:

            label = chat_title

        if st.button(
            label,
            key=f"chat_{chat_id}",
            use_container_width=True,
        ):

            st.session_state.active_chat_id = (
                chat_id
            )

            st.session_state.messages = (
                get_chat_messages(
                    chat_id
                )
            )

            st.session_state.last_voice_hash = None

            st.rerun()

    # ========================================================
    # DOCUMENTS
    # ========================================================

    if st.session_state.pdf_documents:

        st.divider()

        st.caption(
            "Documents"
        )

        pdf_options = {}

        for index, document in enumerate(
            st.session_state.pdf_documents
        ):

            display_name = (
                f"{document['name']} "
                f"({index + 1})"
            )

            pdf_options[
                display_name
            ] = document["document_id"]

        option_names = list(
            pdf_options.keys()
        )

        # ----------------------------------------------------
        # Find active document
        # ----------------------------------------------------

        current_index = 0

        if st.session_state.active_pdf_id:

            for index, name in enumerate(
                option_names
            ):

                if (
                    pdf_options[name]
                    == st.session_state.active_pdf_id
                ):

                    current_index = index
                    break

        selected_pdf_name = st.selectbox(
            "Active document",
            option_names,
            index=current_index,
        )

        selected_pdf_id = pdf_options[
            selected_pdf_name
        ]

        st.session_state.active_pdf_id = (
            selected_pdf_id
        )

        selected_document = next(
            (
                document
                for document
                in st.session_state.pdf_documents
                if (
                    document["document_id"]
                    == selected_pdf_id
                )
            ),
            None,
        )

        if selected_document:

            st.caption(
                selected_document["name"]
            )

            st.caption(
                f"{selected_document['chunks']} chunks"
            )

            # =================================================
            # DELETE DOCUMENT
            # =================================================

            if st.button(
                "Delete document",
                use_container_width=True,
            ):

                try:

                    document_id = (
                        selected_document[
                            "document_id"
                        ]
                    )

                    document_name = (
                        selected_document[
                            "name"
                        ]
                    )

                    delete_vector_store(
                        user["id"],
                        document_id,
                    )

                    delete_pdf_document(
                        user["id"],
                        document_id,
                    )

                    st.session_state.pdf_documents = [
                        document
                        for document
                        in st.session_state.pdf_documents
                        if (
                            document[
                                "document_id"
                            ]
                            != document_id
                        )
                    ]

                    if (
                        st.session_state.pdf_documents
                    ):

                        st.session_state.active_pdf_id = (
                            st.session_state.pdf_documents[0][
                                "document_id"
                            ]
                        )

                    else:

                        st.session_state.active_pdf_id = None

                    st.success(
                        f"{document_name} deleted."
                    )

                    st.rerun()

                except Exception as error:

                    st.error(
                        "Document deletion failed."
                    )

                    st.exception(
                        error
                    )

    # ========================================================
    # LOGOUT
    # ========================================================

    st.divider()

    if st.button(
        "Logout",
        use_container_width=True,
    ):

        logout()

        st.session_state.active_chat_id = None
        st.session_state.pdf_documents = []
        st.session_state.active_pdf_id = None
        st.session_state.pdf_loaded_for_user = None
        st.session_state.last_voice_hash = None

        st.rerun()


# ============================================================
# MAIN HEADER
# ============================================================

st.title("NOVA AI")

st.caption(
    f"Hello {user['username']}. Ask me anything."
)


# ============================================================
# CURRENT CHAT TITLE
# ============================================================

current_chat_title = "New Chat"

for chat in get_chat_sessions(
    user["id"]
):

    if (
        chat[0]
        == st.session_state.active_chat_id
    ):

        current_chat_title = chat[1]
        break


if current_chat_title != "New Chat":

    st.caption(
        current_chat_title
    )


# ============================================================
# ACTIVE DOCUMENT
# ============================================================

if (
    st.session_state.active_pdf_id
    and st.session_state.pdf_documents
):

    active_pdf = next(
        (
            document
            for document
            in st.session_state.pdf_documents
            if (
                document["document_id"]
                == st.session_state.active_pdf_id
            )
        ),
        None,
    )

    if active_pdf:

        st.caption(
            f"Using document: {active_pdf['name']}"
        )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    role = message["role"]
    content = message["content"]

    with st.chat_message(role):

        st.markdown(
            content
        )


# ============================================================
# VOICE INPUT
# ============================================================

st.divider()

st.subheader(
    "🎙️ Talk to NOVA"
)

st.caption(
    "Speak naturally in your preferred language."
)

voice_audio = st.audio_input(
    "Record your message",
    sample_rate=16000,
)


# ============================================================
# VOICE SUBMISSION
# ============================================================

if voice_audio:

    try:

        # ----------------------------------------------------
        # READ AUDIO BYTES
        # ----------------------------------------------------

        audio_bytes = voice_audio.getvalue()

        if not audio_bytes:

            st.error(
                "No audio was received. Please try again."
            )

            st.stop()

        # ----------------------------------------------------
        # DUPLICATE SUBMISSION PROTECTION
        # ----------------------------------------------------

        audio_hash = hashlib.sha256(
            audio_bytes
        ).hexdigest()

        if (
            audio_hash
            == st.session_state.last_voice_hash
        ):

            st.stop()

        st.session_state.last_voice_hash = (
            audio_hash
        )

        # ----------------------------------------------------
        # READ WAV DIRECTLY
        #
        # Streamlit audio_input returns WAV audio.
        # No FFmpeg / ffprobe / pydub required.
        # ----------------------------------------------------

        with st.spinner(
            "Preparing your voice message..."
        ):

            audio_buffer = io.BytesIO(
                audio_bytes
            )

            with wave.open(
                audio_buffer,
                "rb",
            ) as wav_file:

                channels = (
                    wav_file.getnchannels()
                )

                sample_width = (
                    wav_file.getsampwidth()
                )

                sample_rate = (
                    wav_file.getframerate()
                )

                pcm_data = (
                    wav_file.readframes(
                        wav_file.getnframes()
                    )
                )

        # ----------------------------------------------------
        # VALIDATE AUDIO FORMAT
        #
        # Gemini Live expects:
        #
        # Channels      = 1
        # Sample width  = 16-bit
        # Sample rate   = 16000 Hz
        # ----------------------------------------------------

        if channels != 1:

            st.error(
                "Voice recording must be mono audio."
            )

            st.stop()

        if sample_rate != 16000:

            st.error(
                "Voice recording must use a 16 kHz sample rate."
            )

            st.stop()

        if sample_width != 2:

            st.error(
                "Voice recording must use 16-bit PCM audio."
            )

            st.stop()

        if not pcm_data:

            st.error(
                "The recorded audio is empty."
            )

            st.stop()

        # ----------------------------------------------------
        # CREATE UNIQUE OUTPUT FILE
        # ----------------------------------------------------

        output_file = os.path.join(
            tempfile.gettempdir(),
            f"nova_voice_{audio_hash[:16]}.wav",
        )

        # ----------------------------------------------------
        # COMPLETE VOICE PIPELINE
        #
        # Audio
        #   ↓
        # Speech-to-Text
        #   ↓
        # NOVA Answer Engine
        #   ↓
        # Text-to-Speech
        #   ↓
        # Voice Audio
        # ----------------------------------------------------

        with st.spinner(
            "NOVA is listening and thinking..."
        ):

            result = asyncio.run(
                process_voice(
                    pcm_data=pcm_data,
                    user_id=user["id"],
                    chat_messages=st.session_state.messages,
                    active_pdf_id=st.session_state.active_pdf_id,
                    output_file=output_file,
                )
            )

        # ----------------------------------------------------
        # READ RESULT
        # ----------------------------------------------------

        transcript = result.get(
            "transcript",
            "",
        ).strip()

        answer = result.get(
            "answer",
            "",
        )

        route = result.get(
            "route",
            "GENERAL",
        )

        web_sources = result.get(
            "web_sources",
            [],
        )

        audio_file = result.get(
            "audio_file"
        )

        # ----------------------------------------------------
        # EMPTY TRANSCRIPT
        # ----------------------------------------------------

        if not transcript:

            st.warning(
                "I couldn't understand the audio. "
                "Please try speaking again."
            )

            st.stop()

        # ----------------------------------------------------
        # USER VOICE MESSAGE
        # ----------------------------------------------------

        with st.chat_message(
            "user"
        ):

            st.markdown(
                transcript
            )

        st.session_state.messages.append(
            {
                "role": "user",
                "content": transcript,
            }
        )

        save_chat_message(
            st.session_state.active_chat_id,
            "user",
            transcript,
        )

        # ----------------------------------------------------
        # ASSISTANT RESPONSE
        # ----------------------------------------------------

        with st.chat_message(
            "assistant"
        ):

            st.markdown(
                answer
            )

            # ------------------------------------------------
            # ROUTE
            # ------------------------------------------------

            st.caption(
                f"Route: {route}"
            )

            # ------------------------------------------------
            # WEB SOURCES
            # ------------------------------------------------

            if web_sources:

                st.divider()

                st.caption(
                    "Sources"
                )

                for source in web_sources:

                    title = source.get(
                        "title",
                        "Source",
                    )

                    url = source.get(
                        "url",
                        "",
                    )

                    if url:

                        st.markdown(
                            f"- [{title}]({url})"
                        )

            # ------------------------------------------------
            # VOICE RESPONSE
            # ------------------------------------------------

            if (
                audio_file
                and os.path.exists(audio_file)
            ):

                st.audio(
                    audio_file,
                    format="audio/wav",
                )

        # ----------------------------------------------------
        # SAVE MEMORY
        # ----------------------------------------------------

        detected_memory = detect_memory(
            transcript
        )

        if detected_memory:

            save_memory(
                user["id"],
                detected_memory,
            )

        # ----------------------------------------------------
        # SAVE ASSISTANT MESSAGE
        # ----------------------------------------------------

        save_chat_message(
            st.session_state.active_chat_id,
            "assistant",
            answer,
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

        # ----------------------------------------------------
        # AUTOMATIC CHAT TITLE
        # ----------------------------------------------------

        current_title = "New Chat"

        for chat in get_chat_sessions(
            user["id"]
        ):

            if (
                chat[0]
                == st.session_state.active_chat_id
            ):

                current_title = chat[1]
                break

        if current_title == "New Chat":

            title = transcript[:40]

            if len(transcript) > 40:

                title += "..."

            update_chat_title(
                st.session_state.active_chat_id,
                title,
            )

    except wave.Error:

        st.session_state.last_voice_hash = None

        st.error(
            "The recorded audio format could not be read. "
            "Please record again."
        )

    except Exception as error:

        st.session_state.last_voice_hash = None

        st.error(
            "Voice processing failed."
        )

        st.exception(
            error
        )


# ============================================================
# CHAT INPUT
# ============================================================

chat_input = st.chat_input(
    "Message NOVA...",
    accept_file="multiple",
    file_type=["pdf"],
    max_upload_size=200,
)


# ============================================================
# CHAT SUBMISSION
# ============================================================

if chat_input:

    # ========================================================
    # QUESTION
    # ========================================================

    question = chat_input.text.strip()

    # ========================================================
    # FILES
    # ========================================================

    uploaded_files = list(
        chat_input.files
    )

    # ========================================================
    # UPLOAD STATUS
    # ========================================================

    uploaded_pdf_processed = False
    uploaded_pdf_failed = False

    processed_document_names = []

    # ========================================================
    # PROCESS ALL UPLOADED PDF FILES
    # ========================================================

    if uploaded_files:

        with st.spinner(
            "Processing uploaded document(s)..."
        ):

            for uploaded_file in uploaded_files:

                file_name = uploaded_file.name

                try:

                    file_bytes = (
                        uploaded_file.getvalue()
                    )

                except Exception:

                    file_bytes = b""

                if not file_bytes:

                    uploaded_pdf_failed = True

                    st.error(
                        f"{file_name} is empty."
                    )

                    continue

                try:

                    result = process_pdf(
                        uploaded_file,
                        user["id"],
                    )

                    if result["success"]:

                        save_pdf_document(
                            user_id=user["id"],
                            document_id=result[
                                "document_id"
                            ],
                            document_name=result[
                                "document_name"
                            ],
                            characters=result[
                                "characters"
                            ],
                            chunks=result[
                                "chunks"
                            ],
                        )

                        document = {
                            "document_id": (
                                result[
                                    "document_id"
                                ]
                            ),
                            "name": (
                                result[
                                    "document_name"
                                ]
                            ),
                            "characters": (
                                result[
                                    "characters"
                                ]
                            ),
                            "chunks": (
                                result[
                                    "chunks"
                                ]
                            ),
                            "created_at": "",
                        }

                        # ------------------------------------
                        # Add newest document
                        # ------------------------------------

                        st.session_state.pdf_documents.insert(
                            0,
                            document,
                        )

                        # ------------------------------------
                        # Make newest document active
                        # ------------------------------------

                        st.session_state.active_pdf_id = (
                            result[
                                "document_id"
                            ]
                        )

                        uploaded_pdf_processed = True

                        processed_document_names.append(
                            result[
                                "document_name"
                            ]
                        )

                    else:

                        uploaded_pdf_failed = True

                        st.error(
                            f"{file_name}: "
                            f"{result['message']}"
                        )

                except Exception as error:

                    uploaded_pdf_failed = True

                    st.error(
                        f"{file_name}: "
                        "Document processing failed."
                    )

                    st.exception(
                        error
                    )

    # ========================================================
    # NO QUESTION + FILES
    # ========================================================

    if (
        uploaded_pdf_processed
        and not question
    ):

        if len(
            processed_document_names
        ) == 1:

            st.success(
                f"{processed_document_names[0]} is ready."
            )

        else:

            st.success(
                f"{len(processed_document_names)} "
                "documents are ready."
            )

        if uploaded_pdf_failed:

            st.warning(
                "Some documents could not be processed."
            )

        st.rerun()

    # ========================================================
    # NOTHING TO SEND
    # ========================================================

    if not question:

        st.stop()

    # ========================================================
    # UPLOAD FAILED + QUESTION
    # ========================================================

    if (
        uploaded_pdf_failed
        and not uploaded_pdf_processed
    ):

        st.error(
            "The uploaded document could not be processed, "
            "so the question was not sent."
        )

        st.stop()

    # ========================================================
    # SAVE USER MESSAGE
    # ========================================================

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    save_chat_message(
        st.session_state.active_chat_id,
        "user",
        question,
    )

    # ========================================================
    # DISPLAY USER MESSAGE
    # ========================================================

    with st.chat_message(
        "user"
    ):

        st.markdown(
            question
        )

    # ========================================================
    # ASSISTANT RESPONSE
    # ========================================================

    answer = ""
    web_sources = []
    route = "GENERAL"

    with st.chat_message(
        "assistant"
    ):

        with st.spinner(
            "Thinking..."
        ):

            try:

                # =================================================
                # CURRENT DATE
                # =================================================

                if is_date_question(question):

                    route = "GENERAL"

                    answer = (
                        f"Today is "
                        f"{get_current_date()}."
                    )

                # =================================================
                # NEWLY UPLOADED PDF + QUESTION
                # =================================================

                elif uploaded_pdf_processed:

                    route = "PDF"

                    answer = ask_pdf(
                        question,
                        user["id"],
                        st.session_state.active_pdf_id,
                        top_k=5,
                    )

                # =================================================
                # SMART ROUTER
                # =================================================

                else:

                    route = route_question(
                        question
                    )

                    # =============================================
                    # PDF
                    # =============================================

                    if route == "PDF":

                        if (
                            st.session_state.pdf_documents
                            and
                            st.session_state.active_pdf_id
                        ):

                            answer = ask_pdf(
                                question,
                                user["id"],
                                st.session_state.active_pdf_id,
                                top_k=5,
                            )

                        else:

                            # -------------------------------------
                            # Professional fallback:
                            # If PDF is requested but no PDF exists,
                            # use the normal LLM instead of returning
                            # an artificial PDF-only message.
                            # -------------------------------------

                            llm = get_llm()

                            prompt = create_chat_prompt()

                            chain = prompt | llm

                            chat_history = (
                                build_chat_history(
                                    st.session_state.messages[
                                        :-1
                                    ]
                                )
                            )

                            memories = get_memories(
                                user["id"]
                            )

                            if memories:

                                memory_text = "\n".join(
                                    f"- {memory}"
                                    for memory in memories
                                )

                            else:

                                memory_text = (
                                    "No saved memories."
                                )

                            response = chain.invoke(
                                {
                                    "memories": memory_text,
                                    "chat_history": chat_history,
                                    "question": question,
                                }
                            )

                            answer = get_response_text(
                                response
                            )

                            route = "GENERAL"

                    # =============================================
                    # WEB
                    # =============================================

                    elif route == "WEB":

                        web_result = ask_web(
                            question,
                            max_results=6,
                        )

                        answer = (
                            web_result["answer"]
                        )

                        web_sources = (
                            web_result["sources"]
                        )

                    # =============================================
                    # GENERAL
                    # =============================================

                    else:

                        llm = get_llm()

                        prompt = create_chat_prompt()

                        chain = prompt | llm

                        # -----------------------------------------
                        # Previous messages
                        # -----------------------------------------

                        chat_history = (
                            build_chat_history(
                                st.session_state.messages[
                                    :-1
                                ]
                            )
                        )

                        # -----------------------------------------
                        # Long-term memory
                        # -----------------------------------------

                        memories = get_memories(
                            user["id"]
                        )

                        if memories:

                            memory_text = "\n".join(
                                f"- {memory}"
                                for memory in memories
                            )

                        else:

                            memory_text = (
                                "No saved memories."
                            )

                        # -----------------------------------------
                        # Generate answer
                        # -----------------------------------------

                        response = chain.invoke(
                            {
                                "memories": memory_text,
                                "chat_history": chat_history,
                                "question": question,
                            }
                        )

                        answer = get_response_text(
                            response
                        )

                # =================================================
                # EMPTY ANSWER SAFETY
                # =================================================

                if not answer:

                    answer = (
                        "I couldn't generate an answer "
                        "right now. Please try again."
                    )

                # =================================================
                # DISPLAY ANSWER
                # =================================================

                st.markdown(
                    answer
                )

                # =================================================
                # WEB SOURCES
                # =================================================

                if web_sources:

                    st.divider()

                    st.caption(
                        "Sources"
                    )

                    for source in web_sources:

                        title = source.get(
                            "title",
                            "Source",
                        )

                        url = source.get(
                            "url",
                            "",
                        )

                        if url:

                            st.markdown(
                                f"- [{title}]({url})"
                            )

            except Exception as error:

                answer = (
                    "Sorry, something went wrong "
                    "while generating the answer."
                )

                st.error(
                    answer
                )

                st.exception(
                    error
                )

    # ========================================================
    # SAVE MEMORY
    # ========================================================

    detected_memory = detect_memory(
        question
    )

    if detected_memory:

        save_memory(
            user["id"],
            detected_memory,
        )

    # ========================================================
    # SAVE ASSISTANT MESSAGE
    # ========================================================

    save_chat_message(
        st.session_state.active_chat_id,
        "assistant",
        answer,
    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    # ========================================================
    # AUTOMATIC CHAT TITLE
    # ========================================================

    current_title = "New Chat"

    for chat in get_chat_sessions(
        user["id"]
    ):

        if (
            chat[0]
            == st.session_state.active_chat_id
        ):

            current_title = chat[1]
            break

    if current_title == "New Chat":

        title = question[:40]

        if len(question) > 40:

            title += "..."

        update_chat_title(
            st.session_state.active_chat_id,
            title,
        )