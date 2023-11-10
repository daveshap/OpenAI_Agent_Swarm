# Colored clis are more user friendly and easier to read.
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
import os, random

rand = random.Random()
colorama_init()

spinner_index = 0
spinner_base = '▁▃▄▅▆▇█▇▆▅▄▃'
size = os.get_terminal_size() 

def clearLine ():
    print(' ' * size.columns, end="\r")

def header (text):
    clearLine()
    print(Fore.BLUE + text + Style.RESET_ALL)

def hr ():
    print(Fore.LIGHTBLACK_EX + "─" * size.columns + Style.RESET_ALL)
    
def note (text):
    clearLine()
    print(Fore.LIGHTBLACK_EX + f"    > {text}" + Style.RESET_ALL)

def spinner (text):
    global spinner_index
    spinner_text = spinner_base[spinner_index]
    spinner_index = (spinner_index + 1) % len(spinner_base)
    clearLine()
    print(Fore.LIGHTBLACK_EX + f"    {spinner_text} {text}" + Style.RESET_ALL, end="\r")

def complete (text):
    clearLine()
    print(Fore.GREEN + f"    ✓" +  Fore.LIGHTBLACK_EX + f" {text}" + Style.RESET_ALL)

def fail (text):
    clearLine()
    print(Fore.RED + f"    ✗" +  Fore.LIGHTBLACK_EX + f" {text}" + Style.RESET_ALL)