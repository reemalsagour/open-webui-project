import streamlit as st
from api import login


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Internal AI Chat Platform",
    page_icon="🤖",
    layout="wide"
)

# =========================================================
# SESSION STATE
# =========================================================

# TEMPORARY TEST MODE:
# Set logged_in to True so we can preview and test the frontend
# without connecting to the FastAPI backend.
# Change this to False when the backend is ready.
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = True


# Stores the JWT token after successful login
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None


# Controls which page is currently displayed
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "chat"


# Stores messages for the currently opened chat
if "messages" not in st.session_state:
    st.session_state["messages"] = []


# Stores recent chats temporarily for frontend testing
if "chats" not in st.session_state:
    st.session_state["chats"] = []


# Stores the ID of the currently selected chat
if "current_chat_id" not in st.session_state:
    st.session_state["current_chat_id"] = None


# Stores uploaded documents temporarily
if "documents" not in st.session_state:
    st.session_state["documents"] = []


# Stores knowledge bases temporarily
if "knowledge_bases" not in st.session_state:
    st.session_state["knowledge_bases"] = []

# =========================================================
# LOGGED-IN APPLICATION
# =========================================================

if st.session_state["logged_in"]:
    # =====================================================
    # SIDEBAR
    # =====================================================

    with st.sidebar:

        st.title("🤖 AI Platform")


        # -------------------------------------------------
        # NEW CHAT
        # -------------------------------------------------

        if st.button(
            "➕ New Chat",
            use_container_width=True
        ):

            st.session_state["messages"] = []
            st.session_state["current_chat_id"] = None
            st.session_state["current_page"] = "chat"

            st.rerun()


        st.divider()


        # -------------------------------------------------
        # RECENT CHATS
        # -------------------------------------------------

        st.subheader("Recent Chats")

        if len(st.session_state["chats"]) == 0:

            st.caption(
                "Your conversations will appear here."
            )

        else:

            for chat in st.session_state["chats"]:

                if st.button(
                    f"💬 {chat['title']}",
                    key=f"chat_{chat['id']}",
                    use_container_width=True
                ):

                    st.session_state["current_chat_id"] = (
                        chat["id"]
                    )

                    st.session_state["messages"] = (
                        chat["messages"].copy()
                    )

                    st.session_state["current_page"] = "chat"

                    st.rerun()


        st.divider()


        # -------------------------------------------------
        # RESOURCES
        # -------------------------------------------------

        st.subheader("Resources")

        if st.button(
            "📄 Documents",
            use_container_width=True
        ):

            st.session_state["current_page"] = "documents"
            st.rerun()


        if st.button(
            "📚 Knowledge",
            use_container_width=True
        ):

            st.session_state["current_page"] = "knowledge"
            st.rerun()


        st.divider()


        # -------------------------------------------------
        # LOGOUT
        # -------------------------------------------------

        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):

            st.session_state["logged_in"] = False
            st.session_state["access_token"] = None

            st.session_state["current_page"] = "chat"
            st.session_state["messages"] = []
            st.session_state["current_chat_id"] = None

            st.rerun()

    # =====================================================
    # CHAT PAGE
    # =====================================================

    if st.session_state["current_page"] == "chat":

        st.title("Internal AI Assistant")

        st.caption(
            "Ask questions and interact with your "
            "organization's AI assistant."
        )


        # -------------------------------------------------
        # WELCOME MESSAGE
        # -------------------------------------------------

        if len(st.session_state["messages"]) == 0:

            st.info(
                "👋 Welcome! How can I help you today?"
            )


        # -------------------------------------------------
        # DISPLAY MESSAGES
        # -------------------------------------------------

        for message in st.session_state["messages"]:

            with st.chat_message(message["role"]):

                st.write(
                    message["content"]
                )


        # -------------------------------------------------
        # CHAT INPUT
        # -------------------------------------------------

        prompt = st.chat_input(
            "Ask anything..."
        )


        if prompt:

            # ---------------------------------------------
            # CREATE NEW CHAT
            # ---------------------------------------------

            # When the user sends the first message,
            # create a temporary conversation.
            if st.session_state["current_chat_id"] is None:

                new_chat_id = len(
                    st.session_state["chats"]
                ) + 1

                new_chat = {
                    "id": new_chat_id,
                    "title": prompt[:35],
                    "messages": []
                }

                st.session_state["chats"].append(
                    new_chat
                )

                st.session_state["current_chat_id"] = (
                    new_chat_id
                )


            # ---------------------------------------------
            # USER MESSAGE
            # ---------------------------------------------

            st.session_state["messages"].append(
                {
                    "role": "user",
                    "content": prompt
                }
            )


            # ---------------------------------------------
            # TEMPORARY AI RESPONSE
            # ---------------------------------------------

            # This response is only for frontend testing.
            # It will later be replaced with the FastAPI
            # chat endpoint and the real AI response.
            temporary_response = (
                "The AI backend is not connected yet. "
                "Your message was received successfully."
            )

            st.session_state["messages"].append(
                {
                    "role": "assistant",
                    "content": temporary_response
                }
            )


            # ---------------------------------------------
            # SAVE CHAT
            # ---------------------------------------------

            for chat in st.session_state["chats"]:

                if (
                    chat["id"]
                    == st.session_state["current_chat_id"]
                ):

                    chat["messages"] = (
                        st.session_state["messages"].copy()
                    )

                    break


            # Refresh the page so the conversation
            # immediately appears under Recent Chats.
            st.rerun()

    # =====================================================
    # DOCUMENTS PAGE
    # =====================================================

    elif st.session_state["current_page"] == "documents":

        st.title("📄 Documents")

        st.caption(
            "Upload and manage documents "
            "for your AI conversations."
        )

        st.divider()


        # -------------------------------------------------
        # UPLOAD DOCUMENT
        # -------------------------------------------------

        uploaded_file = st.file_uploader(
            "Upload a document",
            type=["pdf", "txt"],
            help="Supported file types: PDF and TXT"
        )


        if uploaded_file is not None:

            st.write(
                f"Selected file: **{uploaded_file.name}**"
            )


            if st.button(
                "Upload Document",
                type="primary"
            ):

                # TEMPORARY FRONTEND STORAGE:
                # FastAPI will handle the real upload later.
                if (
                    uploaded_file.name
                    not in st.session_state["documents"]
                ):

                    st.session_state["documents"].append(
                        uploaded_file.name
                    )

                    st.success(
                        f"{uploaded_file.name} "
                        "uploaded successfully!"
                    )

                else:

                    st.warning(
                        "This document has already been added."
                    )


        st.divider()


        # -------------------------------------------------
        # DOCUMENT LIST
        # -------------------------------------------------

        st.subheader("Your Documents")


        if len(st.session_state["documents"]) == 0:

            st.info(
                "No documents uploaded yet."
            )

        else:

            for document in st.session_state["documents"]:

                col1, col2 = st.columns([5, 1])


                with col1:

                    st.write(
                        f"📄 {document}"
                    )


                with col2:

                    if st.button(
                        "Delete",
                        key=f"delete_document_{document}"
                    ):

                        st.session_state[
                            "documents"
                        ].remove(document)

                        # Also remove the document from
                        # any temporary Knowledge Base.
                        for knowledge in st.session_state[
                            "knowledge_bases"
                        ]:

                            if (
                                document
                                in knowledge.get(
                                    "documents",
                                    []
                                )
                            ):

                                knowledge[
                                    "documents"
                                ].remove(document)

                        st.rerun()
    # =====================================================
    # KNOWLEDGE PAGE
    # =====================================================

    elif st.session_state["current_page"] == "knowledge":

        st.title("📚 Knowledge")

        st.caption(
            "Create and manage knowledge bases "
            "for the AI assistant."
        )

        st.divider()


        # -------------------------------------------------
        # CREATE KNOWLEDGE BASE
        # -------------------------------------------------

        st.subheader(
            "Create Knowledge Base"
        )

        knowledge_name = st.text_input(
            "Knowledge Base Name",
            placeholder="Example: HR Policies"
        )

        knowledge_description = st.text_area(
            "Description",
            placeholder=(
                "Describe the purpose "
                "of this knowledge base..."
            )
        )


        if st.button(
            "➕ Create Knowledge Base",
            type="primary"
        ):

            if not knowledge_name:

                st.warning(
                    "Please enter a Knowledge Base name."
                )

            else:

                # TEMPORARY FRONTEND STORAGE:
                # FastAPI will handle this later.
                knowledge_base = {
                    "name": knowledge_name,
                    "description": knowledge_description,
                    "documents": []
                }

                st.session_state[
                    "knowledge_bases"
                ].append(knowledge_base)

                st.success(
                    f"{knowledge_name} "
                    "created successfully!"
                )


        st.divider()


        # -------------------------------------------------
        # KNOWLEDGE BASE LIST
        # -------------------------------------------------

        st.subheader(
            "Your Knowledge Bases"
        )


        if len(
            st.session_state["knowledge_bases"]
        ) == 0:

            st.info(
                "No knowledge bases created yet."
            )

        else:

            for index, knowledge in enumerate(
                st.session_state["knowledge_bases"]
            ):

                with st.container(border=True):

                    col1, col2 = st.columns(
                        [5, 1]
                    )


                    # -------------------------------------
                    # KNOWLEDGE INFORMATION
                    # -------------------------------------

                    with col1:

                        st.subheader(
                            f"📚 {knowledge['name']}"
                        )


                        if knowledge["description"]:

                            st.write(
                                knowledge["description"]
                            )

                        else:

                            st.caption(
                                "No description provided."
                            )


                        # ---------------------------------
                        # DOCUMENTS IN KNOWLEDGE BASE
                        # ---------------------------------

                        st.write(
                            "**Documents:**"
                        )


                        if len(
                            knowledge["documents"]
                        ) == 0:

                            st.caption(
                                "No documents added yet."
                            )

                        else:

                            for document in knowledge[
                                "documents"
                            ]:

                                st.write(
                                    f"📄 {document}"
                                )


                        # ---------------------------------
                        # ADD DOCUMENT
                        # ---------------------------------

                        if len(
                            st.session_state["documents"]
                        ) > 0:

                            available_documents = [
                                document
                                for document
                                in st.session_state[
                                    "documents"
                                ]
                                if document
                                not in knowledge[
                                    "documents"
                                ]
                            ]


                            if len(
                                available_documents
                            ) > 0:

                                selected_document = (
                                    st.selectbox(
                                        "Select a document",
                                        available_documents,
                                        key=(
                                            "document_select_"
                                            f"{index}"
                                        )
                                    )
                                )


                                if st.button(
                                    "➕ Add Document",
                                    key=(
                                        "add_document_"
                                        f"{index}"
                                    )
                                ):

                                    knowledge[
                                        "documents"
                                    ].append(
                                        selected_document
                                    )

                                    st.success(
                                        f"{selected_document} "
                                        f"added to "
                                        f"{knowledge['name']}!"
                                    )

                                    st.rerun()

                            else:

                                st.caption(
                                    "All uploaded documents "
                                    "are already included in "
                                    "this Knowledge Base."
                                )

                        else:

                            st.caption(
                                "Upload a document from "
                                "the Documents page first."
                            )


                    # -------------------------------------
                    # DELETE KNOWLEDGE BASE
                    # -------------------------------------

                    with col2:

                        if st.button(
                            "Delete",
                            key=(
                                "delete_knowledge_"
                                f"{index}"
                            )
                        ):

                            st.session_state[
                                "knowledge_bases"
                            ].pop(index)

                            st.rerun()
    # =====================================================
    # END OF LOGGED-IN APPLICATION
    # =====================================================

    # Stop execution here while the user is logged in.
    # This prevents the Login page from appearing below
    # Chat, Documents, or Knowledge.
    st.stop()
