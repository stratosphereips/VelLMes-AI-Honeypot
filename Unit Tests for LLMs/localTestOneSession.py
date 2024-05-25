import openai
from dotenv import dotenv_values
import argparse
from datetime import datetime
import yaml
from time import sleep
import random
import os
import tiktoken
import socket
from litellm import completion

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 12345))
server.listen()

connection, address = server.accept()

config = dotenv_values("../.env")
openai.api_key = config["OPENAI_API_KEY"]
today = datetime.now()

history = open("history.txt", "a+", encoding="utf-8")
token_count = 0
input_price = 0
output_price = 0

# Check if history is empty. If yes, load personality as initial prompt.
# If not load conversation history as initial prompt.
if os.stat('history.txt').st_size != 0:
    history.write("\nHere the session stopped. What you see so far is the history of the conversation and you have to continue it, not repeat it. You just " +
                  "write the initial SSH message now, STOP generating output after first location string and wait for the user input. " +
                              "Make sure you use same file and folder names. Ignore date-time in <>. This is not your concern. Never write it in your output. \n")
    history.seek(0)
    prompt = history.read()

    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    token_count = len(encoding.encode(prompt))
    
if token_count > 15500 or os.stat('history.txt').st_size == 0:
    with open('personalitySSH.yml', 'r', encoding="utf-8") as file:
        identity = yaml.safe_load(file)

    identity = identity['personality']
    prompt = identity['prompt']
    history.truncate(0)

def main():
    parser = argparse.ArgumentParser(description = "Simple command line with GPT-3.5-turbo")
    # Give LLM personality or conversation history if it exists.
    parser.add_argument("--personality", type=str, help="A brief summary of chatbot's personality", 
                        default= prompt +
                        f"\nBased on this example make something of your own (different username and hostname) to be a starting message. Always start the communication in this way and make sure your output ends with '$'. For the last login date use {today}\n" #+ 
                        #"Ignore date-time in <> after user input. This is not your concern.\n")
    )
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

        # Get model response
        try:
            res = completion(
                model="ollama/llama2",                 
                messages = messages,
                api_base="http://localhost:11434"
            )

            # Get message as dict from response
            msg = res.choices[0].message.content
            message = {"content": msg, "role": 'assistant'}

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
                
                connection.send((f'\n{messages[len(messages) - 1]["content"]}'.strip() + " ").encode())
                data = connection.recv(1024)
                # Get user input and write it to working memory and to history with current time
                user_input = data.decode()
                messages.append({"role": "user", "content": user_input + f"\t<{datetime.now()}>\n" })
                logs.write(" " + user_input + f"\t<{datetime.now()}>\n")

            else:
                connection.send((f'\n{messages[len(messages) - 1]["content"]}'.strip() + " ").encode())
                data = connection.recv(1024)        

                # Get user input and write it to working memory and to history with current time
                user_input = str(data.decode())
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
