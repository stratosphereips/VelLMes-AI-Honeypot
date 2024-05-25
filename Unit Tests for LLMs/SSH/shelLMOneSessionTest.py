import openai
from dotenv import dotenv_values
import argparse
from datetime import datetime
import yaml
from time import sleep
import random
import os
import tiktoken
import sys

arg = sys.argv[1]

config = dotenv_values(".env")
openai.api_key = config["OPENAI_API_KEY"]
today = datetime.now()

history = open("history.txt", "a+", encoding="utf-8")
token_count = 0
input_price = 0
output_price = 0

if os.stat('history.txt').st_size != 0:
    history.write("\nHere the session stopped. What you see so far is the history of the conversation and you have to continue it, not repeat it. You just " +
                  "write the initial SSH message now, STOP generating output after first location string and wait for the user input. " +
                              "Make sure you use same file and folder names. Ignore date-time in <>. This is not your concern. Never write it in your output. \n")
    history.seek(0)
    prompt = history.read()
    
if arg == "1" or os.stat('history.txt').st_size == 0:
    with open('personalitySSH.yml', 'r', encoding="utf-8") as file:
        identity = yaml.safe_load(file)

    identity = identity['personality']
    prompt = identity['prompt']
    history.truncate(0)

# print(f"The text contains {token_count} tokens.")

def main():
    parser = argparse.ArgumentParser(description = "Simple Linux terminal")
    # Give LLM personality or conversation history if it exists.
    parser.add_argument("--personality", type=str, help="A brief summary of chatbot's personality", 
                        default= prompt +
                        f"\nBased on this example make something of your own (different username and hostname) to be a starting message. Always start the communication in this way and make sure your output ends with '$'. For the last login date use {today}\n" #+ 
                        #"Ignore date-time in <> after user input. This is not your concern.\n")
    )
    parser.add_argument("del_hist", type=str, default=1)
    args = parser.parse_args()

    # Write personality or history to LLM's working memory.
    initial_prompt = f"You are Linux OS terminal. Your personality is: {args.personality}"
    messages = [{"role": "system", "content": initial_prompt}]
    
    # Make sure LLM knows it should continue given conversation and not create all of it on it's own.
    if os.stat('history.txt').st_size == 0:
        for msg in messages:
                    history.write(msg["content"])
    else:
        history.write("The session continues in following lines.\n\n")
    
    history.close()

    run = 1

    global token_count 
    global input_price
    global output_price

    while run == 1:
        
        logs = open("history.txt", "a+", encoding="utf-8")

        # input_price += (token_count/1000) * 0.003
        # print("Input: " + str(input_price) + "$\n")

        # Get model response
        try:
            res = openai.chat.completions.create(
                model = "ft:gpt-3.5-turbo-1106:stratosphere-laboratory::8KS2seKA", #"ft:gpt-3.5-turbo-0613:stratosphere-laboratory::8G6QadzM", #ft:gpt-3.5-turbo-0613:stratosphere-laboratory::8DVYqT1E",
                messages = messages,
                temperature = 0.0,
                max_tokens = 900
            )

            # Get message as dict from response
            msg = res.choices[0].message.content
            message = {"content": msg, "role": 'assistant'}

            # token_temp = len(encoding.encode(message["content"]))/1000
            # token_count += token_temp
            # output_price += token_temp * 0.004

            # print("Output: " + str(output_price) + "$\n")

            if "$cd" in message["content"] or "$ cd" in message["content"]:
                message["content"] = message["content"].split("\n")[1]

            lines = []

            # Write message to working memory
            messages.append(message)

            # Write message in conversation history
            logs.write(messages[len(messages) - 1]["content"])
            logs.close()

            logs = open("history.txt", "a+", encoding="utf-8")
            
            if "will be reported" in messages[len(messages) - 1]["content"] or "logout" in messages[len(messages) - 1]["content"]:
                print(messages[len(messages) - 1]["content"])
                run = 0
                break

            if "PING" in message["content"]:
                lines = message["content"].split("\n")
                print(lines[0])

                for i in range(1, len(lines)-5):
                    print(lines[i])
                    sleep(random.uniform(0.1, 0.5))
                
                for i in range(len(lines)-4, len(lines)-1):
                    print(lines[i])
                
                # Get user input and write it to working memory and to history with current time
                user_input = input(f'{lines[len(lines)-1]}'.strip() + " ")
                messages.append({"role": "user", "content": user_input + f"\t<{datetime.now()}>\n" })
                logs.write(" " + user_input + f"\t<{datetime.now()}>\n")

            else:
                #print("\n", messages[len(messages) - 1]["content"], " ")

                # Get user input and write it to working memory and to history with current time
                print(f'\n{messages[len(messages) - 1]["content"]}'.strip() + " \0")
                user_input = input()
                messages.append({"role": "user", "content": " " + user_input + f"\t<{datetime.now()}>\n"})
                logs.write(" " + user_input + f"\t<{datetime.now()}>\n")
            
        except KeyboardInterrupt:
            # Do not end conversation on ^C. Just print it in the new line and add to working memory.
            messages.append({"role": "user", "content": "^C\n"})
            print("")
            #break
        except EOFError as e:
            print("")
            break

        logs.close()
    # print(res)

if __name__ == "__main__":
    main()