# =========================================================
# LOGIN PAGE
# =========================================================

st.title(
    "🤖 Internal AI Chat Platform"
)

st.write(
    "Secure access to your internal AI assistant"
)

st.divider()


col1, col2, col3 = st.columns(
    [1, 1.5, 1]
)


with col2:

    st.subheader(
        "Sign in"
    )


    username = st.text_input(
        "Username",
        placeholder="Enter your username"
    )


    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password"
    )


    login_button = st.button(
        "Login",
        use_container_width=True
    )


    if login_button:

        if not username or not password:

            st.warning(
                "Please enter your username "
                "and password."
            )

        else:

            try:

                response = login(
                    username,
                    password
                )


                if response.status_code == 200:

                    data = response.json()

                    st.session_state[
                        "access_token"
                    ] = data["access_token"]

                    st.session_state[
                        "logged_in"
                    ] = True

                    st.session_state[
                        "current_page"
                    ] = "chat"

                    st.success(
                        "Login successful!"
                    )

                    st.rerun()


                elif response.status_code == 401:

                    st.error(
                        "Incorrect username "
                        "or password."
                    )


                else:

                    st.error(
                        "Something went wrong. "
                        "Please try again."
                    )


            except Exception:

                st.error(
                    "Cannot connect to the backend. "
                    "Please make sure the FastAPI "
                    "server is running."
                )