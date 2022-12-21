import time
import paho.mqtt.client as mqtt_client
import random
import serial

port = "COM9"
ser = serial.Serial(port, 9600)

mean = 0
otvet = 0
listic = []
listic_len = 5

def po_porogu(data, topic): //если значение больше порога -вкл свет, если меньше - выкл (вкл по одному значению)
    global otvet
    global mean
    if("/mean" in topic):
        mean = float(data)
    elif("/porog" in topic):
        otvet = int(data)
    if (otvet >= mean):
        ser.write("1".encode())
    else:
        ser.write("0".encode())
    print("mean =", mean, "data =", data)

def dec_inc(data): //вкл по вектору
    print(f"recieved sensor level{ data}")
    global listic 
    if(len(listic)>1): //если длина больше 1
        down = 0
        up = 0
        for i in range(1, len(listic)): 
            if (listic[i] < listic[i-1] or listic[i] == listic[i-1]): //если знач уб добавляем 
                down += 1
        for i in range(1, len(listic)):
            if (listic[i] >= listic[i-1] or listic[i] == listic[i-1]): //если знач возраст добавляем 
                up += 1
        if(down == len(listic)-1): //если уб
            ser.write("1".encode()) //вкл
        elif(up == len(listic)-1): //если возраст
            ser.write("0".encode()) //выкл

def on_message(client, userdata, message):
    data = str(message.payload.decode("utf-8")) //получаем сообщение
    topic = message.topic //получаем топик
    global listic //чтобы были видны
    global listic_len
    print(f"Received meassage on topic: {data}")
    if ("/stream4" in topic):
        listic.append(data) //добавляем в массив
        if len(listic) > listic_len: //чтобы в масссиве постоянно были обновл знач и опр длина
            listic.pop(0)
        dec_inc(data)

    if ("/mean" in topic or "/porog" in topic): 
        po_porogu(data, topic)
    return data

broker="broker.emqx.io"

client = mqtt_client.Client(f'lab_{random.randint(10000, 99999)}')
client.on_message = on_message

try: //проверяем подключение
    client.connect(broker)
except Exception:
    print('Failed to connect. Check network')
    exit()
    
client.loop_start()
    
print('Subscribing')
client.subscribe('lab/UNIQUE_ID/photo/instant') //подписываемся на топики
client.subscribe('lab/UNIQUE_ID/photo/averge')
client.subscribe('lab/UNIQUE_ID/photo/stream')
client.subscribe('lab/UNIQUE_ID/photo/stream4')
client.subscribe('lab/UNIQUE_ID/photo/mean')
client.subscribe('lab/UNIQUE_ID/photo/porog')
time.sleep(600) //через время ост
client.disconnect()
client.loop_stop()
print('Stop communication')
