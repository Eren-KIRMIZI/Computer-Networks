import tkinter as tk
from tkinter import ttk
import threading
import time
import random

class SyncAsyncDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("Senkron vs Asenkron Ağ Programlama")
        self.root.geometry("850x600")
        self.root.configure(bg="#0b132b")

        self.is_running = False
        self.build_ui()

    def build_ui(self):
        title = tk.Label(
            self.root,
            text="Senkron vs Asenkron (Ağ Programlama)",
            font=("Segoe UI", 20, "bold"),
            bg="#0b132b",
            fg="#18baff"
        )
        title.pack(pady=10)

        desc = tk.Label(
            self.root,
            text="Senkron: İşlemler sıralı yapılır  |  Asenkron: İşlemler aynı anda yürür",
            font=("Segoe UI", 11),
            bg="#0b132b",
            fg="#8acaff"
        )
        desc.pack()

        box = tk.Frame(self.root, bg="#1c2541", bd=2, relief=tk.RIDGE)
        box.pack(pady=15, padx=15, fill=tk.X)

        tk.Label(
            box,
            text="Simülasyon Tipi:",
            bg="#1c2541",
            fg="#c7d5f0",
            font=("Segoe UI", 10)
        ).grid(row=0, column=0, padx=10, pady=10)

        self.mode = tk.StringVar(value="sync")
        tk.Radiobutton(box, text="Senkron", variable=self.mode, value="sync",
                       bg="#1c2541", fg="#d7e3ff", selectcolor="#3a506b")\
            .grid(row=0, column=1)
        tk.Radiobutton(box, text="Asenkron", variable=self.mode, value="async",
                       bg="#1c2541", fg="#d7e3ff", selectcolor="#3a506b")\
            .grid(row=0, column=2)

        self.start_button = tk.Button(
            box,
            text="Başlat",
            bg="#18baff",
            fg="#0b132b",
            font=("Segoe UI", 11, "bold"),
            command=self.start_sim
        )
        self.start_button.grid(row=0, column=3, padx=20)

        # Progress bars for 3 tasks
        task_box = tk.Frame(self.root, bg="#1c2541", bd=2, relief=tk.RIDGE)
        task_box.pack(pady=15, padx=15, fill=tk.X)

        tk.Label(
            task_box,
            text="Görevler (Sunucuya istek simülasyonu)",
            bg="#1c2541",
            fg="#18baff",
            font=("Segoe UI", 11, "bold")
        ).pack(pady=10)

        self.bars = []
        for i in range(3):
            lbl = tk.Label(task_box, text=f"Görev {i+1}",
                           bg="#1c2541", fg="#d7e3ff")
            lbl.pack()
            bar = ttk.Progressbar(task_box, length=700)
            bar.pack(pady=5)
            self.bars.append(bar)

        # Status log
        self.log = tk.Text(self.root, height=10, bg="#0b132b", fg="#d7e3ff", font=("Consolas", 10))
        self.log.pack(pady=10, padx=15, fill=tk.X)

    # Start
    def start_sim(self):
        if self.is_running:
            return

        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.log.delete("1.0", tk.END)

        for bar in self.bars:
            bar["value"] = 0

        mode = self.mode.get()

        if mode == "sync":
            threading.Thread(target=self.run_sync).start()
        else:
            threading.Thread(target=self.run_async).start()

    # Senkron (Blocking) İş
    def run_sync(self):
        self.write_log("Senkron mod başlatıldı.\n")

        for i in range(3):
            self.write_log(f"Görev {i+1} başladı. (Blocking)")
            self.simulate_task(i)
            self.write_log(f"Görev {i+1} bitti.\n")

        self.finish()

    # Asenkron (Concurrent) İş
    def run_async(self):
        self.write_log("Asenkron mod başlatıldı.\n")

        threads = []
        for i in range(3):
            t = threading.Thread(target=self.simulate_async_task, args=(i,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        self.finish()

    # Blocking I/O simülasyonu
    def simulate_task(self, index):
        duration = random.uniform(1.5, 3.5)
        start = time.time()

        while time.time() - start < duration:
            progress = ((time.time() - start) / duration) * 100
            self.update_bar(index, progress)
            time.sleep(0.1)

        self.update_bar(index, 100)

    # Non-blocking simülasyon
    def simulate_async_task(self, index):
        self.write_log(f"Görev {index+1} başladı. (Non-blocking)")
        self.simulate_task(index)
        self.write_log(f"Görev {index+1} bitti.\n")

    def update_bar(self, index, value):
        self.root.after(0, self.bars[index].config, {"value": value})

    def write_log(self, text):
        self.root.after(0, lambda: self.log.insert(tk.END, text))

    def finish(self):
        self.is_running = False
        self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
        self.write_log("\nTamamlandı.\n")


def main():
    root = tk.Tk()
    app = SyncAsyncDemo(root)
    root.mainloop()

if __name__ == "__main__":
    main()
