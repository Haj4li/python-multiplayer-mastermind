import socket
import random
import os
import termcolor
import threading


# Coded by Haj4li
# https://github.com/Haj4li/python-multiplayer-mastermind/

# لیست کد های رنگی
colors = ["RED", "GREEN", "YELLOW", "BLUE", "PURPLE", "GRAY"]

colors_map = {1:"RED", 2:"GREEN", 3:"YELLOW", 4:"BLUE", 5:"PURPLE", 6:"GRAY"}

# کد رندوم (در صورت نیاز)
random.shuffle(colors)
passcode = colors[:4]

# کد های قابل نمایش به کاربر به صورت مخفی
show_passcode = ['UNK', 'UNK', 'UNK', 'UNK']

# تعداد شانس های کاربر
chances = 8

# کد حدس زده شده در زمان مورد نظر
guess_codes = [['-', '-', '-', '-'] for x in range(chances)]

# راهنمای کاربر
guess_flags = [['-', '-', '-', '-'] for x in range(chances)]

def clear(): # پاک کردن اسکرین
    os.system("cls")
 
# دریافت اطلاعات تخته
def get_board_data(passcode, guess_codes, guess_flags):
    buffer = ""
    buffer += ("       |")
    for x in passcode:
        buffer += ("\t" + x[:3])
    buffer += "\n"
 
    for i in reversed(range(len(guess_codes))):
        buffer += ("-----------------------------------------------\n")
        buffer += "\n"
        buffer += (guess_flags[i][0] + " " + guess_flags[i][1] + " ") + (guess_flags[i][2]  + " " +  guess_flags[i][3] + "|")
         
        for x in guess_codes[i]:
            show = x[:3]
            # کد گذاری رنگی هر قسمت
            if (x[:3] == "RED"):
                show = termcolor.colored(x[:3],"red")
            elif (x[:3] == "BLU"):
                show = termcolor.colored(x[:3],"blue")
            elif (x[:3] == "GRE"):
                show = termcolor.colored(x[:3],"green")
            elif (x[:3] == "YEL"):
                show = termcolor.colored(x[:3],"yellow")
            elif (x[:3] == "GRE"):
                show = termcolor.colored(x[:3],"grey")
            elif (x[:3] == "PUR"):
                show = termcolor.colored(x[:3],"magenta")
            buffer += ("\t" + show)
        buffer += "\n"
    buffer += ("-----------------------------------------------\n")
    return (buffer)

# تنظیم رمز مورد نظر
def set_code(code):
    global passcode,colors_map
    try:
        code = list(map(int, code.split()))
    except ValueError:
        return ([False,"Error"])
    
    if len(code) != 4:
        return ([False,"Error"])

    flag = 0
    for x in code:
        if x > 6 or x < 1:
            flag = 1

    if flag == 1:           
        return ([False,"Error"])

    # ذخیره رمز
    for i in range(4):
        passcode[i] = colors_map[code[i]] 

    return ([True,passcode])

