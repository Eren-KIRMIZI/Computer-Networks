import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import socket
import time
from datetime import datetime

HOST = "127.0.0.1"
PORTS = [5000, 5001, 5002]
ENC = "utf-8"
DELIM = "\n"

def now():
    return datetime.now().strftime("%H:%M:%S")

def safe_close(sock):
    if not sock:
        return
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except Exception:
        pass
    try:
        sock.close()
    except Exception:
        pass

class MiniServer:
    def __init__(self, host, port, on_log):
        self.host = host
        self.port = port
        self.on_log = on_log
        self.sock = None
        self.running = False
        self.accept_thread = None
        self.client_threads = []
        self.lock = threading.Lock()

    def log(self, msg):
        self.on_log(f"[Server {self.port}] {msg}")

    def start(self):
        if self.running:
            return
        self.running = True
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            self.sock.listen(5)
            self.sock.settimeout(1.0)
            self.accept_thread = threading.Thread(target=self.accept_loop, daemon=True)
            self.accept_thread.start()
            self.log(f"Dinlemede {self.host}:{self.port}")
        except Exception as e:
            self.log(f"Hata: {e}")
            self.stop()

    def stop(self):
        if not self.running:
            return
        self.running = False
        safe_close(self.sock)
        self.sock = None

        with self.lock:
            for t in self.client_threads:
                # threadler recv ile kendiliğinden çıkacak, soketler client_handler içinde kapanır
                pass
            self.client_threads.clear()
        self.log("Durduruldu")

    def accept_loop(self):
        while self.running:
            try:
                c, addr = self.sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            except Exception as e:
                self.log(f"accept hatası: {e}")
                continue
            t = threading.Thread(target=self.client_handler, args=(c, addr), daemon=True)
            with self.lock:
                self.client_threads.append(t)
            t.start()

    def client_handler(self, c, addr):
        peer = f"{addr[0]}:{addr[1]}"
        self.log(f"Bağlantı {peer}")
        buf = ""
        c.settimeout(1.0)
        try:
            while self.running:
                try:
                    data = c.recv(4096)
                except socket.timeout:
                    continue
                except OSError:
                    break
                if not data:
                    break
                buf += data.decode(ENC, errors="replace")
                while DELIM in buf:
                    line, buf = buf.split(DELIM, 1)
                    msg = line.strip()
                    if msg:
                        self.log(f"Geldi <- {msg} (port {self.port})")
                        # Basit eko
                        reply = f"Port {self.port} mesajı aldı: {msg}{DELIM}"
                        try:
                            c.sendall(reply.encode(ENC))
                        except Exception as e:
                            self.log(f"Yanıt hatası: {e}")
                            break
        except Exception as e:
            self.log(f"İşleme hatası: {e}")
        finally:
            safe_close(c)
            self.log(f"Bağlantı kapandı {peer}")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("IP & Port Mini Uygulama")
        self.root.geometry("900x640")
        self.root.configure(bg="#1e1e2e")

        # Durumlar
        self.servers = {}
        self.server_states = {p: False for p in PORTS}

        # Üst bilgi
        top = tk.Frame(root, bg="#1e1e2e")
        top.pack(fill=tk.X, padx=16, pady=12)
        tk.Label(top, text="IP Adresi ve Port Nedir?", font=("Arial", 18, "bold"),
                 bg="#1e1e2e", fg="#cdd6f4").pack(anchor=tk.W)
        tk.Label(top, text="IP = Hangi makine?    Port = Hangi uygulama?",
                 font=("Arial", 12), bg="#1e1e2e", fg="#a6adc8").pack(anchor=tk.W, pady=(4,0))

        # Orta bölüm: Sunucu kontrolleri
        servers_frame = tk.Frame(root, bg="#313244", relief=tk.RAISED, bd=2)
        servers_frame.pack(fill=tk.X, padx=16, pady=8)

        tk.Label(servers_frame, text=f"Aynı IP: {HOST}", font=("Arial", 12, "bold"),
                 bg="#313244", fg="#cdd6f4").grid(row=0, column=0, sticky="w", padx=10, pady=10, columnspan=4)

        self.port_vars = {}
        self.port_buttons = {}
        col = 0
        for i, p in enumerate(PORTS):
            frame = tk.Frame(servers_frame, bg="#313244")
            frame.grid(row=1, column=i, padx=10, pady=10, sticky="nsew")
            tk.Label(frame, text=f"Port {p}", font=("Arial", 12, "bold"),
                     bg="#313244", fg="#89b4fa").pack(anchor="w")
            var = tk.StringVar(value="Kapalı")
            lbl = tk.Label(frame, textvariable=var, font=("Arial", 10),
                           bg="#313244", fg="#f38ba8")
            lbl.pack(anchor="w", pady=(2,6))
            btn = tk.Button(frame, text="Başlat", font=("Arial", 10, "bold"),
                            bg="#a6e3a1", fg="#1e1e2e", relief=tk.FLAT,
                            command=lambda port=p: self.toggle_server(port))
            btn.pack(anchor="w")
            self.port_vars[p] = (var, lbl)
            self.port_buttons[p] = btn

        # Client paneli
        client_frame = tk.Frame(root, bg="#313244", relief=tk.RAISED, bd=2)
        client_frame.pack(fill=tk.X, padx=16, pady=8)

        tk.Label(client_frame, text="Client", font=("Arial", 12, "bold"),
                 bg="#313244", fg="#cdd6f4").grid(row=0, column=0, sticky="w", padx=10, pady=10, columnspan=4)

        tk.Label(client_frame, text="IP:", font=("Arial", 10),
                 bg="#313244", fg="#cdd6f4").grid(row=1, column=0, sticky="e", padx=10)
        self.ip_entry = tk.Entry(client_frame, font=("Arial", 11), width=16,
                                 bg="#181825", fg="#cdd6f4", insertbackground="#cdd6f4", relief=tk.FLAT)
        self.ip_entry.grid(row=1, column=1, sticky="w", pady=6)
        self.ip_entry.insert(0, HOST)

        tk.Label(client_frame, text="Port:", font=("Arial", 10),
                 bg="#313244", fg="#cdd6f4").grid(row=1, column=2, sticky="e", padx=10)
        self.port_combo = ttk.Combobox(client_frame, state="readonly", width=10, values=[str(p) for p in PORTS])
        self.port_combo.grid(row=1, column=3, sticky="w")
        self.port_combo.set(str(PORTS[0]))

        tk.Label(client_frame, text="Mesaj:", font=("Arial", 10),
                 bg="#313244", fg="#cdd6f4").grid(row=2, column=0, sticky="e", padx=10)
        self.msg_entry = tk.Entry(client_frame, font=("Arial", 11),
                                  bg="#181825", fg="#cdd6f4", insertbackground="#cdd6f4", relief=tk.FLAT, width=40)
        self.msg_entry.grid(row=2, column=1, columnspan=2, sticky="w", pady=6)
        self.msg_entry.insert(0, "Merhaba, hangi porta gittiğimi gör!")

        self.send_btn = tk.Button(client_frame, text="Gönder", font=("Arial", 11, "bold"),
                                  bg="#89b4fa", fg="#1e1e2e", relief=tk.FLAT,
                                  command=self.client_send)
        self.send_btn.grid(row=2, column=3, sticky="w", padx=4)

        # Log alanları: Sol sunucu logları, sağ client logları
        logs_frame = tk.Frame(root, bg="#1e1e2e")
        logs_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)

        # Sunucu logları
        server_logs_frame = tk.Frame(logs_frame, bg="#1e1e2e")
        server_logs_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,8))
        tk.Label(server_logs_frame, text="Sunucu Logları", font=("Arial", 12, "bold"),
                 bg="#1e1e2e", fg="#cdd6f4").pack(anchor="w", pady=(0,6))
        self.server_log = scrolledtext.ScrolledText(server_logs_frame, height=18, font=("Consolas", 10),
                                                    bg="#181825", fg="#a6e3a1", insertbackground="#cdd6f4",
                                                    relief=tk.FLAT, padx=10, pady=10)
        self.server_log.pack(fill=tk.BOTH, expand=True)

        # Client logları
        client_logs_frame = tk.Frame(logs_frame, bg="#1e1e2e")
        client_logs_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8,0))
        tk.Label(client_logs_frame, text="Client Logları", font=("Arial", 12, "bold"),
                 bg="#1e1e2e", fg="#cdd6f4").pack(anchor="w", pady=(0,6))
        self.client_log = scrolledtext.ScrolledText(client_logs_frame, height=18, font=("Consolas", 10),
                                                    bg="#181825", fg="#89b4fa", insertbackground="#cdd6f4",
                                                    relief=tk.FLAT, padx=10, pady=10)
        self.client_log.pack(fill=tk.BOTH, expand=True)

        # Kapanışta temizlik
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Kısayol
        self.root.bind("<Return>", self.on_enter)

    def on_enter(self, event):
        if self.msg_entry.focus_get() is not None:
            self.client_send()

    def slog(self, text):
        self.server_log.insert(tk.END, f"[{now()}] {text}\n")
        self.server_log.see(tk.END)

    def clog(self, text):
        self.client_log.insert(tk.END, f"[{now()}] {text}\n")
        self.client_log.see(tk.END)

    def toggle_server(self, port):
        running = self.server_states.get(port, False)
        if not running:
            # Start
            srv = MiniServer(HOST, port, on_log=lambda m: self.root.after(0, self.slog, m))
            self.servers[port] = srv
            srv.start()
            self.server_states[port] = True
            var, lbl = self.port_vars[port]
            var.set("Çalışıyor")
            lbl.config(fg="#a6e3a1")
            self.port_buttons[port].config(text="Durdur", bg="#f38ba8")
        else:
            # Stop
            srv = self.servers.get(port)
            if srv:
                srv.stop()
            self.server_states[port] = False
            var, lbl = self.port_vars[port]
            var.set("Kapalı")
            lbl.config(fg="#f38ba8")
            self.port_buttons[port].config(text="Başlat", bg="#a6e3a1")

    def client_send(self):
        ip = self.ip_entry.get().strip()
        try:
            port = int(self.port_combo.get())
        except ValueError:
            self.clog("Geçersiz port")
            return
        msg = self.msg_entry.get().strip()
        if not msg:
            self.clog("Lütfen mesaj yazın")
            return

        self.clog(f"Gönderiliyor -> {ip}:{port} | Mesaj: {msg}")
        t = threading.Thread(target=self._client_send_worker, args=(ip, port, msg), daemon=True)
        t.start()

    def _client_send_worker(self, ip, port, msg):
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3.0)
            s.connect((ip, port))
            s.sendall((msg + DELIM).encode(ENC))
            # Cevap bekle
            s.settimeout(3.0)
            data = s.recv(4096)
            if data:
                text = data.decode(ENC, errors="replace").strip()
                self.root.after(0, self.clog, f"Cevap alındı <- {text} (hangi porttan geldiği yanıtta yazıyor)")
            else:
                self.root.after(0, self.clog, "Sunucudan yanıt gelmedi")
        except ConnectionRefusedError:
            self.root.after(0, self.clog, "Bağlantı reddedildi (o portta sunucu yok)")
        except socket.timeout:
            self.root.after(0, self.clog, "Zaman aşımı")
        except Exception as e:
            self.root.after(0, self.clog, f"Hata: {e}")
        finally:
            safe_close(s)

    def on_close(self):
        # Tüm sunucuları durdur
        for p, srv in list(self.servers.items()):
            srv.stop()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = App(root)
    # Pencerede başlangıç yerleşimi
    root.geometry("+80+60")
    root.mainloop()

if __name__ == "__main__":
    main()
