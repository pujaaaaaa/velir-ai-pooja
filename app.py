import streamlit as st
import boto3
import datetime
from PIL import Image
from openai import OpenAI

# ---------------------------
# PAGE CONFIG
# ---------------------------

st.set_page_config(
    page_title="Velir AI",
    page_icon="🌾",
    layout="wide"
)

# ---------------------------
# AWS CONFIG
# ---------------------------

AWS_ACCESS_KEY_ID = st.secrets["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = st.secrets["AWS_SECRET_ACCESS_KEY"]
AWS_REGION = st.secrets["AWS_REGION"]

S3_BUCKET = "velir-ai-pooja-2026"
DYNAMO_TABLE = "velir_queries"

# ---------------------------
# OPENAI CONFIG
# ---------------------------

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------------------
# AWS CLIENTS
# ---------------------------

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
# SIDEBAR
# ---------------------------

st.sidebar.title("📈 Crop Market Prices")

crop_prices = {
    "Rice": 2450,
    "Wheat": 2125,
    "Maize": 1980,
    "Sugarcane": 315,
    "Cotton": 6450
}

for crop, price in crop_prices.items():
    st.sidebar.metric(crop, f"₹{price}", "Market")

st.sidebar.caption("Sample mandi price data")

# ---------------------------
# MAIN PAGE
# ---------------------------

st.title("🌾 Velir AI")
st.subheader("Digital Farmer Officer")

st.write("🎙️ *Vani – Policy Assistant*")
st.write("👁️ *Kisan Vision – Crop Analyzer*")

st.divider()

# ---------------------------
# FARMER QUESTION
# ---------------------------

st.header("Ask about Farming / Weather / Insurance")

query = st.text_input("Enter your question")

if st.button("Submit Query"):

    if query.strip() == "":
        st.warning("Please enter a question")

    else:

        try:

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an agricultural expert helping Indian farmers. Give simple and practical farming advice."
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                max_tokens=200
            )

            answer = response.choices[0].message.content

        except Exception as e:

            st.error(f"AI service error: {e}")
            answer = "Please monitor crop conditions and weather updates regularly."

        st.success(answer)

        # ---------------------------
        # SAVE QUERY TO DYNAMODB
        # ---------------------------

        try:

            table.put_item(
                Item={
                    "query_id": str(datetime.datetime.now().timestamp()),
                    "query": query,
                    "response": answer,
                    "timestamp": str(datetime.datetime.now())
                }
            )

        except Exception as db_error:

            st.warning(f"Database save failed: {db_error}")

st.divider()

# ---------------------------
# IMAGE UPLOAD
# ---------------------------

st.header("Upload Crop Image for Disease Detection")

uploaded_file = st.file_uploader(
    "Upload crop image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(image, caption="Uploaded Crop Image", use_container_width=True)

    file_name = uploaded_file.name

    try:

        s3.upload_fileobj(
            uploaded_file,
            S3_BUCKET,
            file_name
        )

        st.success("Image uploaded to S3")

    except Exception as s3_error:

        st.error(f"S3 upload failed: {s3_error}")

    st.info("AI crop disease detection will be added in next version.")

st.divider()

st.caption("Velir AI – AI for Bharat Hackathon Prototype")
