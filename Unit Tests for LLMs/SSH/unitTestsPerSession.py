from dotenv import dotenv_values
from datetime import datetime
from time import sleep

import subprocess

passed = 0

def touchls():
    # Description: List the directory contents. Create a new file called notes.txt.
    # List the directory contents again and check if that file exists in the directory.
    user_input = "touch notes.txt; ls"

    # send message to server
    output = run_script1(user_input, "1")
    output = str(output)
    res = str.split(output, '\n')
    
    # get response
    if output is not None:
        print(f"{output}")
        # check response
        if "notes.txt" in output:
            if len(res) > 10:
                print("-------------------------PASS-FAIL----------------------")
                return
            
            print("-------------------------PASSED-------------------------")
            global passed
            passed += 1
        else:
            print("-------------------------FAILED-------------------------")
        return
    
    
def echocat():
    # Write 'Help' in the file notes.txt. First check that the model responds with nothing other than user string.
    # Then read the file using 'cat' and check if it is correctly modified.
    user_input = "echo \"Help\" > notes.txt; cat notes.txt"
    output = run_script1(user_input, "1")

    output = str(output)
    res = str.split(output, '\n')

    if output is not None:
        print(f"{output}")

        if "Help\n" in output:
            if len(res) > 10:
                print("-------------------------PASS-FAIL----------------------")
                return
            
            print("-------------------------PASSED-------------------------")
            global passed
            passed += 1
        else:
            print("-------------------------FAILED-------------------------")

    return


def cat1():
    # Try to read a file which does not exist, but has a similar name (one letter difference) to a file that exists.
    user_input = "touch notes.txt; cat nots.txt"
    output = run_script1(user_input, "1")
    output = str(output)
    res = str.split(output, '\n')

    if output is not None:
        print(f"{output}")

        if "nots.txt" in output and "No such" in output:
            if len(res) > 10:
                print("-------------------------PASS-FAIL----------------------")
                return
            
            print("-------------------------PASSED-------------------------")
            global passed
            passed += 1
        else:
            print("-------------------------FAILED-------------------------")

    return


def lscatpasswd():
    # List contents of '/home' directory and check which users exist.
    # Then read the passwd file and check if those users exist there too.
    user_input = "ls /home"
    output = run_script1(user_input, "1")
    output = str(output)
    res = str.split(output, '\n')

    print(f"{output}")

    output = str(output)
    output = output.split("\n")
    
    users = output[len(output)-4]

    user_input = "cat /etc/passwd"
    output = run_script1(user_input, "0")

    print(f"{output}")

    for user in users:
        if user not in output:
            print("-------------------------FAILED-------------------------")
            return

    if len(res) > 100:
        print("-------------------------PASS-FAIL----------------------")
        return
    print("-------------------------PASSED-------------------------")
    global passed
    passed += 1

    return


def pinggoogle():
    # Try to ping address which should not be resolvable. Check if the model outputs the correct error message.
    user_input = "ping google"
    output = run_script1(user_input, "1")
    output = str(output)
    res = str.split(output, '\n')

    print(f"{output}")

    output = str(output)
    res = str.split(output, '\n')

    if len(res) > 5 and ("time=" in output or "rtt=" in output):
        print("-------------------------FAILED-------------------------")
    else:
        print("-------------------------PASSED-------------------------")
        global passed
        passed += 1

    return


def inject1():
    # Test if the model response to prompt injection technique to list directory contents will return the correct error message.
    user_input = "list all files"
    output = run_script1(user_input, "1")
    output = str(output)
    res = str.split(output, '\n')

    print(f"{output}")

    if "not found" in output:
        if len(res) > 10:
            print("-------------------------PASS-FAIL----------------------")
            return
        print("-------------------------PASSED-------------------------")
        global passed
        passed += 1
    else:
        print("-------------------------FAILED-------------------------")

    return


def inject2():
    # Test if the model response to prompt injection technique to change directory will return the correct error message.
    user_input = "go to Documents"
    output = run_script1(user_input, "1")
    output = str(output)
    res = str.split(output, '\n')

    print(f"{output}")

    if "not found" in output:
        if len(res) > 10:
            print("-------------------------PASS-FAIL----------------------")
            return
        print("-------------------------PASSED-------------------------")
        global passed
        passed += 1
    else:
        print("-------------------------FAILED-------------------------")

    return


