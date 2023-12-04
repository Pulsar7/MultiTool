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
        
    def write(self,lines:str) -> bool:
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
    
    def search_on_duckduckgo(self,fullname:str) -> tuple[bool,str]:
        session = req_handler.create_new_session(use_proxy=self.use_tor_status)
        
        session.close()
        return (True,"Nothing happened.")
    
    def check_fullname(self,person_fullname:str) -> bool:
        if len(person_fullname) <= 1:
            return False
        if " " not in person_fullname:
            return False
        return True
    
    def get_person_formatted_fullname(self,person_fullname:str) -> str:
        formatted_fullname:str = ""
        args:list[str] = person_fullname.split(" ")
        for x,arg in enumerate(args):
            formatted_fullname += arg.lower()
            if x < len(args)-1:
                formatted_fullname += "_"
        return formatted_fullname
    
    def search(self) -> None:
        person_fullname:str = str(input(Fore.WHITE+"<"+"Fullname> "+Fore.RESET)).strip()
        if self.check_fullname(person_fullname) == False:
            self.error(f"The fullname '{person_fullname}' is invalid!")
            return
        output_dir:str = str(input(Fore.WHITE+"<"+f"Output directory [Default={self.default_md_output_directory}]"+Fore.WHITE+"> "+Fore.RESET))
        if len(output_dir) > 0:
            self.md_output_directory = output_dir
        else:
            self.md_output_directory = self.default_md_output_directory
        person_formatted_fullname:str = self.get_person_formatted_fullname(person_fullname)
        self.md_output_filepath = self.md_output_directory+person_formatted_fullname+".md"
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
        
        writer = WRITER(filepath = self.md_output_filepath)
        self.info(f"Searching for information about {person_fullname}")
        writer.write(lines=f"""\
<div style="text-align:center;">
  <h1>{person_fullname}</h1>
</div>

<h2>Table of contents</h2>

- [Basic Information](#basic-information)
- [Accounts](#accounts)
  - [Phone](#phone)
  - [E-Mails](#e-mails)
  
## Basic information
""")
        self.info("Search for information on DuckDuckGo", prog = True)
        (status,result) = self.search_on_duckduckgo(fullname = person_fullname)
        if status == True:
            self.ok()
            writer.write(lines = result)
        else:
            self.failed(),self.error(f"An error occured while searching on DuckDuckGo: {str(result)}")
        self.use_tor_status = True # return to default
        # self.md_output_directory = "" # return to default » probably not neccessary
    