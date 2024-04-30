import subprocess
import sys

#filename = R"C:\Users\bfora\Desktop\cnc\sheep.nc"
#filename = "test.gcode"

def cli_ugs(filename, com_port):
    
    java_command = f'java -cp UniversalGcodeSender.jar com.willwinder.ugs.cli.TerminalClient --controller GRBL --port COM{com_port} --baud 115200 --print-progressbar --home --file {filename}'

    l = []
    with open("test.log", "wb") as f:
        process = subprocess.Popen(java_command, stdout=subprocess.PIPE)
        for c in iter(lambda: process.stdout.read(1), b""):
            c = c.decode()
            line = "".join(l)
            if "\n" in c or "RUN" in line or "ALARM" in line:
                print(line)
                l = []
            else:
                l.append(c[0])


