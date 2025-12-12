import tkinter as tk
from tkinter import ttk
import threading
import time

class LatencyBandwidthDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("Latency vs Bandwidth Demo")
        self.root.geometry("900x500")
        self.root.configure(bg="#0a0e27")

        self.is_running = False
        self.setup_ui()

    def setup_ui(self):
        title = tk.Label(
            self.root,
            text="Latency vs Bandwidth",
            font=("Segoe UI", 20, "bold"),
            bg="#0a0e27",
            fg="#00d4ff"
        )
        title.pack(pady=10)

        subtitle = tk.Label(
            self.root,
            text="Latency geciktirir, Bandwidth hızlandırır",
            font=("Segoe UI", 11),
            bg="#0a0e27",
            fg="#7aa2f7"
        )
        subtitle.pack()

        control = tk.Frame(self.root, bg="#1a1b26", bd=2, relief=tk.RIDGE)
        control.pack(pady=15, padx=20, fill=tk.X)

        # Latency Slider
        tk.Label(control, text="Latency (ms)",
                 bg="#1a1b26", fg="#c0caf5").grid(row=0, column=0, padx=10, pady=10)

        self.latency = tk.IntVar(value=200)
        tk.Scale(
            control, from_=50, to=1000,
            orient=tk.HORIZONTAL,
            variable=self.latency,
            bg="#1a1b26", fg="#c0caf5",
            troughcolor="#24283b",
            highlightthickness=0
        ).grid(row=0, column=1, padx=10)

        # Bandwidth Slider
        tk.Label(control, text="Bandwidth (KB/s)",
                 bg="#1a1b26", fg="#c0caf5").grid(row=1, column=0, padx=10, pady=10)

        self.bandwidth = tk.IntVar(value=200)
        tk.Scale(
            control, from_=50, to=500,
            orient=tk.HORIZONTAL,
            variable=self.bandwidth,
            bg="#1a1b26", fg="#c0caf5",
            troughcolor="#24283b",
            highlightthickness=0
        ).grid(row=1, column=1, padx=10)

        self.start_btn = tk.Button(
            control,
            text="Gönder",
            command=self.start_demo,
            bg="#00d4ff",
            fg="#0a0e27",
            font=("Segoe UI", 11, "bold"),
            padx=20
        )
        self.start_btn.grid(row=0, column=2, rowspan=2, padx=20)

        # Progress Area
        frame = tk.Frame(self.root, bg="#1a1b26", bd=2, relief=tk.RIDGE)
        frame.pack(pady=10, padx=20, fill=tk.X)

        tk.Label(
            frame,
            text="Veri İletimi",
            font=("Segoe UI", 11, "bold"),
            bg="#1a1b26",
            fg="#00d4ff"
        ).pack(pady=10)

        self.progress = ttk.Progressbar(frame, length=700)
        self.progress.pack(pady=20)

        self.status = tk.Label(
            frame,
            text="Hazır",
            bg="#1a1b26",
            fg="#9ece6a",
            font=("Segoe UI", 10)
        )
        self.status.pack(pady=5)

        self.info = tk.Label(
            self.root,
            text="Gecikme yüksekse veri geç başlar, bant genişliği düşükse yavaş dolar.",
            bg="#0a0e27",
            fg="#c0caf5",
            font=("Segoe UI", 10)
        )
        self.info.pack(pady=10)

    def start_demo(self):
        if self.is_running:
            return

        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.progress["value"] = 0

        t = threading.Thread(target=self.transfer)
        t.daemon = True
        t.start()

    def transfer(self):
        latency_delay = self.latency.get() / 1000
        speed = self.bandwidth.get()

        self.update_status(f"Gecikme bekleniyor ({self.latency.get()} ms)")
        time.sleep(latency_delay)

        self.update_status("Veri gelmeye başladı")

        data = 0
        total = 1000

        while data < total:
            data += speed * 0.1
            percent = min((data / total) * 100, 100)
            self.root.after(0, self.progress.configure, {"value": percent})
            time.sleep(0.1)

        self.update_status("İletim tamamlandı")
        self.is_running = False
        self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))

    def update_status(self, text):
        self.root.after(0, self.status.config, {"text": text})


def main():
    root = tk.Tk()
    app = LatencyBandwidthDemo(root)
    root.mainloop()

if __name__ == "__main__":
    main()
