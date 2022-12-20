import paho.mqtt.client as mqtt_client
import random
import time
import serial

broker = "broker.emqx.io" 

client = mqtt_client.Client(f"lab_{random.randint(10000, 99999)}")

def get_connection(port): //подключение к порту
    ser = serial.Serial(port, timeout=1)
    return ser

arr = []
avg_all = 0
avg = 0
duration = 20
stinput = True

if __name__ == '__main__': //подключаемся и выводим сообщение
    ser = get_connection("COM3")
    client.connect(broker)
    print("""Выберете команду:
            1 - передача моментальных значений сеносора
            2 - передача усредненных данных
            3 - потоковая передача данных
            4 - Stream min, max and current values (20 seconds)
            5 - по порогу включение света""")

    while(True): //чтобы можно было ввести команду
        if stinput:
            command = int(input("Введите: ")) //считываем номер команды

        while ser.inWaiting() < 2:
            pass
        
        val = ser.read(2) //считываю значения
        result = val.decode() //декодим

        if(result!=""): //если не пустая строка 
            result = int(result) //переводим в инт
            arr = [result] + arr //добавляем в массив
            avg_all += int(result) //суммируем все что приходит
        if(len(arr)>=100): //если длина массива больше 100
            avg = avg_all / 100 //чтобы найти среднее
            avg_all -= arr.pop() //удаляем самый старый
        if(len(arr) < 100 and len(arr) > 0): //если еще не 100
            avg = avg_all / len(arr) //находим среднее


        if command == 1: 
            client.publish('lab/UNIQUE_ID/photo/instant', result) //моментальные значения в диапазоне от 0 до 100
        elif command == 2:
            client.publish('lab/UNIQUE_ID/photo/averge', avg) //передаем средние данные
        elif command == 3:
            if stinput:
                timer_start = time.time() //начинаем считать время и перестаем считать команды
                stinput = False
            if time.time() - timer_start >= duration: //если время закончилось мы снова приримаем командв
                stinput = True
            client.publish('lab/UNIQUE_ID/photo/stream', result) 
        elif command == 4: //то же что и 3, отличия в другом файле
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
            client.publish('lab/UNIQUE_ID/photo/mean', (max(arr) + min(arr)) / 2) //передаем порог
            client.publish('lab/UNIQUE_ID/photo/porog', result)
client.disconnect()
