import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import socket
import time
from datetime import datetime
from queue import Queue, Empty

HOST = "127.0.0.1"
PORT = 5555
ENCODING = "utf-8"
MSG_DELIM = "\n"  # Satır sonu, mesaj sonu belirteci

def now():
    return datetime.now().strftime("%H:%M:%S")

def safe_shutdown(sock: socket.socket):
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except Exception:
        pass
    try:
        sock.close()
    except Exception:
        pass

class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Server")
        self.root.geometry("560x640")
        self.root.configure(bg="#1e1e2e")

        self.server_socket = None
        self.accept_thread = None
        self.running = False

        # client_id -> (socket, addr, reader_thread)
        self.clients = {}
        self.client_counter = 0
        self.lock = threading.Lock()

        # Top frame
        title_frame = tk.Frame(root, bg="#1e1e2e")
        title_frame.pack(pady=14, fill=tk.X)
        tk.Label(
            title_frame, text="SERVER", font=("Arial", 22, "bold"),
            bg="#1e1e2e", fg="#89b4fa"
        ).pack()
        tk.Label(
            title_frame, text=f"Port: {PORT}", font=("Arial", 11),
            bg="#1e1e2e", fg="#cdd6f4"
        ).pack()

        # Status frame
        status_frame = tk.Frame(root, bg="#313244", relief=tk.RAISED, bd=2)
        status_frame.pack(pady=8, padx=16, fill=tk.X)
        tk.Label(
            status_frame, text="Durum:", font=("Arial", 10, "bold"),
            bg="#313244", fg="#cdd6f4"
        ).pack(side=tk.LEFT, padx=10)

        self.status_label = tk.Label(
            status_frame, text="Kapalı",
            font=("Arial", 10), bg="#313244", fg="#f38ba8"
        )
        self.status_label.pack(side=tk.LEFT, padx=6)

        # Buttons
        button_frame = tk.Frame(root, bg="#1e1e2e")
        button_frame.pack(pady=8)
        self.start_btn = tk.Button(
            button_frame, text="Server Başlat",
            command=self.start_server,
            font=("Arial", 12, "bold"), bg="#a6e3a1",
            fg="#1e1e2e", padx=16, pady=8,
            cursor="hand2", relief=tk.FLAT
        )
        self.start_btn.pack(side=tk.LEFT, padx=6)

        self.stop_btn = tk.Button(
            button_frame, text="Server Durdur",
            command=self.stop_server,
            font=("Arial", 12, "bold"), bg="#f38ba8",
            fg="#1e1e2e", padx=16, pady=8,
            cursor="hand2", relief=tk.FLAT, state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=6)

        # Clients list
        clients_frame = tk.Frame(root, bg="#313244", relief=tk.RAISED, bd=2)
        clients_frame.pack(pady=8, padx=16, fill=tk.X)
        tk.Label(
            clients_frame, text="Bağlı İstemciler:", font=("Arial", 10, "bold"),
            bg="#313244", fg="#cdd6f4"
        ).pack(side=tk.LEFT, padx=10)

        self.clients_combo_var = tk.StringVar(value="Tümü")
        self.clients_combo = ttk.Combobox(
            clients_frame, textvariable=self.clients_combo_var, state="readonly",
            values=["Tümü"], width=30
        )
        self.clients_combo.pack(side=tk.LEFT, padx=10, pady=6)

        # Log
        tk.Label(root, text="Server Logları", font=("Arial", 12, "bold"),
                 bg="#1e1e2e", fg="#cdd6f4").pack(pady=(14, 6))
        self.log_text = scrolledtext.ScrolledText(
            root, height=14, width=66, font=("Consolas", 10),
            bg="#181825", fg="#a6e3a1",
            insertbackground="#cdd6f4", relief=tk.FLAT, padx=10, pady=10
        )
        self.log_text.pack(pady=6, padx=16, fill=tk.BOTH, expand=True)

        # Message input
        input_frame = tk.Frame(root, bg="#313244", relief=tk.RAISED, bd=2)
        input_frame.pack(pady=8, padx=16, fill=tk.X)
        tk.Label(
            input_frame, text="Mesaj:", font=("Arial", 10),
            bg="#313244", fg="#cdd6f4"
        ).pack(anchor=tk.W, padx=10, pady=(10, 4))

        self.message_entry = tk.Entry(
            input_frame, font=("Arial", 11),
            bg="#181825", fg="#cdd6f4",
            insertbackground="#cdd6f4", relief=tk.FLAT
        )
        self.message_entry.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.send_btn = tk.Button(
            root, text="Gönder",
            command=self.send_message_from_server,
            font=("Arial", 13, "bold"), bg="#89b4fa",
            fg="#1e1e2e", padx=20, pady=10,
            cursor="hand2", relief=tk.FLAT, state=tk.DISABLED
        )
        self.send_btn.pack(pady=6)

        # Stats
        stats_frame = tk.Frame(root, bg="#313244", relief=tk.RAISED, bd=2)
        stats_frame.pack(pady=8, padx=16, fill=tk.X)
        tk.Label(
            stats_frame, text="Toplam Mesaj:", font=("Arial", 10),
            bg="#313244", fg="#cdd6f4"
        ).pack(side=tk.LEFT, padx=10)
        self.msg_count_label = tk.Label(
            stats_frame, text="0",
            font=("Arial", 10, "bold"), bg="#313244", fg="#89b4fa"
        )
        self.msg_count_label.pack(side=tk.LEFT)
        self.msg_count = 0

        # For thread-safe logging
        self.log_queue = Queue()
        self.root.after(100, self.flush_log_queue)

    def ui_log(self, message):
        self.log_text.insert(tk.END, f"[{now()}] {message}\n")
        self.log_text.see(tk.END)

    def log(self, message):
        self.log_queue.put(message)

    def flush_log_queue(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.ui_log(msg)
        except Empty:
            pass
        self.root.after(100, self.flush_log_queue)

    def start_server(self):
        if self.running:
            return
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Çalışıyor", fg="#a6e3a1")
        self.send_btn.config(state=tk.NORMAL)

        self.log("Server başlatılıyor...")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen(20)
        self.server_socket.settimeout(1.0)

        self.accept_thread = threading.Thread(target=self.accept_loop, daemon=True)
        self.accept_thread.start()
        self.log(f"Dinleniyor: {HOST}:{PORT}")

    def stop_server(self):
        if not self.running:
            return
        self.running = False
        self.log("Server durduruluyor...")

        # Close listening socket to break accept()
        if self.server_socket:
            safe_shutdown(self.server_socket)
            self.server_socket = None

        # Disconnect all clients
        with self.lock:
            for cid, (csock, _addr, _th) in list(self.clients.items()):
                safe_shutdown(csock)
            self.clients.clear()
            self.update_clients_combo_locked()

        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Kapalı", fg="#f38ba8")
        self.send_btn.config(state=tk.DISABLED)
        self.log("Server durduruldu.")

    def accept_loop(self):
        while self.running:
            try:
                client_sock, addr = self.server_socket.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            except Exception as e:
                self.log(f"Hata(accept): {e}")
                continue

            client_sock.settimeout(1.0)
            with self.lock:
                self.client_counter += 1
                cid = f"Client-{self.client_counter} [{addr[0]}:{addr[1]}]"
                reader_thread = threading.Thread(
                    target=self.client_reader, args=(cid, client_sock, addr), daemon=True
                )
                self.clients[cid] = (client_sock, addr, reader_thread)
                self.update_clients_combo_locked()
                reader_thread.start()

            self.log(f"Bağlantı kabul edildi: {cid}")

    def update_clients_combo_locked(self):
        values = ["Tümü"] + list(self.clients.keys())
        self.root.after(0, lambda: self.clients_combo.configure(values=values))

        # Eğer seçili artık yoksa Tümü yap
        current = self.clients_combo_var.get()
        if current not in values:
            self.root.after(0, lambda: self.clients_combo_var.set("Tümü"))

    def client_reader(self, cid, sock, addr):
        buffer = ""
        try:
            while self.running:
                try:
                    data = sock.recv(4096)
                except socket.timeout:
                    continue
                except OSError:
                    break
                if not data:
                    break
                buffer += data.decode(ENCODING, errors="replace")
                while True:
                    if MSG_DELIM in buffer:
                        line, buffer = buffer.split(MSG_DELIM, 1)
                        msg = line.strip()
                        if msg:
                            self.msg_count += 1
                            count = self.msg_count
                            self.root.after(0, lambda c=count: self.msg_count_label.config(text=str(c)))
                            self.log(f"{cid} -> {msg}")
                    else:
                        break
        except Exception as e:
            self.log(f"Hata({cid}): {e}")
        finally:
            with self.lock:
                if cid in self.clients:
                    safe_shutdown(self.clients[cid][0])
                    del self.clients[cid]
                    self.update_clients_combo_locked()
            self.log(f"Bağlantı kapandı: {cid}")

    def send_message_from_server(self):
        msg = self.message_entry.get().strip()
        if not msg:
            self.log("Lütfen bir mesaj yazın.")
            return

        target = self.clients_combo_var.get()
        to_send = (msg + MSG_DELIM).encode(ENCODING)

        sent_any = False
        with self.lock:
            if target == "Tümü":
                for cid, (csock, _addr, _th) in list(self.clients.items()):
                    try:
                        csock.sendall(to_send)
                        sent_any = True
                    except Exception as e:
                        self.log(f"Gönderim hatası ({cid}): {e}")
            else:
                info = self.clients.get(target)
                if info:
                    csock = info[0]
                    try:
                        csock.sendall(to_send)
                        sent_any = True
                    except Exception as e:
                        self.log(f"Gönderim hatası ({target}): {e}")
                else:
                    self.log("Seçili istemci bulunamadı.")

        if sent_any:
            self.log(f"Server -> {target}: {msg}")
            self.message_entry.delete(0, tk.END)
        else:
            self.log("Mesaj gönderilemedi.")

class ClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Client")
        self.root.geometry("560x640")
        self.root.configure(bg="#1e1e2e")

        self.sock = None
        self.reader_thread = None
        self.connected = False

        # Header
        title_frame = tk.Frame(root, bg="#1e1e2e")
        title_frame.pack(pady=14, fill=tk.X)
        tk.Label(
            title_frame, text="CLIENT", font=("Arial", 22, "bold"),
            bg="#1e1e2e", fg="#f9e2af"
        ).pack()
        tk.Label(
            title_frame, text=f"{HOST}:{PORT}", font=("Arial", 11),
            bg="#1e1e2e", fg="#cdd6f4"
        ).pack()

        # Status
        status_frame = tk.Frame(root, bg="#313244", relief=tk.RAISED, bd=2)
        status_frame.pack(pady=8, padx=16, fill=tk.X)
        tk.Label(
            status_frame, text="Durum:", font=("Arial", 10, "bold"),
            bg="#313244", fg="#cdd6f4"
        ).pack(side=tk.LEFT, padx=10)
        self.status_label = tk.Label(
            status_frame, text="Bağlı değil",
            font=("Arial", 10), bg="#313244", fg="#f38ba8"
        )
        self.status_label.pack(side=tk.LEFT, padx=6)

        # Buttons
        button_frame = tk.Frame(root, bg="#1e1e2e")
        button_frame.pack(pady=8)
        self.connect_btn = tk.Button(
            button_frame, text="Bağlan",
            command=self.connect_server,
            font=("Arial", 12, "bold"), bg="#a6e3a1",
            fg="#1e1e2e", padx=16, pady=8,
            cursor="hand2", relief=tk.FLAT
        )
        self.connect_btn.pack(side=tk.LEFT, padx=6)

        self.disconnect_btn = tk.Button(
            button_frame, text="Ayrıl",
            command=self.disconnect_server,
            font=("Arial", 12, "bold"), bg="#f38ba8",
            fg="#1e1e2e", padx=16, pady=8,
            cursor="hand2", relief=tk.FLAT, state=tk.DISABLED
        )
        self.disconnect_btn.pack(side=tk.LEFT, padx=6)

        # Log
        tk.Label(root, text="Client Logları", font=("Arial", 12, "bold"),
                 bg="#1e1e2e", fg="#cdd6f4").pack(pady=(14, 6))
        self.log_text = scrolledtext.ScrolledText(
            root, height=14, width=66, font=("Consolas", 10),
            bg="#181825", fg="#89b4fa",
            insertbackground="#cdd6f4", relief=tk.FLAT, padx=10, pady=10
        )
        self.log_text.pack(pady=6, padx=16, fill=tk.BOTH, expand=True)

        # Message input
        input_frame = tk.Frame(root, bg="#313244", relief=tk.RAISED, bd=2)
        input_frame.pack(pady=8, padx=16, fill=tk.X)
        tk.Label(
            input_frame, text="Mesaj:", font=("Arial", 10),
            bg="#313244", fg="#cdd6f4"
        ).pack(anchor=tk.W, padx=10, pady=(10, 4))

        self.message_entry = tk.Entry(
            input_frame, font=("Arial", 11),
            bg="#181825", fg="#cdd6f4",
            insertbackground="#cdd6f4", relief=tk.FLAT
        )
        self.message_entry.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.message_entry.insert(0, "Merhaba!")

        self.send_btn = tk.Button(
            root, text="Gönder",
            command=self.send_message,
            font=("Arial", 13, "bold"), bg="#89b4fa",
            fg="#1e1e2e", padx=20, pady=10,
            cursor="hand2", relief=tk.FLAT, state=tk.DISABLED
        )
        self.send_btn.pack(pady=6)

        # Stats
        stats_frame = tk.Frame(root, bg="#313244", relief=tk.RAISED, bd=2)
        stats_frame.pack(pady=8, padx=16, fill=tk.X)
        tk.Label(
            stats_frame, text="Gönderilen Mesaj:", font=("Arial", 10),
            bg="#313244", fg="#cdd6f4"
        ).pack(side=tk.LEFT, padx=10)
        self.sent_count_label = tk.Label(
            stats_frame, text="0",
            font=("Arial", 10, "bold"), bg="#313244", fg="#f9e2af"
        )
        self.sent_count_label.pack(side=tk.LEFT)
        self.sent_count = 0

        # Queue for thread-safe logging
        self.log_queue = Queue()
        self.root.after(100, self.flush_log_queue)

        # Bind Enter key to send when connected
        self.root.bind("<Return>", self.on_enter_send)

    def on_enter_send(self, event):
        if self.connected and self.message_entry.focus_get() is not None:
            self.send_message()

    def ui_log(self, message):
        self.log_text.insert(tk.END, f"[{now()}] {message}\n")
        self.log_text.see(tk.END)

    def log(self, message):
        self.log_queue.put(message)

    def flush_log_queue(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.ui_log(msg)
        except Empty:
            pass
        self.root.after(100, self.flush_log_queue)

    def connect_server(self):
        if self.connected:
            return
        self.log("Bağlanılıyor...")
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((HOST, PORT))
            self.sock.settimeout(1.0)
            self.connected = True
            self.status_label.config(text="Bağlı", fg="#a6e3a1")
            self.connect_btn.config(state=tk.DISABLED)
            self.disconnect_btn.config(state=tk.NORMAL)
            self.send_btn.config(state=tk.NORMAL)

            self.reader_thread = threading.Thread(target=self.reader_loop, daemon=True)
            self.reader_thread.start()
            self.log(f"Bağlandı: {HOST}:{PORT}")
        except Exception as e:
            self.log(f"Bağlantı hatası: {e}")
            self.disconnect_server()

    def disconnect_server(self):
        if self.sock:
            safe_shutdown(self.sock)
        self.sock = None
        self.connected = False
        self.status_label.config(text="Bağlı değil", fg="#f38ba8")
        self.connect_btn.config(state=tk.NORMAL)
        self.disconnect_btn.config(state=tk.DISABLED)
        self.send_btn.config(state=tk.DISABLED)

    def reader_loop(self):
        buffer = ""
        try:
            while self.connected and self.sock:
                try:
                    data = self.sock.recv(4096)
                except socket.timeout:
                    continue
                except OSError:
                    break
                if not data:
                    break
                buffer += data.decode(ENCODING, errors="replace")
                while True:
                    if MSG_DELIM in buffer:
                        line, buffer = buffer.split(MSG_DELIM, 1)
                        msg = line.strip()
                        if msg:
                            self.log(f"Server -> {msg}")
                    else:
                        break
        except Exception as e:
            self.log(f"Hata(alış): {e}")
        finally:
            self.log("Bağlantı sonlandı.")
            self.root.after(0, self.disconnect_server)

    def send_message(self):
        msg = self.message_entry.get().strip()
        if not msg:
            self.log("Lütfen bir mesaj yazın.")
            return
        if not self.connected or not self.sock:
            self.log("Sunucuya bağlı değilsiniz.")
            return
        try:
            self.sock.sendall((msg + MSG_DELIM).encode(ENCODING))
            self.sent_count += 1
            self.sent_count_label.config(text=str(self.sent_count))
            self.log(f"Ben -> {msg}")
            self.message_entry.delete(0, tk.END)
        except Exception as e:
            self.log(f"Gönderim hatası: {e}")
            self.disconnect_server()

def main():
    server_root = tk.Tk()
    server_gui = ServerGUI(server_root)

    client_root = tk.Toplevel(server_root)
    client_gui = ClientGUI(client_root)

    # Place windows side by side
    server_root.geometry("560x640+60+60")
    client_root.geometry("560x640+660+60")

    server_root.mainloop()

if __name__ == "__main__":
    main()
