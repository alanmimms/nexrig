# Lowpass filter ahead of mixer

## Chebyshev 30MHz cutoff, 0.5dB ripple, 50ohm

	Order=2 Lowpass Chebyshev Filter
	Pi: 148.9pF 187.6nH 
	T : 372.1nH 75.02pF 
	-----------------------
	Order=3 Lowpass Chebyshev Filter
	Pi: 169.4pF 290.9nH 169.4pF 
	T : 423.4nH 116.4pF 423.4nH 
	-----------------------
	Order=4 Lowpass Chebyshev Filter
	Pi: 177.2pF 316.3nH 251.1pF 223.3nH 
	T : 443.1nH 126.5pF 627.6nH 89.32pF 
	-----------------------
	Order=5 Lowpass Chebyshev Filter
	Pi: 181.0pF 326.2nH 269.6pF 326.2nH 181.0pF 
	T : 452.5nH 130.5pF 674.0nH 130.5pF 452.5nH 
	-----------------------
	Order=6 Lowpass Chebyshev Filter
	Pi: 183.1pF 331.0nH 276.5pF 348.5nH 262.7pF 230.7nH 
	T : 457.7nH 132.4pF 691.4nH 139.4pF 656.8nH 92.27pF 
	-----------------------
	Order=7 Lowpass Chebyshev Filter
	Pi: 184.3pF 333.8nH 279.9pF 356.6nH 279.9pF 333.8nH 184.3pF 
	T : 460.8nH 133.5pF 699.8nH 142.6pF 699.8nH 133.5pF 460.8nH 
	-----------------------
	Order=8 Lowpass Chebyshev Filter
	Pi: 185.2pF 335.5nH 281.9pF 360.5nH 286.1pF 355.1nH 266.2pF 233.3nH 
	T : 462.9nH 134.2pF 704.7nH 144.2pF 715.3nH 142.1pF 665.6nH 93.32pF 
	-----------------------
	Order=9 Lowpass Chebyshev Filter
	Pi: 185.7pF 336.6nH 283.1pF 362.7nH 289.0pF 362.7nH 283.1pF 336.6nH 185.7pF 
	T : 464.3nH 134.6pF 707.7nH 145.1pF 722.6nH 145.1pF 707.7nH 134.6pF 464.3nH 
	-----------------------

	C1: 185.7pF => 180pF
	C2: 283.1pF => 270pF
	C3: 289.0pF => 300pF
	L1: 336.6nH => 330nH
	L2: 362.7nH => 360nH

With standard C and L values the filter is actually better than with
the calculated values.


## Chebyshev 30MHz, 0.1dB, 50ohm

	Order=2 Lowpass Chebyshev Filter
	Pi: 89.45pF 165.0nH 
	T : 223.6nH 66.00pF 
	-----------------------
	Order=3 Lowpass Chebyshev Filter
	Pi: 109.5pF 304.4nH 109.5pF 
	T : 273.6nH 121.7pF 273.6nH 
	-----------------------
	Order=4 Lowpass Chebyshev Filter
	Pi: 117.6pF 346.5nH 187.8pF 217.0nH 
	T : 294.1nH 138.6pF 469.6nH 86.80pF 
	-----------------------
	Order=5 Lowpass Chebyshev Filter
	Pi: 121.7pF 363.7nH 209.6pF 363.7nH 121.7pF 
	T : 304.2nH 145.5pF 523.9nH 145.5pF 304.2nH 
	-----------------------
	Order=6 Lowpass Chebyshev Filter
	Pi: 123.9pF 372.4nH 218.2pF 402.4nH 201.9pF 228.6nH 
	T : 309.9nH 149.0pF 545.4nH 161.0pF 504.8nH 91.45pF 
	-----------------------
	Order=7 Lowpass Chebyshev Filter
	Pi: 125.3pF 377.4nH 222.5pF 417.4nH 222.5pF 377.4nH 125.3pF 
	T : 313.3nH 151.0pF 556.2nH 166.9pF 556.2nH 151.0pF 313.3nH 
	-----------------------
	Order=8 Lowpass Chebyshev Filter
	Pi: 126.2pF 380.6nH 224.9pF 424.7nH 230.2pF 414.9nH 206.3pF 232.8nH 
	T : 315.6nH 152.2pF 562.3nH 169.9pF 575.6nH 166.0pF 515.8nH 93.14pF 
	-----------------------
	Order=9 Lowpass Chebyshev Filter
	Pi: 126.9pF 382.7nH 226.5pF 428.8nH 234.0pF 428.8nH 226.5pF 382.7nH 126.9pF 
	T : 317.2nH 153.1pF 566.2nH 171.5pF 585.0nH 171.5pF 566.2nH 153.1pF 317.2nH 
	-----------------------

	C1: 126.9pF => 130pF
	C2: 226.5pF => 220pF
	C3: 234.0pF => 240pF
	L1: 382.7nH => 390nH
	L2: 428.8nH => 470nH

This is much inferior to the 0.5dB equiripple filter.
