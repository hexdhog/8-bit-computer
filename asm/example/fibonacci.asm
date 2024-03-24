.text
	LDA 9	# load value at address 9 (first value in data section) to A register
	ADD 10	# load value at address 10 (second value in data section) and add the value to register A
	OUT		# display value of register A on the 7-segment display
	STA 10	# store the value of register A to address 10
	ADD 9	# load value at address 9 and add the value to register A
	OUT		# display value of register A on the 7-segment display
	STA 9	# store the value of register A to address 9
	J 1		# jump to the instruction at address 1 (ADD 10)
	HLT		# halt the computer

.data
	0		# store a 0 at address 9
	1		# store a 1 at address 10
