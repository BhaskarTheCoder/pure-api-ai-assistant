import os
import json
from openai import OpenAI
from tools import tools
from weather_service import get_weather
from file_service import read_file

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

available_functions = {
    "get_weather": get_weather,
    "read_file": read_file,
}

def run_assistant():
    while True:
        user_input = input("You: ")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_input}],
            tools=tools,
            tool_choice="auto"
        )

        message = response.choices[0].message

        if message.tool_calls:
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                function_to_call = available_functions[function_name]
                function_response = function_to_call(**arguments)

                second_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "user", "content": user_input},
                        message,
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": function_response,
                        },
                    ],
                )

                print("Assistant:", second_response.choices[0].message.content)
        else:
            print("Assistant:", message.content)


if __name__ == "__main__":
    run_assistant()