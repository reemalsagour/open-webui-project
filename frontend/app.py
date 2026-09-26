import os
import streamlit as st

from api import (
    login,
    get_current_user,
    get_models,
    get_chats,
    get_chat,
    create_chat,
    send_message,
    update_chat_title,
    delete_chat,
    get_documents,
    get_document,
    upload_document,
    get_document_content,
    delete_document,
    get_knowledge_bases,
    get_knowledge_base,
    create_knowledge_base,
    update_knowledge_base,
    add_document_to_knowledge,
    remove_document_from_knowledge,
    delete_knowledge_base,
    check_health,
)


# =========================================================
# PAGE CONFIGURATION
# إعدادات الصفحة
# =========================================================

st.set_page_config(
    page_title="Internal AI Chat Platform",
    page_icon="🤖",
    layout="wide"
)


# =========================================================
# SESSION STATE
# حالة الجلسة
# =========================================================

# =========================================================
# APPLICATION MODE
# وضع تشغيل التطبيق
# =========================================================

# True  = Frontend Test Mode (backend is not required)
# False = Real Backend Mode (login and backend are required)
#
# True  = وضع اختبار الفرونت إند بدون الحاجة للباك إند
# False = الوضع الحقيقي ويتطلب تسجيل الدخول وتشغيل الباك إند

# Read frontend mode from environment variable.
# قراءة وضع تشغيل الفرونت إند من متغيرات البيئة.
#
# true  = Frontend Test Mode
# false = Real Backend Mode
#
# true  = وضع اختبار الفرونت إند
# false = وضع الباك إند الحقيقي

TEST_MODE = os.getenv(
    "FRONTEND_TEST_MODE",
    "true"
).lower() == "true"


# =========================================================
# LOGIN STATE
# حالة تسجيل الدخول
# =========================================================

if "logged_in" not in st.session_state:

    # In Test Mode, allow access directly to the interface.
    # In Backend Mode, require the user to log in first.
    #
    # في وضع الاختبار ندخل مباشرة إلى الواجهة.
    # في الوضع الحقيقي يجب على المستخدم تسجيل الدخول أولاً.

    st.session_state["logged_in"] = TEST_MODE


# Stores JWT access token after real login.
# يخزن رمز JWT بعد تسجيل الدخول الحقيقي.
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None


# Controls the currently displayed page.
# يحدد الصفحة المعروضة حالياً.
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "chat"


# Stores messages displayed in the current chat.
# يخزن رسائل المحادثة الحالية.
if "messages" not in st.session_state:
    st.session_state["messages"] = []


# Stores recent chats temporarily in test mode.
# يخزن المحادثات مؤقتاً أثناء وضع الاختبار.
if "chats" not in st.session_state:
    st.session_state["chats"] = []


# Stores the current chat ID.
# يخزن معرف المحادثة الحالية.
if "current_chat_id" not in st.session_state:
    st.session_state["current_chat_id"] = None


# Stores documents temporarily when backend is unavailable.
# يخزن المستندات مؤقتاً عندما يكون الباك إند غير متاح.
if "documents" not in st.session_state:
    st.session_state["documents"] = []


# Stores Knowledge Bases temporarily in test mode.
# يخزن قواعد المعرفة مؤقتاً أثناء وضع الاختبار.
if "knowledge_bases" not in st.session_state:
    st.session_state["knowledge_bases"] = []


# =========================================================
# HELPER FUNCTIONS
# دوال مساعدة
# =========================================================

def extract_model_name(model_item):
    """
    Extract model ID/name from different possible
    backend response formats.

    استخراج اسم أو معرف الموديل من أكثر من شكل
    محتمل للاستجابة القادمة من الباك إند.
    """

    if isinstance(model_item, str):
        return model_item

    if isinstance(model_item, dict):
        return (
            model_item.get("id")
            or model_item.get("name")
            or model_item.get("model")
        )

    return None


def extract_ai_response(data):
    """
    Extract assistant text from common backend
    response formats.

    استخراج نص رد الذكاء الاصطناعي من الأشكال
    المحتملة لاستجابة الباك إند.
    """

    if not isinstance(data, dict):
        return str(data)

    result = (
        data.get("response")
        or data.get("message")
        or data.get("content")
        or data.get("assistant_message")
    )

    if isinstance(result, dict):
        return (
            result.get("content")
            or result.get("message")
            or str(result)
        )

    return result


