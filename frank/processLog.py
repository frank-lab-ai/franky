
# Logging of FRANK Inference


class LogLevel:
    ANSWER = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    VERBOSE = 10

class pcolors:    
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[33m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WARNING = '\033[93m'
    RED = '\033[91m'    
    BOLD = '\033[1m' 
    UNDERLINE = '\033[4m'
    RESET = '\033[39m \033[2m' # reset and dim
    RESETALL = '\033[0m'

baseLogLevel = LogLevel.INFO


def println(content, loglevel):
    if(loglevel <= baseLogLevel):
        print(content)
