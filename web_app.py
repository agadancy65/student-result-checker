import streamlit as st
import sqlite3
import csv
import io

# --- 1. Database Setup ---
def setup_database():
    conn = sqlite3.connect('school_results.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT,
            Mth_201 TEXT,
            Ent_201 TEXT,
            Csc_201 TEXT,
            Gns_201 TEXT,
            "Ua-CSC_205" TEXT
        )
    ''')
    
    # Insert sample data ONLY if the table is empty
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ('24/208CSC/656', 'Agada Joseph', 'A1', 'B2', 'A1', 'A1', 'A1'),
            ('24/208CSC/930', 'Dauda Elizabeth', 'B2', 'A1', 'A1', 'A1', 'A1'),
            ('24/208CSC/733', 'Ugwumba Agbaeze', 'A1', 'B2', 'B2', 'B2', 'B2')
        ]
        cursor.executemany('''
            INSERT INTO students (student_id, name, Mth_201, Ent_201, Csc_201, Gns_201, "Ua-CSC_205") 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_data)
        conn.commit()
    conn.close()

setup_database()

# --- 2. Web App Configuration ---
st.set_page_config(page_title="Student Result Portal", page_icon="🎓")

# --- 3. Admin Sidebar (Hidden Menu) ---
st.sidebar.header("🔒 Admin Access")
admin_password = st.sidebar.text_input("Enter Password:", type="password")

if admin_password == "admin123":
    st.sidebar.success("Logged In Successfully!")
    st.sidebar.subheader("Upload New Results")
    
    # Streamlit's built-in file uploader
    uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        if st.sidebar.button("Upload to Database"):
            # Read the uploaded CSV file
            file_contents = uploaded_file.getvalue().decode("utf-8")
            reader = csv.reader(io.StringIO(file_contents))
            next(reader) # Skip header
            
            conn = sqlite3.connect('school_results.db')
            cursor = conn.cursor()
            records_added = 0
            
            for row in reader:
                if len(row) == 7:
                    try:
                        cursor.execute('''
                            INSERT INTO students (student_id, name, Mth_201, Ent_201, Csc_201, Gns_201, "Ua-CSC_205") 
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', row)
                        records_added += 1
                    except sqlite3.IntegrityError:
                        pass # Skip duplicates
            
            conn.commit()
            conn.close()
            st.sidebar.success(f"Added {records_added} new records!")

# --- 4. Main Student Interface ---
st.title("🎓 Student Result Portal")
st.write("Enter your Student ID below to view your grades for this semester.")

# Input box for student ID
student_id = st.text_input("Student ID:", placeholder="e.g., 24/208CSC/656")

if st.button("Check Result", type="primary"):
    if student_id:
        conn = sqlite3.connect('school_results.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE LOWER(student_id) = LOWER(?)", (student_id.strip(),))
        student = cursor.fetchone()
        conn.close()
        
        if student:
            st.success(f"Welcome, **{student[1]}**!")
            
            # Display grades in a nice grid format for mobile
            col1, col2 = st.columns(2)
            col1.metric("Mth_201", student[2])
            col1.metric("Ent_201", student[3])
            col1.metric("Csc_201", student[4])
            
            col2.metric("Gns_201", student[5])
            col2.metric("Ua-CSC_205", student[6])
        else:
            st.error("Error: Student ID not found in the database.")
    else:
        st.warning("Please enter a Student ID.")
