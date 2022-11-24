import paho.mqtt.client as mqtt_client
import random
import time
import serial

broker = "broker.emqx.io" 

client = mqtt_client.Client(f"lab_{random.randint(10000, 99999)}")

def get_connection(port):
    ser = serial.Serial(port, timeout=1)
    return ser

arr = []
avg_all = 0
avg = 0
duration = 20
stinput = True

if __name__ == '__main__':
    ser = get_connection("COM3")
    client.connect(broker)
    print("""Выберете команду:
            1 - передача моментальных значений сеносора
            2 - передача усредненных данных
            3 - потоковая передача данных
            4 - Stream min, max and current values (20 seconds)
            5 - по порогу включение света""")

    while(True):
        if stinput:
            command = int(input("Введите: "))

        while ser.inWaiting() < 2:
            pass
        
        val = ser.read(2)
        result = val.decode()

        if(result!=""):
            result = int(result)
            arr = [result] + arr
            avg_all += int(result)
        if(len(arr)>=100):
            avg = avg_all / 100
            avg_all -= arr.pop()
        if(len(arr) < 100 and len(arr) > 0):
            avg = avg_all / len(arr)


        if command == 1:
            client.publish('lab/UNIQUE_ID/photo/instant', result)
        elif command == 2:
            client.publish('lab/UNIQUE_ID/photo/averge', avg)
        elif command == 3:
            if stinput:
                timer_start = time.time()
                stinput = False
            if time.time() - timer_start >= duration:
                stinput = True
            client.publish('lab/UNIQUE_ID/photo/stream', result)
        elif command == 4:
            if stinput:
                timer_start = time.time()
                stinput = False
            if time.time() - timer_start >= duration:
                stinput = True
            client.publish('lab/UNIQUE_ID/photo/stream4', result)
        elif command == 5:
            if stinput:
                timer_start = time.time()
                stinput = False
            if time.time() - timer_start >= duration:
                stinput = True
            client.publish('lab/UNIQUE_ID/photo/mean', (max(arr) + min(arr)) / 2)
            client.publish('lab/UNIQUE_ID/photo/porog', result)
client.disconnect()
