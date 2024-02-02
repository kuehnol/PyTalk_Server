from datetime import datetime


class Output:
    def __init__(self):  # placeholder or sth idk
        pass

    def printout(self, text):
        # get current time
        curr_time = datetime.now()
        time_str = curr_time.strftime("%H:%M:%S")

        # print out text with timestamp
        print(f"[{time_str}] {text}")
