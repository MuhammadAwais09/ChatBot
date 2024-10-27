
import streamlit as st
from langchain.agents import Tool
import requests
from datetime import datetime, timedelta
import os
from api_request import create_single_schedule, create_multiple_schedule, retreive_test_info
import json
import re


API_O = os.environ.get("OPENAI_API_KEY")
def replace_dates(prompt):
    now = datetime .now()
    formatted_date = now.strftime("%Y-%m-%d")
    if "now" in prompt:
        prompt = prompt.replace("now", formatted_date)
    if "today" in prompt:
        prompt = prompt.replace("today", formatted_date)
    current_utc_time = datetime.utcnow()

    # Add 4 hours to get the current time in GMT+4
    gmt_plus_4_time = current_utc_time + timedelta(hours=4)
    formatted_time = gmt_plus_4_time.strftime("%H:%M")

    return prompt, formatted_time
def extract_curly_braces_content(s):
    # Use re.search to find the first occurrence of content within curly braces
    match = re.search(r'\{.*?\}', s)
    if match:
        # Return the matched content including the braces
        return match.group(0)
    else:
        return s
def get_chat_completion(user_message, content):
    # Define the API endpoint
    url = "https://api.openai.com/v1/chat/completions"

    # Define the headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_O}"
    }

    # Define the data payload
    data = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": content
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    }
    # Send the request
    response = requests.post(url, headers=headers, json=data)
    # Return the JSON response
    return str(response.json()["choices"][0]["message"]["content"]).lower()

def new_chat(prompt):
    """
    Clears session state and starts a new chat.
    """
    save = []
    for i in range(len(st.session_state["generated"]) - 1, -1, -1):
        save.append("User:" + st.session_state["past"][i])
        save.append("Bot:" + st.session_state["generated"][i])
    st.session_state["stored_session"].append(save)
    st.session_state["generated"] = []
    st.session_state["past"] = []
    st.session_state["user_input"] = ""  # Clear user input
    st.session_state["bot_response"] = ""  # Clear bot response

def check_test_status(status_id):
    if status_id:
        try:
            data = json.loads(status_id)
            status_id= int(data["status_id"])
            if "null" in status_id:
                return "status id missing"
            return retreive_test_info(int(status_id))
        except:
            try:
                return retreive_test_info(int(status_id))
            except:
                return "status id missing"
    else :
        return "status id missing"

