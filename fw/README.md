# Notes

## Captive Portal and Out of Box Experience
Use the 169.254.43.x network, and assume that this network is not in
conflict with other devices since it's non-routable and reserved only
for the USB Ethernet we provide.

We need to create these services:

* A DHCP Server to assign the PC an IP (169.254.43.100) and tell it
  the DNS server is at 169.254.43.99 (the transceiver's address).

* An mDNS Responder to answer multicast queries for `sdr.local`.

* A lightweight unicast DNS Server to handle direct requests, enable
  the captive portal, and provide name resolution for non-mDNS
  clients.

* A HTTP[S] server to serve the application, do configuration, provide
  ReST API endpoints.

* A private certificate authority and root certificate for same which
  the user can install in their browser to avoid having the security
  warning each time they access the transceiver.
  * This is painful but one time.
  * The root certificate would expire in, say, 20 years.

* The transceiver's _server certificate_ should expire periodically.
  * This limits the damage window if the private key is compromised.
  * On each startup, transceiver software would:
    1. Generate a brand new server certificate for `sdr.local`.
	2. Set its expiration date to 100-400 days in the future.
	3. Sign the new certificate using private root CA key.
  * This all happens under the covers - user never sees it.
