from utils.reader import measure_sampling_rate


if __name__ == "__main__":
    COM_PORT = 'COM8'
    BAUD_RATE = 115200

    measure_sampling_rate(COM_PORT, BAUD_RATE, 10000)