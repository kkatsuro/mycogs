#!/usr/bin/python3

# @todo: this file needs complete rewrite to make it good

# How to change it to be safe?
# bug:
# command a add something to buffer
# command b prints it
# situation: user gets some random content

# XXX: move dsend dividing logic here?
#      we could create buffer array and store strings up to 2000 chars
#      that way you can be sure you don't divide single print into 2 different
#      messages and could use code=True on dprint instead of dsend
buffer = ''
def dprint(*text_args, sep=' '):
    global buffer

    if len(text_args) == 0:
        buffer += '\n'
        return

    for text in text_args:
        if type(text) != type(str()):
            try:
                text = str(text)
            except:
                buffer += '\n'
                return

        buffer += text + sep

    buffer += '\n'

def buffempty():
    global buffer
    temp = buffer
    buffer = ''
    return temp

# how ugly is this function?
# TODO:
# * fix weird newline when code=True
# * variables for all of those numbers here
async def dsend(channel, code=False):
    buffer = buffempty()
    while buffer:
        # find good place to split
        if len(buffer) < 1998:
            if code:
                buffer = '`' + buffer + '`'
            await channel.send(buffer)
            return

        char = buffer[1997]

        for i in range(1996, 0, -1):
            if char == '\n':
                break
            char = buffer[i]

        if i == 1:  # newline for split not found
            for i in range(1996, 0, -1):
                if char == ' ':
                    break
                char = buffer[i]

        i += 1

        if i == 2:  # space and newline not found
            i = 1998

        bpart  = buffer[:i]
        buffer = buffer[i:]

        if code:
            bpart = '`' + bpart + '`'

        await channel.send(bpart)
