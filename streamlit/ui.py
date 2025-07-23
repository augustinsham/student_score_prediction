import streamlit as st
import requests
import pymongo
from bson import Binary
from PIL import Image
import io

# MongoDB Setup
client = pymongo.MongoClient("mongodb://localhost:27017/")  # Replace with your URI
db = client["student_db"]
collection = db["students"]


# Page Navigation
page = st.sidebar.selectbox("Select Page", ["🏠 Home", "📋 View Records"])

# ----------------- Page 1: Home -----------------
if page == "🏠 Home":
    st.title("📑 Score Predictor ✔️✅")

    st.subheader("📥 Enter Student Details")
    name = st.text_input("Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    photo = st.file_uploader("Upload Profile Photo", type=["jpg", "jpeg", "png"])

    study = st.slider("Study Time", 0, 10)
    atd = st.slider("Attended Days", 0, 80)
    gen = st.selectbox("Gender", ["Male", "Female"])
    gender = 1 if gen == "Male" else 0

    if st.button("Predict and Save"):
        if not all([name, email, phone, photo]):
            st.warning("Please fill all the fields and upload a photo.")
        else:
            # Read image bytes and convert to Binary
            image_bytes = photo.read()
            image_binary = Binary(image_bytes)

            # Prepare data for API
            data = {
                "study_time": study,
                "attendance": atd,
                "gender_Male": gender
            }

            try:
                # Call prediction API
                res = requests.post("https://abc-stud-1.onrender.com/predict", json=data)
                result = res.json()
                score = result["Predicted_score"]
                st.success(f"🎯 Predicted Score: {score}")

                # Save to MongoDB
                student_data = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "gender": gen,
                    "study_time": study,
                    "attendance": atd,
                    "predicted_score": score,
                    "photo": image_binary
                }
                collection.insert_one(student_data)
                st.success("✅ Student data saved successfully!")

            except Exception as e:
                st.error("❌ API or DB Error: " + str(e))

# ----------------- Page 2: View Records -----------------
elif page == "📋 View Records":
    st.title("📋 Student Records")

    # 🔍 Search by Name
    search_name = st.text_input("Search by Name")

    if search_name:
        docs = list(collection.find({"name": {"$regex": search_name, "$options": "i"}}))
    else:
        docs = list(collection.find())

    if not docs:
        st.info("No matching student records found.")
    else:
        for doc in docs:
            with st.container():
                st.markdown("### 👤 Student Profile")
                cols = st.columns([1, 3])
                with cols[0]:
                    image = Image.open(io.BytesIO(doc["photo"]))
                    st.image(image, width=100)
                with cols[1]:
                    st.write(f"**Name:** {doc['name']}")
                    st.write(f"**Email:** {doc['email']}")
                    st.write(f"**Phone:** {doc['phone']}")
                    st.write(f"**Gender:** {doc['gender']}")
                    st.write(f"**Study Time:** {doc['study_time']}")
                    st.write(f"**Attendance:** {doc['attendance']}")
                    st.write(f"**Predicted Score:** {doc['predicted_score']}")

                col1, col2 = st.columns([1, 1])

                # ✏️ Update Form
                with col1:
                    if st.button("✏️ Edit", key=doc["name"] + "_edit"):
                        with st.form(key="update_form_" + doc["name"]):
                            new_name = st.text_input("Name", doc["name"])
                            new_email = st.text_input("Email", doc["email"])
                            new_phone = st.text_input("Phone", doc["phone"])
                            new_study = st.slider("Study Time", 0, 10, int(doc["study_time"]))
                            new_atd = st.slider("Attendance", 0, 80, int(doc["attendance"]))
                            new_gender = st.selectbox("Gender", ["Male", "Female"], index=0 if doc["gender"] == "Male" else 1)

                            submitted = st.form_submit_button("Update")
                            if submitted:
                                collection.update_one(
                                    {"name": doc["name"], "email": doc["email"]},  # Safely update one unique user
                                    {"$set": {
                                        "name": new_name,
                                        "email": new_email,
                                        "phone": new_phone,
                                        "study_time": new_study,
                                        "attendance": new_atd,
                                        "gender": new_gender
                                    }}
                                )
                                st.success("✅ Record updated successfully!")
                                st.experimental_rerun()

                # 🗑️ Delete by Name + Email
                with col2:
                    if st.button("🗑️ Delete", key=doc["name"] + "_delete"):
                        collection.delete_one({"name": doc["name"], "email": doc["email"]})
                        st.warning(f"⚠️ Deleted record of {doc['name']}")
                        st.experimental_rerun()

            st.markdown("---")
