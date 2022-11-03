from operator import ne
import serial.tools.list_ports
import serial as sr
import paho.mqtt.client as mqtt_client
import time, random
import numpy as np

def map(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def help_note():
    print(
"""List of commands:
0 - Exit
1 - Send current value
2 - Send mean value
3 - Stream (20 seconds)
4 - Stream min, max and current values (20 seconds)
5 - Print list of commands"""
    )

port="COM7"
broker = "broker.emqx.io"
my_id = 999
duration = 20
queue = []
avg_value = 0
need_input = True
max_val = 0
min_val = 0
client = mqtt_client.Client(f'lab_{random.randint(10000, 999999)}')
client.connect(broker)
arduino = sr.Serial(port=port, baudrate=9600)

help_note()
while True:
    if need_input:
        command = int(input("Input: "))
    if (command == 5):
        help_note()
        continue
    elif (command == 0):
        arduino.close()
        break
    
    arduino.write(np.array([1], dtype='uint8').tobytes())
    time.sleep(0.01)

    while arduino.inWaiting() < 2:
        pass

    response = arduino.read(2)  # Прочитали
    response = [int(byte_) for byte_ in response]   # массив байт в массив int8
    response = (response[0] << 8 & 0xFF00) + (response[1] & 0xFF)   # Взяли число
    response = map(response, 0, 1024, 0, 100)   # Смена диапазона
    queue = [response] + queue  # Фиксируем новое значение
    avg_value += response
    if len(queue) >= 100:
        avg_value -= queue.pop()

    if command == 1:
        client.publish(f'lab/{my_id}/photo/instant', response) 
    elif command == 2:
        client.publish(f'lab/{my_id}/photo/averge', avg_value/len(queue)) 
    elif command == 3:
        if need_input:
            timer_start = time.time()
            need_input = False
        if time.time() - timer_start >= duration:
            need_input = True
        client.publish(f'lab/{my_id}/photo/stream', response)
    elif command == 4:
        if need_input:
            timer_start = time.time()
            need_input = False
        if time.time() - timer_start >= duration:
            need_input = True
        client.publish(f'lab/{my_id}/photo/max', max(queue))
        client.publish(f'lab/{my_id}/photo/min', min(queue))
        client.publish(f'lab/{my_id}/photo/porog', response)

client.disconnect()
