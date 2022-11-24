import time
import paho.mqtt.client as mqtt_client
import random
import serial

port = "COM9"
ser = serial.Serial(port, 9600)

mean = 0
otvet = 0
# max_porog = 0
# min_porog = 0
listic = []
listic_len = 5

def po_porogu(data, topic):
    global otvet
    global mean
    if("/mean" in topic):
        mean = float(data)
    elif("/porog" in topic):
        otvet = int(data)
    # else:
    #     mean = (max_porog + min_porog) / 2
    if (otvet >= mean):
        ser.write("1".encode())
    else:
        ser.write("0".encode())
    print("mean =", mean, "data =", data)
    # ser.write("1".encode())

def dec_inc(data):
    print(f"recieved sensor level{ data}")
    global listic
    if(len(listic)>1):
        down = 0
        up = 0
        for i in range(1, len(listic)):
            if (listic[i] < listic[i-1] or listic[i] == listic[i-1]):
                down += 1
        for i in range(1, len(listic)):
            if (listic[i] >= listic[i-1] or listic[i] == listic[i-1]):
                up += 1
        if(down == len(listic)-1):
            ser.write("1".encode())
        elif(up == len(listic)-1):
            ser.write("0".encode())

    
def write(data):
    print(f"recieved command {data}")
    if (data == "1"):
        ser.write("1".encode())
        time.sleep(2)
    if (data =="0"):
        ser.write("0".encode())
        time.sleep(2)

def on_message(client, userdata, message):
    data = str(message.payload.decode("utf-8"))
    topic = message.topic
    global listic
    global listic_len
    #topic = str(message.topic.decode("utf-8"))
    print(f"Received meassage on topic: {data}")
    if ("/stream4" in topic):
        listic.append(data)
        if len(listic) > listic_len:
            listic.pop(0)
        dec_inc(data)

    if ("/mean" in topic or "/porog" in topic):
        po_porogu(data, topic)
    #     stack.append(data)
    # po_porogu(data, topic)
    return data

broker="broker.emqx.io"

client = mqtt_client.Client(f'lab_{random.randint(10000, 99999)}')
client.on_message = on_message

try:
    client.connect(broker)
except Exception:
    print('Failed to connect. Check network')
    exit()
    
client.loop_start()

# wait_time = 5
# sleep_time = 1    
# while not client.is_connected():
#     time.sleep(sleep_time)
#     wait_time -= sleep_time
#     if not wait_time:
#         raise ValueError('Failed to connect. Timeout')
    
print('Subscribing')
client.subscribe('lab/UNIQUE_ID/photo/instant')
client.subscribe('lab/UNIQUE_ID/photo/averge')
client.subscribe('lab/UNIQUE_ID/photo/stream')
client.subscribe('lab/UNIQUE_ID/photo/stream4')
client.subscribe('lab/UNIQUE_ID/photo/mean')
# client.subscribe('lab/UNIQUE_ID/photo/min')
client.subscribe('lab/UNIQUE_ID/photo/porog')
time.sleep(600)
client.disconnect()
client.loop_stop()
print('Stop communication')
