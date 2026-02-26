import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def interpret_user_intent(user_input):
    prompt = f"""
    Classify the user's request into one of:
    - weather
    - file
    - database

    User request: {user_input}
    Only return one word.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip().lower()