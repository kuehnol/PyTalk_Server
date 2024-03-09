from datetime import datetime


class Output:  # TODO: replace with logging or sth
    @staticmethod
    def printout(text: str) -> None:
        # get current time
        curr_time = datetime.now()
        time_str = curr_time.strftime("%H:%M:%S")

        # print out text with timestamp
        print(f"[{time_str}] {text}")