def speed_test(prompt):
    test_id = 0
    test_name = "speed_test"
    user_id = 446
    content_one_time_test = "you only answer in shematic format,possibile asnwer are YES, NO. YES if in the prompt both the Start_Date , Start_Time, and the Speed_type are present, No if even only one is missing. IF 'null' is in the input , the answer is NO. ACCEPTED ANSWER : YES / NO."
    content_multiple_tests = "you only answer in shematic format,possibile asnwer are YES, NO. YES if in the prompt, all the following Number_of_tests, Start_Date,Start_Time, Speed_type, Frequency , End_date, End_Time are present, No if even only one is missing.IF 'null' is in the input , the answer is NO. THERE CAN BE MORE IN THE PROMPT, YOU DON'T HAVE TO CAARE ABOUT IT. ACCEPTED ANSWER : YES / NO."

    formatted_prompt = extract_curly_braces_content(str(prompt))

    if "One time test" in prompt:
        response = get_chat_completion(prompt, content_one_time_test)
        if "yes" in str(response).lower():
            data = json.loads(formatted_prompt)
            Start_Date = data["Start_Date"]
            time = data["Start_Time"]
            Speed_type = data["Speed_type"]
            if "fast" in str(Speed_type).lower():
                Speed_type = 0
            elif "ookla" in str(Speed_type).lower():
                Speed_type = 1
            result = create_single_schedule(
                type=test_id, user_id=user_id, start=Start_Date, starttime=time, speedtype=Speed_type)
            print(test_id, user_id, Start_Date, time, Speed_type)
            return f"1. report to the user : {result} 2. run the new_chat tool "
        else:
            return "There are some information needed missing, ask directly to the user the informations that are missing. Information needed: Start_Date, Speed_type, Start_Time"

    elif "Periodic test" in prompt:
        response = get_chat_completion(prompt, content_multiple_tests)
        if "yes" in str(response).lower():
            data = json.loads(formatted_prompt)
            Start_Date = data["Start_Date"]
            time = data["Start_Time"]
            Speed_type = data["Speed_type"]
            Number_of_tests = data["Number_of_tests"]
            Frequency = data["Frequency"]
            if "1 Min" in Frequency:
                Frequency = "1 Mins"
            End_date = data["End_date"]
            End_Time = data["End_Time"]
            if "fast" in str(Speed_type).lower():
                Speed_type = 0
            elif "ookla" in str(Speed_type).lower():
                Speed_type = 1

            result = create_multiple_schedule(
                type=test_id, user_id=user_id, start=Start_Date, speedtype=Speed_type,
                numberOfTests=Number_of_tests, frequency=Frequency, end=End_date, endtime=End_Time, starttime=time)
            print(test_id, user_id, Start_Date, time, Speed_type,
                  Number_of_tests, Frequency, End_date, End_Time)
            return f"1. report to the user : {result} 2. run the new_chat tool "
        else:
            return "There are some information needed missing, ask directly to the user the informations that are missing. Information needed: Number_of_tests, Start_Date, Speed_type, Frequency, End_date, End_Time, Start_Time"

    elif "Driving Mode" in prompt:
        response = get_chat_completion(prompt, content_multiple_tests)
        if "yes" in str(response).lower():
            data = json.loads(formatted_prompt)
            Start_Date = data["Start_Date"]
            time = data["Start_Time"]
            Speed_type = data["Speed_type"]
            Number_of_tests = data["Number_of_tests"]
            Frequency = data["Frequency"]
            if "1 Min" in Frequency:
                Frequency = "1 Mins"
            End_date = data["End_date"]
            End_Time = data["End_Time"]
            if "fast" in str(Speed_type).lower():
                Speed_type = 0
            elif "ookla" in str(Speed_type).lower():
                Speed_type = 1

            result = create_multiple_schedule(
                type=test_id, user_id=user_id, start=Start_Date, speedtype=Speed_type,
                numberOfTests=Number_of_tests, frequency=Frequency, end=End_date, endtime=End_Time,
                starttime=time, drivingMode="on")
            print(test_id, user_id, Start_Date, time, Speed_type,
                  Number_of_tests, Frequency, End_date, End_Time)
            return f"1. report to the user : {result} 2. run the new_chat tool "
        else:
            return "There are some information needed missing, ask directly to the user the informations that are missing. Information needed: Number_of_tests, Start_Date, Speed_type, Frequency, End_date, End_Time, Start_Time"

    else:
        return "Seems like the user did not specify the type of test: Possible choices: 1. One time test, 2. Periodic test, 3. Driving Mode "


