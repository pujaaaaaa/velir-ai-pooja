import streamlit as st
import boto3
import datetime
from PIL import Image

# ---------------------------
# AWS CONFIGURATION
# ---------------------------

AWS_REGION = "ap-south-1"
S3_BUCKET = "velir-ai-pooja-2026"
DYNAMO_TABLE = "velir_queries"

# Initialize AWS services
dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION
)

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION
)

table = dynamodb.Table(DYNAMO_TABLE)

# ---------------------------
# STREAMLIT UI
# ---------------------------

st.set_page_config(
    page_title="Velir AI",
    page_icon="🌾",
    layout="centered"
)

st.title("🌾 Velir AI")
st.subheader("Digital Farmer Officer")

st.write("🎙️ **Vani – Policy Assistant**")
st.write("👁️ **Kisan Vision – Crop Analyzer**")

st.divider()

# ---------------------------
# QUERY INPUT
# ---------------------------

st.header("Ask about Insurance / Weather")

query = st.text_input(
    "Enter your query",
    placeholder="Example: how is my crop?"
)

if st.button("Submit Query"):

    if query == "":
        st.warning("Please enter a question")
    else:

        # Simple AI response logic
        if "crop" in query.lower():
            response = "Your crop condition appears stable. Monitor rainfall and pests."
        elif "insurance" in query.lower():
            response = "You are covered under Prevented Sowing clause."
        elif "weather" in query.lower():
            response = "Rainfall expected in next 3 days."
        else:
            response = "Our system will analyze your request."

        st.success(response)

        # Save query to DynamoDB
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
# IMAGE UPLOAD
# ---------------------------

st.header("Upload Crop Image")

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

st.caption("Velir AI – AI for Bharat Hackathon Prototype")