# VelLMes-AI-Honeypot

The `VelLMes` read as (Vel-L-M-es, from Slavic deity Veles and LLMs) creates interactive, dynamic, and realistic honeypots through the use of Large Language Models (LLMs). The `VelLMes` tool was created from a research project to show the effectiveness of dynamic fake file systems and command responses to keep attackers trapped longer, thus increasing the intelligence collected.

The `VelLMes` can simulate services such as SSH Linux shell (`shelLM`), MySQL, POP3, and HTTP.

This repository also includes the `Attacker LLM` that can interact with Linux shells, search for vulnerabilities, and report on its findings.

The newest addition is the Web Dashboard which displays all the connections to the shelLM honeypot. Furthermore, it provides a view of specific sessions by displaying all the issued commands and shelLM responses by clicking on an ID of a specific session.

## Features

`VelLMes` was developed in Python and currently uses Open AI GPT models. Among its key features are:

1. The content from a previous session can be carried over to a new session to ensure consistency.
2. It uses a combination of techniques for prompt engineering, including chain-of-thought.
3. Uses prompts with precise instructions to address common LLM problems.
4. More creative file and directory names for Linux shells
5. In the Linux shell the users can "move" through folders
6. Response is correct also for non-commands for all services
7. It can simulate databases and their relations in the MySQL honeypot.
8. It can create emails with all the necessary header info in the POP3 honeypots.
9. It can respond to HTTP GET requests 

## Installation

The installation steps are as follows:

```bash
~$ # Install requirements
~$ pip install -r requirements.txt
~$
~$ # Create env file
~$ cp env_TEMPLATE .env
~$ # Edit env file to add OPEN AI API KEY
~$ vim .env
```

## Usage

The `VelLMes` can be run with the following command:
```
~$ python3 VelLMes.py -e [location of .env file] -c [location of the configuration file] 
```

The configuration file should be in a .yml format and should contain the personality prompt and parameters such as max_number_of_tokens, temperature, locations of output and log files, and LLM to be used.
Configuration files for LLM are provided in this repository.

The parameters can be adjusted manually by passing them as arguments when the program is run. Flags are: -t (temperature), -m (LLM), -mt (max_tokens), -o (output_file), -l (log_file).

Another example of how the `VelLMes` can be run:
```
~$ python3 VelLMes.py -e .env -c configSSH.yml -m "gpt-4" -mt 800 -t 0.2 -o "conversation.txt" -l "logs.txt"
```

To use the web dashboard it is necessary to deploy the log_manager.py which acts as a server that communicates with database. The database is filled based on the information received from the server where the shelLM is deployed. 

The information about the database, as well as the server where shelLM is deployed needs to be put in the ssh_module.py at the marked places.

To have the most recent information from shelLM session it is advised to run the ssh_module.py as a cronjob that checks every minute or less if some new shelLM sessions were established and to update the DB accordingly.

The web dashboard needs to be hosted as well. It is communicating with log_manager.py to get the latest information from the DB and display it.

# About

This tool was developed at the Stratosphere Laboratory at the Czech Technical University in Prague.
