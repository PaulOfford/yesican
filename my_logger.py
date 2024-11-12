from datetime import datetime
import shared_memory

def microsec_message(log_level, msg_text: str):
    if log_level <= shared_memory.settings.get_log_level():
        now = datetime.now()
        # we construct the whole print string before calling print() to avoid
        # gui and backend thread logging clashing and so creating mixed content
        log_msg = now.strftime("%Y-%m-%d %H:%M:%S.%f") + " " + msg_text + "\n"
        print(log_msg, end='')
