"""
@MultiTool / Person Lookup
@Version 1.0
@Python 3.10.12
"""
import os
#
from src.modules.logger import (Fore,LOGGER)
import src.modules.http_request_handler as req_handler
#


class WRITER():
    def __init__(self,filepath:str) -> None:
        self.filepath = filepath
        
    def write(self,lines:str) -> object:
        try:
            Lines:list[str] = []
            for line in lines.split("\n"):
                Lines.append(line.strip()+"\n")
            file = open(self.filepath,'a')
            file.writelines(lines)
            file.close()
            return True
        except Exception as _error:
            print(str(_error))
            return False

class PERSON_LOOKUP(LOGGER):
    def __init__(self,timezone:str,network_tool) -> None:
        (self.timezone,self.network_tool) = (timezone,network_tool)
        super().__init__()
        # Search
        self.default_md_output_directory:str = os.getcwd()+"/"
        self.md_output_directory:str = ""
        self.md_output_filepath:str = ""
        self.use_tor_status:bool = True
        self.PERSON:dict = {
            'img_path': "",
            'basic_info': "",
            'accounts': {
                'phone': [],
                'emails': []
            }
        }
        #
    
    def search_on_duckduckgo(self,firstname:str,surname:str) -> tuple((bool,str)):
        session = req_handler.create_new_session(use_proxy=self.use_tor_status)
        
        session.close()
        return (True,"Nothing happened.")
        
    
    def search(self) -> None:
        person_firstname:str = str(input(Fore.WHITE+"<"+"Firstname> "+Fore.RESET))
        if len(person_firstname) <= 1:
            self.error(f"The firstname '{person_firstname}' is invalid!")
            return
        person_surname:str = str(input(Fore.WHITE+"<"+"Surname> "+Fore.RESET))
        if len(person_surname) <= 1:
            self.error(f"The surname '{person_surname}' is invalid!")
            return
        output_dir:str = str(input(Fore.WHITE+"<"+f"Output directory [Default={self.default_md_output_directory}]"+Fore.WHITE+"> "+Fore.RESET))
        if len(output_dir) > 0:
            self.md_output_directory = output_dir
        else:
            self.md_output_directory = self.default_md_output_directory
        self.md_output_filepath = self.md_output_directory+f"{person_firstname.lower()}_{person_surname.lower()}.md"
        self.info(f"Output-Filepath: {self.md_output_filepath}")
        use_tor_status:str = str(input(Fore.WHITE+"<"+"Use Tor-Proxy for requests? [Y/n]> "+Fore.RESET))
        if use_tor_status.lower().strip() == "n":
            self.use_tor_status = False
            self.warning("Not using any proxy for internet-requests")
            proceed_qu:str = str(input(Fore.YELLOW+"Proceed? [y/N]> "+Fore.RESET))
            if proceed_qu.lower().strip() != "y":
                self.error("Stopped person-search.")
                return
            self.warning("Proceeding.")
        else:
            self.info(f"Using Tor as proxy on {Fore.CYAN}{req_handler.PROXIES}")
        
        writer = WRITER(filepath=self.md_output_filepath)
        self.info(f"Searching for information about {person_firstname} {person_surname}")
        writer.write(lines=f"""\
<div style="text-align:center;">
  <h1>{person_firstname} {person_surname}</h1>
</div>

<h2>Table of contents</h2>

- [Basic Information](#basic-information)
- [Accounts](#accounts)
  - [Phone](#phone)
  - [E-Mails](#e-mails)
  
## Basic information
""")
        self.info("Search for information on DuckDuckGo",prog=True)
        (status,result) = self.search_on_duckduckgo(person_firstname,person_surname)
        if status == True:
            self.ok()
            writer.write(lines=f"""\
{result}
            """)
        else:
            self.failed(),self.error(f"An error occured while searching on DuckDuckGo: {str(result)}")
        self.use_tor_status = True # return to default
        # self.md_output_directory = "" # return to default _> probably not neccessary
    