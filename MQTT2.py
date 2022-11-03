import paho.mqtt.client as mqtt_client
import random
import time
import serial

UNIQUE_ID = 999
port = "COM9"
ser = serial.Serial(port, 9600)

min_ =0
min_illum = 0
max_illum = 0
stack = []
stack_len = 5

### функция включения светодиода при проходе порога
def illum(data, topic):
    global max_illum
    global min_illum
    if("/max" in topic):
        max_illum = data
    elif("/min" in topic):
        min_illum = data
    else:
        mean = (max_illum+min_illum)/2
        if (data>=mean):
            ser.write("1".encode())
        else:
            ser.write("0".encode())
        print("mean =", mean, "data =", data)
        


### Функция, включущая светодиод при уменьшии значей датчика
def dec_inc(data):
    print(f"recieved sensor level{ data}")
    global stack
    if(len(stack)>1):
        dw_cnt = 0
        up_cnt = 0
        for i in range(1, len(stack)):
            if (stack[i] < stack[i-1]):
                dw_cnt += 1
        for i in range(1, len(stack)):
            if (stack[i] >= stack[i-1]):
                up_cnt += 1
        if(dw_cnt == len(stack)-1):
            ser.write("1".encode())
        elif(up_cnt == len(stack)-1):
            ser.write("0".encode())

### тестовая функция для записи на ардуино
def write(data):       
    print(f"recieved command {data}")
    if (data == "1"):
        ser.write("1".encode())
        time.sleep(2)
    if (data =="0"):
        ser.write("0".encode())
        time.sleep(2)

def on_message(client, data, message):
    data = float(message.payload.decode("utf-8"))
    topic = message.topic
    global stack
    global stack_len
    # topic = str(message.topic.decode("utf-8"))
    print(f"Received message: {data}")
    if ("/stream" in topic):
        stack.append(data)
        if len(stack) > stack_len:
            stack.pop(0)
    # dec_inc(data)  ### раскоментировать для проверки 4 пункта задания
    
    illum(data, topic)
    return data
    


broker = "broker.emqx.io" 

client = mqtt_client.Client(f"lab_{random.randint(10000, 99999)}")
client.on_message = on_message


try:
    client.connect(broker)
except Exception:
    print("Failed to connect. Check network")
    exit()    

client.loop_start()


print("Subscribing")    

client.subscribe(f'lab/{UNIQUE_ID}/photo/instant')
client.subscribe(f'lab/{UNIQUE_ID}/photo/average')
    
client.subscribe(f'lab/{UNIQUE_ID}/photo/min')
client.subscribe(f'lab/{UNIQUE_ID}/photo/max')
client.subscribe(f'lab/{UNIQUE_ID}/photo/stream')
client.subscribe(f'lab/{UNIQUE_ID}/photo/porog')
time.sleep(600)
client.disconnect()
client.loop_stop()
print("Stop communication")
