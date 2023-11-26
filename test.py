import re
EMOJIREGEX = re.compile((r"<:(\w+):(\d+)>"))
rawMsg = "hello hello <:uwu:913476403415093269> hello"
filteredMsg = re.sub(EMOJIREGEX, "", rawMsg)
filteredMsg = filteredMsg.translate(str.maketrans("", "", "\"\',.:;?\\~"))
print (filteredMsg)