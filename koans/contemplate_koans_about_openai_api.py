from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()


def test_openai_completion():
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-0613",
        messages=[
            {
                "role": "system",
                "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair.",
            },
            {
                "role": "user",
                "content": "Compose a poem that explains the concept of recursion in programming.",
            },
        ],
        max_tokens=64,
        stop=["\n"],
        temperature=0.0,
        seed=42,
        top_p=1,
        presence_penalty=0,
        frequency_penalty=0,
    )
    assert completion.choices[0].message == ...


test_openai_completion()