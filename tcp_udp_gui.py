import socket
import threading
import tkinter as tk
from tkinter import ttk
import random
import time

HOST = "127.0.0.1"
TCP_PORT = 5000
UDP_PORT = 5001

# ---------- GUI ----------
root = tk.Tk()
root.title("TCP vs UDP Paket Teslimi Simülasyonu")
root.geometry("1000x650")
root.configure(bg="#1e1e2e")

# Başlık
title_frame = tk.Frame(root, bg="#1e1e2e")
title_frame.pack(fill="x", pady=15)

tk.Label(
    title_frame,
    text="TCP vs UDP Protokol Karşılaştırması",
    font=("Segoe UI", 18, "bold"),
    bg="#1e1e2e",
    fg="#cdd6f4"
).pack()

tk.Label(
    title_frame,
    text="Paket teslim mekanizmalarını canlı olarak izleyin",
    font=("Segoe UI", 10),
    bg="#1e1e2e",
    fg="#a6adc8"
).pack()

# Ana container
main_container = tk.Frame(root, bg="#1e1e2e")
main_container.pack(fill="both", expand=True, padx=20, pady=10)

# TCP Frame
frame_tcp = tk.Frame(main_container, bg="#313244", relief="solid", bd=2)
frame_tcp.pack(side="left", fill="both", expand=True, padx=(0, 10))

# TCP Header
tcp_header = tk.Frame(frame_tcp, bg="#a6e3a1", height=50)
tcp_header.pack(fill="x")
tcp_header.pack_propagate(False)

tk.Label(
    tcp_header,
    text="TCP (Güvenilir İletim)",
    font=("Segoe UI", 13, "bold"),
    bg="#a6e3a1",
    fg="#1e1e2e"
).pack(pady=12)

# TCP Stats
tcp_stats_frame = tk.Frame(frame_tcp, bg="#313244")
tcp_stats_frame.pack(fill="x", padx=10, pady=8)

tcp_sent_label = tk.Label(
    tcp_stats_frame,
    text="Gönderilen: 0",
    font=("Segoe UI", 9),
    bg="#313244",
    fg="#a6e3a1"
)
tcp_sent_label.pack(side="left", padx=5)

tcp_received_label = tk.Label(
    tcp_stats_frame,
    text="Alınan: 0",
    font=("Segoe UI", 9),
    bg="#313244",
    fg="#a6e3a1"
)
tcp_received_label.pack(side="left", padx=5)

tcp_success_label = tk.Label(
    tcp_stats_frame,
    text="Başarı: %0",
    font=("Segoe UI", 9, "bold"),
    bg="#313244",
    fg="#f9e2af"
)
tcp_success_label.pack(side="right", padx=5)

# TCP Log
tcp_log = tk.Text(
    frame_tcp,
    bg="#1e1e2e",
    fg="#cdd6f4",
    font=("Consolas", 10),
    relief="flat",
    wrap="word"
)
tcp_log.pack(fill="both", expand=True, padx=10, pady=(0, 10))

# UDP Frame
frame_udp = tk.Frame(main_container, bg="#313244", relief="solid", bd=2)
frame_udp.pack(side="right", fill="both", expand=True, padx=(10, 0))

# UDP Header
udp_header = tk.Frame(frame_udp, bg="#f38ba8", height=50)
udp_header.pack(fill="x")
udp_header.pack_propagate(False)

tk.Label(
    udp_header,
    text="UDP (Hızlı İletim)",
    font=("Segoe UI", 13, "bold"),
    bg="#f38ba8",
    fg="#1e1e2e"
).pack(pady=12)

# UDP Stats
udp_stats_frame = tk.Frame(frame_udp, bg="#313244")
udp_stats_frame.pack(fill="x", padx=10, pady=8)

udp_sent_label = tk.Label(
    udp_stats_frame,
    text="Gönderilen: 0",
    font=("Segoe UI", 9),
    bg="#313244",
    fg="#89b4fa"
)
udp_sent_label.pack(side="left", padx=5)

udp_received_label = tk.Label(
    udp_stats_frame,
    text="Alınan: 0",
    font=("Segoe UI", 9),
    bg="#313244",
    fg="#a6e3a1"
)
udp_received_label.pack(side="left", padx=5)

udp_lost_label = tk.Label(
    udp_stats_frame,
    text="Kayıp: 0",
    font=("Segoe UI", 9),
    bg="#313244",
    fg="#f38ba8"
)
udp_lost_label.pack(side="left", padx=5)

udp_success_label = tk.Label(
    udp_stats_frame,
    text="Başarı: %0",
    font=("Segoe UI", 9, "bold"),
    bg="#313244",
    fg="#f9e2af"
)
udp_success_label.pack(side="right", padx=5)

# UDP Log
udp_log = tk.Text(
    frame_udp,
    bg="#1e1e2e",
    fg="#cdd6f4",
    font=("Consolas", 10),
    relief="flat",
    wrap="word"
)
udp_log.pack(fill="both", expand=True, padx=10, pady=(0, 10))

# İstatistikler
tcp_stats = {"sent": 0, "received": 0}
udp_stats = {"sent": 0, "received": 0, "lost": 0}

def tcp_write(msg, color="#cdd6f4"):
    tcp_log.tag_config("custom", foreground=color)
    tcp_log.insert(tk.END, "• " + msg + "\n", "custom")
    tcp_log.see(tk.END)

