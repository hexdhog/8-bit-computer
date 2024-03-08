#include <math.h>
#include <stdint.h>
#include <stdbool.h>
#include <Arduino.h>

#define UART_HEADER			0xcafebabe
#define UART_ACTION_READ	0
#define UART_ACTION_WRITE	1

#define SHIFT_DATA			2
#define SHIFT_CLK			3
#define SHIFT_LATCH			4

#define EEPROM_IO_0			5
#define EEPROM_IO_1			6
#define EEPROM_IO_2			7
#define EEPROM_IO_3			8
#define EEPROM_IO_4			9
#define EEPROM_IO_5			10
#define EEPROM_IO_6			11
#define EEPROM_IO_7			12
#define EEPROM_IO_COUNT		8
#define EEPROM_WRITE_ENABLE	13
#define EEPROM_SIZE			2048

const uint8_t eeprom_io[EEPROM_IO_COUNT] = {
	EEPROM_IO_0,
	EEPROM_IO_1,
	EEPROM_IO_2,
	EEPROM_IO_3,
	EEPROM_IO_4,
	EEPROM_IO_5,
	EEPROM_IO_6,
	EEPROM_IO_7
};

#define DEBUG 0

void reg_write(const uint16_t data) {
#if DEBUG > 0
	char buff[24] = {};
	snprintf(buff, sizeof(buff), "reg_write: %04x", data);
	Serial.println(buff);
#endif
	pinMode(SHIFT_DATA, OUTPUT);
	shiftOut(SHIFT_DATA, SHIFT_CLK, MSBFIRST, data >> 8);
	shiftOut(SHIFT_DATA, SHIFT_CLK, MSBFIRST, data & 0xff);
	digitalWrite(SHIFT_LATCH, HIGH);
	digitalWrite(SHIFT_LATCH, LOW);
}

void set_address(const uint16_t address, const bool output) {
	reg_write((output ? 0 : 1) << 15 | (address & 0x07ff));
}

void eeprom_io_set(uint8_t mode) {
	for (uint8_t i = 0; i < EEPROM_IO_COUNT; i++) pinMode(eeprom_io[i], mode);
}

void eeprom_write() {
	digitalWrite(EEPROM_WRITE_ENABLE, LOW);
	delayMicroseconds(1);
	digitalWrite(EEPROM_WRITE_ENABLE, HIGH);
	delay(10);
}

void eeprom_write(const uint16_t address, const uint8_t data) {
	eeprom_io_set(OUTPUT);
	set_address(address, false);
	for (uint8_t i = 0; i < EEPROM_IO_COUNT; i++) digitalWrite(eeprom_io[i], data >> i & 1);
	eeprom_write();
}

void eeprom_write(const uint16_t address, const void * data, const size_t size) {
	for (size_t i = 0; i < size && address + i < EEPROM_SIZE ; i++) eeprom_write(address + i, *(((uint8_t *) data) + i));
}

void eeprom_write(const uint16_t address, const size_t size, const uint8_t value) {
	for (size_t i = 0; i < size && address + i < EEPROM_SIZE ; i++) eeprom_write(address + i, value);
}

uint8_t eeprom_read(const uint16_t address) {
	eeprom_io_set(INPUT);
	set_address(address, true);
	uint8_t value = 0;
	for (uint8_t i = 0; i < EEPROM_IO_COUNT; i++) value |= digitalRead(eeprom_io[i]) << i;
	return value;
}

size_t eeprom_read(const uint16_t address, const size_t size, void * const buffer, const size_t length) {
	if (buffer == nullptr) return 0;
	size_t i = 0;
	for (; i < size && i < length && address + i < EEPROM_SIZE; i++) *(((uint8_t *) buffer) + i) = eeprom_read(address + i);
	return i;
}

void setup() {
	Serial.begin(115200);
	while (!Serial);

	pinMode(SHIFT_DATA, OUTPUT);
	digitalWrite(SHIFT_DATA, LOW);
	pinMode(SHIFT_CLK, OUTPUT);
	digitalWrite(SHIFT_CLK, LOW);
	pinMode(SHIFT_LATCH, OUTPUT);
	digitalWrite(SHIFT_LATCH, LOW);
	digitalWrite(EEPROM_WRITE_ENABLE, HIGH);
	pinMode(EEPROM_WRITE_ENABLE, OUTPUT);
}

void loop() {
	uint32_t header = 0;
	while (header != UART_HEADER) {
		if (Serial.available() > 0) header = header << 8 | Serial.read();
		delay(1);
	}

	while (Serial.available() < 5);
	uint8_t action = Serial.read();
	uint16_t addr = Serial.read() << 8 | Serial.read();
	uint16_t size = Serial.read() << 8 | Serial.read();
	uint8_t *buffer = (uint8_t *) malloc(size);
  if (buffer == nullptr) return;
	memset(buffer, 0, size);
	uint16_t rsize = addr + size > EEPROM_SIZE ? EEPROM_SIZE - addr : size;

	switch (action) {
		case UART_ACTION_READ: {
			for (uint16_t i = 0; i < rsize; i++) buffer[i] = eeprom_read(addr + i);
			break;
		}
		case UART_ACTION_WRITE: {
			uint16_t i = 0;
			while (i < size) if (Serial.available() > 0) buffer[i++] = Serial.read();
			eeprom_write(addr, buffer, rsize);
			break;
		}
		default: {
			action = 0xff;
			break;
		}
	}

	Serial.write(UART_HEADER >> 24 & 0xff);
	Serial.write(UART_HEADER >> 16 & 0xff);
	Serial.write(UART_HEADER >> 8 & 0xff);
	Serial.write(UART_HEADER & 0xff);
	Serial.write(action);
	Serial.write(addr >> 8 & 0xff);
	Serial.write(addr & 0xff);
	Serial.write(rsize >> 8 & 0xff);
	Serial.write(rsize & 0xff);
	for (uint16_t i = 0; i < rsize; i++) Serial.write(buffer[i]);
	free(buffer);
}
