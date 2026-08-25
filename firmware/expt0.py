""" Read all the data from the Arduino and print it to the console. """

from utils.reader import read_arduino_binary

if __name__ == "__main__":
    COM_PORT = "COM8"  # Update this to your port
    BAUD_RATE = 115200

    sensor_stream = read_arduino_binary(COM_PORT, BAUD_RATE)

    print("Waiting for data...")

    for readings in sensor_stream:
        print(f"Readings: {readings}")