import streamlit as st
import pandas as pd
import json
import urllib.request
from datetime import datetime, date

# Web Page Configuration
st.set_page_config(page_title="Taytay Methodist Church", layout="wide")

def get_clean_url(url_string):
    if "/edit" in url_string:
        return url_string.split("/edit")[0] + "/export?format=csv"
    return url_string

# Daily Bible Verse Setup
verses_list = [
    '"The Lord is a stronghold for the oppressed, a stronghold in times of trouble." — Psalm 9:9',
    '"Trust in the Lord with all your heart, and do not lean on your own understanding." — Proverbs 3:5',
    '"I can do all things through him who strengthens me." — Philippians 4:13',
    '"For God gave us a spirit not of fear but of power and love and self-control." — 2 Timothy 1:7',
    '"Be strong and courageous. Do not be frightened, and do not be dismayed." — Joshua 1:9',
    '"The Lord is my shepherd; I shall not want." — Psalm 23:1',
    '"But seek first the kingdom of God and his righteousness." — Matthew 6:33'
]
today_index = date.today().day % len(verses_list)

# Verse Display Section
st.subheader("📖 Verse of the Day")
st.markdown(f"## **{verses_list[today_index]}**")
st.write("---")

# Welcome Header Messages
st.title("Welcome to our Youth Fellowship Portal!")
st.write("We are glad you are here! Please take a moment to fill out the form below so we can stay connected.")
st.write("---")

# Registration Form Layout
st.subheader("✝️ New Registration Form")
with st.form("registration_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        full_name = st.text_input("Full Name:", placeholder="e.g., John Doe")
        birthday = st.date_input(
            "Birthday:", 
            value=date(2000, 1, 1), 
            min_value=date(1900, 1, 1), 
            max_value=date.today(), 
            format="MM/DD/YYYY"
        )
        gender = st.selectbox("Gender:", ["Male", "Female", "Other"])
        membership_status = st.selectbox("Membership Status:", ["Active Member", "First-Time Visitor"])
        church = st.text_input("Church:", placeholder="e.g., Taytay Methodist Church")

    with col2:
        parent_name = st.text_input("Parent's / Guardian's Name:", placeholder="e.g., Mary Doe")
        fb_profile = st.text_input("Facebook Profile Link or Name:", placeholder="e.g., ://facebook.com")
        contact_number = st.text_input("Contact Number:", placeholder="e.g., 09123456789")
        address = st.text_area("Complete Address:", height=100, placeholder="e.g., 123 Street Name, Barangay, City")

    submit_button = st.form_submit_button("Save Registration Details")

    # Form Submission Handler
    if submit_button:
        if full_name.strip() == "":
            st.error("Full Name is a required field!")
        else:
            bday_str = birthday.strftime("%m/%d/%Y") if birthday else ""
            current_now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
            
            payload = {
                "action": "register",
                "fullName": full_name,
                "birthday": bday_str,
                "gender": gender,
                "status": membership_status,
                "church": church,
                "parentName": parent_name,
                "fbProfile": fb_profile,
                "contactNumber": contact_number,
                "address": address,
                "registrationDate": current_now
            }

            try:
                script_url = st.secrets["SCRIPT_URL"]
                req = urllib.request.Request(
                    script_url, 
                    data=json.dumps(payload).encode("utf-8"), 
                    headers={"Content-Type": "application/json"}
                )
                urllib.request.urlopen(req)
                st.success(f"Successfully registered {full_name} directly to the Cloud database!")
            except Exception as e:
                st.error("Details verified locally, but the online database link is pending setup.")

st.write("---")

# Sidebar Authentication Controls
st.sidebar.title("🔐 Admin ")
admin_password = st.sidebar.text_input("Enter Password:", type="password", key="final_sidebar_admin_password")

# Admin Panel Access Verification
if admin_password:
    if admin_password == st.secrets["ADMIN_PASSWORD"]:
        st.sidebar.success("Correct Password!")
        st.write("---")
        st.subheader("Saved Members List (Live Cloud Data Feed)")

        try:
            raw_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
            csv_url = get_clean_url(raw_url)
            df_clean = pd.read_csv(csv_url)
        except Exception:
            df_clean = pd.DataFrame()

        if not df_clean.empty:
            if "Contact Number" in df_clean.columns:
                df_clean["Contact Number"] = df_clean["Contact Number"].astype(str).str.replace(r'\.0$', '', regex=True)

            if 'Row No.' not in df_clean.columns:
                df_clean.insert(0, 'Row No.', range(1, 1 + len(df_clean)))
            
            # Name Search Functionality
            search_col, empty_space = st.columns(2)
            with search_col:
                search_query = st.text_input("Search list by name:", value="")
                
            if search_query and "Full Name" in df_clean.columns:
                df_clean = df_clean[df_clean['Full Name'].astype(str).str.contains(search_query, case=False, na=False)]
            
            df_clean["Remove"] = False

            edited_df = st.data_editor(
                df_clean,
                use_container_width=False,
                disabled=[col for col in df_clean.columns if col != "Remove"],
                column_config={
                    "Contact Number": st.column_config.TextColumn("Contact Number"),
                    "Remove": st.column_config.CheckboxColumn(
                        "Remove",
                        help="Check this box to prepare row for cloud deletion",
                        default=False,
                    )
                },
                key="member_editor"
            )
            
            # Deletion Panel Handler
            marked_rows = edited_df[edited_df["Remove"] == True]
            if not marked_rows.empty:
                for idx, row in marked_rows.iterrows():
                    target_name = row["Full Name"]
                    
                    box_col, alignment_col = st.columns(2)
                    with box_col:
                        st.error(f"Do you really want to remove {target_name}?")
                        
                        btn_col1, btn_col2, btn_spacer = st.columns(3)
                        with btn_col1:
                            if st.button("Yes", key=f"yes_cloud_{idx}"):
                                delete_payload = {
                                    "action": "delete",
                                    "fullName": target_name
                                }
                                try:
                                    script_url = st.secrets["SCRIPT_URL"]
                                    req = urllib.request.Request(
                                        script_url, 
                                        data=json.dumps(delete_payload).encode("utf-8"), 
                                        headers={"Content-Type": "application/json"}
                                    )
                                    urllib.request.urlopen(req)
                                    st.rerun()
                                except Exception:
                                    st.warning("Request processed locally, database synchronization pending.")
                        with btn_col2:
                            if st.button("No", key=f"no_cloud_{idx}"):
                                if "member_editor" in st.session_state:
                                    st.session_state["member_editor"]["edited_rows"][int(idx)]["Remove"] = False
                                st.rerun()
            
            # Excel / CSV Data File Download Exporter
            csv_data = df_clean.drop(columns=["Remove"]).to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download List as Excel / CSV file",
                data=csv_data,
                file_name=f"registered_members_{date.today().strftime('%m_%d_%Y')}.csv",
                mime="text/csv"
            )
        else:
            st.info("The database is currently loading or empty.")
    else:
        st.sidebar.error("Wrong Password")
