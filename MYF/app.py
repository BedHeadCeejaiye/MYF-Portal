from datetime import date, datetime
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
st.title("Welcome to our Youth Fellowship Portal!")
st.write(
    "We are glad you are here! Please take a moment to fill out the form below"
    " so we can stay connected."
)
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

  with col2:
    parent_name = st.text_input(
        "Parent's / Guardian's Name:", placeholder="e.g., Mary Doe"
    )
    fb_profile = st.text_input(
        "Facebook Profile Link or Name:", placeholder="e.g., facebook.com/johndoe"
    )

    st.write("Contact Number:")
    prefix_col, number_col = st.columns([1, 4])
    with prefix_col:
      st.text_input(
          "Prefix", value="09", disabled=True, label_visibility="collapsed"
      )
    with number_col:
      contact_suffix = st.text_input(
          "Contact Suffix",
          placeholder="123456789",
          max_chars=9,
          label_visibility="collapsed",
      )

    address = st.text_area(
        "Complete Address:",
        height=100,
        placeholder="e.g., 123 Street Name, Barangay, City",
    )

  submit_button = st.form_submit_button("Save Registration Details")

  # Form Submission Handler
  if submit_button:
    full_contact_number = "09" + contact_suffix.strip()

    if (
        full_name.strip() == ""
        or not gender
        or not membership_status
        or not church
        or parent_name.strip() == ""
        or fb_profile.strip() == ""
        or len(contact_suffix.strip()) != 9
        or not contact_suffix.strip().isdigit()
        or address.strip() == ""
    ):
      st.error(
          "All fields are required, and the contact number must be exactly 9"
          " digits after '09'!"
      )
    else:
      bday_str = birthday.strftime("%m/%d/%Y") if birthday else ""
      current_now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
      formatted_contact = f"'{full_contact_number}"

      payload = {
          "action": "register",
          "fullName": full_name,
          "birthday": bday_str,
          "gender": gender,
          "status": membership_status,
          "church": church,
          "parentName": parent_name,
          "fbProfile": fb_profile,
          "contactNumber": formatted_contact,
          "address": address,
          "registrationDate": current_now,
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

st.write("---")

# Sidebar Authentication Controls
st.sidebar.title("🔐 Admin ")
admin_password = st.sidebar.text_input(
    "Enter Password:", type="password", key="final_sidebar_admin_password"
)

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
        df_clean["Contact Number"] = (
            df_clean["Contact Number"]
            .astype(str)
            .str.replace(r"\.0$", "", regex=True)
            .str.replace("'", "", regex=False)
        )

      if "Row No." not in df_clean.columns:
        df_clean.insert(0, "Row No.", range(1, 1 + len(df_clean)))

      # Name Search Functionality
      search_col, empty_space = st.columns(2)
      with search_col:
        search_query = st.text_input("Search list by name:", value="")

      if search_query and "Full Name" in df_clean.columns:
        df_clean = df_clean[
            df_clean["Full Name"]
            .astype(str)
            .str.contains(search_query, case=False, na=False)
        ]

      st.dataframe(df_clean, use_container_width=True)

      # Excel / CSV Data File Download Exporter
      csv_data = df_clean.to_csv(index=False).encode("utf-8")
      st.download_button(
          label="Download List as Excel / CSV file",
          data=csv_data,
          file_name=f"registered_members_{date.today().strftime('%m_%d_%Y')}.csv",
          mime="text/csv",
      )
    else:
      st.info("The database is currently loading or empty.")
  else:
    st.sidebar.error("Wrong Password")
