from scapy.all import rdpcap
import pandas as pd
import time
import datetime

def little_endian_conv(num):
    hex_num = bytes(num,'utf-8')
    big = bytearray.fromhex(str(hex_num, 'utf-8'))
    big.reverse()
    little = ''.join(f"{n:02X}" for n in big)
    hex_bytes= bytearray(int(little, 16).to_bytes(8, 'big')).hex()
    return hex_bytes


pcaps = [
    "noise-storm-icmp-brazil_00000_20240816160936.pcap",
    "noise-storm-icmp-brazil_00001_20240819222104.pcap",
    "noise-storm-icmp-brazil_00002_20240820165721.pcap",
    "noise-storm-icmp-brazil_00003_20240821113203.pcap",
    "noise-storm-icmp-brazil_00004_20240822060521.pcap",
    "noise-storm-icmp-brazil_00005_20240823005218.pcap",
    "noise-storm-icmp-brazil_00006_20240823192859.pcap",
    "noise-storm-icmp-brazil_00007_20240824141504.pcap",
    "noise-storm-icmp-brazil_00008_20240825090124.pcap",
    "noise-storm-icmp-brazil_00009_20240826035404.pcap",
    "noise-storm-icmp-brazil_00010_20240826231701.pcap",
    "noise-storm-icmp-brazil_00011_20240827184617.pcap",
    "noise-storm-icmp-brazil_00012_20240828142706.pcap",
    "noise-storm-icmp-brazil_00013_20240829100324.pcap",
    "noise-storm-icmp-brazil_00014_20240830052320.pcap"
]

i = 0
for pcap in pcaps:
    i = i+1
    print(f"Starting Loop. Iteration {i}")
    # Load PCAP file
    packets = rdpcap(pcap)

    packet_data = []

    for packet in packets:
        if packet.haslayer("IP"):
            src_ip = packet["IP"].src
            dst_ip = packet["IP"].dst
            timestamp = packet.time
            # timestamp = timestamp_utc.strftime('%Y-%m-%d %H:%M:%S') # UTC timestamp
            raw_data = bytes(packet).hex()  # Hex representation of raw data
            match raw_data:
                case str(x) if "4c4f5645" in x:
                    payload = raw_data[56:88]

                    # HiPerConTracer Header
                    magic_number = int(f"0x{payload[0:7]}",0)
                    send_ttl = int(f"0x{payload[8:10]}",0)
                    round_num = int(f"0x{payload[10:12]}",0)
                    checksum_tweak = int(f"0x{payload[12:16]}",0)
                    scrape_timestamp = payload[16:]
                    tmp = int(f"0x{little_endian_conv(scrape_timestamp)}",0)
                    send_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(tmp/1000))
                # Linux Ping
                case str(x) if "20212223" in x:
                    magic_number = None
                    send_ttl = None
                    round_num = None
                    checksum_tweak = None
                    send_ttl = timestamp
                # case "6c69626f":
                case _:
                    magic_number = None
                    send_ttl = None
                    round_num = None
                    checksum_tweak = None
                    send_time = None
                    send_ttl = timestamp

            packet_data.append([src_ip, dst_ip, timestamp,magic_number,send_ttl,round_num,checksum_tweak,send_time,raw_data])

    # Save to CSV
    df = pd.DataFrame(packet_data, columns=["Source_IP", "Destination_IP", "UTC_Arrival_Time", "Magic_Number","TTL","Round","Checksum_Tweak","Send_Timestamp","Raw_Packet_Data"])
    df.to_excel('./output.xlsx',sheet_name=f'{pcap.strip('.pcap')}')
    # df.to_csv(f"./data/{pcap.strip('.pcap')}_parsed_packets.csv", index=False)

print(f"Saved as output.xlsx")
