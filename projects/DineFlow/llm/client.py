# DineFlow/llm/client.py
from openai import OpenAI
from config.settings import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def call_llm(system_prompt: str, user_input: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        response_format={"type": "json_object"},  # HARD GUARANTEE
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )
    print("llm------- response", response.choices[0].message.content)
    return response.choices[0].message.content
