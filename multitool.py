"""
@MultiTool
@Version 1.0
@Python 3.10.12
"""
import os,time,argparse,psutil,os,shutil,re
# own modules
from src.modules.logger import (Fore,LOGGER)
from src.modules.wifi import WIFI
from src.modules.network_tool import NETWORK_TOOL
from src.modules.social_engineering import SOCIAL_ENGINEERING
from src.modules.person_lookup import PERSON_LOOKUP
from src.modules.website_pentesting import WEBSITE_PENTESTING
#

def clear_screen():
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')

class MULTITOOL(LOGGER):
    def __init__(self,timezone:str,social_engineering_login_websites_dir:str) -> None:
        self.timezone:str = timezone
        super().__init__()
        self.network_tool = NETWORK_TOOL(timezone)
        self.wifi_tool = WIFI(timezone,self.network_tool)
        self.social_engineering = SOCIAL_ENGINEERING(timezone,self.network_tool,social_engineering_login_websites_dir)
        self.person_lookup = PERSON_LOOKUP(timezone,self.network_tool)
        self.website_pentesting = WEBSITE_PENTESTING(timezone,self.network_tool)
        self.running:bool = True
        self.modules:dict = {
            'wifi': {
                'descr': "Scanning, DoS-Attacks",
                'commands': {
                    'scan': {
                        'descr': "Scan for wifi-networks in your local area network",
                        'func': self.wifi_tool.scan
                    },
                    'deauth attack': {
                        'descr': "Deauthentication attack",
                        'func': self.wifi_tool.deauth_attack
                    }
                }
            },
            'network-tool': {
                'descr': "Scanning",
                'commands': {
                    'scan': {
                        'descr': "Scan for devices in your network",
                        'func': self.network_tool.scan
                    }
                }
            },
            'social-engineering': {
                'descr': "Fake-Login, Person-Lookup",
                'commands': {
                    'fake-login': {
                        'descr': "Host a fake-login website",
                        'func': self.social_engineering.fake_login
                    },
                    'person-lookup': {
                        'descr': "Lookup information about a person",
                        'func': self.person_lookup.search
                    }
                }
            },
            'website-pentesting': {
                'descr': "WordPress Bruteforce",
                'commands': {
                    'wordpress-login-bruteforce': {
                        'descr': "A WordPress Bruteforce-Tool for the Admin-Login-Page",
                        'func': self.website_pentesting.wordpress_login_bruteforce
                    }
                }
            }
        }
        self.available_tools:list[str] = list(self.modules.keys())
        self.commands:dict = {
            'help': {
                'descr': "Shows this screen",
                'func': self.show_help
            },
            'show network interfaces': {
                "descr": "Shows all available network interfaces of your device",
                'func': self.show_network_interfaces
            },
            'clear': {
                'descr': "Clears the screen",
                'func': clear_screen
            },
            'exit': {
                'descr': "Closes the program",
                'func': self.exit
            },
            'show tools': {
                'descr': f"Shows available tools and its description",
                'func': self.show_tools
            },
            'use ?': {
                'descr': f"Use a tool/module ({', '.join(self.available_tools)})",
                'func': self.use
            },
            'back': {
                'descr': "Exits the current tool/module",
                'func': self.back
            },
            'module help': {
                'descr': "Shows options of the current tool/module you're using",
                'func': self.show_module_help
            }
        }
        self.prompt_args:str = ""
    
    
    def get_prompt(self) -> str:
        return Fore.LIGHTYELLOW_EX+"<"+Fore.LIGHTRED_EX+"multitool"+self.prompt_args+Fore.LIGHTYELLOW_EX+"> "+Fore.RESET
    
    def back(self) -> None:
        if len(self.prompt_args) > 0:
            self.prompt_args = ""
        else:
            self.error("You're not using any tool/module!")
    
    def exit(self) -> None:
        self.running = False
        self.warning("User wants to exit program")
     
    def get_user_input(self,prompt) -> object:
        user_input = input(prompt)
        return user_input

    def show_banner(self) -> None:
        text:str = """\n███╗   ███╗██╗   ██╗██╗  ████████╗██╗████████╗ ██████╗  ██████╗ ██╗     
████╗ ████║██║   ██║██║  ╚══██╔══╝██║╚══██╔══╝██╔═══██╗██╔═══██╗██║     
██╔████╔██║██║   ██║██║     ██║   ██║   ██║   ██║   ██║██║   ██║██║     
██║╚██╔╝██║██║   ██║██║     ██║   ██║   ██║   ██║   ██║██║   ██║██║     
██║ ╚═╝ ██║╚██████╔╝███████╗██║   ██║   ██║   ╚██████╔╝╚██████╔╝███████╗
╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝   ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝"""
        text += f"\n{Fore.LIGHTBLUE_EX}@{Fore.WHITE}Version{Fore.RESET}: 1.0"
        terminal_width, _ = shutil.get_terminal_size()
        lines = text.splitlines()
        centered_lines = []
        for line in lines:
            padding = max(0, (terminal_width - len(line)) // 2)
            centered_line = ' ' * padding + line
            centered_lines.append(centered_line)
        print('\n'.join(centered_lines)+"\n\n")
        
    def show_tools(self) -> None:
        self.print_help(commands=self.modules,title="Available Tools/Modules",
            column1="Tool/Module Name")
        
    def use(self,tool_name:str) -> None:
        if tool_name in self.available_tools:
            self.prompt_args = Fore.WHITE+"/"+Fore.RED+tool_name.upper()+Fore.WHITE
        else:
            self.error("Couldn't use tool/module: Invalid tool-name!")
    
    def show_network_interfaces(self) -> None:
        self.print_network_ifaces(network_interfaces = psutil.net_if_addrs())
 
    def show_help(self) -> None:
        self.print_help(commands=self.commands)
        
    def show_module_help(self) -> None:
        if len(self.prompt_args) > 0:
            current_module:str = self.prompt_args.split("/")[1].strip().lower()
            current_module = ''.join(re.split(re.compile(r'\x1b\[[0-9;]*[mK]'), current_module))
            self.print_help(commands=self.modules[current_module]['commands'],title="Module/Tool Help")
        else:
            self.error("In order to show available commands from a specific module/tool, you have to use one.")

    def check_user_input(self,commands:dict,user_input:str) -> bool:
        valid_command:bool = False
        for command in commands:
            command = command.lower().strip()
            if "?" not in command:
                if command == user_input:
                    commands[command]['func']()
                    valid_command = True
                    break
            else:
                # Command needs another argument
                first_part:str = command.split("?")[0].strip()
                if first_part in user_input: # User wants to use this command
                    user_comm_arg:str = user_input.split(first_part)[1].strip()
                    if len(user_comm_arg) > 0:
                        if "?" in user_comm_arg:
                            pass
                        commands[command]['func'](user_comm_arg)
                        valid_command = True
                        break
                    else:
                        self.error("The command needs another argument!")
        return valid_command
    
    def check_software(self) -> bool:
        for software in REQ_SOFTWARE:
            try:
                response = os.system(f'which {software} > NULL')
                if response != 0:
                    raise Exception("Not installed.")
            except Exception as _error:
                return False
        return True

    def run(self) -> None:
        self.show_banner()
        start:float = time.time()
        self.info("Check if software is installed",prog=True)
        if self.check_software() == False:
            self.failed(),self.error(f"Please install these required software: {REQ_SOFTWARE}")
            return
        self.ok()
        self.info("Started")
        valid_command:bool = False
        while self.running:
            try:
                try:
                    user_input:object = self.get_user_input(self.get_prompt())
                    if isinstance(user_input,str):
                        if len(user_input) > 0:
                            user_input = user_input.lower().strip()
                            valid_command = self.check_user_input(commands=self.commands,user_input=user_input)
                            if len(self.prompt_args) > 0 and valid_command == False:
                                current_module:str = self.prompt_args.split("/")[1].strip().lower()
                                current_module = ''.join(re.split(re.compile(r'\x1b\[[0-9;]*[mK]'), current_module))
                                valid_command = self.check_user_input(commands=self.modules[current_module]['commands'],user_input=user_input)
                    if valid_command == False:
                        self.error("Invalid command")
                    else:
                        valid_command = False
                except KeyboardInterrupt as e:
                    print("\n")
                    raise Exception("Detected Keyboard-Interruption")
            except Exception as _error:
                self.error(f"An error occurred: {str(_error)}")
                self.running = False
                break
        self.info(f"Closed. (Runtime={time.time()-start} Seconds)")
   

#
DEFAULT_TIMEZONE:str = "MET" # Middle European Time
FAKE_SOCIAL_ENGINEERING_LOGIN_WEBSITES_DIR:str = "src/tools/social_engineering/login_websites/"
#
REQ_SOFTWARE:list[str] = [
    "macchanger","airmon-ng","tor","ifconfig"
]
#
parser = argparse.ArgumentParser()
parser.add_argument(
    '-t','--timezone',help=f"Timezone (Default={DEFAULT_TIMEZONE})",
    default=DEFAULT_TIMEZONE,type=str
)
parser.add_argument(
    '-l','--fake-login-websites-dir',help=f"Directory for the Fake-Social-Engineering-login-websites (Default={FAKE_SOCIAL_ENGINEERING_LOGIN_WEBSITES_DIR})",
    default=FAKE_SOCIAL_ENGINEERING_LOGIN_WEBSITES_DIR,type=str
)
args = parser.parse_args()
#
    
if __name__ == '__main__':
    clear_screen() 
    multitool = MULTITOOL(
        timezone=args.timezone,
        social_engineering_login_websites_dir=args.login_websites_dir
    )
    multitool.run()