import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Insurance Policy Tracker", layout="wide")
st.title("🛡️ General Insurance Sub-Agent Policy Tracker")

# Initialize database in session state
if 'policies' not in st.session_state:
    st.session_state.policies = []

tab1, tab2 = st.tabs(["📝 Register New Policy", "📊 View & Export Sales"])

# --- TAB 1: REGISTER POLICY ---
with tab1:
    st.header("Enter Policy Details")
    
    with st.form("policy_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👤 Customer Information")
            cust_type = st.radio("Customer Type", ["Individual", "Corporate"], horizontal=True)
            cust_name = st.text_input("Name / Company Name")
            id_label = "Identity No (NRIC)" if cust_type == "Individual" else "Company Reg No"
            cust_id = st.text_input(id_label)
            contact = st.text_input("Contact Number")
            address = st.text_area("Address", height=68)
            
        with col2:
            st.subheader("📄 Policy Information")
            policy_type = st.selectbox("Type of Policy", ["Motor Insurance", "Fire Insurance", "Travel Insurance", "Others"])
            policy_no = st.text_input("Policy Number")
            sum_assured = st.number_input("Sum Assured (RM)", min_value=0.0, step=1000.0)
            
            start_date = st.date_input("Coverage Start Date", datetime.now())
            end_date = st.date_input("Coverage End Date", datetime.now() + timedelta(days=365))
            
        st.markdown("---")
        
        # Conditional Motor Riders
        if policy_type == "Motor Insurance":
            st.subheader("🚗 Motor Riders & Add-ons")
            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                windscreen = st.checkbox("Windscreen Coverage")
                windscreen_amt = st.number_input("Windscreen Sum Assured (RM)", min_value=0.0, disabled=not windscreen)
            with m_col2:
                perils = st.checkbox("Special Perils (Flood/Storm)")
            with m_col3:
                srcc = st.checkbox("SRCC Coverage")
            st.markdown("---")
        else:
            windscreen, windscreen_amt, perils, srcc = False, 0.0, False, False

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
            
            # Calculations
            total_comm = gross_premium * (comm_pct / 100)
            your_comm = total_comm * (sub_agent_share / 100)
            st.success(f"**Your Net Commission:** RM {your_comm:.2f}")

        # Submit button
        submit = st.form_submit_button("Save Policy")
        
        if submit:
            if not cust_name or not policy_no:
                st.error("Please fill in Name and Policy Number.")
            else:
                policy_data = {
                    "Date Saved": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Customer": cust_name, "ID/Reg No": cust_id, "Type": cust_type, "Contact": contact, "Address": address,
                    "Policy Type": policy_type, "Policy No": policy_no, "Sum Assured": sum_assured,
                    "Start Date": start_date, "End Date": end_date,
                    "Gross Premium": gross_premium, "SST": sst, "Stamp Duty": stamp_duty, "Total Payable": total_payable,
                    "Your Commission (RM)": round(your_comm, 2),
                    "Motor_Windscreen": f"Yes (RM {windscreen_amt})" if windscreen else "No",
                    "Motor_Perils": "Yes" if perils else "No", "Motor_SRCC": "Yes" if srcc else "No"
                }
                st.session_state.policies.append(policy_data)
                st.balloons()
                st.success("Policy recorded successfully!")

# --- TAB 2: VIEW & EXPORT ---
with tab2:
    st.header("📊 Policy Log Ledger")
    if len(st.session_state.policies) == 0:
        st.info("No policies recorded yet.")
    else:
        df = pd.DataFrame(st.session_state.policies)
        
        # Display Metrics summary
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Policies Sold", len(df))
        m2.metric("Total Premium Collected", f"RM {df['Total Payable'].sum():,.2f}")
        m3.metric("Total Net Commission Earned", f"RM {df['Your Commission (RM)'].sum():,.2f}")
        
        st.dataframe(df)
        
        # Export to Excel/CSV capacity
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Ledger to CSV/Excel",
            data=csv,
            file_name=f"insurance_sales_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv',
        )
