import tkinter as tk
from tkinter import messagebox
import threading
import time
from tkinter import ttk
from threading import Lock


## Класс для управления потоками
class ThreadManager:
    def __init__(self):
        self.threads = []
        self.lock = Lock()

    def add_thread(self, thread):
        with self.lock:
            self.threads.append(thread)

    def remove_thread(self, thread):
        with self.lock:
            self.threads.remove(thread)

    def stop_all_threads(self):
        with self.lock:
            for thread in self.threads:
                thread.stop()

# Пользовательский поток
class CustomThread(threading.Thread):
    def __init__(self, thread_manager, name):
        super().__init__()
        self.thread_manager = thread_manager
        self.name = name
        self.stop_event = threading.Event()
        self.start_time = None

    def run(self):
        self.start_time = time.time()
        with open(f"{self.name}.txt", "w") as f:
            f.write(f"Thread {self.name} started at {time.ctime(self.start_time)}\n")

        while not self.stop_event.is_set():
            time.sleep(1)

        end_time = time.time()
        with open(f"{self.name}.txt", "a") as f:
            f.write(f"Thread {self.name} stopped at {time.ctime(end_time)}\n")

        self.thread_manager.remove_thread(self)

    def stop(self):
        self.stop_event.set()

# Основное приложение
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Thread Manager")
        self.geometry("400x550")

        self.thread_manager = ThreadManager()

        self.start_button = tk.Button(self, text="Start", height=2, width=40, command=self.start_thread)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(self, text="Stop", height=2, width=40, command=self.stop_thread)
        self.stop_button.pack(pady=10)

        self.send_button = tk.Button(self, text="Send", height=2, width=40, command=self.send_message)
        self.send_button.pack(pady=10)

        self.exit_button = tk.Button(self, text="Exit", height=2, width=40, command=self.exit_application)
        self.exit_button.pack(pady=10)

        self.message_entry = tk.Entry(self)
        self.message_entry.pack(pady=10)

        self.thread_choice_label = tk.Label(self, text="Choose Thread:")
        self.thread_choice_label.pack(pady=5)

        self.thread_var = tk.StringVar()
        self.thread_var.set("All Threads")
        self.thread_choice = ttk.Combobox(self, textvariable=self.thread_var, values=["All Threads"], height=2, width=40)
        self.thread_choice.pack(pady=10)

        self.thread_info_label = tk.Label(self, text="Active Threads:")
        self.thread_info_label.pack(pady=5)

        self.text_display = tk.Text(self, height=8, width=40)
        self.text_display.pack(pady=10)

        self.update_thread_list()

    def start_thread(self):
        thread_name = f"Thread-{len(self.thread_manager.threads) + 1}"
        new_thread = CustomThread(self.thread_manager, thread_name)
        self.thread_manager.add_thread(new_thread)
        new_thread.start()
        self.update_thread_list()

    def stop_thread(self):
        if self.thread_manager.threads:
            thread_to_stop = self.thread_manager.threads[-1]
            thread_to_stop.stop()
            self.update_thread_list()

    def exit_application(self):
        self.thread_manager.stop_all_threads()
        self.destroy()

    def send_message(self):
        message = self.message_entry.get()
        if not message:
            messagebox.showinfo("Error", "Please enter a message.")
            return

        selected_thread = self.thread_var.get()

        if selected_thread == "All Threads":
            for thread in self.thread_manager.threads:
                with open(f"{thread.name}.txt", "a") as f:
                    f.write(f"Message: {message} at {time.ctime(time.time())}\n")
        else:
            for thread in self.thread_manager.threads:
                if thread.name == selected_thread:
                    with open(f"{thread.name}.txt", "a") as f:
                        f.write(f"Message: {message} at {time.ctime(time.time())}\n")

        self.message_entry.delete(0, tk.END)
        self.update_thread_list()

    def update_thread_list(self):
        active_threads = [thread.name for thread in self.thread_manager.threads if thread.is_alive()]
        self.thread_info_label["text"] = f"Active Threads: {', '.join(active_threads)}"

        self.thread_choice["values"] = ["All Threads"] + active_threads
        self.text_display.delete("1.0", tk.END)
        for thread in self.thread_manager.threads:
            self.text_display.insert(tk.END, f"{thread.name} - {'Running' if thread.is_alive() else 'Stopped'}\n")
        self.after(1000, self.update_thread_list)

if __name__ == "__main__":
    app = Application()
    app.mainloop()
