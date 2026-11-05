# app.py
import streamlit as st
from PIL import Image
import io

from ai_processor import generate_profession_image
from printable_card import generate_printable_card
from database_history import save_history


# --------------------------------------
# PAGE CONFIG
# --------------------------------------
st.set_page_config(page_title="Future Goal AI", layout="wide")
st.title("📸 Future Goal AI - Powered by Nano Banana")


# --------------------------------------
# LOAD FIXED ROBOKALAM LOGO
# --------------------------------------
ROBOKALAM_LOGO_PATH = "assets/robokalam_logo.png"   # <-- your local path
robokalam_logo = Image.open(ROBOKALAM_LOGO_PATH)


# =========================================================
# 1️⃣   TWO-COLUMN FORM LAYOUT
# =========================================================
left, right = st.columns([1, 1])

with left:
    st.subheader("📝 Student Details")

    name = st.text_input("Student Name *")
    school = st.text_input("School Name *")
    phone = st.text_input("Phone Number (India) *", placeholder="+91 XXXXX XXXXX")
    gender_input = st.selectbox("Gender *", ["Male", "Female", "Other"])

    goal = st.selectbox(
        "Future Goal *",
        ["Doctor", "IAS Officer", "Pilot", "Engineer", "Scientist", "Lawyer", "Army Officer"]
    )


with right:
    st.subheader("📷 Capture Student Photo *")
    captured_image = st.camera_input("Take Photo")


# =========================================================
# 2️⃣   GENERATE BUTTON (Centered)
# =========================================================
st.markdown("<br>", unsafe_allow_html=True)
center = st.columns([1, 1, 1])

with center[1]:
    generate_btn = st.button("🚀 Generate Future AI Image", use_container_width=True)


# =========================================================
# 3️⃣   VALIDATION CHECKS (ALL MANDATORY)
# =========================================================
def validate_fields():
    if not name:
        st.error("⚠️ Student name is required.")
        return False
    if not school:
        st.error("⚠️ School name is required.")
        return False
    if not phone:
        st.error("⚠️ Phone number is required.")
        return False
    if not gender_input:
        st.error("⚠️ Gender is required.")
        return False
    if not goal:
        st.error("⚠️ Future goal is required.")
        return False
    if not captured_image:
        st.error("⚠️ Please capture a student photo.")
        return False
    return True


# =========================================================
# 4️⃣   PROCESSING + OUTPUT
# =========================================================
if generate_btn:

    if not validate_fields():
        st.stop()

    try:
        with st.spinner("✨ Processing with Gemini… please wait…"):

            # Convert camera input to bytes
            captured_img = Image.open(captured_image)
            stream = io.BytesIO()
            captured_img.save(stream, format="PNG")

            # Generate AI Future Image
            ai_bytes = generate_profession_image(stream, goal)
            ai_img = Image.open(io.BytesIO(ai_bytes))

        # --------------------------
        # Show SIDE-BY-SIDE output
        # --------------------------
        st.subheader("📸 Input vs 🎯 Future Goal")

        col1, col2 = st.columns(2)
        with col1:
            st.image(captured_img, caption="Captured Photo", width=350)

        with col2:
            st.image(ai_img, caption=f"Future {goal}", width=350)


        # =========================================================
        # 5️⃣   BUILD PRINTABLE CARD (Now using fixed Robokalam logo)
        # =========================================================
        st.subheader("🖨️ Printable A4 Card")

        printable = generate_printable_card(
            name=name,
            school=school,
            goal=goal,
            captured_img=captured_img,
            ai_img=ai_img,
            logo_file=robokalam_logo        # <-- fixed logo
        )

        card_buf = io.BytesIO()
        printable.save(card_buf, format="PNG")
        card_bytes = card_buf.getvalue()

        # =========================================================
        # 6️⃣   SAVE STUDENT DETAILS TO MONGO (no images stored)
        # =========================================================
        try:
            save_history(name, school, goal, phone, gender_input)
            st.success("📦 Student record saved to MongoDB!")
        except Exception as db_err:
            # Don't block the card if the database is unreachable
            st.warning(f"⚠️ Could not save student record: {db_err}")


        # =========================================================
        # 7️⃣   SHOW PRINTABLE CARD + BUTTONS
        # =========================================================
        st.markdown('<div id="print-area">', unsafe_allow_html=True)
        st.image(printable, width=650)
        st.markdown('</div>', unsafe_allow_html=True)

        col_print, col_download, _ = st.columns([1, 1, 2])

        with col_print:
            print_js = """
            <script>
                function printDiv() {
                    var content = document.getElementById('print-area').innerHTML;
                    var w = window.open('', '', 'height=850,width=650');
                    w.document.write('<html><head><title>Print</title></head><body>');
                    w.document.write(content);
                    w.document.write('</body></html>');
                    w.document.close();
                    w.print();
                }
            </script>

            <button onclick="printDiv()" style="
                background-color:#4CAF50; color:white;
                padding:12px 20px; border:none;
                border-radius:8px; cursor:pointer;
                width:100%;
                font-size:18px;
            ">🖨️ Print</button>
            """
            st.markdown(print_js, unsafe_allow_html=True)

        with col_download:
            st.download_button(
                "⬇️ Download PNG",
                card_bytes,
                file_name=f"{name}_{goal}.png",
                mime="image/png",
                use_container_width=True
            )

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