def extract_chat_id(data):
    """
    Extract chat ID from backend response.

    استخراج معرف المحادثة من استجابة الباك إند.
    """

    if not isinstance(data, dict):
        return None

    return (
        data.get("id")
        or data.get("chat_id")
    )


# =========================================================
# LOGGED-IN APPLICATION
# التطبيق بعد تسجيل الدخول
# =========================================================

if st.session_state["logged_in"]:

    # =====================================================
    # SIDEBAR
    # القائمة الجانبية
    # =====================================================

    with st.sidebar:

        st.title("🤖 AI Platform")

        # -------------------------------------------------
        # NEW CHAT
        # محادثة جديدة
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
        # المحادثات الأخيرة
        # -------------------------------------------------

        st.subheader("Recent Chats")

        # Get the current user's access token.
        # الحصول على رمز تسجيل دخول المستخدم الحالي.
        token = st.session_state.get("access_token")


        # =================================================
        # REAL BACKEND MODE
        # وضع الباك إند الحقيقي
        # =================================================

        if token:

            try:

                # Get the logged-in user's chats
                # from the FastAPI backend.
                #
                # جلب محادثات المستخدم المسجل دخوله
                # من FastAPI.

                chats_response = get_chats(token)


                if chats_response.status_code == 200:

                    backend_chats = chats_response.json()


                    # The backend may return the chats
                    # directly as a list or inside a dictionary.
                    #
                    # قد يعيد الباك إند المحادثات كقائمة
                    # مباشرة أو داخل قاموس.

                    if isinstance(backend_chats, dict):

                        backend_chats = (
                            backend_chats.get("chats")
                            or backend_chats.get("items")
                            or []
                        )


                    # -----------------------------------------
                    # NO CHATS
                    # لا توجد محادثات
                    # -----------------------------------------

                    if not backend_chats:

                        st.caption(
                            "No conversations yet."
                        )


                    # -----------------------------------------
                    # DISPLAY CHATS
                    # عرض المحادثات
                    # -----------------------------------------

                    else:

                        for chat in backend_chats:

                            chat_id = (
                                chat.get("id")
                                or chat.get("chat_id")
                            )

                            chat_title = (
                                chat.get("title")
                                or "Untitled Chat"
                            )


                            # Create two columns:
                            # one for opening the chat
                            # and one for deleting it.
                            #
                            # إنشاء عمود لفتح المحادثة
                            # وعمود آخر لحذفها.

                            chat_col, delete_col = st.columns(
                                [5, 1]
                            )


                            # =================================
                            # OPEN CHAT
                            # فتح المحادثة
                            # =================================

                            with chat_col:

                                if st.button(
                                    f"💬 {chat_title}",
                                    key=f"backend_chat_{chat_id}",
                                    use_container_width=True
                                ):

                                    try:

                                        chat_response = get_chat(
                                            token,
                                            chat_id
                                        )


                                        if (
                                            chat_response.status_code
                                            == 200
                                        ):

                                            chat_data = (
                                                chat_response.json()
                                            )


                                            # Get the messages
                                            # stored in this chat.
                                            #
                                            # جلب الرسائل المحفوظة
                                            # داخل المحادثة.

                                            messages = (
                                                chat_data.get(
                                                    "messages",
                                                    []
                                                )
                                                if isinstance(
                                                    chat_data,
                                                    dict
                                                )
                                                else []
                                            )


                                            st.session_state[
                                                "messages"
                                            ] = messages


                                            st.session_state[
                                                "current_chat_id"
                                            ] = chat_id


                                            st.session_state[
                                                "current_page"
                                            ] = "chat"


                                            st.rerun()


                                        else:

                                            st.error(
                                                "Could not load chat."
                                            )


                                    except Exception as error:

                                        st.error(
                                            "Could not load chat."
                                        )

                                        st.caption(
                                            str(error)
                                        )


                            # =================================
                            # DELETE CHAT
                            # حذف المحادثة
                            # =================================

                            with delete_col:

                                if st.button(
                                    "🗑️",
                                    key=f"delete_chat_{chat_id}",
                                    help="Delete chat"
                                ):

                                    try:

                                        delete_response = delete_chat(
                                            token,
                                            chat_id
                                        )


                                        if (
                                            delete_response.status_code
                                            in [200, 204]
                                        ):

                                            # If the deleted chat is
                                            # currently open, clear it.
                                            #
                                            # إذا كانت المحادثة المحذوفة
                                            # مفتوحة حالياً، يتم مسحها.

                                            if (
                                                st.session_state[
                                                    "current_chat_id"
                                                ]
                                                == chat_id
                                            ):

                                                st.session_state[
                                                    "current_chat_id"
                                                ] = None

                                                st.session_state[
                                                    "messages"
                                                ] = []


                                            st.success(
                                                "Chat deleted successfully!"
                                            )

                                            st.rerun()


                                        else:

                                            st.error(
                                                "Could not delete chat."
                                            )

                                            st.caption(
                                                delete_response.text
                                            )


                                    except Exception as error:

                                        st.error(
                                            "Could not delete chat."
                                        )

                                        st.caption(
                                            str(error)
                                        )


                else:

                    st.caption(
                        "Could not load recent chats."
                    )


            except Exception as error:

                st.caption(
                    "Recent chats are currently unavailable."
                )

                # Development information only.
                # معلومات الخطأ أثناء التطوير فقط.
                st.caption(
                    str(error)
                )


        # =================================================
        # FRONTEND TEST MODE
        # وضع اختبار الفرونت إند
        # =================================================

        else:

            # In Test Mode, chats are stored only
            # inside Streamlit session_state.
            #
            # في وضع الاختبار يتم حفظ المحادثات
            # مؤقتاً داخل session_state فقط.

            if len(st.session_state["chats"]) == 0:

                st.caption(
                    "Your conversations will appear here."
                )


            else:

                # Use a copy of the list because a chat
                # may be deleted while displaying it.
                #
                # نستخدم نسخة من القائمة لأن المستخدم
                # قد يحذف محادثة أثناء عرضها.

                for chat in st.session_state["chats"].copy():

                    chat_col, delete_col = st.columns(
                        [5, 1]
                    )


                    # =====================================
                    # OPEN LOCAL CHAT
                    # فتح المحادثة المؤقتة
                    # =====================================

                    with chat_col:

                        if st.button(
                            f"💬 {chat['title']}",
                            key=f"local_chat_{chat['id']}",
                            use_container_width=True
                        ):

                            st.session_state[
                                "current_chat_id"
                            ] = chat["id"]


                            st.session_state[
                                "messages"
                            ] = chat["messages"].copy()


                            st.session_state[
                                "current_page"
                            ] = "chat"


                            st.rerun()


                    # =====================================
                    # DELETE LOCAL CHAT
                    # حذف المحادثة المؤقتة
                    # =====================================

                    with delete_col:

                        if st.button(
                            "🗑️",
                            key=f"delete_local_chat_{chat['id']}",
                            help="Delete chat"
                        ):

                            # Remove the selected chat
                            # from temporary storage.
                            #
                            # حذف المحادثة المحددة
                            # من التخزين المؤقت.

                            st.session_state[
                                "chats"
                            ].remove(chat)


                            # If this chat is currently open,
                            # clear the chat window too.
                            #
                            # إذا كانت المحادثة المحذوفة
                            # مفتوحة، يتم تنظيف نافذة الشات.

                            if (
                                st.session_state[
                                    "current_chat_id"
                                ]
                                == chat["id"]
                            ):

                                st.session_state[
                                    "current_chat_id"
                                ] = None

                                st.session_state[
                                    "messages"
                                ] = []


                            st.rerun()


        st.divider()


        # -------------------------------------------------
        # RESOURCES
        # الموارد
        # -------------------------------------------------

        st.subheader("Resources")

        if st.button(
            "📄 Documents",
            use_container_width=True
        ):

            st.session_state[
                "current_page"
            ] = "documents"

            st.rerun()


        if st.button(
            "📚 Knowledge",
            use_container_width=True
        ):

            st.session_state[
                "current_page"
            ] = "knowledge"

            st.rerun()


        st.divider()


        # -------------------------------------------------
        # LOGOUT
        # تسجيل الخروج
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
    # صفحة المحادثة
    # =====================================================

    if st.session_state["current_page"] == "chat":

        st.title("Internal AI Assistant")

        st.caption(
            "Ask questions and interact with your "
            "organization's AI assistant."
        )


        # -------------------------------------------------
        # WELCOME MESSAGE
        # رسالة الترحيب
        # -------------------------------------------------

        if len(st.session_state["messages"]) == 0:

            st.info(
                "👋 Welcome! How can I help you today?"
            )


        # -------------------------------------------------
        # DISPLAY MESSAGES
        # عرض الرسائل
        # -------------------------------------------------

        for message in st.session_state["messages"]:

            role = message.get(
                "role",
                "assistant"
            )

            content = message.get(
                "content",
                ""
            )

            with st.chat_message(role):
                st.write(content)


        # -------------------------------------------------
        # CHAT INPUT
        # إدخال رسالة المستخدم
        # -------------------------------------------------

        prompt = st.chat_input(
            "Ask anything..."
        )


        # -------------------------------------------------
        # PROCESS MESSAGE
        # معالجة الرسالة
        # -------------------------------------------------

        if prompt:

            # Store the user's message.
            # حفظ رسالة المستخدم.
            st.session_state["messages"].append(
                {
                    "role": "user",
                    "content": prompt
                }
            )

            token = st.session_state.get(
                "access_token"
            )


            # =============================================
            # REAL BACKEND MODE
            # وضع الباك إند الحقيقي
            # =============================================

            if token:

                try:

                    # -------------------------------------
                    # GET AVAILABLE MODELS
                    # جلب الموديلات المتاحة
                    # -------------------------------------

                    models_response = get_models(
                        token
                    )

                    model = None

                    if (
                        models_response.status_code
                        == 200
                    ):

                        models_data = (
                            models_response.json()
                        )

                        # Handle possible wrapped response.
                        # التعامل مع أكثر من شكل للاستجابة.
                        if isinstance(
                            models_data,
                            dict
                        ):

                            models_list = (
                                models_data.get("models")
                                or models_data.get("data")
                                or models_data.get("items")
                                or []
                            )

                        else:

                            models_list = models_data


                        if (
                            isinstance(models_list, list)
                            and len(models_list) > 0
                        ):

                            model = extract_model_name(
                                models_list[0]
                            )


                    # -------------------------------------
                    # NO MODEL AVAILABLE
                    # لا يوجد موديل متاح
                    # -------------------------------------

                    if not model:

                        st.warning(
                            "No AI models are currently "
                            "available."
                        )


                    # =====================================
                    # CREATE NEW CHAT
                    # إنشاء محادثة جديدة
                    # =====================================

                    elif (
                        st.session_state[
                            "current_chat_id"
                        ] is None
                    ):

                        response = create_chat(
                            token=token,
                            message=prompt,
                            model=model
                        )


                        if response.status_code in [
                            200,
                            201
                        ]:

                            chat_data = response.json()

                            chat_id = extract_chat_id(
                                chat_data
                            )

                            st.session_state[
                                "current_chat_id"
                            ] = chat_id


                            ai_response = (
                                extract_ai_response(
                                    chat_data
                                )
                            )


                            if ai_response:

                                st.session_state[
                                    "messages"
                                ].append(
                                    {
                                        "role": "assistant",
                                        "content": (
                                            ai_response
                                        )
                                    }
                                )

                        else:

                            st.error(
                                "Could not create the chat."
                            )

                            st.caption(
                                response.text
                            )


                    # =====================================
                    # SEND MESSAGE
                    # إرسال رسالة للمحادثة الحالية
                    # =====================================

                    else:

                        response = send_message(
                            token=token,
                            chat_id=(
                                st.session_state[
                                    "current_chat_id"
                                ]
                            ),
                            message=prompt,
                            model=model
                        )


                        if response.status_code in [
                            200,
                            201
                        ]:

                            message_data = (
                                response.json()
                            )

                            ai_response = (
                                extract_ai_response(
                                    message_data
                                )
                            )


                            if ai_response:

                                st.session_state[
                                    "messages"
                                ].append(
                                    {
                                        "role": "assistant",
                                        "content": (
                                            ai_response
                                        )
                                    }
                                )

                        else:

                            st.error(
                                "Could not send the message."
                            )

                            st.caption(
                                response.text
                            )


                except Exception as error:

                    st.warning(
                        "Backend connection is currently "
                        "unavailable."
                    )

                    st.caption(
                        str(error)
                    )


            # =============================================
            # FRONTEND TEST MODE
            # وضع اختبار الفرونت إند
            # =============================================

            else:

                # Create a local temporary chat when
                # the first message is sent.
                #
                # إنشاء محادثة محلية مؤقتة عند إرسال
                # أول رسالة.

                if (
                    st.session_state[
                        "current_chat_id"
                    ] is None
                ):

                    new_chat_id = (
                        len(
                            st.session_state[
                                "chats"
                            ]
                        )
                        + 1
                    )

                    new_chat = {
                        "id": new_chat_id,
                        "title": prompt[:35],
                        "messages": []
                    }

                    st.session_state[
                        "chats"
                    ].append(new_chat)

                    st.session_state[
                        "current_chat_id"
                    ] = new_chat_id


                temporary_response = (
                    "Frontend test mode: "
                    "the interface is working, "
                    "but the backend is not connected yet."
                )


                st.session_state[
                    "messages"
                ].append(
                    {
                        "role": "assistant",
                        "content": temporary_response
                    }
                )


                # Save current messages inside
                # the temporary recent chat.
                #
                # حفظ الرسائل داخل المحادثة المؤقتة.

                for chat in st.session_state["chats"]:

                    if (
                        chat["id"]
                        == st.session_state[
                            "current_chat_id"
                        ]
                    ):

                        chat["messages"] = (
                            st.session_state[
                                "messages"
                            ].copy()
                        )

                        break


            st.rerun()


    # =====================================================
    # DOCUMENTS PAGE
    # صفحة المستندات
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
        # رفع مستند
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

                token = st.session_state.get(
                    "access_token"
                )


                # =========================================
                # REAL BACKEND MODE
                # وضع الباك إند الحقيقي
                # =========================================

                if token:

                    try:

                        response = upload_document(
                            token,
                            uploaded_file
                        )

                        if response.status_code in [
                            200,
                            201
                        ]:

                            st.success(
                                f"{uploaded_file.name} "
                                "uploaded successfully!"
                            )

                            st.rerun()

                        else:

                            st.error(
                                "Could not upload document."
                            )

                            st.caption(
                                response.text
                            )

                    except Exception as error:

                        st.error(
                            "Backend connection is "
                            "currently unavailable."
                        )

                        st.caption(
                            str(error)
                        )


                # =========================================
                # FRONTEND TEST MODE
                # وضع اختبار الفرونت إند
                # =========================================

                else:

                    if (
                        uploaded_file.name
                        not in st.session_state[
                            "documents"
                        ]
                    ):

                        st.session_state[
                            "documents"
                        ].append(
                            uploaded_file.name
                        )

                        st.success(
                            f"{uploaded_file.name} "
                            "uploaded successfully "
                            "in test mode!"
                        )

                    else:

                        st.warning(
                            "This document has already "
                            "been added."
                        )


        st.divider()


        # -------------------------------------------------
        # DOCUMENT LIST
        # قائمة المستندات
        # -------------------------------------------------

        st.subheader(
            "Your Documents"
        )

        token = st.session_state.get(
            "access_token"
        )


        # =============================================
        # REAL BACKEND DOCUMENTS
        # المستندات من الباك إند
        # =============================================

        if token:

            try:

                response = get_documents(
                    token
                )

                if response.status_code == 200:

                    documents_data = (
                        response.json()
                    )


                    if isinstance(
                        documents_data,
                        dict
                    ):

                        documents_list = (
                            documents_data.get(
                                "documents"
                            )
                            or documents_data.get(
                                "items"
                            )
                            or []
                        )

                    else:

                        documents_list = (
                            documents_data
                        )


                    if not documents_list:

                        st.info(
                            "No documents uploaded yet."
                        )

                    else:

                        for document in documents_list:

                            if isinstance(
                                document,
                                dict
                            ):

                                document_id = (
                                    document.get("id")
                                    or document.get(
                                        "document_id"
                                    )
                                    or document.get(
                                        "file_id"
                                    )
                                )

                                document_name = (
                                    document.get("name")
                                    or document.get(
                                        "filename"
                                    )
                                    or document.get(
                                        "title"
                                    )
                                    or "Document"
                                )

                            else:

                                document_id = None
                                document_name = str(
                                    document
                                )


                            col1, col2 = st.columns(
                                [5, 1]
                            )


                            with col1:

                                st.write(
                                    f"📄 {document_name}"
                                )


                            with col2:

                                if (
                                    document_id
                                    and st.button(
                                        "Delete",
                                        key=(
                                            "delete_backend_"
                                            f"{document_id}"
                                        )
                                    )
                                ):

                                    delete_response = (
                                        delete_document(
                                            token,
                                            document_id
                                        )
                                    )

                                    if (
                                        delete_response.status_code
                                        in [200, 204]
                                    ):

                                        st.success(
                                            "Document deleted."
                                        )

                                        st.rerun()

                                    else:

                                        st.error(
                                            "Could not delete "
                                            "document."
                                        )

                else:

                    st.error(
                        "Could not load documents."
                    )

            except Exception as error:

                st.warning(
                    "Documents could not be loaded "
                    "from the backend."
                )

                st.caption(
                    str(error)
                )


        # =============================================
        # TEST MODE DOCUMENTS
        # مستندات وضع الاختبار
        # =============================================

        else:

            if len(
                st.session_state["documents"]
            ) == 0:

                st.info(
                    "No documents uploaded yet."
                )

            else:

                for document in (
                    st.session_state["documents"].copy()
                ):

                    col1, col2 = st.columns(
                        [5, 1]
                    )


                    with col1:

                        st.write(
                            f"📄 {document}"
                        )


                    with col2:

                        if st.button(
                            "Delete",
                            key=(
                                "delete_local_"
                                f"{document}"
                            )
                        ):

                            st.session_state[
                                "documents"
                            ].remove(document)


                            # Remove deleted document
                            # from temporary Knowledge Bases.
                            #
                            # إزالة المستند المحذوف من
                            # قواعد المعرفة المؤقتة.

                            for knowledge in (
                                st.session_state[
                                    "knowledge_bases"
                                ]
                            ):

                                if (
                                    document
                                    in knowledge.get(
                                        "documents",
                                        []
                                    )
                                ):

                                    knowledge[
                                        "documents"
                                    ].remove(
                                        document
                                    )

                            st.rerun()


    # =====================================================
    # KNOWLEDGE PAGE
    # صفحة قواعد المعرفة
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
        # إنشاء قاعدة معرفة
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

                token = st.session_state.get(
                    "access_token"
                )


                # =========================================
                # REAL BACKEND MODE
                # وضع الباك إند الحقيقي
                # =========================================

                if token:

                    try:

                        response = create_knowledge_base(
                            token,
                            knowledge_name,
                            knowledge_description
                        )

                        if response.status_code in [
                            200,
                            201
                        ]:

                            st.success(
                                f"{knowledge_name} "
                                "created successfully!"
                            )

                            st.rerun()

                        else:

                            st.error(
                                "Could not create "
                                "Knowledge Base."
                            )

                            st.caption(
                                response.text
                            )

                    except Exception as error:

                        st.error(
                            "Backend connection is "
                            "currently unavailable."
                        )

                        st.caption(
                            str(error)
                        )


                # =========================================
                # FRONTEND TEST MODE
                # وضع اختبار الفرونت إند
                # =========================================

                else:

                    knowledge_base = {
                        "id": (
                            len(
                                st.session_state[
                                    "knowledge_bases"
                                ]
                            )
                            + 1
                        ),
                        "name": knowledge_name,
                        "description": (
                            knowledge_description
                        ),
                        "documents": []
                    }


                    st.session_state[
                        "knowledge_bases"
                    ].append(
                        knowledge_base
                    )


                    st.success(
                        f"{knowledge_name} "
                        "created successfully "
                        "in test mode!"
                    )


        st.divider()


        # -------------------------------------------------
        # KNOWLEDGE BASE LIST
        # قائمة قواعد المعرفة
        # -------------------------------------------------

        st.subheader(
            "Your Knowledge Bases"
        )

        token = st.session_state.get(
            "access_token"
        )


        # =============================================
        # REAL BACKEND KNOWLEDGE BASES
        # قواعد المعرفة من الباك إند
        # =============================================

        if token:

            try:

                response = get_knowledge_bases(
                    token
                )

                if response.status_code == 200:

                    knowledge_data = (
                        response.json()
                    )


                    if isinstance(
                        knowledge_data,
                        dict
                    ):

                        knowledge_list = (
                            knowledge_data.get(
                                "knowledge_bases"
                            )
                            or knowledge_data.get(
                                "items"
                            )
                            or knowledge_data.get(
                                "knowledge"
                            )
                            or []
                        )

                    else:

                        knowledge_list = (
                            knowledge_data
                        )


                    if not knowledge_list:

                        st.info(
                            "No knowledge bases "
                            "created yet."
                        )

                    else:

                        for index, knowledge in enumerate(
                            knowledge_list
                        ):

                            if not isinstance(
                                knowledge,
                                dict
                            ):
                                continue


                            knowledge_id = (
                                knowledge.get("id")
                                or knowledge.get(
                                    "knowledge_id"
                                )
                            )

                            knowledge_title = (
                                knowledge.get("title")
                                or knowledge.get("name")
                                or "Knowledge Base"
                            )

                            description = (
                                knowledge.get(
                                    "description"
                                )
                                or ""
                            )

                            documents = (
                                knowledge.get(
                                    "documents"
                                )
                                or []
                            )


                            with st.container(
                                border=True
                            ):

                                col1, col2 = (
                                    st.columns(
                                        [5, 1]
                                    )
                                )


                                with col1:

                                    st.subheader(
                                        f"📚 "
                                        f"{knowledge_title}"
                                    )

                                    if description:

                                        st.write(
                                            description
                                        )

                                    else:

                                        st.caption(
                                            "No description "
                                            "provided."
                                        )


                                    st.write(
                                        "**Documents:**"
                                    )


                                    if not documents:

                                        st.caption(
                                            "No documents "
                                            "added yet."
                                        )

                                    else:

                                        for document in (
                                            documents
                                        ):

                                            if isinstance(
                                                document,
                                                dict
                                            ):

                                                name = (
                                                    document.get(
                                                        "name"
                                                    )
                                                    or document.get(
                                                        "filename"
                                                    )
                                                    or document.get(
                                                        "title"
                                                    )
                                                    or "Document"
                                                )

                                            else:

                                                name = str(
                                                    document
                                                )

                                            st.write(
                                                f"📄 {name}"
                                            )


                                    # ---------------------
                                    # ADD DOCUMENT
                                    # إضافة مستند
                                    # ---------------------

                                    try:

                                        docs_response = (
                                            get_documents(
                                                token
                                            )
                                        )

                                        if (
                                            docs_response.status_code
                                            == 200
                                        ):

                                            docs_data = (
                                                docs_response.json()
                                            )

                                            if isinstance(
                                                docs_data,
                                                dict
                                            ):

                                                docs_list = (
                                                    docs_data.get(
                                                        "documents"
                                                    )
                                                    or docs_data.get(
                                                        "items"
                                                    )
                                                    or []
                                                )

                                            else:

                                                docs_list = (
                                                    docs_data
                                                )


                                            document_options = {}

                                            for doc in docs_list:

                                                if isinstance(
                                                    doc,
                                                    dict
                                                ):

                                                    doc_id = (
                                                        doc.get("id")
                                                        or doc.get(
                                                            "document_id"
                                                        )
                                                        or doc.get(
                                                            "file_id"
                                                        )
                                                    )

                                                    doc_name = (
                                                        doc.get(
                                                            "name"
                                                        )
                                                        or doc.get(
                                                            "filename"
                                                        )
                                                        or doc.get(
                                                            "title"
                                                        )
                                                        or str(
                                                            doc_id
                                                        )
                                                    )

                                                    if doc_id:

                                                        document_options[
                                                            doc_name
                                                        ] = doc_id


                                            if (
                                                document_options
                                                and knowledge_id
                                            ):

                                                selected_name = (
                                                    st.selectbox(
                                                        "Select a "
                                                        "document",
                                                        list(
                                                            document_options.keys()
                                                        ),
                                                        key=(
                                                            "backend_doc_"
                                                            f"{knowledge_id}"
                                                        )
                                                    )
                                                )


                                                if st.button(
                                                    "➕ Add Document",
                                                    key=(
                                                        "backend_add_"
                                                        f"{knowledge_id}"
                                                    )
                                                ):

                                                    add_response = (
                                                        add_document_to_knowledge(
                                                            token,
                                                            knowledge_id,
                                                            document_options[
                                                                selected_name
                                                            ]
                                                        )
                                                    )


                                                    if (
                                                        add_response.status_code
                                                        in [
                                                            200,
                                                            201,
                                                            204
                                                        ]
                                                    ):

                                                        st.success(
                                                            "Document "
                                                            "added."
                                                        )

                                                        st.rerun()

                                                    else:

                                                        st.error(
                                                            "Could not "
                                                            "add document."
                                                        )

                                    except Exception:

                                        pass


                                with col2:

                                    if (
                                        knowledge_id
                                        and st.button(
                                            "Delete",
                                            key=(
                                                "delete_backend_"
                                                "knowledge_"
                                                f"{knowledge_id}"
                                            )
                                        )
                                    ):

                                        delete_response = (
                                            delete_knowledge_base(
                                                token,
                                                knowledge_id
                                            )
                                        )

                                        if (
                                            delete_response.status_code
                                            in [200, 204]
                                        ):

                                            st.success(
                                                "Knowledge Base "
                                                "deleted."
                                            )

                                            st.rerun()

                                        else:

                                            st.error(
                                                "Could not delete "
                                                "Knowledge Base."
                                            )


                else:

                    st.error(
                        "Could not load Knowledge Bases."
                    )

            except Exception as error:

                st.warning(
                    "Knowledge Bases could not be "
                    "loaded from the backend."
                )

                st.caption(
                    str(error)
                )


        # =============================================
        # TEST MODE KNOWLEDGE BASES
        # قواعد المعرفة في وضع الاختبار
        # =============================================

        else:

            if len(
                st.session_state[
                    "knowledge_bases"
                ]
            ) == 0:

                st.info(
                    "No knowledge bases created yet."
                )

            else:

                for index, knowledge in enumerate(
                    st.session_state[
                        "knowledge_bases"
                    ]
                ):

                    with st.container(
                        border=True
                    ):

                        col1, col2 = st.columns(
                            [5, 1]
                        )


                        with col1:

                            st.subheader(
                                f"📚 "
                                f"{knowledge['name']}"
                            )


                            if knowledge[
                                "description"
                            ]:

                                st.write(
                                    knowledge[
                                        "description"
                                    ]
                                )

                            else:

                                st.caption(
                                    "No description provided."
                                )


                            st.write(
                                "**Documents:**"
                            )


                            if len(
                                knowledge[
                                    "documents"
                                ]
                            ) == 0:

                                st.caption(
                                    "No documents added yet."
                                )

                            else:

                                for document in (
                                    knowledge[
                                        "documents"
                                    ]
                                ):

                                    st.write(
                                        f"📄 {document}"
                                    )


                            # -----------------------------
                            # ADD DOCUMENT
                            # إضافة مستند
                            # -----------------------------

                            if len(
                                st.session_state[
                                    "documents"
                                ]
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
                                                "local_document_"
                                                f"{index}"
                                            )
                                        )
                                    )


                                    if st.button(
                                        "➕ Add Document",
                                        key=(
                                            "local_add_"
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


                        # ---------------------------------
                        # DELETE KNOWLEDGE BASE
                        # حذف قاعدة المعرفة
                        # ---------------------------------

                        with col2:

                            if st.button(
                                "Delete",
                                key=(
                                    "delete_local_knowledge_"
                                    f"{index}"
                                )
                            ):

                                st.session_state[
                                    "knowledge_bases"
                                ].pop(index)

                                st.rerun()


    # =====================================================
    # END OF LOGGED-IN APPLICATION
    # نهاية التطبيق بعد تسجيل الدخول
    # =====================================================

    # Prevent the Login page from appearing below
    # Chat, Documents, or Knowledge.
    #
    # منع ظهور صفحة تسجيل الدخول أسفل صفحات التطبيق.
    st.stop()


# =========================================================
# LOGIN PAGE
# صفحة تسجيل الدخول
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

                # Send username and password
                # to the FastAPI backend.
                #
                # إرسال اسم المستخدم وكلمة المرور
                # إلى FastAPI.

                response = login(
                    username,
                    password
                )


                if response.status_code == 200:

                    data = response.json()


                    # Store JWT access token.
                    # حفظ رمز JWT.
                    st.session_state[
                        "access_token"
                    ] = data["access_token"]


                    # Mark the user as logged in.
                    # تسجيل حالة دخول المستخدم.
                    st.session_state[
                        "logged_in"
                    ] = True


                    st.session_state[
                        "current_page"
                    ] = "chat"


                    st.session_state[
                        "current_chat_id"
                    ] = None


                    st.session_state[
                        "messages"
                    ] = []


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

                    st.caption(
                        response.text
                    )


            except Exception as error:

                st.error(
                    "Cannot connect to the backend. "
                    "Please make sure the FastAPI "
                    "server is running."
                )

                # Development error details.
                # تفاصيل الخطأ أثناء التطوير.
                st.caption(
                    str(error)
                )