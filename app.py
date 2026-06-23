import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse
import requests

st.set_page_config(page_title="Insurance Policy Tracker", layout="wide")
st.title("🛡️ General Insurance Sub-Agent Policy Tracker")

# 🔗 CONNECT TO GOOGLE SHEET READ/WRITE LINKS
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1mnX8oKNsVMLmNl6ywLEuPHaR--cdY5_NhdA0-gluHiQ/edit?gid=0#gid=0"
WEB_APP_URL = https://script.google.com/macros/s/AKfycbxiaJ-c36_VQnqf-YxEWQuNFfF45bSZLICLG1KyuCquxAlwvDnIXSFMCBXQq6J1yw2k9A/exec

@st.cache_data(ttl=5)
def load_data():
    try:
        clean_url = GSHEET_URL.split('/edit')[0] + '/export?format=csv&sheet=Policies'
        return pd.read_csv(clean_url)
    except Exception:
        return pd.DataFrame()

existing_df = load_data()

tab1, tab2, tab3 = st.tabs(["📝 Register New Policy", "🔍 Customer History Lookup", "📊 View Sales Ledger"])

with tab1:
    st.header("Enter Policy Details")
    
    recalled_address = ""
    recalled_contact = ""
    recalled_id = ""
    recalled_email = ""
    
    if not existing_df.empty and "Customer" in existing_df.columns:
        unique_customers = ["-- New Customer --"] + sorted(existing_df["Customer"].dropna().unique().tolist())
        search_cust = st.selectbox("⚡ Quick Search Existing Customer (Optional)", unique_customers)
        
        if search_cust != "-- New Customer --":
            match = existing_df[existing_df["Customer"] == search_cust].iloc[-1]
            recalled_address = match.get("Mailing Address", "")
            recalled_contact = match.get("Contact No", "")
            recalled_id = match.get("Identity/Reg No", "")
            recalled_email = match.get("Email Address", "")
            st.caption(f"✅ Found existing record for {search_cust}. Auto-filling details below.")

    # 📋 MAIN SELECTORS
    st.subheader("📋 Main Selectors")
    sel_col1, sel_col2 = st.columns(2)
    with sel_col1:
        cust_type = st.radio("Customer Type", ["Individual", "Corporate"], horizontal=True)
    with sel_col2:
        policy_type = st.selectbox("Type of Policy", [
            "Motor Insurance", "Fire Insurance", "Travel Insurance", 
            "Golf insurance", "PA insurance", "Condo fire insurance", 
            "Marine insurance", "Others"
        ])

    st.markdown("---")

    # 👤 CORE CUSTOMER INFORMATION
    st.subheader("👤 Part A: CUSTOMER INFORMATION")
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        cust_name = st.text_input("Name / Company Name", value=search_cust if ('search_cust' in locals() and search_cust != "-- New Customer --") else "")
        id_label = "Identity No (NRIC)" if cust_type == "Individual" else "Company Registration No"
        cust_id = st.text_input(id_label, value=recalled_id)
    with c_col2:
        contact = st.text_input("Contact Number", value=recalled_contact)
        email = st.text_input("Email Address", value=recalled_email)
    address = st.text_area("Mailing Address", height=68, value=recalled_address)

    st.markdown("---")

    # ✈️ TRAVEL INSURANCE DYNAMIC DATA SECTION
    travel_summary_log = ""
    if policy_type == "Travel Insurance":
        st.subheader("✈️ Part D: Travel Insurance Plan & Insured Persons Details")
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            destination_country = st.text_input("Destination Country (or Region)", placeholder="e.g. Worldwide, Asia-Pacific, Japan")
        with t_col2:
            travel_plan_type = st.selectbox("Plan Category", ["Individual Plan", "Spouse Plan", "Family Plan"])
        
        st.markdown("#### 👤 Primary Insured Person")
        same_as_cust = st.checkbox("Insured Person is the same as Customer Information account above")
        
        ti_col1, ti_col2 = st.columns(2)
        with ti_col1:
            ip_name = st.text_input("Primary Insured Name", value=cust_name if same_as_cust else "")
            ip_id = st.text_input("Primary Insured NRIC/ID", value=cust_id if same_as_cust else "")
        with ti_col2:
            ip_phone = st.text_input("Primary Insured Contact No", value=contact if same_as_cust else "")
            ip_email = st.text_input("Primary Insured Email Address", value=email if same_as_cust else "")
        
        travel_summary_log = f"Plan: {travel_plan_type} to {destination_country} | Primary Insured: {ip_name} ({ip_id})"
        
        if travel_plan_type in ["Spouse Plan", "Family Plan"]:
            st.markdown("---")
            st.markdown("#### 👩‍❤️‍👨 Spouse Details")
            sp_col1, sp_col2 = st.columns(2)
            with sp_col1:
                spouse_name = st.text_input("Spouse Full Name")
                spouse_id = st.text_input("Spouse NRIC/ID")
            with sp_col2:
                spouse_phone = st.text_input("Spouse Contact No")
                spouse_email = st.text_input("Spouse Email Address")
            travel_summary_log += f" | Spouse: {spouse_name} ({spouse_id})"
        
        if travel_plan_type == "Family Plan":
            st.markdown("---")
            st.markdown("#### 👶 Children Details")
            child_count = st.number_input("How many children are insured under this family policy?", min_value=1, max_value=10, value=1, step=1)
            for idx in range(int(child_count)):
                st.markdown(f"**Child {idx + 1} Profile**")
                ch_col1, ch_col2, ch_col3 = st.columns(3)
                with ch_col1:
                    st.text_input(f"Child {idx+1} Full Name", key=f"ch_name_{idx}")
                with ch_col2:
                    st.text_input(f"Child {idx+1} NRIC / Birth Cert No", key=f"ch_id_{idx}")
                with ch_col3:
                    st.text_input(f"Child {idx+1} Contact No (If applicable)", key=f"ch_phone_{idx}")
            travel_summary_log += f" | Children Total Count: {child_count}"
        st.markdown("---")

    # 🩹 PA INSURANCE DYNAMIC FIELDS
    pa_plan_name = ""
    if policy_type == "PA insurance":
        st.subheader("🩹 Part E: Personal Accident Insurance Details")
        pa_plan_name = st.text_input("PA Plan Name / Package Description", placeholder="e.g. SafeTravel PA Plan A")
        st.markdown("---")

    # 🏢 FIRE INSURANCE PROPERTY DETAILS
    if policy_type in ["Fire Insurance", "Condo fire insurance"]:
        st.subheader("🏢 Part C: Fire Insurance Property Details")
        insured_building_address = st.text_area("Insured Building Address (Risk Location)")
        f_detail1, f_detail2 = st.columns(2)
        with f_detail1:
            building_type = st.text_input("Type of Building / Occupancy")
        with f_detail2:
            construction_class = st.selectbox("Construction Class", ["Class 1A (Fully Non-Combustible)", "Class 1B", "Class 2 (Timber)", "Class 3"])
        st.markdown("---")
    else:
        insured_building_address, building_type, construction_class = "", "", ""

    # 🚗 MOTOR INSURANCE RIDERS SECTION
    if policy_type == "Motor Insurance":
        st.subheader("🚗 Part B: Motor Insurance Details & Riders")
        mot_col1, mot_col2 = st.columns(2)
        with mot_col1:
            car_plate = st.text_input("Car Plate Number")
        with mot_col2:
            ncd_pct = st.selectbox("NCD Percentage", ["0%", "25%", "30%", "38.33%", "45%", "55%"])
            
        st.markdown("**Rider Options Attached:**")
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            windscreen = st.checkbox("Windscreen Coverage")
            windscreen_amt = st.number_input("Windscreen Sum Assured (RM)", min_value=0.0, step=100.0)
            perils = st.checkbox("Special Perils")
        with m_col2:
            llp = st.checkbox("Legal Liability to Passenger (LLP)")
            llop = st.checkbox("Legal Liabilities of Passenger (LLOP)")
            waiver_betterment = st.checkbox("Waiver of Betterment")
        with m_col3:
            waiver_excess = st.checkbox("Waiver Compulsory Excess")
            towing = st.checkbox("24 Hours Unlimited Towing")
        
        st.markdown("**Other Custom Motor Rider:**")
        other_motor_rider_title = st.text_input("Rider Description / Coverage Name")
        other_motor_rider_amt = st.number_input("Rider Amount Coverage (RM)", min_value=0.0, step=100.0)
        st.markdown("---")
    else:
        car_plate, ncd_pct, windscreen, windscreen_amt, perils, llp, llop, waiver_betterment, waiver_excess, towing = "", "0%", False, 0.0, False, False, False, False, False, False
        other_motor_rider_title, other_motor_rider_amt = "", 0.0

    # 💰 FINANCIALS & COMMISSION SHARING
    st.subheader("💰 Financials & Commission Sharing")
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        gross_premium = st.number_input("Gross Premium (RM)", min_value=0.0, step=10.0, format="%.2f")
        sst = st.number_input("SST (RM)", min_value=0.0, step=1.0, format="%.2f")
        stamp_duty = st.number_input("Stamp Duty (RM)", min_value=0.0, step=10.0, value=10.0, format="%.2f")
        total_payable = gross_premium + sst + stamp_duty
        st.info(f"**Total Payable by Client:** RM {total_payable:,.2f}")
    with f_col2:
        comm_pct = st.number_input("Total Policy Commission (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5)
        sub_agent_share = st.number_input("Your Sharing Share (%)", min_value=0.0, max_value=100.0, value=60.0, step=1.0)
        total_comm = gross_premium * (comm_pct / 100)
        your_comm = total_comm * (sub_agent_share / 100)
        st.success(f"**Your Net Commission:** RM {your_comm:,.2f}")

    st.markdown("---")

    with st.form("final_submission_gate"):
        st.subheader("📄 Base Record Matrix")
        policy_no = st.text_input("Policy Number")
        sum_assured = st.number_input("Sum Assured (RM)", min_value=0.0, step=1000.0, format="%.2f")
        start_date = st.date_input("Coverage Start Date", datetime.now())
        end_date = st.date_input("Coverage End Date", datetime.now() + timedelta(days=365))
        
        submit = st.form_submit_button("🚀 Save Directly to Google Sheets")
        
        if submit:
            if not cust_name or not policy_no:
                st.error("Please fill in Name and Policy Number.")
            elif WEB_APP_URL == "PASTE_YOUR_COPIED_APPS_SCRIPT_URL_HERE":
                st.error("Please paste your Google Apps Script Web App URL on line 13 of the code.")
            else:
                row_dict = {
                    "Date Saved": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Customer": cust_name, "Identity/Reg No": cust_id, "Type": cust_type, 
                    "Contact No": contact, "Email Address": email, "Mailing Address": address,
                    "Policy Type": f"PA ({pa_plan_name})" if policy_type == "PA insurance" else policy_type, 
                    "Policy No": policy_no, "Sum Assured": f"RM {sum_assured:,.2f}",
                    "Start Date": str(start_date), "End Date": str(end_date),
                    "Insured Building Address": insured_building_address, "Building Classification": f"{building_type} ({construction_class})",
                    "Car Plate": car_plate, "NCD %": ncd_pct, "Travel Policy Structure": travel_summary_log,
                    "Gross Premium": f"RM {gross_premium:,.2f}", "SST": f"RM {sst:,.2f}", "Stamp Duty": f"RM {stamp_duty:,.2f}", 
                    "Total Payable": f"RM {total_payable:,.2f}", "Your Commission (RM)": f"RM {your_comm:,.2f}",
                    "Windscreen": f"Yes (RM {windscreen_amt:,.2f})" if windscreen else "No", "Special Perils": "Yes" if perils else "No",
                    "LLP": "Yes" if llp else "No", "LLOP": "Yes" if llop else "No", "Waiver Betterment": "Yes" if waiver_betterment else "No", 
                    "Waiver Excess": "Yes" if waiver_excess else "No", "Unlimited Towing": "Yes" if towing else "No",
                    "Custom Motor Rider": f"{other_motor_rider_title} (RM {other_motor_rider_amt:,.2f})" if other_motor_rider_title else "None"
                }
                
                # Trigger the webhook save
                try:
                    response = requests.get(WEB_APP_URL, params=row_dict)
                    if response.text == "Success":
                        st.success("🎉 Policy successfully written straight to Google Sheets!")
                        st.balloons()
                        st.cache_data.clear() # Forces database pull refresh
                    else:
                        st.error("Form processed locally, but cloud macro pipeline returned an invalid handshake.")
                except Exception as e:
                    st.error(f"Form validation cleared, but webhook delivery failed: {e}")

# --- TAB 2: CUSTOMER HISTORY LOOKUP ---
with tab2:
    st.header("🔍 Customer Purchase History")
    if existing_df.empty:
        st.info("Reading active structural history logs...")
    else:
        search_name = st.selectbox("Select Customer to View History", sorted(existing_df["Customer"].dropna().unique().tolist()))
        customer_history = existing_df[existing_df["Customer"] == search_name]
        st.subheader(f"History Breakdown for {search_name}")
        st.metric("Total Policies Bought", len(customer_history))
        st.dataframe(customer_history)

# --- TAB 3: VIEW LEDGER ---
with tab3:
    st.header("📊 Complete Database Ledger")
    if existing_df.empty:
        st.info("Sheet database is empty or checking connectivity parameters.")
    else:
        st.dataframe(existing_df)
