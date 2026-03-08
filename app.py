import streamlit as st
import boto3
import json
from PIL import Image
import uuid
import os

# -----------------------------
# AWS CONFIG
# -----------------------------

AWS_REGION = "ap-south-1"
S3_BUCKET = "velir-ai-pooja-images"
TABLE_NAME = "velir-ai-pooja-queries"

# AWS clients
s3 = boto3.client("s3", region_name=AWS_REGION)

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(TABLE_NAME)

bedrock = boto3.client(
    "bedrock-runtime",
    region_name=AWS_REGION
)

# -----------------------------
# STREAMLIT UI
# -----------------------------

st.title("🌾 Velir AI - Smart Farming Assistant")

st.write("Upload crop image or ask farming questions")

# -----------------------------
# IMAGE UPLOAD SECTION
# -----------------------------

st.header("📸 Crop Disease Detection")

uploaded_file = st.file_uploader(
    "Upload crop leaf image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(image, caption="Uploaded Crop Image", use_container_width=True)

    file_name = str(uuid.uuid4()) + "_" + uploaded_file.name

    # Upload to S3
    s3.upload_fileobj(
        uploaded_file,
        S3_BUCKET,
        file_name
    )

    st.success("Image uploaded to S3")

    # Ask Bedrock
    prompt = """
    A farmer uploaded an image of a crop leaf.

    Predict possible crop disease.

    Provide:
    1. Disease name
    2. Cause
    3. Treatment
    4. Prevention

    Explain simply for farmers.
    """

    body = json.dumps({
        "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
        "max_tokens_to_sample": 300,
        "temperature": 0.5
    })

    response = bedrock.invoke_model(
        modelId="anthropic.claude-v2",
        body=body
    )

    result = json.loads(response["body"].read())

    diagnosis = result["completion"]

    st.subheader("🌿 AI Diagnosis")

    st.write(diagnosis)

# -----------------------------
# FARMER QUESTION SECTION
# -----------------------------

st.header("💬 Ask Farming Question")

question = st.text_input("Enter your question")

if st.button("Ask AI"):

    if question != "":

        prompt = f"""
        You are an agricultural expert.

        Answer the farmer question clearly.

        Question: {question}
        """

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

        answer = result["completion"]

        st.success(answer)

        # Save to DynamoDB
        table.put_item(
            Item={
                "query_id": str(uuid.uuid4()),
                "question": question,
                "answer": answer
            }
        )
