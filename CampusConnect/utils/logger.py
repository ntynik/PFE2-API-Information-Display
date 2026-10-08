def log(message):
    with open("logs/system.log", "a") as log_file:
        log_file.write(message + "\n")