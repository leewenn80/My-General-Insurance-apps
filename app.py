import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Insurance Policy Tracker", layout="wide")
st.title("🛡️ General Insurance Sub-Agent Policy Tracker")

# 🔗 CONNECT TO GOOGLE SHEET
GSHEET_URL = "PASTE_YOUR_GOOGLE_SHEET_URL_HERE"

@st.cache_data(ttl=10)
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

    # 🔄 MOVED OUTSIDE THE FORM FOR INSTANT INTERACTIVE SWITCHING
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

    # Start the actual input form
    with st.form("main_policy_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👤 Part A: CUSTOMER INFORMATION")
            cust_name = st.text_input("Name / Company Name", value=search_cust if ('search_cust' in locals() and search_cust != "-- New Customer --") else "")
            
            # FIXED: Guaranteed instant text swap
            id_label = "Identity No (NRIC)" if cust_type == "Individual" else "Company Registration No"
            cust_id = st.text_input(id_label, value=recalled_id)
            
            contact = st.text_input("Contact Number", value=recalled_contact)
            email = st.text_input("Email Address", value=recalled_email)
            address = st.text_area("Mailing Address", height=68, value=recalled_address)
            
        with col2:
            st.subheader("📄 Policy Information")
            policy_no = st.text_input("Policy Number")
            sum_assured = st.number_input("Sum Assured (RM)", min_value=0.0, step=1000.0)
            start_date = st.date_input("Coverage Start Date", datetime.now())
            end_date = st.date_input("Coverage End Date", datetime.now() + timedelta(days=365))
            
        st.markdown("---")
        
        # 🚗 HIDDEN EXCLUSIVELY UNLESS MOTOR IS SELECTED
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
                # FIXED: Simple layout fixes form input locking issues
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
            
            # NEW: Custom type-in rider option
            st.markdown("**Other Custom Motor Rider:**")
            other_motor_rider_title = st.text_input("Rider Description / Coverage Name", placeholder="e.g. Current Year Betterment Scale Waiver")
            other_motor_rider_amt = st.number_input("Rider Amount Coverage (RM)", min_value=0.0, step=100.0)
            st.markdown("---")
        else:
            car_plate, ncd_pct, windscreen, windscreen_amt, perils, llp, llop, waiver_betterment, waiver_excess, towing = "", "0%", False, 0.0, False, False, False, False, False, False
            other_motor_rider_title, other_motor_rider_amt = "", 0.0

        # 🏢 HIDDEN EXCLUSIVELY UNLESS FIRE / CONDO FIRE IS SELECTED
        if policy_type in ["Fire Insurance", "Condo fire insurance"]:
            st.subheader("🏢 Part C: Fire Insurance Property Details")
            insured_building_address = st.text_area("Insured Building Address (Risk Location)", placeholder="Enter the physical address of the property or residential block being insured...")
            
            # Fire-specific details section
            f_detail1, f_detail2 = st.columns(2)
            with f_detail1:
                building_type = st.text_input("Type of Building / Occupancy", placeholder="e.g. 4-Storey Flat, Commercial Shophouse, Light Factory")
            with f_detail2:
                construction_class = st.selectbox("Construction Class", ["Class 1A (Fully Non-Combustible)", "Class 1B", "Class 2 (Timber Walls/Roof)", "Class 3"])
            st.markdown("---")
        else:
            insured_building_address, building_type, construction_class = "", "", ""

        # Financials and Commission
        st.subheader("💰 Financials & Commission Sharing")
        f_col1, f_col2 = st.columns(2)
        
        with f_col1:
            gross_premium = st.number_input("Gross Premium (RM)", min_value=0.0, step=10.0)
            sst = st.number_input("SST (RM)", min_value=0.0, step=1.0)
            stamp_duty = st.number_input("Stamp Duty (RM)", min_value=10.0, step=10.0, value=10.0)
            total_payable = gross_premium + sst + stamp_duty
            st.info(f"**Total Payable by Client:** RM {total_payable:.2f}")
            
        with f_col2:
            comm_pct = st.number_input("Total Policy Commission (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5)
            sub_agent_share = st.number_input("Your Sharing Share (%)", min_value=0.0, max_value=100.0, value=60.0, step=1.0)
            
            total_comm = gross_premium * (comm_pct / 100)
            your_comm = total_comm * (sub_agent_share / 100)
            st.success(f"**Your Net Commission:** RM {your_comm:.2f}")

        submit = st.form_submit_button("Save Policy")
        
        if submit:
            if not cust_name or not policy_no:
                st.error("Please fill in Name and Policy Number.")
            else:
                new_row = pd.DataFrame([{
                    "Date Saved": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Customer": cust_name, "Identity/Reg No": cust_id, "Type": cust_type, 
                    "Contact No": contact, "Email Address": email, "Mailing Address": address,
                    "Policy Type": policy_type, "Policy No": policy_no, "Sum Assured": sum_assured,
                    "Start Date": str(start_date), "End Date": str(end_date),
                    "Insured Building Address": insured_building_address, "Building Classification": f"{building_type} ({construction_class})",
                    "Car Plate": car_plate, "NCD %": ncd_pct,
                    "Gross Premium": gross_premium, "SST": sst, "Stamp Duty": stamp_duty, "Total Payable": total_payable,
                    "Your Commission (RM)": round(your_comm, 2),
                    "Windscreen": f"Yes (RM {windscreen_amt})" if windscreen else "No",
                    "Special Perils": "Yes" if perils else "No", "LLP": "Yes" if llp else "No", 
                    "LLOP": "Yes" if llop else "No", "Waiver Betterment": "Yes" if waiver_betterment else "No", 
                    "Waiver Excess": "Yes" if waiver_excess else "No", "Unlimited Towing": "Yes" if towing else "No",
                    "Custom Motor Rider": f"{other_motor_rider_title} (RM {other_motor_rider_amt})" if other_motor_rider_title else "None"
                }])
                
                st.success("🎉 Policy Form validated successfully!")
                st.dataframe(new_row)
