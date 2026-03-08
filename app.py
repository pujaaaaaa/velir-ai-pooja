import streamlit as st
import boto3
import datetime
from PIL import Image
import json

# ---------------------------
# AWS CONFIGURATION
# ---------------------------

AWS_REGION = st.secrets["AWS_REGION"]
AWS_ACCESS_KEY_ID = st.secrets["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = st.secrets["AWS_SECRET_ACCESS_KEY"]

S3_BUCKET = "velir-ai-pooja-2026"
DYNAMO_TABLE = "velir_queries"

# AWS Clients
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

bedrock = boto3.client(
    "bedrock-runtime",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

table = dynamodb.Table(DYNAMO_TABLE)

# ---------------------------
# STREAMLIT PAGE CONFIG
# ---------------------------

st.set_page_config(
    page_title="Velir AI",
    page_icon="🌾",
    layout="wide"
)

# ---------------------------
# SIDEBAR - MARKET PRICES
# ---------------------------

st.sidebar.title("🌾 Market Prices")

prices = {
    "Rice (1kg)": "₹55",
    "Wheat (1kg)": "₹40",
    "Tomato (1kg)": "₹30",
    "Onion (1kg)": "₹35",
    "Potato (1kg)": "₹28",
    "Maize (1kg)": "₹22"
}

for item, price in prices.items():
    st.sidebar.metric(item, price)

st.sidebar.info("Prices are indicative sample data.")

# ---------------------------
# MAIN HEADER
# ---------------------------

st.title("🌾 Velir AI")
st.subheader("Digital Farmer Officer")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🎙️ Vani – Policy Assistant")
    st.write("Ask about crop insurance, weather and farming guidance.")

with col2:
    st.markdown("### 👁️ Kisan Vision – Crop Analyzer")
    st.write("Upload crop images to store and analyze farm conditions.")

st.divider()

# ---------------------------
# QUERY INPUT
# ---------------------------

st.header("Ask Farming Question")

query = st.text_input(
    "Enter your question",
    placeholder="Example: How is my crop condition?"
)

def ask_bedrock(prompt):

    body = json.dumps({
        "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
        "max_tokens_to_sample": 200,
        "temperature": 0.5
    })

    response = bedrock.invoke_model(
        modelId="anthropic.claude-v2",
        body=body
    )

    result = json.loads(response["body"].read())
    return result["completion"]

if st.button("Submit Query"):

    if query == "":
        st.warning("Please enter a question")

    else:

        with st.spinner("🤖 AI analyzing your query..."):

            try:
                response = ask_bedrock(query)
            except:
                response = "AI service temporarily unavailable."

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

    st.success("Image uploaded to S3 successfully")

    st.info("Future version will analyze crop disease using AI.")

st.divider()

st.caption("Velir AI – AI for Bharat Hackathon Prototype")
