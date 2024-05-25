"""
Honeypot tool that uses LLMs to generate realistic
shell environments with high interaction and simulate 
various protocols such as SSH, HTTP, MySQL, POP3... (2023-2024).

Authors:
    - Muris Sladić, Stratosphere Laboratory, AI Center, FEE, CTU in Prague
"""

import argparse
import os
import random
from datetime import datetime
from time import sleep
import yaml
from dotenv import dotenv_values
import tiktoken
import openai

today = datetime.now()

def read_arguments():
    parser = argparse.ArgumentParser(description='Your script description')

    # Mandatory arguments
    parser.add_argument('-e', '--env', required=True, help='Path to environment file (.env)')
    parser.add_argument('-c', '--config', required=True, help='Path to config file (yaml)')

    # Optional arguments
    parser.add_argument('-m', '--model', help='Model name')
    parser.add_argument('-t', '--temperature', type=float, help='Temperature')
    parser.add_argument('-mt', '--max_tokens', type=int, help='Max tokens')
    parser.add_argument('-o', '--output', help='Output directory')
    parser.add_argument('-l', '--log', help='Log file')

    args = parser.parse_args()

    # Access the arguments
    config_path = args.config
    env_path = args.env
    model_name = args.model
    temperature = args.temperature
    max_tokens = args.max_tokens
    output_dir = args.output
    log_file = args.log

    return config_path, env_path, model_name, temperature, max_tokens, output_dir, log_file

def set_key(env_path):
    env = dotenv_values(env_path)
    openai.api_key = env["OPENAI_API_KEY"]


def read_history(identity, output_dir, reset_prompt):
    
    history = open(output_dir, "a+", encoding="utf-8")
    TOKEN_COUNT = 0

    prompt = identity['prompt']
    history.truncate(0)

    history.close()

    return prompt

def setParameters(identity, model_name, model_temperature, model_max_tokens, output_dir, log_file):
    if model_name == None:
        model_name = identity['model'].strip()

    if model_max_tokens == None:
        model_max_tokens = int(identity['max_tokens'].strip())

    if model_temperature == None:
        model_temperature = float(identity['temperature'].strip())

    if output_dir == None:
        output_dir = identity['output'].strip()
    
    if log_file == None:
            log_file = identity['log'].strip()

    return model_name, model_temperature, model_max_tokens, output_dir, log_file

def ping(message, messages, logs):
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


def getUserInput(messages, logs):
    user_input = input(f'\n{messages[len(messages) - 1]["content"]}'.strip() + " ")
    messages.append({"role": "user", "content": " " + user_input + f"\t<{datetime.now()}>\n"})
    logs.write(" " + user_input + f"\t<{datetime.now()}>\n")

    return user_input
    

def getHTTPCommands(message, messages, logs):
    command = 0

    while 1:
        if message["content"] != '':
            user_input = input(f'\n{messages[len(messages) - 1]["content"]}'.strip() + "\n\n")
            messages.append({"role": "user", "content": " " + user_input + f"\n"})

            logs.write(" " + user_input + f"\t<{datetime.now()}>\n")
                   
            message["content"] = ''
            if user_input != "":
                command = 1
        else:
            user_input = input("")
            messages.append({"role": "user", "content": " " + user_input + f"\n"})

            logs.write(" " + user_input + f"\t<{datetime.now()}>\n")

            if user_input != "":
                command = 1
            elif user_input == "" and command == 1:
                break
    return user_input


def main():
    # Read the user's arguments
    config_path, env_path, model_name, model_temperature, model_max_tokens, output_dir, log_file = read_arguments()

    # Set the API key
    set_key(env_path)

    # Read config file
    with open(config_path, 'r', encoding="utf-8") as file:
        identity = yaml.safe_load(file)
    
    identity = identity['personality']
    output_dir = identity['output'].strip()
    reset_prompt = identity['reset_prompt']
    final_instruction = identity['final_instr']
    protocol = identity['type'].strip()
    log_file = identity['log'].strip()

    current_datetime = datetime.now()

    formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

    output_dir = output_dir.replace('.txt', '_' + formatted_datetime + '.txt')

    prompt = read_history(identity, output_dir, reset_prompt)

    model_name, model_temperature, model_max_tokens, output_dir, log_file = setParameters(identity, model_name, model_temperature, model_max_tokens, output_dir, log_file)

    """
    The core of the LLM-shell that loads an initial personality and
    generates the interaction with the user.
    """
    # Give LLM personality or conversation history if it exists.

    personality = prompt + final_instruction + f"\nFor the last login date use {today}\n"

    # Write personality or history to LLM's working memory.
    initial_prompt = f"Your personality is: {personality}"
    messages = [{"role": "system", "content": initial_prompt}]

    history = open(output_dir, "a+", encoding="utf-8")

    if os.stat(output_dir).st_size == 0:
        for msg in messages:
            history.write(msg["content"])
    else:
        history.write("The session continues in following lines.\n\n")

    history.close()

    run = 1

    while run == 1:

        logs = open(output_dir, "a+", encoding="utf-8")

        # Get model response
        try:
            res = openai.chat.completions.create(
                model = model_name,
                messages = messages,
                temperature = model_temperature,
                max_tokens = model_max_tokens
            )

            # Get message as dict from response
            msg = res.choices[0].message.content
            message = {"content": msg, "role": 'assistant'}

            # Write message to working memory
            messages.append(message)

            last = messages[len(messages) - 1]["content"]

            # Write message in conversation history
            logs.write(last)
            logs.close()

            logs = open(output_dir, "a+", encoding="utf-8")

            if "will be reported" in last or "logout" in last and not "_logout" in last:
                print(last)
                run = 0
                break

            if protocol == "POP3" and "Connection closed" in last:
                print(last)
                run = 0
                break

            if protocol == "HTTP" and "Bad Request" in last:
                 print(last + "\n")
                 print("Connection closed by foreign host.")
                 run = 0
                 break

            if protocol == "HTTP" and "Connection closed by foreign host." in last:
                print(last)
                run = 0
                break

            if protocol == "SSH" and "PING" in message["content"]:
                ping(message, messages, logs)

            elif protocol == "HTTP":
                # message = {"content": "", "role": 'assistant'}
                # messages.append(message)
                user_input = getHTTPCommands(message, messages, logs)

            else:
                # Get user input and write it to working memory and to history with current time
                user_input = getUserInput(messages, logs)
                if protocol == "MySQL" and "\\q" == user_input or "exit" == user_input:
                    run = 0

        except KeyboardInterrupt:
            # Do not end conversation on ^C. Just print it in the new line and add to working memory.
            messages.append({"role": "user", "content": "^C\n"})
            
            print("")

        except EOFError:
            print("")
            break

        except Exception as e:
            logfile = open(log_file, "a+", encoding="utf-8")
            logfile.write("\n")
            logfile.write(str(datetime.now()))
            logfile.write("\nError generating response!")
            logfile.write(str(e))
            logfile.close()
            break

        logs.close()

    return

if __name__ == '__main__':
    main()