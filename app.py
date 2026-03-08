import streamlit as st
import boto3
import datetime
import json
import base64
from PIL import Image
from io import BytesIO

# ---------------------------
# STREAMLIT PAGE CONFIG
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

bedrock = boto3.client(
    "bedrock-runtime",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

table = dynamodb.Table(DYNAMO_TABLE)

# ---------------------------
# SIDEBAR - CROP PRICES
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

    st.sidebar.metric(
        label=crop,
        value=f"₹{price}",
        delta="Market"
    )

st.sidebar.caption("Sample mandi price data")

# ---------------------------
# MAIN TITLE
# ---------------------------

st.title("🌾 Velir AI")
st.subheader("Digital Farmer Officer")

st.write("🎙️ *Vani – Policy Assistant*")
st.write("👁️ *Kisan Vision – Crop Analyzer*")

st.divider()

# ---------------------------
# QUERY INPUT
# ---------------------------

st.header("Ask about Insurance / Weather")

query = st.text_input(
    "Enter your question",
    placeholder="Example: how is my crop?"
)

if st.button("Submit Query"):

    if query.strip() == "":
        st.warning("Please enter a question")

    else:

        prompt = f"""
You are an agricultural expert helping Indian farmers.

Answer clearly and simply.

Question:
{query}
"""

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 300,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })

        try:

            response = bedrock.invoke_model(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                body=body
            )

            result = json.loads(response["body"].read())

            answer = result["content"][0]["text"]

        except Exception as e:

            answer = "AI service temporarily unavailable."

        st.success(answer)

        try:

            table.put_item(
                Item={
                    "query_id": str(datetime.datetime.now().timestamp()),
                    "query": query,
                    "response": answer,
                    "timestamp": str(datetime.datetime.now())
                }
            )

        except:
            st.warning("Database storage failed")

st.divider()

# ---------------------------
# IMAGE UPLOAD
# ---------------------------

st.header("Upload Crop Image for Disease Detection")

uploaded_file = st.file_uploader(
    "Upload crop photo",
    type=["jpg","jpeg","png"]
)

if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(image, caption="Uploaded Crop Image", use_container_width=True)

    file_name = uploaded_file.name

    # Upload image to S3
    try:

        s3.upload_fileobj(
            uploaded_file,
            S3_BUCKET,
            file_name
        )

        st.success("Image uploaded to S3")

    except Exception as e:

        st.error("S3 upload failed")
        st.stop()

    # Convert image to base64
    buffered = BytesIO()
    image.save(buffered, format="JPEG")

    img_base64 = base64.b64encode(buffered.getvalue()).decode()

    st.info("Analyzing crop health with AI...")

    prompt = """
Analyze this crop image and detect possible plant diseases.

Provide:
1. Disease name
2. Cause
3. Treatment
4. Prevention tips

Explain simply for farmers.
"""

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 400,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": img_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    })

    try:

        response = bedrock.invoke_model(
    modelId="anthropic.claude-3-haiku-20240307-v1:0",
    body=body,
    contentType="application/json",
    accept="application/json"
)
        

        result = json.loads(response["body"].read())

        diagnosis = result["content"][0]["text"]

        st.success("🌿 Crop Analysis")

        st.write(diagnosis)

    except Exception as e:

        st.error("AI crop analysis failed")

st.divider()

st.caption("Velir AI – AI for Bharat Hackathon Prototype")

