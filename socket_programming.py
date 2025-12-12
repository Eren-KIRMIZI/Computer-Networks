import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import random


class EnhancedSocketDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Socket Programming - Interactive Demo")
        self.root.geometry("1200x800")
        self.root.configure(bg="#0a0e27")

        self.server_running = False
        self.client_connected = False
        self.is_sending = False
        self.packet_count = 0
        self.success_count = 0
        self.fail_count = 0

        self.setup_ui()
        self.draw_scene()
        self.update_stats()

    def setup_ui(self):
        # Title
        title_frame = tk.Frame(self.root, bg="#0a0e27")
        title_frame.pack(pady=10)
        
        title = tk.Label(
            title_frame,
            text="Socket Programming Simülasyonu",
            font=("Segoe UI", 22, "bold"),
            fg="#00d4ff",
            bg="#0a0e27"
        )
        title.pack()
        
        subtitle = tk.Label(
            title_frame,
            text="Gerçek Zamanli Çift Yönlü Iletisim",
            font=("Segoe UI", 10),
            fg="#7aa2f7",
            bg="#0a0e27"
        )
        subtitle.pack()

        # Control Panel
        panel = tk.Frame(self.root, bg="#1a1b26", bd=2, relief=tk.RIDGE)
        panel.pack(pady=10, padx=20, fill=tk.X)

        # Row 1: Server Controls
        tk.Label(
            panel, 
            text="Server Port:", 
            fg="#c0caf5", 
            bg="#1a1b26",
            font=("Segoe UI", 10)
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.port_entry = tk.Entry(panel, width=10, bg="#24283b", fg="#c0caf5", font=("Consolas", 10))
        self.port_entry.insert(0, "8080")
        self.port_entry.grid(row=0, column=1, padx=10)

        self.server_btn = tk.Button(
            panel,
            text="Server Baslat",
            bg="#9ece6a",
            fg="#0a0e27",
            font=("Segoe UI", 10, "bold"),
            command=self.start_server,
            padx=20,
            pady=5
        )
        self.server_btn.grid(row=0, column=2, padx=10)

        self.server_status = tk.Label(
            panel,
            text="Kapali",
            fg="#f7768e",
            bg="#1a1b26",
            font=("Segoe UI", 10, "bold")
        )
        self.server_status.grid(row=0, column=3, padx=10)

        # Row 2: Client Controls
        tk.Label(
            panel, 
            text="Client:", 
            fg="#c0caf5", 
            bg="#1a1b26",
            font=("Segoe UI", 10)
        ).grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.client_btn = tk.Button(
            panel,
            text="Client Baglan",
            bg="#7aa2f7",
            fg="#0a0e27",
            font=("Segoe UI", 10, "bold"),
            command=self.connect_client,
            state=tk.DISABLED,
            padx=20,
            pady=5
        )
        self.client_btn.grid(row=1, column=2, padx=10)

        self.client_status = tk.Label(
            panel,
            text="Bagli Degil",
            fg="#f7768e",
            bg="#1a1b26",
            font=("Segoe UI", 10, "bold")
        )
        self.client_status.grid(row=1, column=3, padx=10)

        # Row 3: Message Controls
        tk.Label(
            panel, 
            text="Mesaj:", 
            fg="#c0caf5", 
            bg="#1a1b26",
            font=("Segoe UI", 10)
        ).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        
        self.msg_entry = tk.Entry(panel, width=40, bg="#24283b", fg="#c0caf5", font=("Consolas", 10))
        self.msg_entry.insert(0, "Hello Server!")
        self.msg_entry.grid(row=2, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
        self.msg_entry.bind("<Return>", lambda e: self.send_from_client())

        self.send_client_btn = tk.Button(
            panel,
            text="Client >> Server",
            bg="#00d4ff",
            fg="#0a0e27",
            font=("Segoe UI", 9, "bold"),
            state=tk.DISABLED,
            command=self.send_from_client,
            padx=15,
            pady=5
        )
        self.send_client_btn.grid(row=2, column=3, padx=10)

        self.send_server_btn = tk.Button(
            panel,
            text="Server >> Client",
            bg="#9ece6a",
            fg="#0a0e27",
            font=("Segoe UI", 9, "bold"),
            state=tk.DISABLED,
            command=self.send_from_server,
            padx=15,
            pady=5
        )
        self.send_server_btn.grid(row=2, column=4, padx=10)

        # Statistics Panel
        stats_frame = tk.Frame(self.root, bg="#1a1b26", bd=2, relief=tk.RIDGE)
        stats_frame.pack(pady=5, padx=20, fill=tk.X)

        tk.Label(
            stats_frame,
            text="Istatistikler",
            bg="#1a1b26",
            fg="#00d4ff",
            font=("Segoe UI", 11, "bold")
        ).pack(side=tk.LEFT, padx=20, pady=5)

        self.stats_label = tk.Label(
            stats_frame,
            text="Paket: 0 | Basarili: 0 | Kayip: 0 | Basari Orani: 0%",
            bg="#1a1b26",
            fg="#c0caf5",
            font=("Consolas", 10)
        )
        self.stats_label.pack(side=tk.LEFT, padx=20, pady=5)

        # Animation Canvas
        self.canvas = tk.Canvas(self.root, width=1100, height=380, bg="#24283b", highlightthickness=0)
        self.canvas.pack(pady=10)

        # Log area
        log_frame = tk.Frame(self.root, bg="#1a1b26", bd=2, relief=tk.RIDGE)
        log_frame.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)

        tk.Label(
            log_frame,
            text="Sistem Loglari",
            bg="#1a1b26",
            fg="#00d4ff",
            font=("Segoe UI", 11, "bold")
        ).pack(pady=5)

        self.log = scrolledtext.ScrolledText(
            log_frame, 
            bg="#24283b", 
            fg="#c0caf5", 
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.log.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Configure log tags
        self.log.tag_config("success", foreground="#9ece6a")
        self.log.tag_config("error", foreground="#f7768e")
        self.log.tag_config("info", foreground="#7aa2f7")
        self.log.tag_config("warning", foreground="#e0af68")

    def draw_scene(self):
        # Background effects
        for i in range(5):
            y = 50 + i * 70
            self.canvas.create_line(
                0, y, 1100, y, 
                fill="#414868", 
                width=1, 
                dash=(2, 4)
            )

        # Server Box with shadow
        self.canvas.create_rectangle(105, 145, 305, 265, fill="#1a1b26", outline="")
        self.server_box = self.canvas.create_rectangle(
            100, 140, 300, 260, 
            fill="#9ece6a", 
            outline="#00d4ff", 
            width=3
        )
        self.canvas.create_text(
            200, 180, 
            text="SERVER", 
            fill="#0a0e27", 
            font=("Segoe UI", 14, "bold")
        )
        self.server_port_text = self.canvas.create_text(
            200, 210, 
            text="Port: 8080", 
            fill="#0a0e27", 
            font=("Consolas", 10)
        )
        self.server_status_text = self.canvas.create_text(
            200, 235, 
            text="OFFLINE", 
            fill="#f7768e", 
            font=("Segoe UI", 9, "bold")
        )

        # Client Box with shadow
        self.canvas.create_rectangle(805, 145, 1005, 265, fill="#1a1b26", outline="")
        self.client_box = self.canvas.create_rectangle(
            800, 140, 1000, 260, 
            fill="#7aa2f7", 
            outline="#00d4ff", 
            width=3
        )
        self.canvas.create_text(
            900, 180, 
            text="CLIENT", 
            fill="#0a0e27", 
            font=("Segoe UI", 14, "bold")
        )
        self.client_status_text = self.canvas.create_text(
            900, 210, 
            text="DISCONNECTED", 
            fill="#f7768e", 
            font=("Segoe UI", 9, "bold")
        )

        # Connection Line
        self.line = self.canvas.create_line(
            300, 200, 800, 200, 
            fill="#414868", 
            width=4, 
            dash=(8, 4)
        )

        # Internet Cloud in the middle
        cloud_x, cloud_y = 550, 200
        self.canvas.create_oval(
            cloud_x - 60, cloud_y - 30, 
            cloud_x + 60, cloud_y + 30, 
            fill="#1a1b26", 
            outline="#7aa2f7", 
            width=2
        )
        self.canvas.create_text(
            cloud_x, cloud_y - 5, 
            text="INTERNET", 
            fill="#7aa2f7", 
            font=("Segoe UI", 10, "bold")
        )

    def log_msg(self, text, tag="info"):
        timestamp = time.strftime("%H:%M:%S")
        self.log.insert(tk.END, f"[{timestamp}] {text}\n", tag)
        self.log.see(tk.END)

    def update_stats(self):
        success_rate = (self.success_count / self.packet_count * 100) if self.packet_count > 0 else 0
        self.stats_label.config(
            text=f"Paket: {self.packet_count} | Basarili: {self.success_count} | "
                 f"Kayip: {self.fail_count} | Basari Orani: {success_rate:.1f}%"
        )

    def start_server(self):
        if self.server_running:
            return

        port = self.port_entry.get()
        if not port.isdigit():
            messagebox.showerror("Hata", "Gecersiz port numarasi!")
            return

        self.server_running = True
        self.server_btn.config(state=tk.DISABLED, text="Server Calisiyor")
        self.client_btn.config(state=tk.NORMAL)
        self.server_status.config(text="Aktif", fg="#9ece6a")

        self.log_msg(f"Server baslatildi >> Port {port} dinleniyor", "success")
        
        # Update canvas
        self.canvas.itemconfig(self.server_box, fill="#9ece6a", outline="#00d4ff")
        self.canvas.itemconfig(self.server_port_text, text=f"Port: {port}")
        self.canvas.itemconfig(self.server_status_text, text="ONLINE", fill="#0a0e27")
        self.canvas.itemconfig(self.line, fill="#7aa2f7")

        # Pulse animation
        self.pulse_server()

    def pulse_server(self):
        if self.server_running:
            current = self.canvas.itemcget(self.server_box, "width")
            new_width = 5 if float(current) == 3.0 else 3
            self.canvas.itemconfig(self.server_box, width=new_width)
            self.root.after(500, self.pulse_server)

    def connect_client(self):
        if not self.server_running:
            self.log_msg("UYARI: Server calismiyor!", "error")
            return

        if self.client_connected:
            return

        self.log_msg("Client baglanti kuruyor...", "info")
        
        def connect():
            time.sleep(1)
            self.client_connected = True
            self.root.after(0, self._finish_connection)

        threading.Thread(target=connect, daemon=True).start()

    def _finish_connection(self):
        self.client_btn.config(state=tk.DISABLED, text="Baglandi")
        self.client_status.config(text="Bagli", fg="#9ece6a")
        self.send_client_btn.config(state=tk.NORMAL)
        self.send_server_btn.config(state=tk.NORMAL)

        self.log_msg("Client >> Server baglantisi basarili (3-Way Handshake tamamlandi)", "success")
        
        self.canvas.itemconfig(self.client_box, fill="#7aa2f7", outline="#00d4ff")
        self.canvas.itemconfig(self.client_status_text, text="CONNECTED", fill="#0a0e27")
        self.canvas.itemconfig(self.line, fill="#00d4ff", dash=())

        # Show handshake animation
        self.show_handshake()

    def show_handshake(self):
        steps = ["SYN", "SYN-ACK", "ACK"]
        positions = [(300, 800), (800, 300), (300, 800)]
        
        def animate(i):
            if i >= len(steps):
                return
            
            start_x, end_x = positions[i]
            packet = self.canvas.create_oval(
                start_x - 15, 185, start_x + 15, 215,
                fill="#e0af68", outline="#0a0e27", width=2
            )
            text = self.canvas.create_text(
                start_x, 200, text=steps[i],
                font=("Consolas", 8, "bold"), fill="#0a0e27"
            )
            
            direction = 1 if end_x > start_x else -1
            for _ in range(50):
                self.canvas.move(packet, direction * 10, 0)
                self.canvas.move(text, direction * 10, 0)
                time.sleep(0.015)
            
            self.canvas.delete(packet, text)
            self.root.after(200, lambda: animate(i + 1))
        
        threading.Thread(target=lambda: animate(0), daemon=True).start()

    def send_from_client(self):
        self.send_message("client", "server")

    def send_from_server(self):
        self.send_message("server", "client")

    def send_message(self, sender, receiver):
        if not self.client_connected or self.is_sending:
            return

        msg = self.msg_entry.get().strip()
        if not msg:
            return

        self.is_sending = True
        self.send_client_btn.config(state=tk.DISABLED)
        self.send_server_btn.config(state=tk.DISABLED)

        threading.Thread(
            target=self._animate_packet, 
            args=(msg, sender, receiver), 
            daemon=True
        ).start()

    def _animate_packet(self, msg, sender, receiver):
        self.packet_count += 1
        
        # Random packet loss simulation (10% chance)
        will_fail = random.random() < 0.1
        
        if sender == "client":
            self.log_msg(f"Client >> Server: '{msg}'", "info")
            start_x, end_x = 800, 300
            color = "#7aa2f7"
        else:
            self.log_msg(f"Server >> Client: '{msg}'", "info")
            start_x, end_x = 300, 800
            color = "#9ece6a"

        # Create packet
        packet = self.canvas.create_rectangle(
            start_x - 50, 180, start_x, 220,
            fill=color, outline="#0a0e27", width=2
        )
        text = self.canvas.create_text(
            start_x - 25, 200,
            text=msg[:10] + "..." if len(msg) > 10 else msg,
            font=("Consolas", 8, "bold"),
            fill="#0a0e27"
        )

        # Animate packet movement
        direction = 1 if end_x > start_x else -1
        steps = 50
        
        for i in range(steps):
            if will_fail and i == steps // 2:
                # Packet loss animation
                self.canvas.itemconfig(packet, fill="#f7768e")
                self.canvas.itemconfig(text, text="X LOST")
                time.sleep(0.5)
                break
            
            self.canvas.move(packet, direction * 10, random.randint(-2, 2))
            self.canvas.move(text, direction * 10, random.randint(-2, 2))
            time.sleep(0.02)

        self.canvas.delete(packet, text)

        if will_fail:
            self.fail_count += 1
            self.log_msg(f"Paket kayboldu! (Timeout)", "error")
        else:
            self.success_count += 1
            target = "Server" if receiver == "server" else "Client"
            self.log_msg(f"{target} mesaji aldi ve isledi", "success")
            
            # Auto-response
            if receiver == "server":
                response = "ACK: Mesaj alindi"
                time.sleep(0.5)
                self.root.after(0, lambda: self._send_response(response, "server", "client"))

        self.root.after(0, self._finish_sending)
        self.root.after(0, self.update_stats)

    def _send_response(self, msg, sender, receiver):
        threading.Thread(
            target=self._animate_packet,
            args=(msg, sender, receiver),
            daemon=True
        ).start()

    def _finish_sending(self):
        self.is_sending = False
        self.send_client_btn.config(state=tk.NORMAL)
        self.send_server_btn.config(state=tk.NORMAL)


def main():
    root = tk.Tk()
    app = EnhancedSocketDemo(root)
    root.mainloop()


if __name__ == "__main__":
    main()
