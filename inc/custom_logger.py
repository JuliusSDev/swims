import logging
import time

# USAGE
# # Get the custom logger
# logger = get_custom_logger('my_logger', level=logging.DEBUG)
# # Log messages
# logger.debug('This is a debug message.') # e.g. for variable values, in which if-Statement/function we are ...
# logger.info('This is an info message.') # e.g. if a process is finished e.g. server is setup 
# logger.warning('This is a warning message.') # possible unknown behavior / Wrong if-Statements e.g. waiting for a server connection then you can log it with Warning
# logger.error('This is an error message.') # Values that should not appear
# logger.critical('This is a critical message.') # I don't know what the fuck is going on




# Define the start time of the program
program_start_time = time.time()

# Custom logging formatter
class CustomFormatter(logging.Formatter):
    def format(self, record):
        runtime = (time.time() - program_start_time) * 1000  # Convert to milliseconds
        record.message = f"[{runtime:.2f} ms] [{record.levelname}] {record.getMessage()}"
        return record.message

def get_custom_logger(name, level=logging.DEBUG):
    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create a console handler
    console_handler = logging.StreamHandler()

    # Set the custom formatter for the handler
    formatter = CustomFormatter()
    console_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(console_handler)
    
    return logger
