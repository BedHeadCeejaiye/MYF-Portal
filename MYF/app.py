from datetime import date, datetime
import base64
import json
import urllib.request
import pandas as pd
import streamlit as st

# Web Page Configuration
st.set_page_config(page_title="Taytay Methodist Church", layout="wide")

def get_clean_url(url_string):
    if "/edit" in url_string:
        return url_string.split("/edit")[0] + "/export?format=csv"
    return url_string
    
# Daily Bible Verse Setup
verses_list = [
    (
        '"The Lord is a stronghold for the oppressed, a stronghold in times of'
        ' trouble." — Psalm 9:9'
    ),
    (
        '"Trust in the Lord with all your heart, and do not lean on your own'
        ' understanding." — Proverbs 3:5'
    ),
    '"I can do all things through him who strengthens me." — Philippians 4:13',
    (
        '"For God gave us a spirit not of fear but of power and love and'
        ' self-control." — 2 Timothy 1:7'
    ),
    (
        '"Be strong and courageous. Do not be frightened, and do not be'
        ' dismayed." — Joshua 1:9'
    ),
    '"The Lord is my shepherd; I shall not want." — Psalm 23:1',
    '"But seek first the kingdom of God and his righteousness." — Matthew 6:33',
]
today_index = date.today().day % len(verses_list)

# Verse Display Section
st.subheader("📖 Verse of the Day")
st.markdown(f"## **{verses_list[today_index]}**")
st.write("---")

# Welcome Header Messages
st.title("Hello, Kabataan!")
st.write("---")

tab_register, tab_attendance = st.tabs(
    ["Registration Form", "Attendance Check-In"]
)

with tab_register:
    st.subheader("✝ Registration Form")
    
    with st.form("registration_form", clear_on_submit=True):
        form_col, _ = st.columns([2, 1])
        with form_col:
            col1, col2 = st.columns(2)

            with col1:
                full_name = st.text_input("Full Name:", placeholder="e.g., John Doe")
                birthday = st.date_input(
                    "Birthday:",
                    value=date(2000, 1, 1),
                    min_value=date(1900, 1, 1),
                    max_value=date.today(),
                    format="MM/DD/YYYY",
                )

                gender = st.selectbox(
                    "Gender:",
                    ["Male", "Female", "Other"],
                    index=None,
                    placeholder="Select Gender",
                )
                membership_status = st.selectbox(
                    "Membership Status:",
                    ["Active Member", "First-Time Visitor"],
                    index=None,
                    placeholder="Select Status",
                )
                church = st.selectbox(
                    "Church:",
                    [
                        "Taytay Methodist Church",
                        "Upper Javier Methodist Mission",
                        "Baras Mission Methodist Church",
                        "Halayhayin Peace Methodist Church",
                        "Tanay Methodist Mission",
                        "Higher Ground Methodist Church",
                        "River of Life Methodist Church",
                        "O Mira Gratia Evangelical Brethren Church",
                    ],
                    index=None,
                    placeholder="Select Church",
                )
                
                profile_image = st.file_uploader("Upload Profile Picture:", type=["jpg", "jpeg", "png"])

            with col2:
                parent_name = st.text_input(
                    "Parent's / Guardian's Name:", placeholder="e.g., Mary Doe"
                )
                fb_profile = st.text_input(
                    "Facebook Profile Link or Name:",
                    placeholder="e.g., facebook.com/johndoe",
                )

                contact_number = st.text_input(
                    "Contact Number:",
                    placeholder="09123456789",
                    max_chars=11,
                )

                address = st.text_area(
                    "Complete Address:",
                    height=100,
                    placeholder="e.g., 123 Street Name, Barangay, City",
                )

            submit_button = st.form_submit_button("Save Registration Details")

        if submit_button:
            clean_contact = "".join(filter(str.isdigit, contact_number))

            if full_name.strip() == "":
                st.error("Please enter your **Full Name**.")
            elif not gender:
                st.error("Please select your **Gender**.")
            elif not membership_status:
                st.error("Please select your **Membership Status**.")
            elif not church:
                st.error("Please select your **Church**.")
            elif parent_name.strip() == "":
                st.error("Please enter your **Parent's / Guardian's Name**.")
            elif fb_profile.strip() == "":
                st.error("Please enter your **Facebook Profile Link or Name**.")
            elif not clean_contact.startswith("09") or len(clean_contact) != 11:
                st.error(
                    "Please enter a valid **Contact Number** (must be 11 digits and start"
                    " with '09')."
                )
            elif address.strip() == "":
                st.error("Please enter your **Complete Address**.")
            else:
                today = date.today()
                computed_age = (
                    today.year
                    - birthday.year
                    - ((today.month, today.day) < (birthday.month, birthday.day))
                )

                bday_str = birthday.strftime("%m/%d/%Y") if birthday else ""
                current_now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

                formatted_contact = (
                    f"'{clean_contact[:4]}-{clean_contact[4:7]}-{clean_contact[7:]}"
                )

                image_base64 = ""
                image_name = ""
                if profile_image is not None:
                    image_base64 = base64.b64encode(profile_image.read()).decode("utf-8")
                    image_name = profile_image.name

                payload = {
                    "action": "register",
                    "fullName": full_name,
                    "birthday": bday_str,
                    "age": computed_age,
                    "gender": gender,
                    "status": membership_status,
                    "church": church,
                    "parentName": parent_name,
                    "fbProfile": fb_profile,
                    "contactNumber": formatted_contact,
                    "address": address,
                    "registrationDate": current_now,
                    "imageBase64": image_base64,
                    "imageName": image_name,
                }

                try:
                    script_url = st.secrets["SCRIPT_URL"]
                    req = urllib.request.Request(
                        script_url,
                        data=json.dumps(payload).encode("utf-8"),
                        headers={"Content-Type": "application/json"},
                    )
                    urllib.request.urlopen(req)
                    st.success(
                        f"Successfully registered {full_name} directly to the Cloud"
                        " database!"
                    )
                except Exception as e:
                    st.error(
                        "Details verified locally, but the online database link is pending"
                        " setup."
                    )

