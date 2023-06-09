import credentials
import pytextnow
import json
import time

client = pytextnow.Client(username=credentials.get_username(), sid_cookie=credentials.get_sid(),
                          csrf_cookie=credentials.get_csrf())


def ask(number, question, timeout=60, default="", advanced=False):

    timer_timeout = time.perf_counter()
    client.send_sms(number, question)

    while time.perf_counter() - timer_timeout <= timeout:

        time.sleep(1)
        new_messages = client.get_unread_messages()

        for message in new_messages:
            if message.number == message.number:

                message.mark_as_read()
                if advanced:
                    return message
                else:
                    return message.content

    # timeout error messages

    time.sleep(1)
    if default != "":

        client.send_sms(number, f'ERROR:TIMEOUT. User took too long to respond. Default response: {default}.')

    else:

        client.send_sms(number, "ERROR:TIMEOUT. User took too long to respond. Please use command again to retry.")

    return default


def send_group_sms(content, from_,  except_=""):

    with open("SERVER.json", 'r') as f:

        try:

            list1 = json.loads(f.read())

        except json.decoder.JSONDecodeError:

            # if there is corruption in file
            list1 = {"ChatNumbers": {}}

        for number in list1["ChatNumbers"].keys():

            if number != except_:

                if from_ != "sys":
                    try:
                        client.send_sms(number, f"{list1['ChatNumbers'][from_]}: {content}")
                    except KeyError:
                        client.send_sms(number, f"sys: An unauthorized number registered in the group seems to have sent a message: '{from_}: {content}'")
                        print(f"sys: An unauthorized number registered in the group seems to have sent a message: '{from_}: {content}'")
                else:
                    client.send_sms(number, f"System: {content}")

            time.sleep(2)


def is_in_chat(number):

    with open("SERVER.json", 'r') as f:

        try:

            list1 = json.loads(f.read())

        except json.decoder.JSONDecodeError:

            # if there is corruption in file
            list1 = {"ChatNumbers": {}}

        if number in list1["ChatNumbers"].keys():  # if number exists already

            return True

        else:

            return False


def add(content, name):

    with open("SERVER.json", 'r') as f:

        try:

            list1 = json.loads(f.read())

        except json.decoder.JSONDecodeError:

            # if there is corruption in file
            list1 = {"ChatNumbers": {}}

        if content in list1["ChatNumbers"].keys():  # if number exists already

            return False

    with open("SERVER.json", 'w') as f:

        # write the data to file
        list1["ChatNumbers"][content] = name
        f.write(json.dumps(list1))

        return True


# see if file is created yet
with open("SERVER.json", 'r') as f:
    try:
        list1 = json.loads(f.read())

    except json.decoder.JSONDecodeError:

        # if there is corruption in file, reset json
        list1 = {"ChatNumbers": {}}
        with open("SERVER.json", 'w') as f:
            f.write(json.dumps(list1))


send_group_sms("The server is now online.", from_="sys")
print('Notified users.')


@client.on("message")
def handler(msg):
    if msg.type == pytextnow.MESSAGE_TYPE:
        # on command
        if msg.content[0] == "!":

            if msg.content == "!add":

                # do user addition procedure
                name = ask(msg.number, "What is your name?", default=msg.number)

                if add(str(msg.number), name):

                    msg.send_sms("You have been added!")
                    send_group_sms(f"'{name}' has been added to the group!", from_="SYSTEM", except_=msg.number)

                else:

                    msg.send_sms("Bruh you are already in this chat.")

        elif is_in_chat(msg.number):

            send_group_sms(msg.content, from_=msg.number, except_=msg.number)
            print(f"{msg.number}: {msg.content}")