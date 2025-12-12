import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import random


class AdvancedHandshakeDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("TCP 3-Way Handshake - Detayli Simulasyon")
        self.root.geometry("1200x800")
        self.root.configure(bg="#0b132b")

        self.running = False
        self.client_seq = 0
        self.server_seq = 0

        self.animation_speed = tk.DoubleVar(value=0.05)

        self.build_ui()

    def build_ui(self):
        title = tk.Label(
            self.root,
            text="TCP 3-Way Handshake - Detayli Simulasyon",
            font=("Segoe UI", 22, "bold"),
            bg="#0b132b",
            fg="#00c6ff"
        )
        title.pack(pady=10)

        subtitle = tk.Label(
            self.root,
            text="Sequence Numbers, ACK Numbers, Window Size ve TCP Flags",
            font=("Segoe UI", 11),
            bg="#0b132b",
            fg="#8acaff"
        )
        subtitle.pack(pady=5)

        control = tk.Frame(self.root, bg="#1c2541", bd=2, relief=tk.RIDGE)
        control.pack(padx=20, pady=10, fill=tk.X)

        info_frame = tk.Frame(control, bg="#1c2541")
        info_frame.pack(pady=10)

        tk.Label(info_frame, text="Client IP:", bg="#1c2541", fg="#c6d4f0").grid(row=0, column=0, padx=10, sticky="w")
        self.client_ip = tk.Entry(info_frame, width=15, bg="#0b132b", fg="#d7e3ff")
        self.client_ip.insert(0, "192.168.1.100")
        self.client_ip.grid(row=0, column=1, padx=10)

        tk.Label(info_frame, text="Client Port:", bg="#1c2541", fg="#c6d4f0").grid(row=0, column=2, padx=10)
        self.client_port = tk.Entry(info_frame, width=8, bg="#0b132b", fg="#d7e3ff")
        self.client_port.insert(0, str(random.randint(50000, 60000)))
        self.client_port.grid(row=0, column=3, padx=10)

        tk.Label(info_frame, text="Server IP:", bg="#1c2541", fg="#c6d4f0").grid(row=1, column=0, padx=10)
        self.server_ip = tk.Entry(info_frame, width=15, bg="#0b132b", fg="#d7e3ff")
        self.server_ip.insert(0, "93.184.216.34")
        self.server_ip.grid(row=1, column=1, padx=10)

        tk.Label(info_frame, text="Server Port:", bg="#1c2541", fg="#c6d4f0").grid(row=1, column=2, padx=10)
        self.server_port = tk.Entry(info_frame, width=8, bg="#0b132b", fg="#d7e3ff")
        self.server_port.insert(0, "80")
        self.server_port.grid(row=1, column=3, padx=10)

        network_frame = tk.Frame(control, bg="#1c2541")
        network_frame.pack(pady=10)

        tk.Label(network_frame, text="RTT:", bg="#1c2541", fg="#c6d4f0").grid(row=0, column=0, padx=10)
        self.rtt = tk.IntVar(value=100)

        self.rtt_scale = tk.Scale(
            network_frame, from_=10, to=500, orient=tk.HORIZONTAL,
            variable=self.rtt, length=200, bg="#1c2541",
            fg="#d7e3ff", troughcolor="#3a506b", highlightthickness=0
        )
        self.rtt_scale.grid(row=0, column=1, padx=10)

        self.rtt_label = tk.Label(network_frame, text="100 ms", bg="#1c2541", fg="#88ffb7")
        self.rtt_label.grid(row=0, column=2, padx=10)

        # trace_variable kaldırıldı - yerine trace_add
        self.rtt.trace_add("write", lambda *args: self.rtt_label.config(text=f"{self.rtt.get()} ms"))

        # Simülasyon Hızı
        tk.Label(network_frame, text="Simülasyon Hızı:", bg="#1c2541", fg="#c6d4f0").grid(row=1, column=0, padx=10)
        tk.Scale(
            network_frame, from_=0.005, to=0.2, resolution=0.005,
            orient=tk.HORIZONTAL, variable=self.animation_speed,
            length=200, bg="#1c2541", fg="#d7e3ff", troughcolor="#3a506b"
        ).grid(row=1, column=1, padx=10)

        tk.Label(network_frame, text="Yavaş  <--->  Hızlı", bg="#1c2541", fg="#88ffb7").grid(row=1, column=2, padx=10)

        self.start_button = tk.Button(
            control, text="Handshake Baslat", bg="#00c6ff", fg="#0b132b",
            font=("Segoe UI", 12, "bold"), padx=30, pady=10, command=self.start_handshake
        )
        self.start_button.pack(pady=10)

        canvas_frame = tk.Frame(self.root, bg="#1c2541", bd=2, relief=tk.RIDGE)
        canvas_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        tk.Label(canvas_frame, text="Visualizasyon", bg="#1c2541", fg="#00c6ff").pack(pady=5)

        self.canvas = tk.Canvas(canvas_frame, width=1100, height=300, bg="#0b132b")
        self.canvas.pack(pady=10)

        self.draw_scene()

        details_frame = tk.Frame(self.root, bg="#1c2541", bd=2, relief=tk.RIDGE)
        details_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        columns_frame = tk.Frame(details_frame, bg="#1c2541")
        columns_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        client_col = tk.Frame(columns_frame, bg="#1c2541")
        client_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(client_col, text="CLIENT STATE", bg="#1c2541", fg="#7aa2f7").pack()
        self.client_state = scrolledtext.ScrolledText(client_col, height=8, bg="#0b132b", fg="#d7e3ff")
        self.client_state.pack(fill=tk.BOTH, expand=True, pady=5)

        server_col = tk.Frame(columns_frame, bg="#1c2541")
        server_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(server_col, text="SERVER STATE", bg="#1c2541", fg="#9ece6a").pack()
        self.server_state = scrolledtext.ScrolledText(server_col, height=8, bg="#0b132b", fg="#d7e3ff")
        self.server_state.pack(fill=tk.BOTH, expand=True, pady=5)

    def draw_scene(self):
        self.canvas.create_rectangle(50, 80, 200, 220, fill="#7aa2f7", outline="#00c6ff", width=3)
        self.canvas.create_text(125, 130, text="CLIENT", fill="#0b132b")
        self.client_state_text = self.canvas.create_text(125, 160, text="CLOSED", fill="#0b132b")

        self.canvas.create_rectangle(900, 80, 1050, 220, fill="#9ece6a", outline="#00c6ff", width=3)
        self.canvas.create_text(975, 130, text="SERVER", fill="#0b132b")
        self.server_state_text = self.canvas.create_text(975, 160, text="LISTEN", fill="#0b132b")

        self.canvas.create_line(200, 150, 900, 150, fill="#3a506b", width=2, dash=(5, 5))

    def start_handshake(self):
        if self.running:
            return

        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.client_state.delete("1.0", tk.END)
        self.server_state.delete("1.0", tk.END)

        self.client_seq = random.randint(1000, 9999)
        self.server_seq = random.randint(1000, 9999)

        threading.Thread(target=self.run_handshake, daemon=True).start()

    def animate_packet(self, label, start_x, end_x, color, details):
        packet = self.canvas.create_rectangle(start_x - 40, 130, start_x + 40, 170,
                                              fill=color, outline="#0b132b", width=2)
        text1 = self.canvas.create_text(start_x, 145, text=label, fill="#0b132b")
        text2 = self.canvas.create_text(start_x, 160, text=details, fill="#0b132b")

        direction = 1 if end_x > start_x else -1
        steps = 40
        step_size = abs(end_x - start_x) / steps

        for _ in range(steps):
            self.canvas.move(packet, direction * step_size, 0)
            self.canvas.move(text1, direction * step_size, 0)
            self.canvas.move(text2, direction * step_size, 0)
            time.sleep(self.animation_speed.get())

        self.canvas.delete(packet, text1, text2)

    def run_handshake(self):
        rtt_delay = self.rtt.get() / 1000.0

        self.update_client_state("SYN-SENT")
        time.sleep(0.5)

        self.animate_packet("SYN", 200, 900, "#7aa2f7", f"SEQ={self.client_seq}")
        time.sleep(rtt_delay / 2)

        self.update_server_state("SYN-RECEIVED")
        time.sleep(0.5)

        self.animate_packet("SYN-ACK", 900, 200, "#9ece6a",
                            f"SEQ={self.server_seq}\nACK={self.client_seq + 1}")
        time.sleep(rtt_delay / 2)

        self.update_client_state("ESTABLISHED")
        time.sleep(0.5)

        self.animate_packet("ACK", 200, 900, "#7aa2f7",
                            f"SEQ={self.client_seq + 1}\nACK={self.server_seq + 1}")
        time.sleep(rtt_delay / 2)

        self.update_server_state("ESTABLISHED")
        time.sleep(1)

        self.end()

    def update_client_state(self, state):
        self.root.after(0, lambda: self.canvas.itemconfig(self.client_state_text, text=state))

    def update_server_state(self, state):
        self.root.after(0, lambda: self.canvas.itemconfig(self.server_state_text, text=state))

    def log_client(self, text):
        self.root.after(0, lambda: self.client_state.insert(tk.END, text))
        self.root.after(0, lambda: self.client_state.see(tk.END))

    def log_server(self, text):
        self.root.after(0, lambda: self.server_state.insert(tk.END, text))
        self.root.after(0, lambda: self.server_state.see(tk.END))

    def end(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)


def main():
    root = tk.Tk()
    app = AdvancedHandshakeDemo(root)
    root.mainloop()


if __name__ == "__main__":
    main()
