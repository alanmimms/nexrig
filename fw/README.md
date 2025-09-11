# Notes

## Captive Portal and Out of Box Experience
Use the 169.254.43.x network, and assume that this network is not in
conflict with other devices since it's non-routable and reserved only
for the USB Ethernet we provide.

We need to create these services:

* A DHCP Server to assign the PC an IP (169.254.43.100) and tell it
  where the DNS server is.

* An mDNS Responder to answer multicast queries for my-sdr.local.

* A lightweight unicast DNS Server to handle direct requests, enable
  the captive portal, and provide name resolution for non-mDNS
  clients.

* A HTTP[S] server to serve the application, do configuration, provide
  ReST API endpoints.
