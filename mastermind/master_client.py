import socket
import os

# Coded by Haj4li
# https://github.com/Haj4li/python-multiplayer-mastermind/


# مقدار دهی متغییر های اولیه
HOST = '127.0.0.1' # آدرس ایپی برای اتصال به سرور
PORT = 9500 # پورت مورد نیاز
myTurn = False
myID = 0

menu = "-----------------------------------------\n" # نمایش منو بازی برای کاربر
menu += "\t\tMenu\n"
menu += "-----------------------------------------\n"
menu += "Enter code using numbers.\n"
menu += "1 - RED, 2 - GREEN, 3 - YELLOW, 4 - BLUE, 5 - PURPLE, 6 - GRAY\n"
menu += "Example: RED YELLOW GRAY PURPLE ---> 1 3 6 5\n"
menu += "-----------------------------------------\n"

def cls(): # پاک کردن کنسول
    os.system("cls")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: # ایجاد سوکت و شروع به کار
    s.connect((HOST, PORT)) # تلاش برای اتصال به ادرس و پورت 
    
    msg = s.recv(1024).decode()# پیام دریافتی از سرور
    myID = int(msg[:1])

    msg = msg[1:]
    print(msg)
    
    inp = "" # ورودی کاربر
    while True: # ایجاد یک حلقه برای دریافت و ارسال پیام
        try:
            msg = s.recv(1024).decode() # تلاش برای دریافت پاسخ از سمت سرور
            if (not msg): # بررسی پیام سرور برای بستن اتصال
                print("Connection Terminated .")
                break

            if (msg[:7] == "update:"):# دریافت آپدیت از سرور
                msg = msg[7:] 
                cls()
                print(menu)
                print("Your ID : " + str(myID))
                print(msg) # چاپ پیام سرور
            elif (msg[:6] == "coder:"): # بررسی پیام برای رمزنگار بودن کاربر
            
                print(msg[6:])
                while True:
                    guess = input("Enter Your Code : ") # دریافت ورودی برای حرکت 
                    if (guess):
                        s.send(guess.encode())
                        msg = s.recv(1024).decode()
                        print(msg)
                        if (msg != "Server : Invalid code please try again ."): # در صورتی که کد مورد قبول سرور باشد ادا
                            break
                    else:
                        print("Check Error : Invalid Code !")

            elif (msg[:6] == "guess:"): # بررسی نوبت فعلی 
                print(msg[6:])
                while True:
                    guess = input("Enter your choice = ") # دریافت ورودی برای حرکت 
                    if (guess):
                        s.send(guess.encode())
                        msg = s.recv(1024).decode()
                        print(msg)
                        if (msg != "Server : Invalid input !"): # در صورتی که حرکت مورد قبول سرور باشد ادامه می دهیم
                            break
                    else:
                        print("Check Error : Invalid move")
            else:
                print(msg) # چاپ پیام سرور
        except:
            print("Error in receving data from server .")
            break
    print("Disconnected .")
    s.close() # قطع اتصال 
