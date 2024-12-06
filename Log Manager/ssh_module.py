import paramiko
import mysql.connector
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os


# Load environment variables from .env file
load_dotenv('db_credentials.env')

MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_HOST = os.getenv('MYSQL_HOST')


def parse_last_output(last_output):
    sessions = []
    
    # Process the output line by line
    for line in last_output.splitlines():
        # Skip empty lines or irrelevant lines
        if not line.strip() or line.startswith("wtmp") or "reboot" in line:
            continue
        
        parts = line.split()  # Split the line into words
        
        # Extract details based on fixed column positions
        username = parts[0]
        terminal = parts[1]
        src_ip = parts[2] if parts[2] != ":0" else "127.0.0.1"  # Default to localhost for local logins
        time_date_start = " ".join(parts[3:8])  # Combine the time and date parts

        # Convert time strings to MySQL-compatible format
        time_date_start = datetime.strptime(time_date_start, "%a %b %d %H:%M:%S %Y").strftime("%Y-%m-%d %H:%M:%S")
    
        # Destination IP (your server IP or localhost for testing)
        dst_ip = "olympus.felk.cvut.cz"
        dst_port = 1337

        # Append parsed data as a tuple
        sessions.append((username, time_date_start, src_ip, dst_ip, dst_port))

    return sessions


def connect_to_db():
    # Connect to the MySQL server
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database='shellm_sessions'
    )
    cursor = conn.cursor()

    return conn, cursor


# Function to insert data into MySQL
def insert_into_ssh_session(data):
    conn, cursor = connect_to_db()

    # Insert data into ssh_session table
    for session in data:
        cursor.execute("""
            INSERT INTO ssh_session (username, time_date, src_ip, dst_ip, dst_port)
            VALUES (%s, %s, %s, %s, %s)
        """, session)
    
    # Commit and close
    conn.commit()
    cursor.close()
    conn.close()


# Function to insert data into MySQL
def insert_into_attacker_session(data):
    conn, cursor = connect_to_db()

    # Insert data into ssh_session table
    for session in data:
        src_ip = session[2]
        cursor.execute("""
            INSERT INTO attacker_session (src_ip)
            VALUES (%s)
        """, (src_ip,))
    
    # Commit and close
    conn.commit()
    cursor.close()
    conn.close()


# Function to count how many new connections were to ssh since last database entry
def count_newest(data):
    conn, cursor = connect_to_db()

    cursor.execute("""
                    SELECT time_date FROM ssh_session ORDER BY id DESC LIMIT 1;
                """)
    
    latest_entry = cursor.fetchone()

    if latest_entry:
        time_date = latest_entry[0]

        # Check if it's a datetime object or a string 
        if isinstance(time_date, datetime):
            # If it's a datetime object, format it as a string
            time_date_str = time_date.strftime(f"%Y-%m-%d %H:%M:%S")
        else:
            # If it's already a string, use it directly
            time_date_str = str(time_date)
    
    counter = 0

    # Go through ssh logs and stop when old entries are reached
    for session in data:
        if session[1] <= time_date_str: # time_date_str - the specific date is only for testing
            break
        else:
            counter += 1

    # Commit and close
    conn.commit()
    cursor.close()
    conn.close()
    
    return counter


def create_filenames(data):
    filenames = []

    for session in data:
        # Extract the time_date value from the session tuple
        time_date = session[1]  # Assuming time_date is the second element in the tuple
        
        # Convert the time_date to a string if it's not already
        if isinstance(time_date, datetime):
            time_date = time_date + timedelta(seconds=1)
            time_date_str = time_date.strftime(f"%Y-%m-%d_%H-%M-%S")
        else:
            time_date_str = str(time_date).replace(" ", "_").replace(":", "-")

        # Create the filename using the formatted time_date
        filename = f"historySSH_{time_date_str}.txt"
        filenames.append(filename)

    return filenames
        

