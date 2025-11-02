# L1L2 series config in rx preselector

    L1  L2  L1L2
     0   0    0     Neither L in circuit (L1 hot open (!), L2 hot grounded)
     0   0    1     UNUSED: L1 hot and L2 cold tied together (!)
     0   1    0     L2
     0   1    1     L1++L2
     1   0    0     L1 in circuit, L2 hot grounded
	 1   0    1     UNUSED: L1 in circuit, L2 cold open (!)
     1   1    0     L1||L2
	 1   1    1     UNUSED: L1 in circuit, L2 cold open (!)

L1L2 => L2


    0: link L1 gnd     gnd L2 gnd
    1:  L2c L1 gnd     gnd L2 L1h
    2: link L1 gnd      RF L2 gnd
    3:   RF L1 gnd      RF L2 gnd
    4:   RF L1 gnd     gnd L2 gnd
    5:   RF L1 gnd     gnd L2 link
    6:   RF L1 gnd      RF L2 gnd
    7:   RF L1 gnd      RF L2 link