with tab_attendance:
    st.subheader("Attendance Check-In")
    st.write("Quick check-in: Just type your name and select the date!")

    with st.form("attendance_form", clear_on_submit=True):
        col_att, _ = st.columns([1, 2])
        with col_att:
            att_name = st.text_input("Full Name:", placeholder="e.g., John Doe")
            att_date = st.date_input("Attendance Date:", value=date.today())

        submit_attendance = st.form_submit_button("Check-In")

        if submit_attendance:
            if att_name.strip() == "":
                st.error("Please enter your **Full Name**.")
            else:
                att_date_str = att_date.strftime("%m/%d/%Y")
                current_time_str = datetime.now().strftime("%H:%M:%S")
                attendance_value = f"{att_date_str} {current_time_str}"

                payload = {
                    "action": "attendance",
                    "fullName": att_name,
                    "attendanceDate": attendance_value,
                }

                try:
                    script_url = st.secrets["SCRIPT_URL"]
                    req = urllib.request.Request(
                        script_url,
                        data=json.dumps(payload).encode("utf-8"),
                        headers={"Content-Type": "application/json"},
                    )
                    response = urllib.request.urlopen(req)
                    res_data = json.loads(response.read().decode("utf-8"))

                    if res_data.get("status") == "duplicate":
                        st.warning(
                            f"⚠️ **{att_name}** has already checked in for"
                            f" **{att_date_str}**!"
                        )
                    else:
                        st.success(
                            f"✅ Attendance recorded for **{att_name}** at"
                            f" **{attendance_value}**!"
                        )
                except Exception as e:
                    st.error(
                        "Details verified locally, but the online database link is pending"
                        " setup."
                    )
st.write("---")

