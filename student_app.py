import streamlit as st
import pandas as pd
import os
import io
import matplotlib.pyplot as plt

# File to save student data
DATA_FILE = "students.csv"

# Load existing data
if os.path.exists(DATA_FILE):
    students = pd.read_csv(DATA_FILE)
else:
    students = pd.DataFrame(columns=["Name", "Age", "Address", "Parent Phone", "Status", "Picture"])

st.title("🎓 Student Management System")

# --- Dashboard Summary ---
st.subheader("📊 Dashboard")

if not students.empty:
    total = len(students)
    paid = len(students[students["Status"] == "Paid"])
    not_paid = len(students[students["Status"] == "Not Paid"])
    partial = len(students[students["Status"] == "Partially Paid"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 Total Students", total)
    col2.metric("✅ Paid", paid)
    col3.metric("❌ Not Paid", not_paid)
    col4.metric("⚠️ Partially Paid", partial)

    # --- Pie chart (Payment Status) ---
    labels = ["Paid", "Not Paid", "Partially Paid"]
    sizes = [paid, not_paid, partial]
    colors = ["#4CAF50", "#F44336", "#FFEB3B"]

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90, colors=colors)
    ax1.axis("equal")
    st.pyplot(fig1)

    # --- Bar chart (Age Distribution) ---
    age_counts = students["Age"].value_counts().sort_index()

    fig2, ax2 = plt.subplots()
    ax2.bar(age_counts.index, age_counts.values, color="#2196F3")
    ax2.set_xlabel("Age")
    ax2.set_ylabel("Number of Students")
    ax2.set_title("Age Distribution")
    st.pyplot(fig2)

else:
    st.info("No students available to display dashboard.")

# --- Add Student Form ---
st.subheader("📝 Add New Student")

with st.form("student_form", clear_on_submit=True):
    name = st.text_input("Full Name")
    age = st.number_input("Age", min_value=1, max_value=100, step=1)
    address = st.text_area("Address")
    parent_phone = st.text_input("Parent Phone Number")
    status = st.selectbox("Payment Status", ["Paid", "Not Paid", "Partially Paid"])
    picture = st.file_uploader("Upload Picture", type=["jpg", "png", "jpeg"])
    submitted = st.form_submit_button("Add Student")

    if submitted and name and parent_phone:
        # Save picture if uploaded
        pic_path = ""
        if picture:
            os.makedirs("images", exist_ok=True)
            pic_path = f"images/{picture.name}"
            with open(pic_path, "wb") as f:
                f.write(picture.getbuffer())
        
        # Add to DataFrame
        new_student = pd.DataFrame([[name, age, address, parent_phone, status, pic_path]], 
                                   columns=["Name", "Age", "Address", "Parent Phone", "Status", "Picture"])
        students = pd.concat([students, new_student], ignore_index=True)
        students.to_csv(DATA_FILE, index=False)
        st.success(f"{name} added successfully!")
        st.rerun()

# --- Student Records ---
st.subheader("📋 Student Records")

if not students.empty:
    # Search box
    search_query = st.text_input("🔍 Search by name or parent phone")

    # Payment status filter
    status_filter = st.selectbox(
        "🎯 Filter by Payment Status",
        ["All", "Paid", "Not Paid", "Partially Paid"]
    )

    # Apply search
    filtered_students = students[
        students["Name"].str.contains(search_query, case=False, na=False) |
        students["Parent Phone"].astype(str).str.contains(search_query, case=False, na=False)
    ] if search_query else students

    # Apply status filter
    if status_filter != "All":
        filtered_students = filtered_students[filtered_students["Status"] == status_filter]

    # --- Export buttons ---
    if not filtered_students.empty:
        # CSV export
        csv = filtered_students.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Export as CSV",
            data=csv,
            file_name="filtered_students.csv",
            mime="text/csv"
        )

        # Excel export with formatting
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
            filtered_students.to_excel(writer, index=False, sheet_name="Students")

            workbook = writer.book
            worksheet = writer.sheets["Students"]

            # Define formats
            header_format = workbook.add_format({
                "bold": True,
                "text_wrap": True,
                "valign": "top",
                "fg_color": "#4F81BD",
                "font_color": "white",
                "border": 1
            })
            paid_format = workbook.add_format({"bg_color": "#C6EFCE", "font_color": "#006100"})  # Green
            not_paid_format = workbook.add_format({"bg_color": "#FFC7CE", "font_color": "#9C0006"})  # Red
            partial_format = workbook.add_format({"bg_color": "#FFEB9C", "font_color": "#9C6500"})  # Yellow

            # Format header row
            for col_num, value in enumerate(filtered_students.columns.values):
                worksheet.write(0, col_num, value, header_format)

            # Auto-adjust column widths
            for i, col in enumerate(filtered_students.columns):
                max_len = max(filtered_students[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, max_len)

            # Apply row formatting based on Status column
            status_col_idx = filtered_students.columns.get_loc("Status")
            for row_num, status in enumerate(filtered_students["Status"], start=1):
                if status == "Paid":
                    worksheet.set_row(row_num, None, paid_format)
                elif status == "Not Paid":
                    worksheet.set_row(row_num, None, not_paid_format)
                elif status == "Partially Paid":
                    worksheet.set_row(row_num, None, partial_format)

        st.download_button(
            label="⬇️ Export as Excel",
            data=excel_buffer.getvalue(),
            file_name="filtered_students.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # --- Display results ---
    if filtered_students.empty:
        st.warning("No students found.")
    else:
        for i, row in filtered_students.iterrows():
            st.write(f"**{row['Name']}** ({row['Age']} yrs) - 💳 {row['Status']}")
            st.write(f"📍 {row['Address']}")
            st.write(f"📞 Parent: {row['Parent Phone']}")
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
                    st.rerun()

    # --- Edit Form ---
    if "edit_index" in st.session_state:
        idx = st.session_state["edit_index"]
        st.subheader(f"✏️ Edit Student: {students.at[idx, 'Name']}")
        
        with st.form("edit_form"):
            new_name = st.text_input("Full Name", students.at[idx, "Name"])
            new_age = st.number_input("Age", min_value=1, max_value=100, step=1, value=int(students.at[idx, "Age"]))
            new_address = st.text_area("Address", students.at[idx, "Address"])
            new_parent_phone = st.text_input("Parent Phone Number", students.at[idx, "Parent Phone"])
            new_status = st.selectbox("Payment Status", 
                                      ["Paid", "Not Paid", "Partially Paid"], 
                                      index=["Paid", "Not Paid", "Partially Paid"].index(students.at[idx, "Status"]))
            new_picture = st.file_uploader("Upload New Picture", type=["jpg", "png", "jpeg"])
            save_changes = st.form_submit_button("Save Changes")

            if save_changes:
                # Update fields
                students.at[idx, "Name"] = new_name
                students.at[idx, "Age"] = new_age
                students.at[idx, "Address"] = new_address
                students.at[idx, "Parent Phone"] = new_parent_phone
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
                st.rerun()
else:
    st.info("No students added yet.")
