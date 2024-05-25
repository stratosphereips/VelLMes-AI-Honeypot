from dotenv import dotenv_values
import argparse
from datetime import datetime
import yaml
from time import sleep
import random
import subprocess
import time
import socket
import openai


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 54321))


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


def setParameters(identity, model_name, model_temperature, model_max_tokens):
    if model_name == None:
        model_name = identity['model'].strip()

    if model_max_tokens == None:
        model_max_tokens = int(identity['max_tokens'].strip())

    if model_temperature == None:
        model_temperature = float(identity['temperature'].strip())

    return model_name, model_temperature, model_max_tokens


def set_initial_prompt(identity):
    
    prompt = identity['prompt']
    return prompt


def rec():
    response = client.recv(16384)
    output = response.decode()
    print(output)
    return output


if __name__ == "__main__":
    response = client.recv(16384)
    output = response.decode()
    print(output)

    config_path, env_path, model_name, model_temperature, model_max_tokens, output_dir, log_file = read_arguments()

    # Set the API key
    set_key(env_path)

    # Read config file
    with open(config_path, 'r', encoding="utf-8") as file:
        identity = yaml.safe_load(file)
    
    identity = identity['personality']
    if not output_dir:
        output_dir = identity['output'].strip()
    reset_prompt = identity['reset_prompt']
    final_instruction = identity['final_instr']
    protocol = identity['type'].strip()
    log_file = identity['log'].strip()

    model_name, model_temperature, model_max_tokens = setParameters(identity, model_name, model_temperature, model_max_tokens)

    prompt = set_initial_prompt(identity)

    # Give LLM personality or conversation history if it exists.

    personality = prompt + final_instruction

    # Write personality or history to LLM's working memory.
    initial_prompt = f"Your personality is: {personality}"
    messages = [{"role": "system", "content": initial_prompt}]

    message = {"content": output, "role": 'user'}
    messages.append(message)

    finish = 0

    while 1:

        logs = open(output_dir, "a+", encoding="utf-8")

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

            print(message["content"])

            if finish == 1:
                logs.write(messages[len(messages) - 1]["content"])
                logs.write('\n')
                logs.write(message["content"])
                logs.write('\n')
                logs.write("----------------------------------------\n")
                logs.close()
                break

            client.send(message["content"].encode())

            # Write message to working memory
            messages.append(message)

            # Write message in conversation history
            logs.write(messages[len(messages) - 1]["content"])
            logs.write('\n')
            logs.close()

            try:
                output = rec()
                if output == "":
                    raise Exception

            except:
                message = {"content": "Now write the result that is requested of you and if you found some vulnerabilities. " +
                           "Also the system you have been interacting with might have been a real one or it might have been all LLM generated. " + 
                           "At the end you have to also say if you think the system was real or LLM and why you think so.", "role": 'user'}
                messages.append(message)
                finish = 1

            message = {"content": output, "role": 'user'}
            messages.append(message)

        except KeyboardInterrupt:
            # Do not end conversation on ^C. Just print it in the new line and add to working memory.
            messages.append({"role": "user", "content": "^C\n"})
            
            print("")

        except EOFError:
            print("")
            break

        except Exception as e:

            break