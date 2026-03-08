import streamlit as st
import boto3
import datetime
from PIL import Image

# ---------------------------
# PAGE CONFIG
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
st.sidebar.write("Temperature: 31°C")

st.sidebar.divider()

st.sidebar.subheader("🚨 Farmer Alerts")

st.sidebar.warning("Heavy rainfall expected in next 48 hours")
st.sidebar.info("Delay fertilizer spraying due to expected rain")
st.sidebar.error("Cyclone risk advisory for coastal farmers")

st.sidebar.divider()

st.sidebar.success("AI Services Online")

# ---------------------------
# MAIN HEADER
# ---------------------------

st.title("🌾 Velir AI")
st.subheader("Digital Farmer Officer")

# ---------------------------
# WEATHER ALERT
# ---------------------------

st.warning(
    "⚠ WEATHER ALERT: Heavy rainfall expected in Tamil Nadu within 48 hours. Ensure proper drainage in fields."
)

# ---------------------------
# AI MODULE CARDS
# ---------------------------

col1, col2 = st.columns(2)

with col1:
    st.info("🎙️ Vani – Policy Assistant")

with col2:
    st.info("👁️ Kisan Vision – Crop Analyzer")

st.divider()

# ---------------------------
# SMART ADVISORY
# ---------------------------

st.subheader("🌾 Smart Advisory")

col1, col2, col3 = st.columns(3)

with col1:
    st.success("🌱 Soil moisture levels are optimal")

with col2:
    st.warning("🌧 Rain expected — delay pesticide spray")

with col3:
    st.info("🐛 Monitor crops for pest activity")

st.divider()

# ---------------------------
# QUERY INPUT
# ---------------------------

st.header("💬 Ask about Insurance / Weather / Crops")

query = st.text_input(
    "Enter your question",
    placeholder="Example: Will rain affect my crop insurance?"
)

if st.button("🔍 Analyze Query"):

    if query.strip() == "":
        st.warning("Please enter a question")

    else:

        q = query.lower()

        if "crop" in q:
            response = "Your crop condition appears stable. Ensure proper irrigation and monitor pest activity."

        elif "insurance" in q:
            response = "You may be eligible under the Prevented Sowing clause of crop insurance."

        elif "weather" in q:
            response = "Rainfall is expected within the next 3 days. Farmers should delay pesticide spraying."

        elif "pest" in q:
            response = "Inspect crop leaves for pest damage and apply recommended pesticide if necessary."

        else:
            response = "Velir AI recommends monitoring weather updates and maintaining proper soil moisture."

        st.success(response)

        # Save to DynamoDB
        table.put_item(
            Item={
                "query_id": str(datetime.datetime.now().timestamp()),
                "query": query,
                "response": response,
                "timestamp": str(datetime.datetime.now())
            }
        )

        st.info("Query stored in database")

st.divider()

# ---------------------------
# IMAGE UPLOAD
# ---------------------------

st.header("📷 Crop Image Analyzer")

uploaded_file = st.file_uploader(
    "Upload crop photo",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(image, caption="Uploaded Crop Image", use_container_width=True)

    file_name = uploaded_file.name

    # Upload to S3
    s3.upload_fileobj(
        uploaded_file,
        S3_BUCKET,
        file_name
    )

    st.success("Image uploaded successfully")

    # SAMPLE AI ANALYSIS
    st.subheader("🌿 Crop Health Analysis")

    st.success("Plant condition: Healthy")

    st.write("Possible Issue: Minor leaf discoloration detected")

    st.write("Recommendation: Apply mild organic pesticide and monitor moisture levels.")

    st.info("This is a prototype AI crop analysis result.")

st.divider()

# ---------------------------
# FOOTER
# ---------------------------

st.caption("Velir AI – AI for Bharat Hackathon Prototype")