def get_latest_sessions_ids(counter):
    ids = []
    
    conn, cursor = connect_to_db()
    cursor.execute("""
                    SELECT id FROM ssh_session ORDER BY id DESC LIMIT %s;
                """,(counter,))
    ids = [row[0] for row in cursor.fetchall()]

    return ids


def get_latest_attackers_ids(counter):
    ids = []
    
    conn, cursor = connect_to_db()
    cursor.execute("""
                    SELECT attacker_session_id FROM attacker_session ORDER BY attacker_session_id DESC LIMIT %s;
                """,(counter,))
    ids = [row[0] for row in cursor.fetchall()]

    return ids


def parse_historylog(filename, ssh):
    stdin, stdout, stderr = ssh.exec_command(f"cat /path/to/specific/historylog/{filename}")
    conversation = stdout.read().decode('utf-8')
    conversation_error = stderr.read().decode('utf-8')

    commands = []
    answers = []
    timestamps = []
    start = ""

    lines = conversation.splitlines()

    previous_line = None
    output = None

    for line in lines:

        if "For the last login date use" in line:
            line_parts = line.split()
            start = line_parts[-2] + " " + line_parts[-1]

        # Check if the line contains a command
        if line.strip().endswith('>'):  # Command line ends with '>'

            # First make sure if there is a multiline output to put it to answers
            if output is not None:
                answers.append(output)
                output = None

            split_line = line.split()

            command = split_line[1:-2]
            command = ' '.join(command)

            if previous_line is not None and ":~" in previous_line:
                output = split_line[0]
                answers.append(output)
                output = None
            
            # print(line)
            # print(command)

            # For the exit command just put ""
            if command == "exit":
                answers.append("")

            # Extract timestamp from the command line
            try:
                timestamp = split_line[-2] + split_line[-1]
                timestamps.append(timestamp)
            except (IndexError, ValueError):
                pass  # Ignore lines without valid timestamps

            commands.append(command)

            previous_line = line

        else:
            # Collect lines of output for the current command
            if previous_line is not None:
                if ":~" in previous_line:
                    output = line.strip()
                    previous_line = line
                else:
                    output = output + "\n" + line.strip()
                    previous_line = line

    # Determine start and end times
    timestamps = [timestamps[0], timestamps[-1]]
    start_time = start if start else timestamps[0] if timestamps else None
    end_time = timestamps[1] if timestamps else None

    # print(timestamps)
    # print(commands)
    # print(answers)

    return commands, answers, start_time, end_time


def insert_into_commands_and_answers(commands, shellm_session_id, answers):
    conn, cursor = connect_to_db()

    try:
        # Ensure we have a matching number of commands and answers
        if len(commands) != len(answers):
            raise ValueError("The number of commands and answers must be equal.")
        
        answer_counter = 0

        # Insert each command and its corresponding answer
        for command in commands:
            # Insert command into 'commands' table
            cursor.execute("""
            INSERT INTO commands (shellm_session_id, command)
            VALUES (%s, %s)
            """, (shellm_session_id, command))
            
            # Fetch the last inserted 'command_id'
            cursor.execute("""
            SELECT LAST_INSERT_ID();
            """)
            command_id = cursor.fetchone()[0]  # Extract the value from the tuple
            
            # Insert answer into 'answers' table
            cursor.execute("""
            INSERT INTO answers (command_id, answer)
            VALUES (%s, %s)
            """, (command_id, answers[answer_counter]))
            
            answer_counter += 1

        # Commit the transaction
        conn.commit()

    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()  # Rollback in case of error

    finally:
        # Clean up resources
        cursor.close()
        conn.close()


