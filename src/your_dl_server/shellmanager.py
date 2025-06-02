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
        self.last_was_download = False  # Track if the last printed line was a download line

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
        last_line_length = 0  # Track the length of the last line
        while self.running:
            output = self.process.stdout.readline()
            if output:
                with self.lock:
                    self.output += output
                    self.last_output_time = time.time()

                # Check if the line starts with "[download]" or is related to Axel's output
                if output.startswith("[download]"):
                    # Clear the line by filling it with spaces and a carriage return
                    print(f"\r{' ' * last_line_length}\r", end='', flush=True)
                    # Print the new output and update last_line_length
                    print(f"\r{output.strip()}", end='', flush=True)
                    last_line_length = len(output.strip())
                    self.last_was_download = True  # Mark that the last line was a download line
                elif output.startswith("EXIT_CODE:"):
                    pass
                else:
                    # Ensure non-download lines start on a new line if the last was a download line
                    if self.last_was_download:
                        print()  # Print a newline to separate from the download line
                    print(f"{output}", end='')
                    last_line_length = 0  # Reset length tracking
                    self.last_was_download = False  # Mark that the last line was not a download line

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
