import socket
import tkinter as tk
from tkinter import scrolledtext
import threading
import ipaddress

def send_message():
    message = text_area.get("1.0", tk.END).strip()
    if message:
        chat_log.configure(state=tk.NORMAL)
        chat_log.insert(tk.END, f"{message}\n")  # Используем глобальную nickname
        chat_log.see(tk.END)
        chat_log.configure(state=tk.DISABLED)
        text_area.delete("1.0", tk.END)
        try:
            sock.sendall(f"Вы: {message}".encode())
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
                sender, message = data.split(":", 1)
                chat_log.configure(state=tk.NORMAL)
                chat_log.insert(tk.END, f"{sender}: {message}\n")
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

def start_client(host, port, nickname_from_entry):
    global sock, chat_log, text_area, nickname  # Объявляем nickname глобальной переменной
    nickname = nickname_from_entry # Присваиваем значение из поля ввода

    try:
        if ':' in host:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            try:
                ipaddress.ip_address(host)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            except ValueError:
                chat_log.configure(state=tk.NORMAL)
                chat_log.insert(tk.END, f"Неверный IP-адрес {host}\n")
                chat_log.configure(state=tk.DISABLED)
                return

        sock.connect((host, port))

        receiver_thread = threading.Thread(target=receive_message)
        receiver_thread.daemon = True
        receiver_thread.start()

        connect_frame.pack_forget()
        chat_frame.pack(expand=True, fill='both')

    except (ConnectionRefusedError, OSError) as e:
        chat_log.configure(state=tk.NORMAL)
        chat_log.insert(tk.END, f"Ошибка подключения: {e}\n")
        chat_log.configure(state=tk.DISABLED)


def copy_text():
    try:
        selected_text = chat_log.selection_get()
        root.clipboard_clear()
        root.clipboard_append(selected_text)
    except tk.TclError:
        pass


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Simple Messenger Client")

    connect_frame = tk.Frame(root)
    connect_frame.pack(pady=10)

    host_label = tk.Label(connect_frame, text="Хост:")
    host_label.grid(row=0, column=0)
    host_entry = tk.Entry(connect_frame)
    host_entry.grid(row=0, column=1)
    host_entry.insert(0, "185.149.50.20") # Замените на ваш публичный IP или доменное имя

    port_label = tk.Label(connect_frame, text="Порт:")
    port_label.grid(row=1, column=0)
    port_entry = tk.Entry(connect_frame)
    port_entry.grid(row=1, column=1)
    port_entry.insert(0, "22837")

    nickname_label = tk.Label(connect_frame, text="Никнейм:")
    nickname_label.grid(row=2, column=0)
    nickname_entry = tk.Entry(connect_frame)
    nickname_entry.grid(row=2, column=1)


    chat_frame = tk.Frame(root)
    chat_frame.pack(expand=True, fill='both')
    chat_frame.pack_forget()

    chat_log = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, state=tk.DISABLED)
    chat_log.pack(expand=True, fill='both')
    chat_log.bind("<Button-3>", lambda event: copy_text())

    text_area = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, height=3)
    text_area.pack()

    send_button = tk.Button(chat_frame, text="Отправить", command=send_message)
    send_button.pack()

    connect_button = tk.Button(connect_frame, text="Подключиться", command=lambda: start_client(host_entry.get(), int(port_entry.get()), nickname_entry.get()))
    connect_button.grid(row=3, columnspan=2)


    root.mainloop()
