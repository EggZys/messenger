import socket
import tkinter as tk
from tkinter import scrolledtext
import threading
import ipaddress

def send_message():
    message = entry.get()
    if message:
        chat_log.configure(state=tk.NORMAL)
        chat_log.insert(tk.END, f"Вы: {message}\n")
        chat_log.see(tk.END)
        chat_log.configure(state=tk.DISABLED)
        entry.delete(0, tk.END)
        try:
            sock.sendall(message.encode())
        except Exception as e:
            chat_log.configure(state=tk.NORMAL)
            chat_log.insert(tk.END, f"Ошибка отправки: {e}\n")
            chat_log.configure(state=tk.DISABLED)
            sock.close()
            root.destroy()


def receive_message():
    while True:
        try:
            data = sock.recv(1024).decode()
            if data:
                chat_log.configure(state=tk.NORMAL)
                chat_log.insert(tk.END, data + "\n")
                chat_log.see(tk.END)
                chat_log.configure(state=tk.DISABLED)
        except ConnectionResetError:
            chat_log.configure(state=tk.NORMAL)
            chat_log.insert(tk.END, "Соединение разорвано.\n")
            chat_log.configure(state=tk.DISABLED)
            sock.close()
            root.destroy()
            break
        except Exception as e:
            chat_log.configure(state=tk.NORMAL)
            chat_log.insert(tk.END, f"Ошибка приема: {e}\n")
            chat_log.configure(state=tk.DISABLED)
            sock.close()
            root.destroy()
            break


def start_client():
    global sock, host_entry, port_entry
    try:
        host = host_entry.get()
        port = int(port_entry.get())
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if ':' in host: # Если это IPv6-адрес
          sock.connect((host,port))
        else: # Если это IPv4-адрес
          try:
            ipaddress.ip_address(host)
            sock.connect((host, port))
          except ValueError:
            print("Неверный IPv4 адрес")
            exit()
        print("Подключение к серверу установлено.")
        receiver_thread = threading.Thread(target=receive_message)
        receiver_thread.daemon = True
        receiver_thread.start()
        root.mainloop()


    except ValueError as e:
      chat_log.configure(state=tk.NORMAL)
      chat_log.insert(tk.END, f"Ошибка ввода: {e}\n")
      chat_log.configure(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Simple Messenger Client")

    host_label = tk.Label(root, text="Хост:")
    host_label.pack()
    host_entry = tk.Entry(root)
    host_entry.pack()

    port_label = tk.Label(root, text="Порт:")
    port_label.pack()
    port_entry = tk.Entry(root)
    port_entry.pack()

    connect_button = tk.Button(root, text="Подключиться", command=start_client)
    connect_button.pack()

    chat_log = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED)
    chat_log.pack(expand=True, fill='both')

    entry = tk.Entry(root)
    entry.pack()

    send_button = tk.Button(root, text="Отправить", command=send_message)
    send_button.pack()
    root.mainloop()