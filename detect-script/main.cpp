#include <iostream>
#include "SystemUtils.h"
#include "Packet.h"
#include "PcapFileDevice.h"
#include <IcmpLayer.h>
#include <RawPacket.h>
#include <PayloadLayer.h>
#include <vector>
#include <set>
#include <string>
#include <stdint.h>
using namespace std;


std::string getProtocolTypeAsString(pcpp::ProtocolType protocolType)
{
    switch (protocolType)
    {
    case pcpp::Ethernet:
        return "Ethernet";
    case pcpp::IPv4:
        return "IPv4";
    case pcpp::TCP:
        return "TCP";
    case pcpp::ICMP:
        return "ICMP";
    default:
        return "Unknown";
    }
}

vector<char> getFullPayloadAsVector(pcpp::Layer* curLayer)
{
    const uint8_t* payload = curLayer->getLayerPayload();
    const size_t payload_size = curLayer->getLayerPayloadSize();
    vector<char> full_payload;
    for (int i=0; i < payload_size; i++) {
        full_payload.push_back(payload[i]);
    }
    return full_payload;
}


int main(int argc, char* argv[])
{
   // create a pcap file reader
    pcpp::PcapFileReaderDevice reader("merged_output.pcap");
    if (!reader.open())
	{
		std::cerr << "Error opening the pcap file" << std::endl;
		return 1;
	}

    pcpp::RawPacket rawPacket;
    pcpp::IPv4Address srcIP = pcpp::IPv4Address();
    pcpp::IPv4Address destIP = pcpp::IPv4Address();
    set<pcpp::IPv4Address> srcAddresses;
    set<pcpp::IPv4Address> destAddresses;

    while (reader.getNextPacket(rawPacket)) {

	// parse the raw packet into a parsed packet
        pcpp::Packet parsedPacket(&rawPacket);
        pcpp::IPv4Layer * ipLayer = parsedPacket.getLayerOfType<pcpp::IPv4Layer>();

        // verify the packet is ICMP
            if (parsedPacket.isPacketOfType(pcpp::ICMP)) {
            uint8_t header_type = parsedPacket.getLayerOfType<pcpp::IcmpLayer>()->getIcmpHeader()->type;
            uint16_t checksum = parsedPacket.getLayerOfType<pcpp::IcmpLayer>()->getIcmpHeader()->checksum;

            if ((srcAddresses.find(ipLayer->getSrcIPv4Address()) == srcAddresses.end()) && (int(header_type) == 8) && (destAddresses.find(ipLayer->getSrcIPv4Address()) == destAddresses.end())) {
            // extract source and dest IPs
                pcpp::IPv4Layer * ipLayer = parsedPacket.getLayerOfType<pcpp::IPv4Layer>();
                pcpp::IPv4Address srcIP = ipLayer->getSrcIPv4Address();
                pcpp::IPv4Address destIP = ipLayer->getDstIPv4Address();
                pcpp::IcmpLayer * icmp_layer = parsedPacket.getLayerOfType<pcpp::IcmpLayer>();
                vector<char> vec = getFullPayloadAsVector(parsedPacket.getFirstLayer());
                string payload(vec.begin(), vec.end());
                if (payload.find("LOVE") != std::string::npos) {
                    srcAddresses.insert(srcIP);
                    destAddresses.insert(destIP);
                    std::cout
                    << "Packet type: '" << int(header_type) << "'; (8 is Request, 0 is Reply) \n"
                    << "Source IP is '" << srcIP << "'; \n"
                    << "Dest IP is '" << destIP << "'; \n" 
                    << "IP ID: 0x" << std::hex << pcpp::netToHost16(ipLayer->getIPv4Header()->ipId) << "; \n"
                    << "Checksum: 0x" << std::hex << checksum << "; \n"
                    << "TTL: " << (int)ipLayer->getIPv4Header()->timeToLive << "; \n"
                    << "Packet payload is '" << payload << "; \n"
                    << "\n" << std::endl;
                }
            }
        }
    }
    std::cout << "Source IP Addresses: " << std::endl;
    for (pcpp::IPv4Address const& ip : srcAddresses)
        {
            std::cout << ip << ' ';
        }
    std::cout << "\n" << std::endl;
    std::cout << "Destination IP Addresses: " << std::endl;
    for (pcpp::IPv4Address const& ip : destAddresses)
        {
            std::cout << ip << ' ';
        }
    std::cout << "\n" << std::endl;
	// close the file
	reader.close();
	return 0;
}
