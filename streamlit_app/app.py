import streamlit as st
import mimetypes

mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')
import requests
import time
import json
import os

API_URL = os.environ.get("API_URL", "http://backend:8000/v1")

st.set_page_config(page_title="AI Research Agent", layout="wide")

# Sidebar for Settings
st.sidebar.title("⚙️ Settings")
st.sidebar.markdown("Enter your API keys below. They are required to generate reports.")
gemini_key = st.sidebar.text_input("Gemini API Key", type="password")
tavily_key = st.sidebar.text_input("Tavily API Key", type="password")

st.title("🏢 AI Company Research & Recommendation Agent")
st.markdown("Generate a comprehensive business intelligence report on any company.")

company_name = st.text_input("Enter Company Name (e.g., Adani Realty)", "")

if st.button("Generate Report"):
    if not gemini_key or not tavily_key:
        st.error("Please enter both Gemini and Tavily API keys in the sidebar.")
        st.stop()
        
    if len(company_name) < 2:
        st.error("Company name must be at least 2 characters long.")
    else:
        # Start generation
        with st.spinner("Initializing request..."):
            try:
                response = requests.post(
                    f"{API_URL}/reports",
                    json={
                        "company_name": company_name, 
                        "options": {
                            "api_keys": {
                                "gemini": gemini_key,
                                "tavily": tavily_key
                            }
                        }
                    }
                )
                response.raise_for_status()
                data = response.json()
                report_id = data["report_id"]
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to start report generation: {e}")
                st.stop()
        
        status_placeholder = st.empty()
        progress_bar = st.progress(0)
        
        # Poll for status
        while True:
            try:
                status_res = requests.get(f"{API_URL}/reports/{report_id}/status")
                status_res.raise_for_status()
                status_data = status_res.json()
                status = status_data["status"]
                
                if status == "PENDING":
                    status_placeholder.info("Report is pending in queue...")
                elif status == "RESEARCHING" or status == "PROCESSING":
                    prog = status_data.get("progress")
                    if prog:
                        pct = prog.get("percentage", 0)
                        task = prog.get("current_task", "Processing...")
                        progress_bar.progress(pct)
                        status_placeholder.info(f"Status: {status} - {task} ({pct}%)")
                    else:
                        status_placeholder.info(f"Status: {status}...")
                elif status == "COMPLETE":
                    progress_bar.progress(100)
                    status_placeholder.success("Report Generation Complete!")
                    break
                elif status == "FAILED":
                    status_placeholder.error("Report Generation Failed!")
                    st.stop()
                    
            except requests.exceptions.RequestException as e:
                status_placeholder.warning(f"Error checking status: {e}. Retrying...")
            
            time.sleep(3)
        
        # Fetch complete report
        try:
            report_res = requests.get(f"{API_URL}/reports/{report_id}")
            report_res.raise_for_status()
            report_data = report_res.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to fetch report: {e}")
            st.stop()
            
        st.header(f"Report: {report_data['company']['name']}")
        
        sections = report_data.get("sections", {})
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Overview", "Business Info", "Challenges", "AI Opportunities", "CEO Pitch"
        ])
        
        with tab1:
            overview = sections.get("company_overview") or {}
            st.subheader("Company Overview")
            st.write(overview.get("summary", "N/A"))
            st.markdown(f"**Industry:** {overview.get('industry', 'N/A')}")
            st.markdown(f"**Scale:** {overview.get('scale', 'N/A')}")
            st.markdown(f"**Geographic Presence:** {', '.join(overview.get('geographic_presence', []))}")
            
        with tab2:
            biz = sections.get("business_info") or {}
            st.subheader("Business Information")
            st.markdown("**Offerings:**")
            for item in biz.get("offerings", []):
                st.markdown(f"- {item}")
            st.markdown("**Recent Developments:**")
            for item in biz.get("developments", []):
                st.markdown(f"- {item}")
            st.markdown("**Expansion Plans:**")
            for item in biz.get("expansion_plans", []):
                st.markdown(f"- {item}")
                
        with tab3:
            chal = sections.get("challenges") or {}
            st.subheader("Business Challenges")
            for idx, item in enumerate(chal.get("items", [])):
                st.markdown(f"### {idx+1}. {item.get('challenge')}")
                st.markdown(f"**Category:** {item.get('category')} | **Severity:** {item.get('severity')}")
                st.markdown(f"**Reasoning:** {item.get('reasoning')}")
                st.divider()
                
        with tab4:
            ai = sections.get("ai_opportunities") or {}
            st.subheader("AI Opportunities")
            for idx, item in enumerate(ai.get("items", [])):
                st.markdown(f"### {idx+1}. {item.get('opportunity')}")
                st.markdown(f"**Category:** {item.get('category')} | **Impact:** {item.get('impact')} | **Effort:** {item.get('effort')}")
                st.markdown(f"**Rationale:** {item.get('rationale')}")
                st.divider()
                
        with tab5:
            pitch = sections.get("ceo_pitch") or {}
            st.subheader("CEO Pitch")
            st.write(pitch.get("content", "N/A"))
            
        # Download JSON
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Download Raw JSON",
                data=json.dumps(report_data, indent=2),
                file_name=f"{report_data['company']['canonical_name']}_report.json",
                mime="application/json"
            )
            
        with col2:
            try:
                pdf_res = requests.get(f"{API_URL}/reports/{report_id}/pdf")
                if pdf_res.status_code == 200:
                    st.download_button(
                        label="Download PDF",
                        data=pdf_res.content,
                        file_name=f"{report_data['company']['canonical_name']}_report.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error("Failed to generate PDF.")
            except Exception as e:
                st.error(f"Failed to fetch PDF: {e}")