def udp_write(msg, color="#cdd6f4"):
    udp_log.tag_config("custom", foreground=color)
    udp_log.insert(tk.END, "• " + msg + "\n", "custom")
    udp_log.see(tk.END)

def update_tcp_stats():
    tcp_sent_label.config(text=f"Gönderilen: {tcp_stats['sent']}")
    tcp_received_label.config(text=f"Alınan: {tcp_stats['received']}")
    if tcp_stats['sent'] > 0:
        success = (tcp_stats['received'] / tcp_stats['sent']) * 100
        tcp_success_label.config(text=f"Başarı: %{success:.0f}")

def update_udp_stats():
    udp_sent_label.config(text=f"Gönderilen: {udp_stats['sent']}")
    udp_received_label.config(text=f"Alınan: {udp_stats['received']}")
    udp_lost_label.config(text=f"Kayıp: {udp_stats['lost']}")
    if udp_stats['sent'] > 0:
        success = (udp_stats['received'] / udp_stats['sent']) * 100
        udp_success_label.config(text=f"Başarı: %{success:.0f}")

# ---------- TCP ----------
def tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, TCP_PORT))
    server.listen(1)
    tcp_write("Sunucu başlatıldı, bağlantı bekleniyor...", "#89b4fa")

    conn, _ = server.accept()
    tcp_write("İstemci bağlandı - bağlantı kuruldu", "#a6e3a1")

    while True:
        data = conn.recv(1024)
        if not data:
            break
        tcp_stats['received'] += 1
        update_tcp_stats()
        tcp_write(f"{data.decode()} - onaylandı", "#a6e3a1")

    tcp_write("Bağlantı kapatıldı", "#f9e2af")
    conn.close()
    server.close()

def tcp_client():
    time.sleep(1)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, TCP_PORT))

    for i in range(1, 11):
        msg = f"Paket #{i}"
        client.sendall(msg.encode())
        tcp_stats['sent'] += 1
        update_tcp_stats()
        tcp_write(f"{msg} gönderildi", "#89dceb")
        time.sleep(0.5)

    tcp_write("Tüm paketler başarıyla gönderildi", "#a6e3a1")
    client.close()

# ---------- UDP ----------
def udp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, UDP_PORT))
    udp_write("Sunucu başlatıldı, paket bekleniyor...", "#89b4fa")

    received_count = 0
    while received_count < 10:
        data, _ = server.recvfrom(1024)
        udp_stats['received'] += 1
        update_udp_stats()
        udp_write(f"{data.decode()} - alındı", "#a6e3a1")
        received_count += 1

def udp_client():
    time.sleep(0.5)
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for i in range(1, 11):
        if random.random() < 0.35:  # %35 kayıp oranı
            udp_stats['sent'] += 1
            udp_stats['lost'] += 1
            update_udp_stats()
            udp_write(f"Paket #{i} KAYBOLDU (ağ hatası)", "#f38ba8")
            time.sleep(0.5)
            continue

        msg = f"Paket #{i}"
        client.sendto(msg.encode(), (HOST, UDP_PORT))
        udp_stats['sent'] += 1
        update_udp_stats()
        udp_write(f"{msg} gönderildi", "#89dceb")
        time.sleep(0.5)

    udp_write("Gönderim tamamlandı (bazı paketler kaybolmuş olabilir)", "#f9e2af")

# ---------- BUTTONS ----------
btn_frame = tk.Frame(root, bg="#1e1e2e")
btn_frame.pack(fill="x", padx=20, pady=(0, 15))

def reset_logs():
    tcp_log.delete(1.0, tk.END)
    udp_log.delete(1.0, tk.END)
    tcp_stats.update({"sent": 0, "received": 0})
    udp_stats.update({"sent": 0, "received": 0, "lost": 0})
    update_tcp_stats()
    update_udp_stats()

def start_tcp_test():
    reset_logs()
    threading.Thread(target=tcp_server, daemon=True).start()
    threading.Thread(target=tcp_client, daemon=True).start()

def start_udp_test():
    reset_logs()
    threading.Thread(target=udp_server, daemon=True).start()
    threading.Thread(target=udp_client, daemon=True).start()

tk.Button(
    btn_frame,
    text="TCP Testi Başlat",
    font=("Segoe UI", 11, "bold"),
    bg="#a6e3a1",
    fg="#1e1e2e",
    activebackground="#94e2d5",
    relief="flat",
    padx=20,
    pady=10,
    cursor="hand2",
    command=start_tcp_test
).pack(side="left", padx=10)

tk.Button(
    btn_frame,
    text="UDP Testi Başlat",
    font=("Segoe UI", 11, "bold"),
    bg="#f38ba8",
    fg="#1e1e2e",
    activebackground="#eba0ac",
    relief="flat",
    padx=20,
    pady=10,
    cursor="hand2",
    command=start_udp_test
).pack(side="left", padx=10)

tk.Button(
    btn_frame,
    text="Temizle",
    font=("Segoe UI", 11),
    bg="#45475a",
    fg="#cdd6f4",
    activebackground="#585b70",
    relief="flat",
    padx=20,
    pady=10,
    cursor="hand2",
    command=reset_logs
).pack(side="right", padx=10)

# Bilgi notu
info_label = tk.Label(
    root,
    text="İpucu: TCP her paketi garanti ederken, UDP hızlıdır ancak paket kaybı yaşayabilir",
    font=("Segoe UI", 9),
    bg="#1e1e2e",
    fg="#a6adc8"
)
info_label.pack(pady=(0, 10))

root.mainloop()
