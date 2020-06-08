import os
import sys
import socket
import json

import config as c

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((c.BIND_ADDR, c.BIND_PORT))
server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
server_socket.setblocking(False)
server_socket.listen(True)
print(f"Successfully bound to {c.BIND_ADDR}:{c.BIND_PORT}")

def receive_request(socket):
	resp = ""

	try:
		conn, addr = socket.accept()
	except BlockingIOError:
		return None, None

	while True:
		data = conn.recv(c.REQ_CHUNKSIZE)
		if not data:
			break
		resp += data.decode("utf-8")

	js = json.loads(resp)
	cli_addr, cli_port = conn.getpeername()

	print(f"{cli_addr}:{cli_port} > {js}")

	return conn, js

def reply(conn, data):
	conn.sendall(bytes(json.dumps(data), "utf-8"))

	cli_addr, cli_port = conn.getpeername()

	print(f"{cli_addr}:{cli_port} < {data}")

serverlist = []

def add_server(conn, data):
	if "name" in data:
		if not isinstance(data["name"], str): return False
	else: return False

	if "desc" in data:
		if not isinstance(data["desc"], str): return False
	else: return False

	if "players" in data:
		if not isinstance(data["players"], int): return False
	else: return False

	if "maxplayers" in data:
		if not isinstance(data["maxplayers"], int): return False
	else: return False

	if "pnames" in data:
		if not isinstance(data["pnames"], list): return False
		print("n")
		for pname in data["pnames"]:
			if not isinstance(pname, str): return False
	else: return False

	cli_addr, cli_port = conn.getpeername()
	new_server = {"addr": cli_addr, "port": cli_port, "server": data}

	serverlist.append(new_server)
	return True

def mk_lobby():
	num_players = 0
	for server in serverlist:
		num_players += server["server"]["players"]

	return {"name": c.LOBBY_NAME, "players": num_players}

try:
	while True:
		conn, resp = receive_request(server_socket)
		if conn == None:
			continue

		if resp["command"] == "":
			continue
		elif resp["command"] == "getserverlist":
			reply(conn, serverlist)
		elif resp["command"] == "getlobby":
			reply(conn, mk_lobby())
		elif resp["command"] == "publish":
			if add_server(conn, resp["data"]):
				reply(conn, "OK")
			else:
				reply(conn, "FAIL")
		else:
			continue

finally:
	server_socket.close()
