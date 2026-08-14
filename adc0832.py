import RPi.GPIO as GPIO
import time

def read_adc(cs_pin, clk_pin, dio_pin, channel=0):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(cs_pin, GPIO.OUT)
    GPIO.setup(clk_pin, GPIO.OUT)
    GPIO.setup(dio_pin, GPIO.OUT)

    # Start - CS low
    GPIO.output(cs_pin, GPIO.LOW)
    time.sleep(0.002)

    # Start bit
    GPIO.output(clk_pin, GPIO.LOW)
    GPIO.output(dio_pin, GPIO.HIGH)
    time.sleep(0.002)
    GPIO.output(clk_pin, GPIO.HIGH)
    time.sleep(0.002)

    # SGL/DIF = 1 (single-ended)
    GPIO.output(clk_pin, GPIO.LOW)
    GPIO.output(dio_pin, GPIO.HIGH)
    time.sleep(0.002)
    GPIO.output(clk_pin, GPIO.HIGH)
    time.sleep(0.002)

    # Channel select: 0=CH0, 1=CH1
    GPIO.output(clk_pin, GPIO.LOW)
    if channel == 0:
        GPIO.output(dio_pin, GPIO.LOW)
    else:
        GPIO.output(dio_pin, GPIO.HIGH)
    time.sleep(0.002)
    GPIO.output(clk_pin, GPIO.HIGH)
    time.sleep(0.002)

    # Switch to input for reading
    GPIO.output(clk_pin, GPIO.LOW)
    time.sleep(0.002)
    GPIO.setup(dio_pin, GPIO.IN)

    # Read 8 bits MSB first
    value_msb = 0
    for i in range(8):
        GPIO.output(clk_pin, GPIO.HIGH)
        time.sleep(0.002)
        bit = GPIO.input(dio_pin)
        value_msb = (value_msb << 1) | bit
        GPIO.output(clk_pin, GPIO.LOW)
        time.sleep(0.002)

    # Read 8 bits LSB (for verification)
    value_lsb = 0
    for i in range(8):
        bit = GPIO.input(dio_pin)
        value_lsb = value_lsb | (bit << i)
        GPIO.output(clk_pin, GPIO.HIGH)
        time.sleep(0.002)
        GPIO.output(clk_pin, GPIO.LOW)
        time.sleep(0.002)

    # End communication
    GPIO.output(cs_pin, GPIO.HIGH)
    GPIO.setup(dio_pin, GPIO.OUT)

    # If both readings match, data is reliable
    if value_msb == value_lsb:
        return value_msb
    return value_msb

if __name__ == "__main__":
    CS = 8
    CLK = 25
    DIO = 24
    try:
        for i in range(10):
            gas = read_adc(CS, CLK, DIO, channel=0)
            flame = read_adc(CS, CLK, DIO, channel=1)
            print(f"Gas: {gas}  |  Flame: {flame}")
            time.sleep(1)
    finally:
        GPIO.cleanup()