# Admin Panel
st.sidebar.title("🔐 Admin Panel")
admin_password = st.sidebar.text_input(
    "Enter Password:", type="password", key="final_sidebar_admin_password"
)

# Admin Panel Access Verification
if admin_password:
    if admin_password == st.secrets["ADMIN_PASSWORD"]:
        st.sidebar.success("Correct Password!")
        st.write("---")
        st.subheader("Admin Dashboard")

        admin_tab1, admin_tab2 = st.tabs(["Database Records", "Attendance Logs"])

        with admin_tab1:
            st.subheader("Saved Members List")
            try:
                raw_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
                csv_url = get_clean_url(raw_url)
                df_clean = pd.read_csv(csv_url)
            except Exception:
                df_clean = pd.DataFrame()

            if not df_clean.empty:
                if "Contact Number" in df_clean.columns:
                    df_clean["Contact Number"] = (
                        df_clean["Contact Number"]
                        .astype(str)
                        .str.replace(r"\.0$", "", regex=True)
                        .str.replace("'", "", regex=False)
                    )

                if "Row No." not in df_clean.columns:
                    df_clean.insert(0, "Row No.", range(1, 1 + len(df_clean)))

                col_s1, _ = st.columns([1, 2])
                with col_s1:
                    search_query = st.text_input(
                        "Search list by name:", value=""
                    )

                if search_query and "Full Name" in df_clean.columns:
                    df_clean = df_clean[
                        df_clean["Full Name"]
                        .astype(str)
                        .str.contains(search_query, case=False, na=False)
                    ]

                column_configs = {}
                if "Profile Picture" in df_clean.columns:
                    column_configs["Profile Picture"] = st.column_config.ImageColumn(
                        "Profile Picture",
                        help="Member profile photo",
                        width="small"
                    )

                st.dataframe(
                    df_clean,
                    use_container_width=False,
                    column_config=column_configs
                )

                csv_data = df_clean.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Download List as Excel/CSV file",
                    data=csv_data,
                    file_name=f"registered_members_{date.today().strftime('%m_%d_%Y')}.csv",
                    mime="text/csv",
                )
            else:
                st.info("The database is currently loading or empty.")

        with admin_tab2:
            st.subheader("Attendance Logs")
            try:
                raw_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
                base_csv_url = get_clean_url(raw_url)
                attendance_csv_url = (
                    base_csv_url.split("export?format=csv")[0]
                    + "export?format=csv&gid=1206935683"
                )
                df_att = pd.read_csv(attendance_csv_url)
            except Exception:
                df_att = pd.DataFrame()

            if not df_att.empty:
                if "Row No." not in df_att.columns:
                    df_att.insert(0, "Row No.", range(1, 1 + len(df_att)))

                new_columns = []
                date_count = 0
                for col in df_att.columns:
                    if col in ["Row No.", "Full name", "Full Name"]:
                        new_columns.append(col)
                    else:
                        if date_count == 0:
                            new_columns.append("Date")
                        else:
                            new_columns.append(" " * date_count)
                        date_count += 1
                df_att.columns = new_columns

                col_s2, _ = st.columns([1, 2])
                with col_s2:
                    search_att = st.text_input(
                        "Search attendance by name:", value=""
                    )

                name_col = "Full name" if "Full name" in df_att.columns else ("Full Name" if "Full Name" in df_att.columns else df_att.columns[1])
                if search_att and name_col in df_att.columns:
                    df_att = df_att[
                        df_att[name_col]
                        .astype(str)
                        .str.contains(search_att, case=False, na=False)
                    ]

                st.dataframe(df_att, use_container_width=False)
                att_csv_data = df_att.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Download Attendance Logs as CSV",
                    data=att_csv_data,
                    file_name=f"attendance_logs_{date.today().strftime('%m_%d_%Y')}.csv",
                    mime="text/csv",
                )
            else:
                st.info("No attendance logs recorded yet.")
    else:
        st.sidebar.error("Wrong Password")
