import tkinter as tk
from tkinter import ttk
import threading
import time
import socket

class HTTPDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("HTTP Request Demo")
        self.root.geometry("950x600")
        self.root.configure(bg="#0b132b")

        self.is_running = False

        self.build_ui()

    def build_ui(self):
        title = tk.Label(
            self.root,
            text="HTTP Request Mantığı",
            font=("Segoe UI", 20, "bold"),
            bg="#0b132b",
            fg="#00c6ff"
        )
        title.pack(pady=10)

        desc = tk.Label(
            self.root,
            text="DNS -> TCP Bağlantısı -> HTTP GET -> Response Header -> Response Body",
            font=("Segoe UI", 11),
            bg="#0b132b",
            fg="#8acaff"
        )
        desc.pack(pady=5)

        box = tk.Frame(self.root, bg="#1c2541", bd=2, relief=tk.RIDGE)
        box.pack(pady=10, padx=15, fill=tk.X)

        # Host field
        tk.Label(box, text="Host:", bg="#1c2541", fg="#c6d4f0").grid(row=0, column=0, padx=10, pady=10)
        self.host_entry = tk.Entry(box, width=40)
        self.host_entry.insert(0, "www.google.com")
        self.host_entry.grid(row=0, column=1, padx=10)

        # Latency slider
        tk.Label(box, text="Latency (ms):", bg="#1c2541", fg="#c6d4f0").grid(row=1, column=0, padx=10)
        self.latency = tk.IntVar(value=50)
        tk.Scale(
            box, from_=50, to=1500, orient=tk.HORIZONTAL,
            variable=self.latency,
            length=300,
            bg="#1c2541", fg="#d7e3ff", troughcolor="#3a506b",
            highlightthickness=0
        ).grid(row=1, column=1, padx=10)

        # Bandwidth slider
        tk.Label(box, text="Bandwidth (KB/s):", bg="#1c2541", fg="#c6d4f0").grid(row=2, column=0, padx=10)
        self.bandwidth = tk.IntVar(value=50)
        tk.Scale(
            box, from_=50, to=800, orient=tk.HORIZONTAL,
            variable=self.bandwidth,
            length=300,
            bg="#1c2541", fg="#d7e3ff", troughcolor="#3a506b",
            highlightthickness=0
        ).grid(row=2, column=1, padx=10)

        self.start_button = tk.Button(
            box,
            text="HTTP GET Gönder",
            command=self.start_request,
            bg="#00c6ff",
            fg="#0b132b",
            font=("Segoe UI", 12, "bold"),
            padx=20
        )
        self.start_button.grid(row=0, column=2, rowspan=3, padx=20)

        # Progress area
        section = tk.Frame(self.root, bg="#1c2541", bd=2, relief=tk.RIDGE)
        section.pack(pady=10, padx=15, fill=tk.X)

        tk.Label(
            section,
            text="İlerleme",
            bg="#1c2541",
            fg="#00c6ff",
            font=("Segoe UI", 11, "bold")
        ).pack(pady=10)

        self.progress = ttk.Progressbar(section, length=750)
        self.progress.pack(pady=20)

        self.status = tk.Label(
            section,
            text="Hazır",
            bg="#1c2541",
            fg="#88ffb7",
            font=("Segoe UI", 10)
        )
        self.status.pack(pady=5)

        self.log = tk.Text(
            self.root,
            height=10,
            bg="#0b132b",
            fg="#d7e3ff",
            font=("Consolas", 10)
        )
        self.log.pack(pady=10, padx=15, fill=tk.X)

    # Background thread başlat
    def start_request(self):
        if self.is_running:
            return

        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.progress["value"] = 0
        self.log.delete("1.0", tk.END)

        t = threading.Thread(target=self.perform_http)
        t.daemon = True
        t.start()

    def perform_http(self):
        host = self.host_entry.get().strip()
        latency_delay = self.latency.get() / 1000
        speed = self.bandwidth.get()

        self.set_status("DNS çözümü yapılıyor...")
        time.sleep(latency_delay)
        try:
            ip = socket.gethostbyname(host)
            self.log_write(f"DNS: {host} -> {ip}\n")
        except:
            self.log_write("DNS çözümlemesi başarısız.\n")
            self.finish()
            return

        self.increment_progress(10)

        # TCP bağlantısı
        self.set_status("TCP bağlantısı kuruluyor...")
        time.sleep(latency_delay)
        self.log_write("TCP bağlantısı kuruldu.\n")
        self.increment_progress(20)

        # HTTP GET gönderme
        self.set_status("HTTP GET isteği gönderiliyor...")
        time.sleep(latency_delay)
        request_data = f"GET / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        self.log_write(f"Gönderilen istek:\n{request_data}\n")
        self.increment_progress(30)

        # Response header simülasyonu
        self.set_status("Response header alınıyor...")
        time.sleep(latency_delay)
        header = (
            "HTTP/1.1 200 OK\n"
            "Content-Type: text/html\n"
            "Content-Length: 5000\n\n"
        )
        self.log_write(f"Sunucudan gelen header:\n{header}\n")
        self.increment_progress(50)

        # Response Body (download)
        self.set_status("Response body indiriliyor...")

        total = 5000
        downloaded = 0

        while downloaded < total:
            downloaded += speed * 10
            percent = min((downloaded / total) * 100, 100)
            self.root.after(0, self.progress.configure, {"value": percent})
            time.sleep(0.1)

        self.log_write("İndirme tamamlandı.\n")
        self.set_status("Tamamlandı")
        self.finish()

    def set_status(self, text):
        self.root.after(0, self.status.config, {"text": text})

    def increment_progress(self, val):
        self.root.after(0, lambda: self.progress.config(value=val))

    def log_write(self, text):
        self.root.after(0, lambda: self.log.insert(tk.END, text))

    def finish(self):
        self.is_running = False
        self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))


def main():
    root = tk.Tk()
    app = HTTPDemo(root)
    root.mainloop()

if __name__ == "__main__":
    main()
