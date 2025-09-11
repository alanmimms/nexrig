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
  

# Features

## Logging and Other Media Data
Transceiver can hold log data for a while then download to user's PC
in some standard format for import to eg SmartLogger.

* Q: Is it worth adding an SD card interface?
  This provides large storage and ability save much more than logs:
  * Could save recorded QSOs, voice recordings to play back as
    microphone audio, etc.


# Things to Ponder
* Should we provide Ethernet as well as USB connectivity?
  * If Ethernet is used, power comes from +12V only.
  * If USB is used, receiver may be able to run on +5V from USB.

* Is it worth making this transceiver capable of running without being
  attached to a PC?
  * Need to provide audio out and headphone jack and/or speaker.
  * Need to provide audio in for microphone.
  * Need to provide touch screen.
    * Can use HDMI + USB HID.
	* Or use built in 1024x768 LCD driver + touch controller.
  * Maybe needs GNSS receiver and/or battery backed RTC.
