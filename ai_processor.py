# ai_processor.py
import base64
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extract_between(text, start, end):
    """Utility: safely extract content between two markers."""
    try:
        return text.split(start)[1].split(end)[0].strip()
    except:
        return ""


def generate_profession_image(image_stream, goal):
    """
    Robust version:
    - GPT-4o extracts identity (gender/ethnicity/face)
    - NO JSON (avoids JSONDecodeError)
    - Builds stable prompt
    - gpt-image-1 generates final future-goal portrait
    """

    # Convert webcam image to base64 data URI
    img_b64 = base64.b64encode(image_stream.getvalue()).decode("utf-8")
    data_uri = f"data:image/png;base64,{img_b64}"

    # STEP 1 — Extract identity in a structured, non-JSON format
    identity_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract identity of the student. "
                    "Return the result in THIS EXACT FORMAT:\n\n"
                    "GENDER: <male/female/other>\n"
                    "ETHNICITY: <ethnicity>\n"
                    "FACE: <detailed face description>\n\n"
                    "DO NOT add anything else."
                )
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this student's face."},
                    {"type": "image_url", "image_url": {"url": data_uri}},
                ],
            },
        ],
    )

    identity_text = identity_response.choices[0].message.content

    # Extract sections safely
    gender = extract_between(identity_text, "GENDER:", "\n")
    ethnicity = extract_between(identity_text, "ETHNICITY:", "\n")
    face_desc = extract_between(identity_text, "FACE:", "\n")

    # STEP 2 — Build final prompt with identity locked
    dalle_prompt = (
        f"Photorealistic portrait of the SAME PERSON described below. "
        f"Do NOT change gender, ethnicity or identity.\n\n"
        f"--- LOCKED IDENTITY ---\n"
        f"Gender: {gender}\n"
        f"Ethnicity: {ethnicity}\n"
        f"Facial Identity: {face_desc}\n\n"
        f"--- FUTURE ROLE ---\n"
        f"The person is shown as a future {goal} in India.\n"
        f"Clothing: authentic Indian {goal} professional uniform.\n"
        f"Background: realistic Indian workplace.\n"
        f"Lighting: soft Indian natural lighting.\n"
        f"Ultra-realistic portrait.\n"
    )

    # STEP 3 — Generate final portrait
    img_result = client.images.generate(
        model="gpt-image-1",
        prompt=dalle_prompt,
        size="1024x1024"
    )

    out_b64 = img_result.data[0].b64_json
    return base64.b64decode(out_b64)
