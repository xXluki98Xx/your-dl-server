import subprocess
import threading
import time
import sys

from your_dl_server.dto import dto


class ShellManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.running = True
        self.output = ""
        self.error = ""
        self.last_output_time = time.time()
        self.command_exit_code = None
        self.start_shell()

    def start_shell(self):
        dto().publishLoggerDebug("Starting new shell process.")
        self.process = subprocess.Popen(
            ['bash'], 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        self.output_thread = threading.Thread(target=self.read_output)
        self.error_thread = threading.Thread(target=self.read_error)
        self.output_thread.start()
        self.error_thread.start()

    def read_output(self):
        # dto().publishLoggerDebug("Reading stdout from process.")
        while self.running:
            output = self.process.stdout.readline()
            if output:
                with self.lock:
                    self.output += output
                    self.last_output_time = time.time()
                print(f"{output}", end='')
                if output.startswith("EXIT_CODE:"):
                    self.command_exit_code = int(output.split(":")[1].strip())
                    dto().publishLoggerWarn(f"Detected exit code: {self.command_exit_code}")

    def read_error(self):
        # dto().publishLoggerDebug("Reading stderr from process.")
        while self.running:
            error = self.process.stderr.readline()
            if error:
                with self.lock:
                    self.error += error
                    self.last_output_time = time.time()
                print(f"{error}", end='', file=sys.stderr)
                # dto().publishLoggerDebug(error)

    def send_command(self, command):
        # dto().publishLoggerDebug(f"Sending command: {command}")
        with self.lock:
            self.process.stdin.write(f"{command}; echo EXIT_CODE:$?\n")
            self.process.stdin.flush()

    def wait_for_command(self, timeout=30):
        # dto().publishLoggerDebug("Waiting for command to complete.")
        self.process.stdin.flush()
        while True:
            with self.lock:
                current_time = time.time()
                if current_time - self.last_output_time > timeout:
                    
                    # if the downloader is doing some fixup, we dont want to restart
                    if "[FixupM3u8]" in self.output:
                        dto().publishLoggerWarn(f"No new output for {timeout} seconds. Fixup not complete...")
                        continue

                    dto().publishLoggerWarn(f"No new output for {timeout} seconds. Restarting command...")
                    return 'timeout'

                if self.command_exit_code is not None:
                    return self.command_exit_code

            time.sleep(1)

    def stop(self):
        # dto().publishLoggerDebug("Stopping the shell process.")
        self.running = False
        self.process.terminate()
        self.output_thread.join()
        self.error_thread.join()

    def get_output(self):
        with self.lock:
            output = self.output
            self.output = ""
        return output

    def get_error(self):
        with self.lock:
            error = self.error
            self.error = ""
        return error