# تابع اصلی بازی
def game(CLIENT_LIST):
    # متغییر های مورد نیاز
    global colors,colors_map,passcode,show_passcode,chances,guess_codes,guess_flags
    
    clear()
    # نوبت فعلی
    turn = 0

    coder = random.randint(0,2) # مشخص کردن رمزنگار به صورت تصادفی
    CLIENT_LIST[coder].send("coder:Server : You're the coder ! Please send me the code ...".encode())
    PLAYERS = []
    for i in CLIENT_LIST:
        if (i != CLIENT_LIST[coder]):
            PLAYERS.append(i) # جدا کردن لیست بازیکنان از رمزنگار
            i.send(("Server : Waiting for {} to specify the code ... ".format(coder+1)).encode())
    
    checkCode = False
    while(not checkCode): # بررسی درست بودن کد از طرف رمزنگار
        codinp = CLIENT_LIST[coder].recv(1024).decode()
        if (not codinp):
            print("There is some error !")
            return
        trySet = set_code(codinp)
        checkCode = trySet[0]
        if (checkCode):
            print("The board code set to {} ".format(trySet[1]))
            CLIENT_LIST[coder].send("Server : Your code has set.".encode())
        else:
            CLIENT_LIST[coder].send("Server : Invalid code please try again .".encode())
    cturn = 0 # نوبت بازیکن
    while turn < chances:
        
        if (cturn == 1):
            cturn = 0
        else:
            cturn = 1
        
        buf = get_board_data(show_passcode, guess_codes, guess_flags)
        for i in CLIENT_LIST:
            i.send(("update:"+buf).encode()) # ارسال تخته

        print(buf)
        
        getID = 0
        for i in CLIENT_LIST:
            getID += 1
            if (i == PLAYERS[cturn]):
                break
        
        for i in CLIENT_LIST:
            if (i != PLAYERS[cturn]):
                i.send(("Server : Waiting for {} to send their answer ...".format(getID)).encode())
            else:
                i.send(("guess:Server : Please send your answer : ").encode())
        
        
        while (True):
            gues = PLAYERS[cturn].recv(1024).decode() # دریافت حدس از کاربر فعلی
            
            try: # بررسی قالب بندی حدس
                code = list(map(int, gues.split()))
                if len(code) != 4:
                    clear()
                    PLAYERS[cturn].send(("Server : Invalid input !").encode())
                    continue
                
                flag = 0
                for x in code:
                    if x > 6 or x < 1:
                        flag = 1
         
                if flag == 1:           
                    clear()
                    PLAYERS[cturn].send(("Server : Invalid input !").encode())
                    continue  
                
                PLAYERS[cturn].send(("Server : OK").encode())
                break
            except ValueError:
                PLAYERS[cturn].send(("Server : Invalid input !").encode())
 
        # ذخیره حدس کاربر
        for i in range(4):
            guess_codes[turn][i] = colors_map[code[i]]  
 
        # تنظیم تصادفی راهنمای کاربر
        dummy_passcode = [x for x in passcode]  
 
        pos = 0
 
        # مشخص کردن راهنما
        for x in code:
            if colors_map[x] in dummy_passcode:
                if code.index(x) == passcode.index(colors_map[x]):
                    guess_flags[turn][pos] = 'R'
                else:
                    guess_flags[turn][pos] = 'W'
                pos += 1
                dummy_passcode.remove(colors_map[x])
 
        random.shuffle(guess_flags[turn])               
 
 
        # بررسی برد بازیکن
        if guess_codes[turn] == passcode:
            clear()
            buf = get_board_data(show_passcode, guess_codes, guess_flags)
            for i in CLIENT_LIST:
                i.send(("update:"+buf).encode())
                i.send(("Server : {} Wins !".format(getID)).encode())
            print(buf)
            break

        turn += 1          
        clear()
 
    # بررسی باخت
    if turn == chances:
        clear()
        buf = (get_board_data(passcode, guess_codes, guess_flags))
        for i in CLIENT_LIST:
            i.send(("update:"+buf).encode())
            i.send(("Server : Out of chances !\n" + "The Code Was : " + str(passcode)).encode())
        print(buf)
        print(passcode)

def onConnect(client,addr,id):
    print(str(addr) + " Just Connected {} .".format(id))
    client.send(("{}Welcome {}st Player !, waiting fot other players to join ...".format(id,id)).encode())

# The Main function
if __name__ == '__main__':

    # مقدار دهی متغییر های اولیه
    HOST = '127.0.0.1' # ادرس ای پی برای بایند و راه اندازی سرور
    PORT = 9500 # پورت مورد نیاز
    ID = 0 # ایدی برای رصد کلاینت های متصل شده
    
    CLIENT_LIST = []
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # ساخت یک آبجکت از کلاس سوکت 
    sock.bind((HOST,PORT)) # بایند سوکت به ادرس و پورت داده شده 
    sock.listen() # شروع انتظار سوکت برای اتصالات ورودی
    
    print("Server started on {}:{}".format(HOST,PORT))
    
    while True:
        connection,address = sock.accept() # دریافت اتصالات ورودی 
        ID += 1 # افزودن 1 به تعداد ایدی های کلاینت
        if (ID > 3):
            print("Server cannot handle more connections !")
            connection.close()
            break
        else:
            CLIENT_LIST.append(connection)
            threading.Thread(target=onConnect, args=(connection,address,ID,)).start() # ورود بازیکن جدید به بازی
        if (ID == 3):
            print("Starting Game ...")
            break
    
    try:
        game(CLIENT_LIST) # شروع بازی 
    except:
        pass
    
    for client in CLIENT_LIST:
        try:
            client.close()
        except:
            print("Error in closing connection ...")
    
    print("Server Closed .")
    sock.close() # بستن سرور
