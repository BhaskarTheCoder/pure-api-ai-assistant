from llm import interpret_user_intent
from weather_service import get_weather
from file_service import read_file
from db_service import query_database

def main():
    while True:
        user_input = input("You: ")

        intent = interpret_user_intent(user_input)

        if intent == "weather":
            print(get_weather("Houston"))

        elif intent == "file":
            print(read_file("readme.md"))

        elif intent == "database":
            print(query_database("select * from segment_test"))

        else:
            print("I don't understand.")

if __name__ == "__main__":
    main()