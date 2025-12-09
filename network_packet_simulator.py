import tkinter as tk
from tkinter import scrolledtext, ttk
import time
import threading
import random

class NetworkPacketSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Packet Simulator - TCP/IP Paket İletimi")
        self.root.geometry("1100x750")
        self.root.configure(bg="#0a0e27")
        
        self.is_animating = False
        self.packet_loss_enabled = False
        self.received_packets = []
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#0a0e27")
        header_frame.pack(pady=15, fill=tk.X)
        
        tk.Label(
            header_frame,
            text="Network Packet Simulator",
            font=("Segoe UI", 20, "bold"),
            bg="#0a0e27",
            fg="#00d4ff"
        ).pack()
        
        tk.Label(
            header_frame,
            text="TCP/IP protokolünde veri paketlere bölünerek hedefe ulaşır",
            font=("Segoe UI", 11),
            bg="#0a0e27",
            fg="#7aa2f7"
        ).pack(pady=5)
        
        # Control Panel
        control_frame = tk.Frame(self.root, bg="#1a1b26", relief=tk.RIDGE, bd=2)
        control_frame.pack(pady=10, padx=20, fill=tk.X)
        
        # Message Input
        input_frame = tk.Frame(control_frame, bg="#1a1b26")
        input_frame.pack(pady=15, padx=15)
        
        tk.Label(
            input_frame,
            text="Mesaj:",
            font=("Segoe UI", 11, "bold"),
            bg="#1a1b26",
            fg="#c0caf5"
        ).grid(row=0, column=0, padx=5, sticky=tk.W)
        
        self.msg_entry = tk.Entry(
            input_frame,
            font=("Segoe UI", 12),
            width=35,
            bg="#24283b",
            fg="#c0caf5",
            insertbackground="#00d4ff",
            relief=tk.FLAT,
            bd=5
        )
        self.msg_entry.grid(row=0, column=1, padx=10)
        self.msg_entry.insert(0, "NETWORK PACKET SIMULATION")
        
        # Settings
        settings_frame = tk.Frame(control_frame, bg="#1a1b26")
        settings_frame.pack(pady=10, padx=15)
        
        tk.Label(
            settings_frame,
            text="Paket Boyutu:",
            font=("Segoe UI", 10),
            bg="#1a1b26",
            fg="#c0caf5"
        ).grid(row=0, column=0, padx=5)
        
        self.packet_size_var = tk.IntVar(value=4)
        packet_size_spin = tk.Spinbox(
            settings_frame,
            from_=2,
            to=10,
            textvariable=self.packet_size_var,
            width=8,
            font=("Segoe UI", 10),
            bg="#24283b",
            fg="#c0caf5",
            relief=tk.FLAT
        )
        packet_size_spin.grid(row=0, column=1, padx=5)
        
        tk.Label(
            settings_frame,
            text="Gecikme (ms):",
            font=("Segoe UI", 10),
            bg="#1a1b26",
            fg="#c0caf5"
        ).grid(row=0, column=2, padx=10)
        
        self.delay_var = tk.IntVar(value=500)
        delay_spin = tk.Spinbox(
            settings_frame,
            from_=100,
            to=2000,
            increment=100,
            textvariable=self.delay_var,
            width=8,
            font=("Segoe UI", 10),
            bg="#24283b",
            fg="#c0caf5",
            relief=tk.FLAT
        )
        delay_spin.grid(row=0, column=3, padx=5)
        
        # Packet Loss Checkbox
        self.packet_loss_var = tk.BooleanVar()
        packet_loss_check = tk.Checkbutton(
            settings_frame,
            text="Paket Kaybı Simülasyonu (%20)",
            variable=self.packet_loss_var,
            font=("Segoe UI", 10),
            bg="#1a1b26",
            fg="#f7768e",
            selectcolor="#24283b",
            activebackground="#1a1b26",
            activeforeground="#f7768e"
        )
        packet_loss_check.grid(row=0, column=4, padx=15)
        
        # Buttons
        button_frame = tk.Frame(control_frame, bg="#1a1b26")
        button_frame.pack(pady=10)
        
        self.send_btn = tk.Button(
            button_frame,
            text="Gönder",
            font=("Segoe UI", 11, "bold"),
            bg="#00d4ff",
            fg="#0a0e27",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.start_sending
        )
        self.send_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = tk.Button(
            button_frame,
            text="Temizle",
            font=("Segoe UI", 11, "bold"),
            bg="#f7768e",
            fg="#0a0e27",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.clear_canvas
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Main content area with Canvas and Message Display
        main_content = tk.Frame(self.root, bg="#0a0e27")
        main_content.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Left side - Canvas
        canvas_frame = tk.Frame(main_content, bg="#1a1b26", relief=tk.RIDGE, bd=2)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(
            canvas_frame,
            text="PAKET İLETİM SİMÜLASYONU",
            font=("Segoe UI", 12, "bold"),
            bg="#1a1b26",
            fg="#00d4ff"
        ).pack(pady=10)
        
        self.canvas = tk.Canvas(
            canvas_frame,
            width=640,
            height=280,
            bg="#24283b",
            highlightthickness=0
        )
        self.canvas.pack(pady=10, padx=10)
        
        # Draw sender and receiver
        self.draw_network_nodes()
        
        # Right side - Message Display
        message_frame = tk.Frame(main_content, bg="#1a1b26", relief=tk.RIDGE, bd=2, width=300)
        message_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        message_frame.pack_propagate(False)
        
        tk.Label(
            message_frame,
            text="MESAJ TAKİBİ",
            font=("Segoe UI", 12, "bold"),
            bg="#1a1b26",
            fg="#00d4ff"
        ).pack(pady=10)
        
        # Original Message
        tk.Label(
            message_frame,
            text="Gönderilen:",
            font=("Segoe UI", 9, "bold"),
            bg="#1a1b26",
            fg="#7aa2f7"
        ).pack(anchor=tk.W, padx=10, pady=(5, 2))
        
        self.original_msg_display = tk.Text(
            message_frame,
            height=2,
            font=("Consolas", 10, "bold"),
            bg="#24283b",
            fg="#7aa2f7",
            relief=tk.FLAT,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.original_msg_display.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Received Packets
        tk.Label(
            message_frame,
            text="Alınan Paketler:",
            font=("Segoe UI", 9, "bold"),
            bg="#1a1b26",
            fg="#9ece6a"
        ).pack(anchor=tk.W, padx=10, pady=(5, 2))
        
        self.received_display = scrolledtext.ScrolledText(
            message_frame,
            height=6,
            font=("Consolas", 9),
            bg="#24283b",
            fg="#f7768e",
            relief=tk.FLAT,
            wrap=tk.WORD
        )
        self.received_display.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Reconstructed Message
        tk.Label(
            message_frame,
            text="Birleştirilmiş Mesaj:",
            font=("Segoe UI", 9, "bold"),
            bg="#1a1b26",
            fg="#00d4ff"
        ).pack(anchor=tk.W, padx=10, pady=(5, 2))
        
        self.reconstructed_display = tk.Text(
            message_frame,
            height=3,
            font=("Consolas", 11, "bold"),
            bg="#313244",
            fg="#00d4ff",
            relief=tk.FLAT,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.reconstructed_display.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Bottom - Log Area
        log_frame = tk.Frame(self.root, bg="#1a1b26", relief=tk.RIDGE, bd=2)
        log_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        tk.Label(
            log_frame,
            text="İletim Logları",
            font=("Segoe UI", 11, "bold"),
            bg="#1a1b26",
            fg="#00d4ff"
        ).pack(pady=5)
        
        self.log = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            font=("Consolas", 9),
            bg="#24283b",
            fg="#9ece6a",
            relief=tk.FLAT,
            wrap=tk.WORD
        )
        self.log.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def draw_network_nodes(self):
        # Sender
        self.canvas.create_rectangle(20, 100, 100, 180, fill="#7aa2f7", outline="#00d4ff", width=2)
        self.canvas.create_text(60, 140, text="SENDER", fill="#0a0e27", font=("Segoe UI", 10, "bold"))
        
        # Receiver
        self.canvas.create_rectangle(540, 100, 620, 180, fill="#9ece6a", outline="#00d4ff", width=2)
        self.canvas.create_text(580, 140, text="RECEIVER", fill="#0a0e27", font=("Segoe UI", 10, "bold"))
        
        # Connection line
        self.canvas.create_line(100, 140, 540, 140, fill="#414868", width=2, dash=(5, 5))
        
    def log_msg(self, text, color="#9ece6a"):
        self.log.tag_config(color, foreground=color)
        self.log.insert(tk.END, text + "\n", color)
        self.log.see(tk.END)
        
    def update_received_display(self, packet_num, payload):
        self.received_display.insert(tk.END, f"#{packet_num}: [{payload}]\n")
        self.received_display.see(tk.END)
        
    def update_reconstructed_message(self):
        reconstructed = ''.join(self.received_packets)
        self.reconstructed_display.config(state=tk.NORMAL)
        self.reconstructed_display.delete("1.0", tk.END)
        self.reconstructed_display.insert("1.0", reconstructed)
        self.reconstructed_display.config(state=tk.DISABLED)
        
    def split_packets(self, message, packet_size):
        return [message[i:i + packet_size] for i in range(0, len(message), packet_size)]
    
    def clear_canvas(self):
        self.canvas.delete("packet")
        self.log.delete("1.0", tk.END)
        self.received_display.delete("1.0", tk.END)
        self.reconstructed_display.config(state=tk.NORMAL)
        self.reconstructed_display.delete("1.0", tk.END)
        self.reconstructed_display.config(state=tk.DISABLED)
        self.original_msg_display.config(state=tk.NORMAL)
        self.original_msg_display.delete("1.0", tk.END)
        self.original_msg_display.config(state=tk.DISABLED)
        self.received_packets = []
        
    def start_sending(self):
        if self.is_animating:
            return
            
        msg = self.msg_entry.get().strip()
        if not msg:
            self.log_msg("Lütfen bir mesaj girin!", "#f7768e")
            return
        
        self.is_animating = True
        self.send_btn.config(state=tk.DISABLED)
        self.canvas.delete("packet")
        self.log.delete("1.0", tk.END)
        self.received_display.delete("1.0", tk.END)
        self.received_packets = []
        
        # Clear reconstructed message
        self.reconstructed_display.config(state=tk.NORMAL)
        self.reconstructed_display.delete("1.0", tk.END)
        self.reconstructed_display.config(state=tk.DISABLED)
        
        # Display original message
        self.original_msg_display.config(state=tk.NORMAL)
        self.original_msg_display.delete("1.0", tk.END)
        self.original_msg_display.insert("1.0", msg)
        self.original_msg_display.config(state=tk.DISABLED)
        
        packet_size = self.packet_size_var.get()
        packets = self.split_packets(msg, packet_size)
        
        self.log_msg(f"Gönderilecek Mesaj: {msg}", "#00d4ff")
        self.log_msg(f"Toplam Paket Sayısı: {len(packets)}", "#7aa2f7")
        self.log_msg(f"Paket Boyutu: {packet_size} karakter", "#7aa2f7")
        self.log_msg("=" * 60, "#414868")
        
        t = threading.Thread(
            target=self.animate_packets,
            args=(packets,),
            daemon=True
        )
        t.start()
        
    def animate_packets(self, packets):
        delay = self.delay_var.get() / 1000.0
        packet_loss_enabled = self.packet_loss_var.get()
        
        successful = 0
        lost = 0
        
        for seq, payload in enumerate(packets, start=1):
            # Check for packet loss
            is_lost = packet_loss_enabled and random.random() < 0.2
            
            if is_lost:
                lost += 1
                self.root.after(0, self.log_msg, f"Paket #{seq} KAYBOLDU | Payload: [{payload}]", "#f7768e")
                time.sleep(delay)
                continue
            
            successful += 1
            checksum = sum(ord(c) for c in payload) % 256
            header = f"SEQ:{seq} | LEN:{len(payload)} | CHK:{checksum}"
            
            self.root.after(0, self.log_msg, f"Paket #{seq} gönderiliyor... | Payload: [{payload}]", "#e0af68")
            
            # Create packet visualization
            packet_id = self.create_packet(header, payload, seq)
            
            # Animate packet movement
            for _ in range(44):
                for item in packet_id:
                    self.canvas.move(item, 10, 0)
                time.sleep(0.02)
            
            # Remove packet
            for item in packet_id:
                self.canvas.delete(item)
            
            # Add to received packets
            self.received_packets.append(payload)
            self.root.after(0, self.update_received_display, seq, payload)
            self.root.after(0, self.update_reconstructed_message)
            
            self.root.after(0, self.log_msg, f"Paket #{seq} başarıyla teslim edildi", "#9ece6a")
            time.sleep(delay)
        
        summary = f"\n{'=' * 60}\n"
        summary += f"İletim Özeti:\n"
        summary += f"Başarılı: {successful} paket\n"
        if lost > 0:
            summary += f"Kayıp: {lost} paket\n"
        summary += f"Başarı Oranı: {(successful/(successful+lost)*100):.1f}%\n"
        summary += f"{'=' * 60}"
        
        self.root.after(0, self.log_msg, summary, "#00d4ff")
        self.is_animating = False
        self.send_btn.config(state=tk.NORMAL)
        
    def create_packet(self, header, payload, seq):
        x_start = 120
        y_start = 80
        
        # Packet container
        container = self.canvas.create_rectangle(
            x_start, y_start, x_start + 140, y_start + 120,
            fill="#1a1b26",
            outline="#00d4ff",
            width=2,
            tags="packet"
        )
        
        # Header section
        header_rect = self.canvas.create_rectangle(
            x_start + 5, y_start + 5, x_start + 135, y_start + 50,
            fill="#e0af68",
            outline="",
            tags="packet"
        )
        header_text = self.canvas.create_text(
            x_start + 70, y_start + 27,
            text=header,
            fill="#0a0e27",
            font=("Consolas", 8, "bold"),
            tags="packet"
        )
        
        # Payload section
        payload_rect = self.canvas.create_rectangle(
            x_start + 5, y_start + 55, x_start + 135, y_start + 95,
            fill="#7aa2f7",
            outline="",
            tags="packet"
        )
        payload_text = self.canvas.create_text(
            x_start + 70, y_start + 75,
            text=payload,
            fill="#0a0e27",
            font=("Consolas", 11, "bold"),
            tags="packet"
        )
        
        # Packet number
        seq_text = self.canvas.create_text(
            x_start + 70, y_start + 107,
            text=f"PKT #{seq}",
            fill="#00d4ff",
            font=("Segoe UI", 9, "bold"),
            tags="packet"
        )
        
        return [container, header_rect, header_text, payload_rect, payload_text, seq_text]

def main():
    root = tk.Tk()
    app = NetworkPacketSimulator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
