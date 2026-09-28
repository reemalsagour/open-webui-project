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


# Compact spacing for the chat interface.
# تقليل المسافات في واجهة المحادثة.
st.markdown(
    """
    <style>
    div[data-testid="stVerticalBlock"] {
        gap: 0.65rem;
    }
    div[data-testid="stChatInput"] {
        margin-top: 0.25rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
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

# Authenticated user ID used for resource ownership checks.
# معرف المستخدم الحالي المستخدم للتحقق من ملكية العناصر.
if "current_user_id" not in st.session_state:
    st.session_state["current_user_id"] = None


# Restore the JWT from the URL after a browser refresh.
# استعادة رمز الدخول من الرابط بعد تحديث الصفحة.
#
# Note: this is a frontend persistence fallback. For production,
# an HttpOnly secure cookie is preferable when backend support exists.
if not TEST_MODE and not st.session_state["access_token"]:
    saved_token = st.query_params.get("session_token")

    if saved_token:
        try:
            user_response = get_current_user(saved_token)

            if user_response.status_code == 200:
                st.session_state["access_token"] = saved_token
                st.session_state["logged_in"] = True

                user_data = user_response.json()
                if isinstance(user_data, dict):
                    st.session_state["current_user_id"] = (
                        user_data.get("id") or user_data.get("user_id")
                    )
            else:
                st.query_params.pop("session_token", None)

        except Exception:
            pass


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


# Stores the title of the currently opened chat.
# يخزن عنوان المحادثة المفتوحة حالياً.
if "current_chat_title" not in st.session_state:
    st.session_state["current_chat_title"] = "New Chat"


# Stores persistent UI notifications across reruns.
# يخزن رسائل الواجهة حتى لا تختفي مباشرة بعد إعادة التشغيل.
if "flash_message" not in st.session_state:
    st.session_state["flash_message"] = None


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
    Extract assistant text from both new-chat and existing-chat
    backend response formats.

    استخراج نص رد الذكاء الاصطناعي من استجابة الباك إند
    سواء عند إنشاء محادثة جديدة أو إرسال رسالة لمحادثة موجودة.
    """

    if not isinstance(data, dict):
        return str(data)

    # New-chat backend response:
    # {"chat": {...}, "usermessage": {...},
    #  "assistantmessage": {"content": "..."}}
    # استجابة إنشاء محادثة جديدة تحتوي رد المساعد داخل assistantmessage.
    assistant_message = (
        data.get("assistantmessage")
        or data.get("assistant_message")
    )

    if isinstance(assistant_message, dict):
        return (
            assistant_message.get("content")
            or assistant_message.get("message")
        )

    if isinstance(assistant_message, str):
        return assistant_message

    # Existing-chat and fallback response formats.
    # أشكال الاستجابة الأخرى والاحتياطية.
    result = (
        data.get("response")
        or data.get("message")
        or data.get("content")
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
    Extract the chat ID from direct responses or from the nested
    chat object returned when a new chat is created.

    استخراج معرف المحادثة من الاستجابة المباشرة أو من كائن
    chat الموجود داخل استجابة إنشاء محادثة جديدة.
    """

    if not isinstance(data, dict):
        return None

    chat = data.get("chat")

    if isinstance(chat, dict):
        chat_id = chat.get("id") or chat.get("chat_id")
        if chat_id:
            return chat_id

    return data.get("id") or data.get("chat_id")


def get_logged_in_user_id(token):
    """Return and cache the authenticated user's ID."""
    cached_user_id = st.session_state.get("current_user_id")
    if cached_user_id:
        return cached_user_id

    if not token:
        return None

    try:
        response = get_current_user(token)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                user_id = data.get("id") or data.get("user_id")
                if user_id:
                    st.session_state["current_user_id"] = user_id
                    return user_id
    except Exception:
        pass

    return None


def normalize_list_response(data, *keys):
    """
    Return a list from either a direct list response or a wrapped response.

    إعادة قائمة سواء كانت الاستجابة قائمة مباشرة
    أو موجودة داخل مفتاح في قاموس.
    """
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in keys:
            value = data.get(key)
            if isinstance(value, list):
                return value

    return []


def normalize_chat_messages(messages):
    """
    Keep chat messages in chronological order so new messages
    always appear at the bottom of the conversation.

    ترتيب رسائل المحادثة زمنياً حتى تظهر الرسائل الجديدة
    دائماً في أسفل المحادثة.
    """
    if not isinstance(messages, list):
        return []

    # Python sort is stable, so messages with the same/missing timestamp
    # keep the order returned by the backend.
    return sorted(
        messages,
        key=lambda message: (
            str(message.get("created_date") or message.get("created_at") or "9999")
            if isinstance(message, dict)
            else "9999"
        ),
    )


def refresh_chat_messages(token, chat_id):
    """
    Reload a chat from the backend so the newest AI response
    appears immediately after sending a message.

    إعادة تحميل المحادثة من الباك إند حتى يظهر
    أحدث رد للذكاء الاصطناعي مباشرة.
    """
    response = get_chat(token, chat_id)

    if response.status_code != 200:
        return False

    data = response.json()

    if not isinstance(data, dict):
        return False

    st.session_state["messages"] = normalize_chat_messages(data.get("messages", []))

    title = data.get("title")
    if title:
        st.session_state["current_chat_title"] = title

    return True


def show_flash_message():
    """
    Display a stored success/error message once after rerun.

    عرض رسالة نجاح أو خطأ محفوظة بعد إعادة التشغيل.
    """
    flash = st.session_state.get("flash_message")

    if not flash:
        return

    message_type = flash.get("type", "info")
    message_text = flash.get("text", "")

    if message_type == "success":
        st.success(message_text)
    elif message_type == "error":
        st.error(message_text)
    elif message_type == "warning":
        st.warning(message_text)
    else:
        st.info(message_text)

    st.session_state["flash_message"] = None


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
            st.session_state["current_chat_title"] = "New Chat"
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

                            # Only show the delete button when the chat
                            # has a user ID.
                            # إظهار زر الحذف فقط إذا كانت المحادثة
                            # مرتبطة بمعرف مستخدم.
                            chat_user_id = chat.get("user_id")


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
                                            ] = normalize_chat_messages(messages)


                                            st.session_state[
                                                "current_chat_id"
                                            ] = chat_id

                                            st.session_state[
                                                "current_chat_title"
                                            ] = (
                                                chat_data.get("title")
                                                or chat_title
                                            )

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

                                # Do not render Delete when user_id is missing.
                                # لا نعرض زر الحذف إذا لم يوجد user_id.
                                if chat_user_id and st.button(
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

                                                st.session_state[
                                                    "current_chat_title"
                                                ] = "New Chat"


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
                                "current_chat_title"
                            ] = chat["title"]


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

                                st.session_state[
                                    "current_chat_title"
                                ] = "New Chat"


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
            st.session_state["current_user_id"] = None
            st.query_params.pop("session_token", None)

            st.session_state["current_page"] = "chat"
            st.session_state["messages"] = []
            st.session_state["current_chat_id"] = None
            st.session_state["current_chat_title"] = "New Chat"

            st.rerun()


    # =====================================================
    # CHAT PAGE
    # صفحة المحادثة
    # =====================================================

    if st.session_state["current_page"] == "chat":

        st.title("Internal AI Assistant")

        st.subheader(
            f"💬 {st.session_state.get('current_chat_title', 'New Chat')}"
        )

        st.caption(
            "Ask questions and interact with your "
            "organization's AI assistant."
        )

        show_flash_message()

        token = st.session_state.get("access_token")

        selected_model = None
        selected_file_ids = []
        selected_knowledge_ids = []

        # =================================================
        # CHAT SETTINGS - REAL BACKEND
        # إعدادات الشات - الباك إند الحقيقي
        # =================================================

        if token:

            # Keep this allow-list aligned with the approved
            # project models.
            #
            # يجب أن تحتوي هذه القائمة فقط على الموديلات
            # المعتمدة في المشروع.
            APPROVED_MODELS = [
                "models/gemini-3.5-flash-lite",
                "models/gemini-3.5-flash",
            ]

            available_models = []
            document_options = {}
            knowledge_options = {}

            # Load and filter models.
            # تحميل الموديلات وتصفيتها.
            try:
                response = get_models(token)

                if response.status_code == 200:
                    models_list = normalize_list_response(
                        response.json(),
                        "models",
                        "data",
                        "items",
                    )

                    for item in models_list:
                        model_name = extract_model_name(item)

                        if (
                            model_name
                            and model_name in APPROVED_MODELS
                            and model_name not in available_models
                        ):
                            available_models.append(model_name)

            except Exception as error:
                st.warning("Could not load AI models.")
                st.caption(str(error))

            # Load documents for multi-selection.
            # تحميل المستندات للاختيار المتعدد.
            try:
                response = get_documents(token)

                if response.status_code == 200:
                    documents_list = normalize_list_response(
                        response.json(),
                        "documents",
                        "items",
                        "data",
                    )

                    for document in documents_list:
                        if not isinstance(document, dict):
                            continue

                        document_id = (
                            document.get("id")
                            or document.get("document_id")
                            or document.get("file_id")
                        )

                        document_name = (
                            document.get("name")
                            or document.get("filename")
                            or document.get("title")
                            or str(document_id)
                        )

                        if document_id:
                            document_options[
                                f"{document_name} [{document_id}]"
                            ] = document_id

            except Exception as error:
                st.warning("Could not load documents.")
                st.caption(str(error))

            # Load Knowledge Bases for multi-selection.
            # تحميل قواعد المعرفة للاختيار المتعدد.
            try:
                response = get_knowledge_bases(token)

                if response.status_code == 200:
                    knowledge_list = normalize_list_response(
                        response.json(),
                        "knowledge_bases",
                        "knowledge",
                        "items",
                        "data",
                    )

                    for knowledge in knowledge_list:
                        if not isinstance(knowledge, dict):
                            continue

                        knowledge_id = (
                            knowledge.get("id")
                            or knowledge.get("knowledge_id")
                        )

                        knowledge_name = (
                            knowledge.get("title")
                            or knowledge.get("name")
                            or str(knowledge_id)
                        )

                        if knowledge_id:
                            knowledge_options[
                                f"{knowledge_name} [{knowledge_id}]"
                            ] = knowledge_id

            except Exception as error:
                st.warning("Could not load Knowledge Bases.")
                st.caption(str(error))

            # Chat controls are rendered later, directly above
            # the message input box.
            # سيتم عرض خيارات الشات لاحقاً مباشرة فوق مربع الكتابة.
        # =================================================
        # CHAT SETTINGS - TEST MODE
        # إعدادات الشات - وضع الاختبار
        # =================================================

        else:

            # Prepare test-mode options. The controls themselves
            # are rendered later above the message input.
            # تجهيز خيارات وضع الاختبار، وسيتم عرضها لاحقاً
            # فوق مربع كتابة الرسالة.
            # Keep only names in the chat selector while test-mode storage
            # also keeps each file's bytes for local download.
            test_documents = [
                document.get("name", "Document")
                if isinstance(document, dict)
                else str(document)
                for document in st.session_state.get("documents", [])
            ]

            test_knowledge = [
                knowledge.get("name", "Knowledge Base")
                for knowledge in st.session_state.get(
                    "knowledge_bases",
                    []
                )
            ]

        # -------------------------------------------------
        # CHAT MESSAGE AREA
        # منطقة رسائل المحادثة
        # -------------------------------------------------

        # Keep the conversation in a dedicated scrollable area.
        # This keeps the controls and message box together at the bottom.
        #
        # إبقاء المحادثة داخل منطقة مستقلة قابلة للتمرير.
        # بهذه الطريقة تبقى خيارات الشات ومربع الكتابة معاً في الأسفل.
        with st.container(height=390, border=False):

            # ---------------------------------------------
            # WELCOME MESSAGE
            # رسالة الترحيب
            # ---------------------------------------------
            if len(st.session_state["messages"]) == 0:
                st.info(
                    "👋 Welcome! How can I help you today?"
                )

            # ---------------------------------------------
            # DISPLAY MESSAGES
            # عرض الرسائل
            # ---------------------------------------------
            for message in st.session_state["messages"]:
                role = message.get("role", "assistant")
                content = message.get("content", "")

                with st.chat_message(role):
                    st.write(content)

        # -------------------------------------------------
        # CHAT COMPOSER
        # منطقة خيارات الشات وكتابة الرسالة
        # -------------------------------------------------

        # IMPORTANT:
        # st.chat_input is placed INSIDE this container instead of directly
        # in the page body. This prevents Streamlit from pinning the input
        # separately at the bottom of the browser window.
        #
        # مهم:
        # وضع st.chat_input داخل هذا الـ container يمنع Streamlit من تثبيت
        # مربع الكتابة منفصلاً في أسفل الشاشة، وبالتالي تبقى خيارات
        # Model / Documents / Knowledge مباشرة فوق مربع الكتابة.
        with st.container(key="chat_composer"):

            if token:

                model_col, docs_col, knowledge_col = st.columns(
                    [1.15, 1, 1]
                )

                with model_col:
                    if available_models:
                        selected_model = st.selectbox(
                            "🤖 Model",
                            available_models,
                            key="chat_model",
                        )
                    else:
                        st.warning(
                            "No approved models available."
                        )

                with docs_col:
                    selected_documents = st.multiselect(
                        "📎 Documents",
                        options=list(document_options.keys()),
                        key="chat_documents",
                        placeholder="Select documents",
                        help="You can select more than one document.",
                    )

                    selected_file_ids = [
                        document_options[name]
                        for name in selected_documents
                    ]

                with knowledge_col:
                    selected_knowledge = st.multiselect(
                        "📚 Knowledge",
                        options=list(knowledge_options.keys()),
                        key="chat_knowledge",
                        placeholder="Select knowledge",
                        help="You can select more than one Knowledge Base.",
                    )

                    selected_knowledge_ids = [
                        knowledge_options[name]
                        for name in selected_knowledge
                    ]

            else:

                model_col, docs_col, knowledge_col = st.columns(
                    [1.15, 1, 1]
                )

                with model_col:
                    selected_model = st.selectbox(
                        "🤖 Model",
                        [
                            "gemini-3.1-flash-lite",
                            "gemini-3.5-flash-lite",
                            "gemini-3.5-flash",
                        ],
                        key="test_chat_model",
                    )

                with docs_col:
                    st.multiselect(
                        "📎 Documents",
                        options=test_documents,
                        key="test_chat_documents",
                        placeholder=(
                            "No documents"
                            if not test_documents
                            else "Select documents"
                        ),
                    )

                with knowledge_col:
                    st.multiselect(
                        "📚 Knowledge",
                        options=test_knowledge,
                        key="test_chat_knowledge",
                        placeholder=(
                            "No knowledge"
                            if not test_knowledge
                            else "Select knowledge"
                        ),
                    )

            # ---------------------------------------------
            # CHAT INPUT
            # إدخال رسالة المستخدم
            # ---------------------------------------------
            prompt = st.chat_input(
                "Ask anything...",
                key="main_chat_input",
            )

        # -------------------------------------------------
        # PROCESS MESSAGE
        # معالجة الرسالة
        # -------------------------------------------------

        if prompt:

            st.session_state["messages"].append(
                {
                    "role": "user",
                    "content": prompt,
                }
            )

            # =============================================
            # REAL BACKEND MODE
            # وضع الباك إند الحقيقي
            # =============================================

            if token:

                try:

                    if not selected_model:
                        st.session_state["flash_message"] = {
                            "type": "warning",
                            "text": "Please select an approved AI model.",
                        }
                        st.rerun()

                    # -------------------------------------
                    # CREATE NEW CHAT
                    # إنشاء محادثة جديدة
                    # -------------------------------------

                    if (
                        st.session_state["current_chat_id"]
                        is None
                    ):

                        response = create_chat(
                            token=token,
                            message=prompt,
                            model=selected_model,
                            file_ids=selected_file_ids or None,
                            knowledge_ids=(
                                selected_knowledge_ids or None
                            ),
                        )

                        if response.status_code in [200, 201]:

                            chat_data = response.json()
                            chat_id = extract_chat_id(chat_data)
                            ai_response = extract_ai_response(chat_data)

                            st.session_state[
                                "current_chat_id"
                            ] = chat_id

                            # Use the backend title when available; otherwise
                            # keep the same short frontend title.
                            # استخدام عنوان الباك إند إن وجد، وإلا نستخدم
                            # العنوان المختصر الموجود في الفرونت إند.
                            backend_chat = chat_data.get("chat", {})
                            backend_title = (
                                backend_chat.get("title")
                                if isinstance(backend_chat, dict)
                                else None
                            )
                            new_title = backend_title or prompt[:35]
                            st.session_state[
                                "current_chat_title"
                            ] = new_title

                            # The POST /chats/ response already contains the
                            # assistant message. Add it immediately so the user
                            # does not need to refresh the browser.
                            # استجابة إنشاء الشات تحتوي رد AI بالفعل، لذلك
                            # نضيفه مباشرة حتى يظهر بدون Refresh.
                            if ai_response:
                                st.session_state["messages"].append(
                                    {
                                        "role": "assistant",
                                        "content": ai_response,
                                    }
                                )

                            if chat_id:
                                # Keep the existing title update behavior.
                                # الإبقاء على سلوك تحديث عنوان المحادثة الحالي.
                                try:
                                    update_chat_title(
                                        token,
                                        chat_id,
                                        new_title,
                                    )
                                except Exception:
                                    pass

                                # Synchronize with the backend after using the
                                # immediate POST response. If synchronization
                                # fails, the response already displayed above
                                # remains in session_state.
                                # مزامنة الرسائل مع الباك إند بعد عرض الرد
                                # مباشرة، وإذا فشلت يبقى الرد ظاهرًا محليًا.
                                try:
                                    refresh_chat_messages(
                                        token,
                                        chat_id,
                                    )
                                except Exception:
                                    pass

                            st.rerun()

                        else:
                            st.error(
                                "Could not create the chat."
                            )
                            st.caption(response.text)

                    # -------------------------------------
                    # SEND MESSAGE TO EXISTING CHAT
                    # إرسال رسالة إلى شات موجود
                    # -------------------------------------

                    else:

                        chat_id = st.session_state[
                            "current_chat_id"
                        ]

                        response = send_message(
                            token=token,
                            chat_id=chat_id,
                            message=prompt,
                            model=selected_model,
                            file_ids=selected_file_ids or None,
                            knowledge_ids=(
                                selected_knowledge_ids or None
                            ),
                        )

                        if response.status_code in [200, 201]:

                            # The user message is already appended locally above.
                            # Append the assistant response directly after it so the
                            # new exchange stays at the bottom without a page refresh.
                            #
                            # رسالة المستخدم مضافة محلياً مسبقاً، لذلك نضيف رد
                            # المساعد بعدها مباشرة ليبقى ترتيب المحادثة صحيحاً.
                            message_data = response.json()
                            ai_response = extract_ai_response(message_data)

                            if ai_response:
                                st.session_state["messages"].append(
                                    {
                                        "role": "assistant",
                                        "content": ai_response,
                                    }
                                )
                            else:
                                # Fallback only if the send endpoint does not return
                                # assistant content in the expected format.
                                refresh_chat_messages(token, chat_id)

                            st.rerun()

                        else:
                            st.error(
                                "Could not send the message."
                            )
                            st.caption(response.text)

                except Exception as error:
                    st.error(
                        "Backend connection is currently "
                        "unavailable."
                    )
                    st.caption(str(error))

            # =============================================
            # FRONTEND TEST MODE
            # وضع اختبار الفرونت إند
            # =============================================

            else:

                if (
                    st.session_state["current_chat_id"]
                    is None
                ):

                    new_chat_id = (
                        len(st.session_state["chats"]) + 1
                    )

                    new_title = prompt[:35]

                    new_chat = {
                        "id": new_chat_id,
                        "title": new_title,
                        "messages": [],
                    }

                    st.session_state["chats"].append(
                        new_chat
                    )

                    st.session_state[
                        "current_chat_id"
                    ] = new_chat_id

                    st.session_state[
                        "current_chat_title"
                    ] = new_title

                temporary_response = (
                    "Frontend test mode: "
                    "the interface is working, "
                    "but the backend is not connected yet."
                )

                st.session_state["messages"].append(
                    {
                        "role": "assistant",
                        "content": temporary_response,
                    }
                )

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
                        chat["title"] = (
                            st.session_state[
                                "current_chat_title"
                            ]
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

                    existing_names = [
                        document.get("name")
                        if isinstance(document, dict)
                        else str(document)
                        for document in st.session_state["documents"]
                    ]

                    if uploaded_file.name not in existing_names:
                        # Save bytes as well as the name so Download works
                        # locally without the backend.
                        st.session_state["documents"].append(
                            {
                                "name": uploaded_file.name,
                                "content": uploaded_file.getvalue(),
                                "mime_type": uploaded_file.type
                                or "application/octet-stream",
                            }
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

            current_user_id = get_logged_in_user_id(token)

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

                                document_user = document.get("user")
                                document_user_id = (
                                    document_user.get("id")
                                    if isinstance(document_user, dict)
                                    else None
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
                                document_user_id = None
                                document_name = str(
                                    document
                                )


                            col1, col2, col3 = st.columns(
                                [4, 1, 1]
                            )


                            with col1:

                                st.write(
                                    f"📄 {document_name}"
                                )


                            with col2:

                                # Low-priority download feature.
                                # ميزة تحميل المستند.
                                if document_id:
                                    try:
                                        content_response = (
                                            get_document_content(
                                                token,
                                                document_id
                                            )
                                        )

                                        if (
                                            content_response.status_code
                                            == 200
                                        ):
                                            st.download_button(
                                                "Download",
                                                data=(
                                                    content_response.content
                                                ),
                                                file_name=document_name,
                                                key=(
                                                    "download_backend_"
                                                    f"{document_id}"
                                                ),
                                            )
                                    except Exception:
                                        pass


                            with col3:

                                if (
                                    document_id
                                    and document_user_id is not None
                                    and current_user_id is not None
                                    and str(document_user_id) == str(current_user_id)
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

            if len(st.session_state["documents"]) == 0:
                st.info("No documents uploaded yet.")

            else:
                for index, document in enumerate(
                    st.session_state["documents"].copy()
                ):
                    if isinstance(document, dict):
                        document_name = document.get("name", "Document")
                        document_content = document.get("content", b"")
                        document_mime = document.get(
                            "mime_type", "application/octet-stream"
                        )
                    else:
                        # Compatibility with old test-mode entries.
                        document_name = str(document)
                        document_content = None
                        document_mime = "application/octet-stream"

                    col1, col2, col3 = st.columns([4, 1, 1])

                    with col1:
                        st.write(f"📄 {document_name}")

                    with col2:
                        if document_content is not None:
                            st.download_button(
                                "Download",
                                data=document_content,
                                file_name=document_name,
                                mime=document_mime,
                                key=f"download_local_{index}_{document_name}",
                            )
                        else:
                            st.caption("Re-upload to download")

                    with col3:
                        if st.button(
                            "Delete",
                            key=f"delete_local_{index}_{document_name}",
                        ):
                            st.session_state["documents"].remove(document)

                            # Remove the deleted file from temporary
                            # Knowledge Bases too.
                            for knowledge in st.session_state["knowledge_bases"]:
                                if document_name in knowledge.get("documents", []):
                                    knowledge["documents"].remove(document_name)

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

            current_user_id = get_logged_in_user_id(token)

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

                            knowledge_user = knowledge.get("user")
                            knowledge_user_id = (
                                knowledge_user.get("id")
                                if isinstance(knowledge_user, dict)
                                else None
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

                            # The list endpoint may omit document details.
                            # Fetch the selected Knowledge Base itself so its
                            # actual document list is displayed.
                            #
                            # قد لا تعيد قائمة قواعد المعرفة تفاصيل الملفات،
                            # لذلك نجلب تفاصيل قاعدة المعرفة نفسها.
                            documents = (
                                knowledge.get("documents")
                                or knowledge.get("files")
                                or []
                            )

                            if knowledge_id:
                                try:
                                    detail_response = (
                                        get_knowledge_base(
                                            token,
                                            knowledge_id
                                        )
                                    )

                                    if (
                                        detail_response.status_code
                                        == 200
                                    ):
                                        detail_data = (
                                            detail_response.json()
                                        )

                                        if isinstance(
                                            detail_data,
                                            dict
                                        ):
                                            detail_user = detail_data.get("user")
                                            if isinstance(detail_user, dict):
                                                knowledge_user_id = detail_user.get("id")
                                            elif detail_user is None and "user" in detail_data:
                                                knowledge_user_id = None

                                            documents = (
                                                detail_data.get(
                                                    "documents"
                                                )
                                                or detail_data.get(
                                                    "files"
                                                )
                                                or detail_data.get(
                                                    "items"
                                                )
                                                or documents
                                            )

                                except Exception:
                                    pass


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
                                        and knowledge_user_id is not None
                                        and current_user_id is not None
                                        and str(knowledge_user_id) == str(current_user_id)
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
                                    (
                                        document.get("name", "Document")
                                        if isinstance(document, dict)
                                        else str(document)
                                    )
                                    for document in st.session_state["documents"]
                                    if (
                                        document.get("name", "Document")
                                        if isinstance(document, dict)
                                        else str(document)
                                    ) not in knowledge["documents"]
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

                    # Keep the session after browser refresh.
                    # المحافظة على تسجيل الدخول بعد تحديث الصفحة.
                    st.query_params["session_token"] = (
                        data["access_token"]
                    )


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