def video_streaming_Test(prompt):
    test_name = "video_streaming_test"
    test_id = 1
    user_id = 446

    content_one_time_test = "you only answer in shematic format,possibile asnwer are YES, NO. YES if in the prompt the Start_Date and Start_Time are present, No if is missing. IF 'null' is in the input , the answer is NO. ACCEPTED ANSWER : YES / NO."
    content_multiple_tests = "you only answer in shematic format,possibile asnwer are YES, NO. YES if in the prompt, all the following: Start_Time, Number_of_tests, Start_Date, Frequency , End_date, End_Time are present, No if even only one is missing.IF 'null' is in the input , the answer is NO. THERE CAN BE MORE IN THE PROMPT, YOU DON'T HAVE TO CAARE ABOUT IT. ACCEPTED ANSWER : YES / NO."

    formatted_prompt = extract_curly_braces_content(str(prompt))

    if "One time test" in prompt:
        response = get_chat_completion(formatted_prompt, content_one_time_test)
        if "yes" in str(response).lower():
            data = json.loads(formatted_prompt)
            Start_Date = data["Start_Date"]
            time = data["Start_Time"]

            result = create_single_schedule(
                type=test_id, user_id=user_id, start=Start_Date, starttime=time)
            print(result)

            return f"1. report to the user : {result} 2. run the new_chat tool "
        else:
            return "There are some information needed missing, ask directly to the user the informations that are missing. Information needed: Start_Date, Start_Time "

    elif "Periodic test" in prompt:
        response = get_chat_completion(
            formatted_prompt, content_multiple_tests)
        if "yes" in str(response).lower():
            data = json.loads(formatted_prompt)
            Start_Date = data["Start_Date"]
            time = data["Start_Time"]
            Number_of_tests = data["Number_of_tests"]
            Frequency = data["Frequency"]
            if "1 Min" in Frequency:
                Frequency = "1 Mins"
            End_date = data["End_date"]
            End_Time = data["End_Time"]

            result = create_multiple_schedule(
                type=test_id, user_id=user_id, start=Start_Date,
                numberOfTests=Number_of_tests, frequency=Frequency, end=End_date,
                endtime=End_Time, starttime=time)
            print(result)

            return f"1. report to the user : {result} 2. run the new_chat tool "
        else:
            return "There are some information needed missing, ask directly to the user the informations that are missing. Information needed: Number_of_tests, Start_Date, Frequency, End_date, End_Time, Start_Time "

    elif "Driving Mode" in prompt:
        response = get_chat_completion(
            formatted_prompt, content_multiple_tests)
        if "yes" in str(response).lower():
            data = json.loads(formatted_prompt)
            Start_Date = data["Start_Date"]
            time = data["Start_Time"]
            Number_of_tests = data["Number_of_tests"]
            Frequency = data["Frequency"]
            if "1 Min" in Frequency:
                Frequency = "1 Mins"
            End_date = data["End_date"]
            End_Time = data["End_Time"]

            result = create_multiple_schedule(
                type=test_id, user_id=user_id, start=Start_Date,
                numberOfTests=Number_of_tests, frequency=Frequency, end=End_date,
                endtime=End_Time, starttime=time, drivingMode="on")
            print(result)

            return f"1. report to the user : {result} 2. run the new_chat tool "
        else:
            return "There are some information needed missing, ask directly to the user the informations that are missing. Information needed: Number_of_tests, Start_Date, Frequency, End_date, End_Time, Start_Time "
    else:
        return "Seems like the user did not specify the type of test: Possible choices: 1. One time test, 2. Periodic test, 3. Driving Mode "


def ping_test(prompt):
    test_name = "ping_test"
    test_id = 2
    user_id = 446
    content_one_time_test = "you only answer in schematic format, possible answers are YES, NO. YES if in the prompt all the following: Start_Time, host_or_ip, ping_count, Start_Date, are present. NO if even one is missing. If 'null' is in the input, the answer is NO. ACCEPTED ANSWER: YES / NO."
    content_multiple_tests = "you only answer in schematic format, possible answers are YES, NO. YES if in the prompt all the following: Start_Time, host_or_ip, ping_count, Number_of_tests, Start_Date, Frequency, End_date, End_Time, are present. NO if even one is missing. If 'null' is in the input, the answer is NO. THERE CAN BE MORE IN THE PROMPT, YOU DON'T HAVE TO CARE ABOUT IT. ACCEPTED ANSWER: YES / NO."

    formatted_prompt = extract_curly_braces_content(str(prompt))

    if "One time test" in prompt:
        response = get_chat_completion(prompt, content_one_time_test)
        if "yes" in str(response).lower():
            data = json.loads(formatted_prompt)
            Start_Date = data["Start_Date"]
            time = data["Start_Time"]
            host_or_ip = data["host_or_ip"]
            ping_count = data["ping_count"]

            result = create_single_schedule(
                type=test_id, user_id=user_id, start=Start_Date,
                starttime=time, pingHost=host_or_ip, pingCount=ping_count
            )
            print(result)
            return f"1. report to the user: {result} 2. run the new_chat tool"
        else:
            return "There are some information needed missing, ask directly to the user the informations that are missing. Information needed: Start_Date, host_or_ip, ping_count, Start_Time"

    elif "Periodic test" in prompt:
        response = get_chat_completion(prompt, content_multiple_tests)
        if "yes" in str(response).lower():
            data = json.loads(formatted_prompt)
            Start_Date = data["Start_Date"]
            time = data["Start_Time"]
            Number_of_tests = data["Number_of_tests"]
            Frequency = data["Frequency"]
            if "1 Min" in Frequency:
                Frequency = "1 Mins"
            End_date = data["End_date"]
            End_Time = data["End_Time"]
            host_or_ip = data["host_or_ip"]
            ping_count = data["ping_count"]

            result = create_multiple_schedule(
                type=test_id, user_id=user_id, start=Start_Date, numberOfTests=Number_of_tests,
                frequency=Frequency, end=End_date, endtime=End_Time,
                starttime=time, pingHost=host_or_ip, pingCount=ping_count
            )
            print(result)
            return f"1. report to the user: {result} 2. run the new_chat tool"
        else:
            return "There are some information needed missing, ask directly to the user the informations that are missing. Information needed: Number_of_tests, Start_Date, host_or_ip, ping_count, Frequency, End_date, End_Time, Start_Time"

    elif "Driving Mode" in prompt:
        response = get_chat_completion(prompt, content_multiple_tests)
        if "yes" in str(response).lower():
            data = json.loads(formatted_prompt)
            Start_Date = data["Start_Date"]
            time = data["Start_Time"]
            Number_of_tests = data["Number_of_tests"]
            Frequency = data["Frequency"]
            if "1 Min" in Frequency:
                Frequency = "1 Mins"
            End_date = data["End_date"]
            End_Time = data["End_Time"]
            host_or_ip = data["host_or_ip"]
            ping_count = data["ping_count"]

            result = create_multiple_schedule(
                type=test_id, user_id=user_id, start=Start_Date, numberOfTests=Number_of_tests,
                frequency=Frequency, end=End_date, endtime=End_Time,
                starttime=time, pingHost=host_or_ip, pingCount=ping_count, drivingMode="on"
            )
            print(result)
            return f"1. report to the user: {result} 2. run the new_chat tool"
        else:
            return "There are some information needed missing, ask directly to the user the informations that are missing. Information needed: Number_of_tests, Start_Date, host_or_ip, ping_count, Frequency, End_date, End_Time, Start_Time"

    else:
        return "Seems like the user did not specify the type of test: Possible choices: 1. One time test, 2. Periodic test, 3. Driving Mode"