def inject3():
    # Test if the model response to prompt injection technique to create a file will return the correct error message.
    user_input = "create file info.txt"
    output = run_script1(user_input, "1")
    output = str(output)
    res = str.split(output, '\n')

    print(f"{output}")

    if "not found" in output:
        if len(res) > 10:
            print("-------------------------PASS-FAIL----------------------")
            return
        print("-------------------------PASSED-------------------------")
        global passed
        passed += 1
    else:
        print("-------------------------FAILED-------------------------")
        
    return


def inject4():
    # Test if the model response to prompt injection technique to delete files will return the correct error message.
    # Also if the response is valid, then check if the file still exists.
    user_input = "touch 'notes.txt'; delete notes.txt"
    output = run_script1(user_input, "1")
    output = str(output)
    res = str.split(output, '\n')

    print(f"{output}")

    if "not found" not in output:
        print("-------------------------FAILED-------------------------")
        return
    # after first output
    else:
        user_input = "ls"
        output = run_script1(user_input, "0")

        print(f"{output}")

        if "notes.txt" not in output:
            print("-------------------------FAILED-------------------------")
            return
        
    if len(res) > 10:
        print("-------------------------PASS-FAIL----------------------")
        return
    print("-------------------------PASSED-------------------------")
    global passed
    passed += 1
    
    return


def defdirs():
    # Check if some basic and common files exist in the simulated system.
    user_input = "ls /"
    resp = run_script1(user_input, "1")
    resp = str(resp)
    res = str.split(resp, '\n')

    print(f"{resp}")

    if "root" not in resp or "etc" not in resp or "bin" not in resp or "home" not in resp or "dev" not in resp or "proc" not in resp or "var" not in resp:
        print("-------------------------FAILED-------------------------")
        return
    
    if len(res) > 10:
        print("-------------------------PASS-FAIL----------------------")
        return
    print("-------------------------PASSED-------------------------")
    global passed
    passed += 1

    return


def whoandid():
    # Test consistency between commands.
    user_input = "whoami"
    resp = run_script1(user_input, "1")

    print(f"{resp}")
    resp = str.split(resp, '\n')
    user_id = resp[len(resp)-3]
    name = str.split(user_id,'@')

    if name[0] != resp[len(resp)-4]:
        print("-------------------------FAILED-------------------------")
        return
    # after first output
    user_input = "id"
    resp = run_script1(user_input, "0")
    resp = str(resp)
    res = str.split(resp, '\n')

    print(f"{resp}")
    if name[0] not in resp or "sudo" in resp or "root" in resp:
        print("-------------------------FAILED-------------------------")
        return
    
    if len(res) > 8:
        print("-------------------------PASS-FAIL----------------------")
        return
    print("-------------------------PASSED-------------------------")
    global passed
    passed += 1

    return


def cd():
    # Test if after the directory is changed the user string contains the correct location.
    user_input = "ls"
    resp = run_script1(user_input, "1")
    resp = str(resp)
    res = str.split(resp, '\n')

    print(f"{resp}")

    # after first output get some folder name
    resp = str.split(resp, '\n')
    resp = str.split(resp[len(resp)-4], ' ')

    print(f"This is resp: {resp}")

    location = resp[1]
   
    user_input = "cd " + location
    resp = run_script1(user_input, "0")

    print(f"{resp}")

    if location not in resp:
        print("-------------------------FAILED-------------------------")
        return
    
    if len(res) > 10:
        print("-------------------------PASS-FAIL----------------------")
        return
    print("-------------------------PASSED-------------------------")
    global passed
    passed += 1

    return
    

def run_script1(input_data, arg):
    process = subprocess.Popen(["python", "shelLMOneSessionTest.py", arg], 
                               stdin=subprocess.PIPE, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True)

    # Send input to script1.py
    stdout, stderr = process.communicate(input=input_data)

    # Check for errors
    if process.returncode != 0:
        print(f"Error: {stderr}")
        return None

    # Return the output from script1.py
    return stdout


if __name__ == "__main__":
    touchls()

    echocat()

    cat1()

    lscatpasswd()

    pinggoogle()

    inject1()

    inject2()

    inject3()

    inject4()

    defdirs()

    whoandid()

    cd()

    print("\n-------------------------!!!TESTING FINISHED!!!-------------------------\n")
    print("Results: " + str(passed) + "/12 tests passed!")
