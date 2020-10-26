
# Logging of FRANK Inference


class LogLevel:
    ANSWER = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    VERBOSE = 10


baseLogLevel = LogLevel.INFO


def println(content, loglevel):
    if(loglevel <= baseLogLevel):
        print(content)