tools = [

    Tool(
        name="video_streaming_Test",
        func=lambda prompt: video_streaming_Test(prompt),
        description=f"""Use when the user wants to do a video_streaming_Test, 
                        start the tool IF AND ONLY IF  you have ALL the information needed.(""
                        There are three options for this test,  ask DIRECTLLY the user which one of the following test options they want to perform, don't try to guess it.
                        1: One time test. Information Needed : (Start_Time: str[%H:%M] Start_Date : str[%Y-%m-%d])
                        2: Periodic test. Information Needed : (Number_of_tests : int, Start_Date : str[%Y-%m-%d], Start_Time: str[%H:%M], End_date: str[%Y-%m-%d], End_Time: str[%H:%M], Frequency: str:[options: 5 Mins/10 Mins/15 Mins/30 Mins/1 Hour].)
                        3: Driving Mode. Information Needed : (Number_of_tests : int, Start_Date : str[%Y-%m-%d], Start_Time: str[%H:%M], End_date: str[%Y-%m-%d], End_Time: str[%H:%M], Frequency: str:[options: 30 Secs/1 Mins/2 Mins/5 Mins/10 Mins/15 Mins/30 Mins/1 Hour].)
                        So first of all you have to understand which tetst does the user wants to do.ask DIRECTLLY the user which test options they want to perform, don't try to guess it. Then you have to find the informaton needed for that test.Users alway forget something, if you are missing some info, just pass none. NEVER CREATE INPUT IF NOT WRITTEN BY THE USER. IN THE INPUT PASS THE INFORMATION IN JSON FORMAT. IN THE INPUR PASS THE SPECIFIED TET TYPE, ask if missing test_type:(One time test/Periodic test/Driving Mode)"""
    ),
    Tool(
        name="ping_test",
        func=lambda prompt: ping_test(prompt),
        description=f"""Use when the user wants to do a ping_test, 
                        start the tool IF AND ONLY IF  you have ALL the information needed.
                        There are three options for this test,  ask DIRECTLLY the user which one of the following test options they want to perform, don't try to guess it.
                        1: One time test. Information Needed : (Start_Date : str[%Y-%m-%d], Start_Time: str[%H:%M], host_or_ip: str/int, ping_count: int[predefined: 5])
                        2: Periodic test. Information Needed : (Number_of_tests : int, Start_Date : str[%Y-%m-%d], Start_Time: str[%H:%M], End_date: str[%Y-%m-%d], End_Time: str[%H:%M], host_or_ip: str/int, ping_count: int[predefined: 5], Frequency: str:[options: 5 Mins/10 Mins/15 Mins/30 Mins/1 Hour].)
                        3: Driving Mode. Information Needed : (Number_of_tests : int, Start_Date : str[%Y-%m-%d], Start_Time: str[%H:%M], End_date: str[%Y-%m-%d], End_Time: str[%H:%M], host_or_ip: str/int, ping_count: int[predefined: 5], Frequency: str:[options: 30 Secs/1 Mins/2 Mins/5 Mins/10 Mins/15 Mins/30 Mins/1 Hour].)
                        So first of all you have to understand which tetst does the user wants to do. ask DIRECTLLY the user which test options they want to perform, don't try to guess it. Then you have to find the informaton needed for that test.Users alway forget something, if you are missing some info, just pass none. NEVER CREATE INPUT IF NOT WRITTEN BY THE USER. IN THE INPUT PASS THE INFORMATION IN JSON FORMAT. IN THE INPUR PASS THE SPECIFIED TET TYPE, ask if missing test_type:(One time test/Periodic test/Driving Mode)"""
    ),
    Tool(
        name="speed_test",
        # KIPS: TODO
        func=lambda prompt: speed_test(prompt),
        description=f"""Use when the user wants to do a speed_test, 
                        start the tool IF AND ONLY IF  you have ALL the information needed.
                        There are three options for this test,  ask DIRECTLLY the user which one of the following test options they want to perform, don't try to guess it.
                        1: One time test. Information Needed : (Start_Date : str[%Y-%m-%d], Start_Time: str[%H:%M], Speed_type: str[ Fast/Ookla (ALWAYS ASK- ask DIRECTLLY the user which one of the Speed_type test options they want to perform)])
                        2: Periodic test. Information Needed : (Number_of_tests : int, Start_Date : str[%Y-%m-%d], Start_Time: str[%H:%M], End_date: str[%Y-%m-%d], End_Time: str[%H:%M], Speed_type: str[ Fast/Ookla (ALWAYS ASK- ask DIRECTLLY the user which one of the Speed_type test options they want to perform)], Frequency: str:[options: 5 Mins/10 Mins/15 Mins/30 Mins/1 Hour].)
                        3: Driving Mode. Information Needed : (Number_of_tests : int, Start_Date : str[%Y-%m-%d], Start_Time: str[%H:%M], End_date: str[%Y-%m-%d], End_Time: str[%H:%M], Speed_type: str[ Fast/Ookla (ALWAYS ASK- ask DIRECTLLY the user which one of the Speed_type test options they want to perform)], Frequency: str:[options: 30 Secs/1 Mins/2 Mins/5 Mins/10 Mins/15 Mins/30 Mins/1 Hour].)
                        So first of all you have to understand which tetst does the user wants to do. ask DIRECTLLY the user which test options they want to perform, don't try to guess it. Then you have to find the informaton needed for that test.Users alway forget something, if you are missing some info, just pass none. NEVER CREATE INPUT IF NOT WRITTEN BY THE USER. IN THE INPUT PASS THE INFORMATION IN JSON FORMAT. IN THE INPUR PASS THE SPECIFIED TET TYPE, ask if missing test_type:(One time test/Periodic test/Driving Mode)"""
    ),
    Tool(
        name="new_chat",
        func=lambda prompt: new_chat(prompt),
        description="use this tool always when the agent made to finish a succesfull action, when the chain is finished ,or when the kpi_information are provided , this tool is used to clear the chat and to create a new one. Use when the agent decides to use the new_chat tool. promt_input/Action Input: delete"
    ),

    Tool(
        name="check_test_status",
        func=lambda status_id: check_test_status(status_id),
        description="""use this tool when the user wants to know about the satus of one of its test.
                        Information required: (status_id : int). 
                        IF NOT PROVIDED, INPUT= null"""

    )
]
