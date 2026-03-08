import streamlit as st
import boto3
import datetime
from PIL import Image

# ---------------------------
# STREAMLIT CONFIG
# ---------------------------

st.set_page_config(
    page_title="Velir AI",
    page_icon="🌾",
    layout="wide"
)

# ---------------------------
# AWS CONFIGURATION
# ---------------------------

S3_BUCKET = "velir-ai-pooja-2026"
DYNAMO_TABLE = "velir_queries"

AWS_ACCESS_KEY_ID = st.secrets["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = st.secrets["AWS_SECRET_ACCESS_KEY"]
AWS_REGION = st.secrets["AWS_REGION"]

dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

table = dynamodb.Table(DYNAMO_TABLE)

# ---------------------------
# SIDEBAR DASHBOARD
# ---------------------------

st.sidebar.title("🌾 Velir AI Dashboard")

st.sidebar.subheader("📈 Crop Market Prices")

st.sidebar.metric("Rice", "₹2450 / quintal", "+2.1%")
st.sidebar.metric("Wheat", "₹2120 / quintal", "+1.3%")
st.sidebar.metric("Maize", "₹1980 / quintal", "-0.8%")
st.sidebar.metric("Cotton", "₹6450 / quintal", "+3.4%")
st.sidebar.metric("Sugarcane", "₹315 / ton", "+0.5%")

st.sidebar.divider()

st.sidebar.subheader("🌦 Weather Status")

st.sidebar.write("Location: Tamil Nadu")
st.sidebar.write("Condition: 🌤 Partly Cloudy")
st.sidebar.write("Rainfall: Expected in 3 days")

st.sidebar.divider()

st.sidebar.subheader("🟢 System Status")
st.sidebar.success("AI Services Online")

# ---------------------------
# MAIN PAGE
# ---------------------------

st.title("🌾 Velir AI")
st.subheader("Digital Farmer Officer")

col1, col2 = st.columns(2)

with col1:
    st.info("🎙️ **Vani – Policy Assistant**")

with col2:
    st.info("👁️ **Kisan Vision – Crop Analyzer**")

st.divider()

# ---------------------------
# QUERY INPUT SECTION
# ---------------------------

st.header("💬 Ask about Insurance / Weather / Crops")

with st.container():

    query = st.text_input(
        "Enter your query",
        placeholder="Example: Will rain affect my crop insurance?"
    )

    if st.button("🔍 Analyze Query"):

        if query == "":
            st.warning("Please enter a question")

        else:

            if "crop" in query.lower():
                response = "Your crop condition appears stable. Monitor rainfall and pests."

            elif "insurance" in query.lower():
                response = "You are covered under the Prevented Sowing clause."

            elif "weather" in query.lower():
                response = "Rainfall is expected within the next 3 days."

            else:
                response = "Our system will analyze your request."

            st.success(response)

            table.put_item(
                Item={
                    "query_id": str(datetime.datetime.now()),
                    "query": query,
                    "response": response,
                    "timestamp": str(datetime.datetime.now())
                }
            )

            st.info("Query stored in database")

st.divider()

# ---------------------------
# IMAGE UPLOAD SECTION
# ---------------------------

st.header("📷 Crop Image Analyzer")

with st.container():

    uploaded_file = st.file_uploader(
        "Upload crop photo",
        type=["jpg","jpeg","png"]
    )

    if uploaded_file:

        image = Image.open(uploaded_file)

        st.image(image, caption="Uploaded Crop Image", use_container_width=True)

        file_name = uploaded_file.name

        s3.upload_fileobj(
            uploaded_file,
            S3_BUCKET,
            file_name
        )

        st.success("Image uploaded to S3")

        st.info("AI crop disease detection will be added in next version.")

st.divider()

# ---------------------------
# FOOTER
# ---------------------------

st.caption("Velir AI – AI for Bharat Hackathon Prototype")
