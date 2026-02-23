"""Prospecting Icebreaker Generator - Streamlit App."""

import os

from dotenv import load_dotenv
import streamlit as st

from api_client import run_crew_and_wait

load_dotenv()

# --- Configuration -----------------------------------------------------------

CREW1_URL = os.environ["CREW1_URL"]
CREW1_TOKEN = os.environ["CREW1_TOKEN"]
CREW2_URL = os.environ["CREW2_URL"]
CREW2_TOKEN = os.environ["CREW2_TOKEN"]

# --- Session state defaults ---------------------------------------------------

DEFAULTS = {
    "phase": 1,
    "company_name": "",
    "company_domain": "",
    "supplemental_info": "",
    "recon_report": "",
    "prospect_company": "",
    "prospect_name": "",
    "supplemental_prospect_info": "",
    "icebreaker_email": "",
    "error_message": None,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- Helpers ------------------------------------------------------------------


def reset_all():
    """Clear everything and go back to Phase 1."""
    for key, value in DEFAULTS.items():
        st.session_state[key] = value


def reset_prospect():
    """Clear prospect data and go back to Phase 2, keeping company recon."""
    st.session_state.phase = 2
    st.session_state.prospect_company = ""
    st.session_state.prospect_name = ""
    st.session_state.supplemental_prospect_info = ""
    st.session_state.icebreaker_email = ""
    st.session_state.error_message = None


# --- Page config --------------------------------------------------------------

st.set_page_config(
    page_title="Prospecting Icebreaker",
    page_icon=":envelope:",
    menu_items={},
)

# Hide the entire Streamlit toolbar (deploy, screencast, hamburger menu)
st.markdown(
    "<style>[data-testid='stToolbar'] { display: none; }</style>",
    unsafe_allow_html=True,
)

st.title("Prospecting Icebreaker Generator")

# --- Display errors -----------------------------------------------------------

if st.session_state.error_message:
    st.error(st.session_state.error_message)
    st.session_state.error_message = None

# ==============================================================================
# Phase 1: Company Information
# ==============================================================================

if st.session_state.phase == 1:
    st.header("Step 1: Your Company")
    st.markdown("Tell us about your company so we can research your products and services.")

    company_name = st.text_input("Company Name *", value=st.session_state.company_name)
    company_domain = st.text_input("Company Domain *", value=st.session_state.company_domain, placeholder="example.com")
    supplemental_info = st.text_area(
        "Supplemental Information (optional)",
        value=st.session_state.supplemental_info,
        placeholder="Any additional context about your company, products, or services...",
    )

    if st.button("Research Company", type="primary", use_container_width=True):
        if not company_name.strip() or not company_domain.strip():
            st.error("Company Name and Company Domain are required.")
        else:
            st.session_state.company_name = company_name.strip()
            st.session_state.company_domain = company_domain.strip()
            st.session_state.supplemental_info = supplemental_info.strip()

            inputs = {
                "company_name": st.session_state.company_name,
                "company_domain": st.session_state.company_domain,
                "supplemental_info": st.session_state.supplemental_info,
            }

            try:
                with st.spinner("Researching your company... This may take a few minutes."):
                    result = run_crew_and_wait(CREW1_URL, CREW1_TOKEN, inputs)
                st.session_state.recon_report = result
                st.session_state.phase = 2
                st.rerun()
            except TimeoutError:
                st.session_state.error_message = "Company research timed out. Please try again."
                st.rerun()
            except Exception as e:
                st.session_state.error_message = f"Error during company research: {e}"
                st.rerun()

# ==============================================================================
# Phase 2: Prospect Information
# ==============================================================================

elif st.session_state.phase == 2:
    st.header("Step 2: Prospect Information")

    with st.expander("Company Research Summary", expanded=False):
        st.markdown(f"**Company:** {st.session_state.company_name}")
        st.markdown(f"**Domain:** {st.session_state.company_domain}")
        if st.session_state.supplemental_info:
            st.markdown(f"**Notes:** {st.session_state.supplemental_info}")
        st.divider()
        st.markdown(st.session_state.recon_report)

    st.markdown("Provide details about who you'd like to prospect to.")

    prospect_company = st.text_input("Prospect Company (optional)", value=st.session_state.prospect_company)
    prospect_name = st.text_input("Prospect Individual Name (optional)", value=st.session_state.prospect_name)
    supplemental_prospect_info = st.text_area(
        "Supplemental Prospect Information (optional)",
        value=st.session_state.supplemental_prospect_info,
        placeholder="Specifics about what you want to sell, things you know about the prospect, talking points...",
        height=150,
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Over", use_container_width=True):
            reset_all()
            st.rerun()
    with col2:
        if st.button("Generate Icebreaker", type="primary", use_container_width=True):
            st.session_state.prospect_company = prospect_company.strip()
            st.session_state.prospect_name = prospect_name.strip()
            st.session_state.supplemental_prospect_info = supplemental_prospect_info.strip()

            inputs = {
                "company_name": st.session_state.company_name,
                "company_domain": st.session_state.company_domain,
                "supplemental_info": st.session_state.supplemental_info,
                "recon_report": st.session_state.recon_report,
                "prospect_company": st.session_state.prospect_company,
                "prospect_name": st.session_state.prospect_name,
                "supplemental_prospect_info": st.session_state.supplemental_prospect_info,
            }

            try:
                with st.spinner("Generating icebreaker email... This may take a few minutes."):
                    result = run_crew_and_wait(CREW2_URL, CREW2_TOKEN, inputs)
                st.session_state.icebreaker_email = result
                st.session_state.phase = 3
                st.rerun()
            except TimeoutError:
                st.session_state.error_message = "Icebreaker generation timed out. Please try again."
                st.rerun()
            except Exception as e:
                st.session_state.error_message = f"Error generating icebreaker: {e}"
                st.rerun()

# ==============================================================================
# Phase 3: Results
# ==============================================================================

elif st.session_state.phase == 3:
    st.header("Your Icebreaker Email")

    with st.expander("Context", expanded=False):
        st.markdown(f"**Your Company:** {st.session_state.company_name}")
        if st.session_state.prospect_name:
            st.markdown(f"**Prospect:** {st.session_state.prospect_name}")
        if st.session_state.prospect_company:
            st.markdown(f"**Prospect Company:** {st.session_state.prospect_company}")

    st.markdown(st.session_state.icebreaker_email)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Prospect Another Entity", use_container_width=True):
            reset_prospect()
            st.rerun()
    with col2:
        if st.button("Start Over", use_container_width=True):
            reset_all()
            st.rerun()
