import streamlit as st
import pandas as pd
import os

# File to save student data
DATA_FILE = "students.csv"

# Load existing data
if os.path.exists(DATA_FILE):
    students = pd.read_csv(DATA_FILE)
else:
    students = pd.DataFrame(columns=["Name", "Status", "Picture"])

st.title("🎓 Student Management System")

# --- Add Student Form ---
with st.form("student_form"):
    name = st.text_input("Student Name")
    status = st.selectbox("Status", ["Active", "Graduated", "Suspended"])
    picture = st.file_uploader("Upload Picture", type=["jpg", "png", "jpeg"])
    submitted = st.form_submit_button("Add Student")

    if submitted and name:
        # Save picture if uploaded
        pic_path = ""
        if picture:
            os.makedirs("images", exist_ok=True)
            pic_path = f"images/{picture.name}"
            with open(pic_path, "wb") as f:
                f.write(picture.getbuffer())
        
        # Add to DataFrame
        new_student = pd.DataFrame([[name, status, pic_path]], 
                                   columns=["Name", "Status", "Picture"])
        students = pd.concat([students, new_student], ignore_index=True)
        students.to_csv(DATA_FILE, index=False)
        st.success(f"{name} added successfully!")

# --- Student Records ---
st.subheader("📋 Student Records")

if not students.empty:
    for i, row in students.iterrows():
        st.write(f"**{row['Name']}** - {row['Status']}")
        if row["Picture"] and os.path.exists(str(row["Picture"])):
            st.image(row["Picture"], width=100)

        # Edit and Delete buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"✏️ Edit {row['Name']}", key=f"edit_{i}"):
                st.session_state["edit_index"] = i
        with col2:
            if st.button(f"🗑️ Delete {row['Name']}", key=f"delete_{i}"):
                students = students.drop(i).reset_index(drop=True)
                students.to_csv(DATA_FILE, index=False)
                st.experimental_rerun()

    # --- Edit Form ---
    if "edit_index" in st.session_state:
        idx = st.session_state["edit_index"]
        st.subheader(f"✏️ Edit Student: {students.at[idx, 'Name']}")
        
        with st.form("edit_form"):
            new_name = st.text_input("Student Name", students.at[idx, "Name"])
            new_status = st.selectbox("Status", 
                                      ["Active", "Graduated", "Suspended"], 
                                      index=["Active", "Graduated", "Suspended"].index(students.at[idx, "Status"]))
            new_picture = st.file_uploader("Upload New Picture", type=["jpg", "png", "jpeg"])
            save_changes = st.form_submit_button("Save Changes")

            if save_changes:
                # Update name & status
                students.at[idx, "Name"] = new_name
                students.at[idx, "Status"] = new_status

                # Update picture if new one uploaded
                if new_picture:
                    os.makedirs("images", exist_ok=True)
                    pic_path = f"images/{new_picture.name}"
                    with open(pic_path, "wb") as f:
                        f.write(new_picture.getbuffer())
                    students.at[idx, "Picture"] = pic_path

                students.to_csv(DATA_FILE, index=False)
                st.success("Student updated successfully!")
                del st.session_state["edit_index"]
                st.experimental_rerun()
else:
    st.info("No students added yet.")
