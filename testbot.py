import socket
from time import sleep

def ping(data):
    irc.send( "PONG " + data.split() [ 1 ] + "\r\n" )

def argument(data):
    arg = ""
    for i in data.split(":")[2].split()[1:]:
        arg += i

    return(arg) 


def send(data, message):
    """
    sends message to channel or user depending on where it is from
    """
    sender = data.split("!")[0].strip(":")
    destination = data.split()[2]

    if destination[0] == "#":
        irc.send( "PRIVMSG " + destination + " :" + message + "\r\n")

    else:
        irc.send( "PRIVMSG " + sender + " :" + message + "\r\n")


def hello(data):
    sender = data.split("!")[0].strip(":")
    answer = "Hello " + sender + "!"
    send(data, answer)


def arithmetic(data):
    
    expression = argument(data)
    condition = "0123456789+-/*.()"
    newexpression = ""
    for i in expression:
        if i in condition:
            newexpression += str(i)

    if ("**" in newexpression):
        answer = "You tried to use a power. Unfortunately I do not have that functionnality at the moment."
    if (len(newexpression) > 15):
        answer = "Your expression was too long. I only accept expressions up to 15 characters long."

    else:

        try:
            answer = eval("1.0 * " + newexpression)
        except ZeroDivisionError:
            answer = "Error! You tried to divide by zero"
        except SyntaxError:
            answer = "Error! Invalid input"

    send(data, "The answer to " + expression + " is: " + str(answer))


def join_channel(data):
    message = data.split(":")[2]
    channel_name = message.split()[1]
    if channel_name in channels:
        send(data, "I am already in " + channel_name)
    else:
        irc.send("JOIN " + channel_name + "\r\n")
        send(data, "I have joined " + channel_name)
        channels.append(channel_name)

def part_channel(data):
    message = data.split(":")[2]
    channel_name = message.split()[1]
    if channel_name not in channels:
        send(data, "I am not in " + channel_name)
    else:
        irc.send("PART " + channel_name + "\r\n")
        send(data, "I have left " + channel_name)
        channels.remove(channel_name)

def add_admin(data):
    message = data.split(":")[2]
    add_name = message.split()[1]
    admins.append(add_name)
    send(data, add_name + " has been added to the admin list")

def list_admins(data):
    adminList = ""
    for i in admins:
        if len(adminList) == 0:
            adminList += i

        else:
            adminList += ", " + i

    send(data, "This is a list of the current admins: " + i)

    
functions = {".math" : {"argument": True, "function": arithmetic, "require_admin" : False}
             , "hello" : {"argument" : False, "function" : hello, "require_admin" : False}
             , ".join" : {"argument" : True, "function" : join_channel, "require_admin" : True}
             , ".part" : {"argument" : True, "function" : part_channel, "require_admin" : True}
             , ".addadmin" : {"argument" : True, "function" : add_admin, "require_admin" : True}
             , ".listadmins" : {"argument" : False, "function" : list_admins, "require_admin" : False}}

network = "irc.freenode.net"
port = 6667
irc = socket.socket (socket.AF_INET, socket.TCP_NODELAY)
irc.connect ( ( network, port ) )
data = irc.recv ( 4096 )
channels = ["#elenusbottest", "#elenusbottest2"]
admins = ["elonus"]
print(data)

irc.send ( "NICK ElonusBot2\r\n" )
irc.send ( "USER ElonusBot2 ElonusBot2 ElonusBot2 :Elonus testbot\r\n" )
sleep(2)
irc.send ( "PRIVMSG NickServ: identify elonusbot gutta4197\r\n")

data = irc.recv(4096)

if data.find("PING"):
    ping(data)

for i in channels:
    irc.send ( "JOIN " + i + "\r\n" )
    irc.send("PRIVMSG " + i + " :Hello\r\n")
    sleep(0.5)

sleep(1)

while True:
    data = irc.recv(4096).strip("\r\n")
    print(data)

    if data.find("PING") != -1:
        ping(data)

    elif data.find("PRIVMSG") != -1:
        message = data.split(":")[2]
        codeword = message.split()[0]
        codeword = codeword.lower()
        sender = data.split("!")[0].strip(":")
        
        data2 = str(data)

        if (sender not in admins) and functions[codeword]["require_admin"]:
            send(data, codeword + " requires admin access")

        else:
            if codeword in functions:

                if functions[codeword]["argument"]:
                    try:
                        message.split()[1]

                    except IndexError:
                        send(data, codeword + " expects an argument")

                    else:
                        functions[codeword]["function"](data2)

                else:
                    functions[codeword]["function"](data2)
