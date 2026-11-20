import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Connect to the existing backend detection modules.
BACKEND_PATH = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_PATH))

from toxicity_detector import detect_toxicity
from spam_detector import detect_spam


st.set_page_config(
    page_title="ToxicShield",
    page_icon="🛡️",
    layout="wide"
)

# Light dashboard styling
st.markdown("""
<style>
.stApp {
    background-color: #F5F7FB;
    color: #172033;
}
[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #E5EAF2;
}
h1, h2, h3 {
    color: #172B4D;
}
.stButton > button {
    background: linear-gradient(90deg, #3867E8, #438CF5);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 22px;
    font-weight: 600;
}
.stButton > button:hover {
    border: 1px solid #3867E8;
    color: #FFFFFF;
}
[data-testid="stMetric"] {
    background-color: #FFFFFF;
    padding: 18px;
    border: 1px solid #E5EAF2;
    border-radius: 14px;
    box-shadow: 0 2px 8px rgba(30, 50, 90, 0.05);
}
[data-testid="stFileUploader"] {
    background-color: #FFFFFF;
    padding: 15px;
    border: 1px dashed #AAB9D0;
    border-radius: 12px;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}
</style>
""", unsafe_allow_html=True)


# Keep analysis history during the current Streamlit session.
if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []


def analyze_comment(comment):
    """Run the existing toxicity and spam detectors for one comment."""
    toxicity = detect_toxicity(comment)
    spam = detect_spam(comment)

    return {
        "Comment": comment,
        "Toxicity": toxicity["category"],
        "Toxicity Score": toxicity["confidence"],
        "Spam Status": "Spam" if spam["is_spam"] else "Not Spam",
        "Spam Risk Score": spam["risk_score"]
    }


# Sidebar navigation
st.sidebar.title("🛡️ ToxicShield")
st.sidebar.caption("AI Content Protection")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Manual Analysis", "CSV Analysis", "About"]
)

st.sidebar.divider()
st.sidebar.caption("Multilingual AI Protection")

# Main page header
st.title("🛡️ ToxicShield")
st.write("AI-Powered Toxic Comment & Spam Detection")


if page == "Dashboard":
    st.header("Dashboard Overview")
    st.write("Welcome to your AI-powered content protection system.")

    history = st.session_state.analysis_history

    if st.button("Clear Analysis History"):
        st.session_state.analysis_history = []
        st.rerun()

    total = len(history)
    toxic = sum(item["Toxicity"] == "Toxic" for item in history)
    spam = sum(item["Spam Status"] == "Spam" for item in history)
    safe = sum(
        item["Toxicity"] == "Non-toxic"
        and item["Spam Status"] == "Not Spam"
        for item in history
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Analyzed", total)
    col2.metric("Toxic Comments", toxic)
    col3.metric("Spam Comments", spam)
    col4.metric("Safe Comments", safe)

    st.divider()

    if total > 0:
        st.subheader("Detection Overview")
        chart_data = pd.DataFrame({
            "Category": ["Toxic", "Non-toxic", "Spam", "Not Spam"],
            "Count": [toxic, total - toxic, spam, total - spam]
        })
        st.bar_chart(chart_data, x="Category", y="Count")

        st.subheader("Recent Analysis")
        st.dataframe(
            pd.DataFrame(history).tail(10),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info(
            "No analysis history yet. Analyze comments or upload a CSV "
            "to see your statistics."
        )


elif page == "Manual Analysis":
    st.header("Analyze a Single Comment")
    comment = st.text_area(
        "Enter your comment",
        height=130,
        placeholder="Type a comment here..."
    )

    if st.button("Analyze Comment", key="manual_analyze"):
        if not comment.strip():
            st.warning("Please enter a comment.")
        else:
            try:
                with st.spinner("Analyzing comment..."):
                    result = analyze_comment(comment.strip())
                    st.session_state.analysis_history.append(result)

                st.subheader("Analysis Results")
                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Toxicity", result["Toxicity"])
                    st.metric(
                        "Toxicity Score",
                        f'{result["Toxicity Score"]}%'
                    )

                with col2:
                    st.metric("Spam Status", result["Spam Status"])
                    st.metric(
                        "Spam Risk Score",
                        result["Spam Risk Score"]
                    )

                if result["Toxicity"] == "Toxic":
                    st.error("This comment is classified as toxic.")
                else:
                    st.success("This comment is classified as non-toxic.")

                if result["Spam Status"] == "Spam":
                    st.warning("This comment is also classified as spam.")

            except Exception as error:
                st.error(f"Analysis failed: {error}")


elif page == "CSV Analysis":
    st.header("Bulk Comment Analysis")
    st.write("Upload a CSV file containing a column named `comment`.")

    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type=["csv"],
        key="csv_uploader"
    )

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)

            if "comment" not in df.columns:
                st.error("CSV must contain a column named 'comment'.")
            else:
                comments = (
                    df["comment"].dropna().astype(str).str.strip()
                )
                comments = comments[comments != ""].tolist()
                st.write(f"Comments found: {len(comments)}")

                if st.button("Analyze CSV", key="csv_analyze"):
                    if not comments:
                        st.warning("No comments found in this file.")
                    else:
                        results = []
                        progress = st.progress(0)
                        status = st.empty()

                        try:
                            for index, comment in enumerate(comments):
                                results.append(analyze_comment(comment))
                                progress.progress((index + 1) / len(comments))
                                status.write(
                                    f"Analyzed {index + 1} of "
                                    f"{len(comments)} comments"
                                )

                            results_df = pd.DataFrame(results)
                            st.session_state.analysis_history.extend(results)

                            st.subheader("Analysis Summary")
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Total Comments", len(results_df))
                            col2.metric(
                                "Toxic Comments",
                                int((results_df["Toxicity"] == "Toxic").sum())
                            )
                            col3.metric(
                                "Spam Comments",
                                int((results_df["Spam Status"] == "Spam").sum())
                            )

                            st.subheader("Detection Results")
                            st.dataframe(
                                results_df,
                                use_container_width=True,
                                hide_index=True
                            )

                            st.subheader("Toxicity Distribution")
                            st.bar_chart(results_df["Toxicity"].value_counts())

                            st.subheader("Spam Distribution")
                            st.bar_chart(results_df["Spam Status"].value_counts())

                            st.download_button(
                                "Download Analysis Report",
                                data=results_df.to_csv(
                                    index=False
                                ).encode("utf-8-sig"),
                                file_name="ToxicShield_Analysis.csv",
                                mime="text/csv"
                            )

                        except Exception as error:
                            st.error(f"CSV analysis failed: {error}")

        except Exception as error:
            st.error(f"Could not read CSV: {error}")


elif page == "About":
    st.header("About ToxicShield")
    st.write("""
    ToxicShield is an AI-powered comment moderation application.

    **Detection capabilities:**
    - Multilingual toxicity detection
    - Spam identification
    - Manual comment analysis
    - Bulk CSV analysis
    - Downloadable analysis reports

    **Technologies used:**
    - Python
    - Streamlit
    - PyTorch
    - Transformers
    - Pandas
    """)
