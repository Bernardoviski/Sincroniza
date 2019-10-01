# Sincroniza Web App - Por João Lucas | Desenvolvido como requisito para a Mostra Cientifica
import socket
import threading
from utils import *
from urllib.parse import unquote
from python_parser import pythonfier


content_dir = "web/"


class WebServer(object):
    def __init__(self, port):
        self.port = port
        self.host = socket.gethostbyname(socket.gethostname())
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _headers(self, status, cookie=""):
        preset = f"\nServer: Sincroniza\nConnection: close\n\n"
        if cookie != "":
            preset = f"\nServer: Sincroniza\nConnection: close\n{cookie}\n\n"
        if status == 200:
            header = "HTTP/1.1 200 Response OK" + preset
        elif status == 401:
            header = "HTTP/1.1 400 Not Authorized." + preset
        elif status == 403:
            header = "HTTP/1.1 403 Permissions Required." + preset
        elif status == 404:
            header = "HTTP/1.1 404 Not Found." + preset
        else:
            header = "HTTP/1.1 500 Server Could Not Process the Request." + preset
        return header

    def _request_handler(self, type, body):
        cookies = ""
        vars = {"cookies": {}, "url_params": {}}
        for line in body.split("\n"):
            if line.startswith("Cookie:"):
                cook = line[8:].split("; ")
                for cokizinho in cook:
                    for cokizinho in cook:
                        if cokizinho.endswith("\r"):
                            vars["cookies"].update({cokizinho.split("=")[0]: cokizinho.split("=")[1][:-1]})
                        else:
                            vars["cookies"].update({cokizinho.split("=")[0]: cokizinho.split("=")[1]})
        file = body.split(" ")[1].split("?")[0]
        try:
            for param in body.split(" ")[1].split("?")[1].split("&"):
                vars["url_params"].update({param.split("=")[0]: param.split("=")[1]})
        except:
            pass
        file = content_dir + file
        if type in ["GET", "HEAD"]:
            if file == content_dir + "/": file = content_dir + "index.html"
            try:
                file_contents = htmlfy(open(file, "rb").read())
                if file.endswith(".html"): cookies, file_contents = pythonfier(file_contents.decode(), vars)
                return self._headers(200, cookies).encode() + file_contents
            except FileNotFoundError:
                return self._headers(
                    404).encode() + b"<html><head><title>UC | 404</title></head><body><center><h1>Erro 404</h1></center></body></html>"
            except OSError:
                return self._headers(403).encode() + htmlfy(
                    f"<html><head><title>UC | 403</title></head><body><center><h1>Erro 403</h1><br><p>Esta p&aacutegina &eacute restrita.</p></center></body></html>").encode()
            except Exception as e:
                return self._headers(500).encode() + htmlfy(
                    f"<html><head><title>UC | 500</title></head><body><center><h1>Erro 500</h1><br><p>Um erro occoreu no servidor. detalhes:<br>{e}</p></center></body></html>").encode()
        elif type == "POST":
            values = {"cookies": {}}
            for line in body.split("\n"):
                if line.startswith("Cookie:"):
                    cook = line[8:].split("; ")
                    for cokizinho in cook:
                        if cokizinho.endswith("\r"):
                            values["cookies"].update({cokizinho.split("=")[0]: cokizinho.split("=")[1][:-1]})
                        else:
                            values["cookies"].update({cokizinho.split("=")[0]: cokizinho.split("=")[1]})
            try:
                for value in unquote(body.split("\n")[-1]).split("&"):
                    values.update({value.split("=")[0]: value.split("=")[1]})
            except Exception as e:
                print(e)
            if file == content_dir + "/": file = content_dir + "index.html"
            try:
                file_contents = htmlfy(open(file, "rb").read())
                if file.endswith(".html"): cookies, file_contents = pythonfier(file_contents.decode("utf-8"), values)
                return self._headers(200, cookies).encode() + file_contents
            except FileNotFoundError:
                return self._headers(
                    404).encode() + b"<html><head><title>UC | 404</title></head><body><center><h1>Erro 404</h1></center></body></html>"
            except OSError:
                return self._headers(403).encode() + htmlfy(
                    f"<html><head><title>UC | 403</title></head><body><center><h1>Erro 403</h1><br><p>Esta p&aacutegina &eacute restrita.</p></center></body></html>".encode()).encode()
            except Exception as e:
                return self._headers(500).encode() + htmlfy(
                    f"<html><head><title>UC | 500</title></head><body><center><h1>Erro 500</h1><br><p>Um erro occoreu no servidor. detalhes:<br>{e}</p></center></body></html>".encode()).encode()
        return self._headers(200).encode() + body.encode()

    def _handler(self, client, addr):
        while True:
            data = client.recv(1000024)
            if not data: break
            try:
                data = data.decode('utf-8')
            except Exception as e:
                print("[WEB] Unknown")
                client.close()
                break
            method = data.split(" ")[0]
            response = self._request_handler(method, data)
            client.send(response)
            client.close()
            break

    def start(self):
        try:
            print(f"[WEB] Binding to {self.host}:{self.port}")
            self.socket.bind((self.host, self.port))
            print("[WEB] Binded.")
        except Exception as e:
            self.socket.close()
            print(f"[WEB] Failed to bind. {e}")
            exit()
        self._listener()

    def _listener(self):
        self.socket.listen(5)
        while True:
            (client, addr) = self.socket.accept()
            client.settimeout(60)
            print(f"[WEB] Recieved incoming connection. {addr}")
            print("[WEB] Starting Handler Thread")
            threading.Thread(target=self._handler, args=(client, addr)).start()

print("[LOG] Hello from Jão!")
while True:
    print("[LOG] Starting WEB")
    WebServer(80).start()
