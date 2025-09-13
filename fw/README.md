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

## Transmit Path Power Amplifier Efficiency
The transmit path will use Envelope Elimination and Restoration (EER)
for the Vdd supplied to the PA MOSFET. This derives the amplitude
portion of the transmitted signal from the Vdd value while the PA
MOSFET continually switches at the carrier frequency with phase offset
provided by the NCO in the FPGA to provide the phase aspect of the
output signal.

In this scheme, the PA MOSFET's Vdd comes from a buck regulator
designed to track the amplitude of the modulation in real time, so the
MOSFET can always be saturated ON or fully OFF as much as possible to
reduce dissipation.

The FPGA, which receives the phase offset part of the modulation from
the DSP in the microcontroller, uses a numerically controlled
oscillator (NCO) to drive the PA MOSFET's gate. This can also be
further modified to switch the MOSFET at real zero-crossing times to
provide "class E amplifier" behavior to further reduce dissipation.


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


## Consider PWM/PDM for NCO Gate Output
This would improve spectral purity of the PA's output by making its
square wave into a signal that is already PWMed or PDMed into a form
that is easier to low pass filter into the final carrier wave. The
idea is to gate the FPGA's NCO output with the PWM or PDM pattern to
produce this square-sine signal for the carrier while still following
the NCO's phase offset for the phase modulation component of the
signal.

## Consider Digital Pre-Distortion
Digitally distort the input signal to the PA that is the inverse of
the PA's nonlinear distortion(s). This would also be applied on a
wave-to-wave basis by the FPGA by looking up values in internal FPGA
table RAMs on the fly. The table RAMs' contents would be occasionally
updated by the microcontroller (through SPI) based on measurements of
the actual distortion (via the receive path's ADC, perhaps) or based
on drift of the factors that lead to the distortion compared to a
baseline assumption that is baseline precalculated. The drift factors
are things like temperature, input supply voltage, and load impedance.
(The microcontroller already has to track input supply voltage to do
its PWM calculations for the EER envelope buck converter.)
