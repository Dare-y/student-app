import streamlit as st
import pandas as pd
import os
import io

# --- File to store data ---
DATA_FILE = "students.csv"

# --- Initialize CSV if missing ---
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Name", "Age", "Address", "Parent Phone", "Status", "Picture"])
    df.to_csv(DATA_FILE, index=False)

# --- Load data ---
students = pd.read_csv(DATA_FILE)

# --- App Title ---
st.title("🎓 Student Management App")

# --- New Student Form ---
st.subheader("➕ Add / Edit Student")

with st.form("student_form", clear_on_submit=True):
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=1, step=1)
    address = st.text_area("Address")
    parent_phone = st.text_input("Parent Phone")
    status = st.selectbox("Payment Status", ["Paid", "Not Paid", "Partially Paid"])
    picture = st.file_uploader("Upload Picture", type=["jpg", "jpeg", "png"])
    submitted = st.form_submit_button("Save Student")

if submitted:
    pic_path = ""
    if picture:
        pic_dir = "pictures"
        os.makedirs(pic_dir, exist_ok=True)
        pic_path = os.path.join(pic_dir, picture.name)
        with open(pic_path, "wb") as f:
            f.write(picture.getbuffer())

    new_student = pd.DataFrame([{
        "Name": name,
        "Age": age,
        "Address": address,
        "Parent Phone": parent_phone,
        "Status": status,
        "Picture": pic_path
    }])

    students = pd.concat([students, new_student], ignore_index=True)
    students.to_csv(DATA_FILE, index=False)
    st.success(f"✅ {name} added successfully!")

# --- Student Records ---
st.subheader("📋 Student Records")

if not students.empty:
    # Search + Filter
    search_query = st.text_input("🔍 Search by name or parent phone")
    status_filter = st.selectbox("📌 Filter by status", ["All", "Paid", "Not Paid", "Partially Paid"])

    filtered = students.copy()
    if search_query:
        filtered = filtered[
            filtered["Name"].str.contains(search_query, case=False, na=False) |
            filtered["Parent Phone"].astype(str).str.contains(search_query, case=False, na=False)
        ]
    if status_filter != "All":
        filtered = filtered[filtered["Status"] == status_filter]

    if filtered.empty:
        st.warning("No students found.")
    else:
        for i, row in filtered.iterrows():
            st.write(f"**{row['Name']}** ({row['Age']} yrs) - 💳 {row['Status']}")
            st.write(f"📍 {row['Address']}")
            st.write(f"📞 Parent: {row['Parent Phone']}")
            if row["Picture"] and os.path.exists(str(row["Picture"])):
                st.image(row["Picture"], width=100)

            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✏️ Edit {row['Name']}", key=f"edit_{i}"):
                    st.info("Editing is not in minimal mode. Use full app for edit.")
            with col2:
                if st.button(f"🗑️ Delete {row['Name']}", key=f"delete_{i}"):
                    students = students.drop(i).reset_index(drop=True)
                    students.to_csv(DATA_FILE, index=False)
                    st.warning(f"{row['Name']} deleted.")
                    st.experimental_rerun()
else:
    st.info("No student records yet.")

# --- Export to Excel ---
if not students.empty:
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        students.to_excel(writer, index=False, sheet_name="Students")

    st.download_button(
        label="⬇️ Export as Excel",
        data=excel_buffer.getvalue(),
        file_name="students.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
