### HiPerConTracer Usage

Program is used the exact same as the original, documentation can be found for here https://github.com/anthonypower0923/FYP/blob/main/modified-hipercontracer/README.md

### Detection Script Usage

To run the current example version of the detection script you will require the 'merged_output.pcap'. This file could not be uploaded to the repo as it was too large, so to get this file go to this page on GitHub from GreyNoise https://github.com/GreyNoise-Intelligence/2024-09-noise-storms/tree/main/noise-storm-icmp-brazil, click into the icmp sample and in the README should be instruction on how to obtain this merged packet capture file.

### Packet Parser Usage

This script is ran like any other Python script and the files it takes are from the paths or files in the array
pcaps. The current version, has all the packet captures from the merged capture. 
Note: For packet captures the same or larger size than the merged capture please segment it as the script
has not been tested for that large a file to parse.

### Netmonitor Usage
This script when ran with no arguments defaults to eth0 as the interface. The first argument for the script is the interface
to listen on i.e. `./netmonitor.sh en0ps1` to listen on the enp0s1 interface. To edit the interval between readings modify the
interval variable, currently set to 30 mins or 36000 seconds. To push the results to MQTT uncomment the lines at the bottom of the script and modify them.