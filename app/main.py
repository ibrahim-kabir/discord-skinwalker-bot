import threading
import subprocess

def run_script(script_name):
    subprocess.run(["python", script_name])

if __name__ == "__main__":
    thread1 = threading.Thread(target=run_script, args=("app/recording_bot.py",))
    thread2 = threading.Thread(target=run_script, args=("app/skinwalker_bot.py",))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()
