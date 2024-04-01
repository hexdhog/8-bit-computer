.text
	# copy initial values to their corresponding address
	# this way, if the program restarts, it will always start from the beginning of the sequence
	LDA 13
	STA 15
	LDA 12
	STA 14
	ADD 15	# load value at address 12 (second value in data section) and add the value to register A
	OUT		# display value of register A on the 7-segment display
	STA 15	# store the value of register A to address 15
	ADD 14	# load value at address 14 and add the value to register A
	OUT		# display value of register A on the 7-segment display
	STA 14	# store the value of register A to address 14
	J 4		# jump to the instruction at address 1 (ADD 15)
	HLT		# halt the computer

.data
	0		# first initial value
	1		# second initial value
	0		# first value address (will be overwritten upon program start)
	0		# second value address (will be overwritten upon program start)