def insert_into_shellm_session(start_time, end_time, latest_session_ids, latest_attacker_ids):
    conn, cursor = connect_to_db()

    ssh_session_id = latest_session_ids[0]
    latest_attacker_id = latest_attacker_ids[0]
    
    cursor.execute("""
        INSERT INTO shellm_session (ssh_session_id, model, start_time, end_time, attacker_id)
        VALUES (%s, %s, %s, %s, %s)
            """, (ssh_session_id, "FT GPT-3.5-16k", start_time, end_time, latest_attacker_id))

    conn.commit()
    cursor.close()
    conn.close()


def get_latest_shellm_session():

    conn, cursor = connect_to_db()

    cursor.execute("""
                    SELECT id FROM shellm_session ORDER BY id DESC LIMIT 1;
                """)
    
    shellm_session_id = cursor.fetchone()

    # Commit and close
    conn.commit()
    cursor.close()
    conn.close()

    return shellm_session_id


def format_datetime_for_db(raw_time):
    # Step 1: Remove angle brackets
    cleaned_time = raw_time.strip('<>')

    # Step 2: Insert a space between the date and time
    formatted_time = cleaned_time[:10] + ' ' + cleaned_time[10:]

    # Step 3: Convert to datetime object (validates the format)
    datetime_obj = datetime.strptime(formatted_time, f"%Y-%m-%d %H:%M:%S.%f")

    # Step 4: Format to MySQL-compatible DATETIME string
    return datetime_obj.strftime(f"%Y-%m-%d %H:%M:%S")


def get_logs_from_server():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Load your private key to log in to remote server with logs
    private_key = paramiko.RSAKey.from_private_key_file('\\pathtoprivatekey\\id_rsa')

    # Connect to the SSH server using key-based authentication
    ssh.connect(hostname="hostname.com", port="<portnumber>", username="user", pkey=private_key)

    # Execute commands as before
    stdin, stdout, stderr = ssh.exec_command("docker exec container_id last -F")
    error_output = stderr.read().decode('utf-8')
    docker_history = stdout.read().decode('utf-8')

    ssh_data = parse_last_output(docker_history)
    counter = count_newest(ssh_data)
    ssh_data = ssh_data[:counter][::-1]

    stdin, stdout, stderr = ssh.exec_command(f"ls /path/to/directory/of/logs")
    shellm_histories = stdout.read().decode('utf-8')
    error_getting_histories = stderr.read().decode('utf-8')

    # Get just the last <count> created histories. Ignore earlier. This is to know exact file names of history logs.
    shellm_histories = shellm_histories.split()
    shellm_histories = shellm_histories[-counter:][::1]
    # print(shellm_histories)
    
    if counter > 0:
        if docker_history:
            insert_into_ssh_session(ssh_data)
            insert_into_attacker_session(ssh_data)
        else:
            print(error_output)

        # filenames = create_filenames(ssh_data)
        # print(filenames)

        # Get ids of the latest created session. They are FKs in shellm_session table. Invert them to get them in right order.
        latest_sessions_ids = get_latest_sessions_ids(counter)
        latest_sessions_ids = latest_sessions_ids[:][::-1]
        latest_attacker_ids = get_latest_attackers_ids(counter)
        latest_attacker_ids = latest_attacker_ids[:][::-1]
        # print(latest_sessions_ids)

        for filename in shellm_histories:
            commands, answers, start_time, end_time = parse_historylog(filename, ssh)

            start_time = format_datetime_for_db(start_time)
            end_time = format_datetime_for_db(end_time)

            insert_into_shellm_session(start_time, end_time, latest_sessions_ids, latest_attacker_ids)

            shellm_session_id = get_latest_shellm_session()
            # print(shellm_session_id)

            insert_into_commands_and_answers(commands, shellm_session_id[0], answers)

            # Pop the processed ssh_session
            latest_sessions_ids = latest_sessions_ids[1:]
            latest_attacker_ids = latest_attacker_ids[1:]


        # log_file_content = stdout.read().decode()

    ssh.close()

    return docker_history#, log_file_content

if __name__ == "__main__":
    get_logs_from_server()