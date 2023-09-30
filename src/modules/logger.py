"""
@MultiTool / Logger.py
@Version 1.0
@Python 3.10.12
"""
import sys,pytz
from colorama import (Fore,init)
from datetime import datetime
from rich.console import Console
from rich.table import Table

init()

class LOGGER():
    def __init__(self) -> None:
        pass
    
    def get_now(self) -> str:
        n = datetime.now(pytz.timezone(self.timezone))
        return f"{Fore.RESET}({Fore.BLUE}{n.hour}:{n.minute}:{n.second}{Fore.RESET}) "
    
    def info(self,msg:str,prog:bool=False) -> None:
        if prog == True:
            sys.stdout.write("\r"+self.get_now()+f"{Fore.RESET}[{Fore.LIGHTYELLOW_EX}*{Fore.RESET}] {Fore.WHITE}{msg}{Fore.RESET}...")
            sys.stdout.flush()
        else:
            print(self.get_now()+f"{Fore.RESET}[{Fore.YELLOW}*{Fore.RESET}] {Fore.RESET}{msg}{Fore.RESET}")
            
    def warning(self,msg:str) -> None:
        print(self.get_now()+f"{Fore.RESET}[{Fore.LIGHTYELLOW_EX}#{Fore.RESET}] {Fore.YELLOW}{msg}{Fore.RESET}")
        
    def error(self,msg:str) -> None:
        print(self.get_now()+f"{Fore.RESET}[{Fore.RED}*{Fore.RESET}] {Fore.LIGHTRED_EX}{msg}{Fore.RESET}")
        
    def ok(self,msg:str="OK") -> None:
        print(f"{Fore.LIGHTGREEN_EX}{msg}")
    
    def failed(self,msg:str="FAILED") -> None:
        print(f"{Fore.LIGHTRED_EX}{msg}")
        
    def print_help(self,commands:dict,title:str="Help",column1:str="Command",column2:str="Description") -> None:
        table = Table(title=title)
        table.add_column(column1,justify="left")
        table.add_column(column2,justify="right")
        for x,command in enumerate(commands):
            table.add_row(command,commands[command]['descr'])
            # if x%3 == 0:
            table.add_section()
        print(""),Console().print(table)
        
    def found(self,msg:str) -> None:
        print(f"{Fore.RESET}[{Fore.LIGHTCYAN_EX}+{Fore.RESET}] {Fore.RESET}{msg}{Fore.RESET}")
    
    def found_ap(self,type_of_resp:str,essid:str="?",bssid:str="?",channel_frequency:str="?",channel:str="?",rssi:str="?") -> None:
        print(Fore.WHITE+f" ["+Fore.LIGHTGREEN_EX+type_of_resp+Fore.WHITE+"]"+Fore.RESET+" ESSID = "+Fore.YELLOW+essid+Fore.RESET+" BSSID = "+Fore.YELLOW+bssid+Fore.RESET+" <Frequency> "+Fore.YELLOW+channel_frequency+" MHz"+Fore.RESET+" <Channel> "+Fore.YELLOW+channel+Fore.RESET+" <RSSI> "+Fore.YELLOW+rssi+Fore.RESET+" dBm")

    def print_network_ifaces(self,network_interfaces:dict) -> None:
        table = Table(title="Available network interfaces")
        table.add_column("Name",justify="left")
        table.add_column("Address",justify="center")
        table.add_column("Netmask",justify="right")
        for interface, addresses in network_interfaces.items():
            table.add_row(interface,network_interfaces[interface][0].address,network_interfaces[interface][0].netmask)
            table.add_section()
        print(""),Console().print(table)