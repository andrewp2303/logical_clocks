from multiprocessing import Process
import os
import socket
from _thread import *
import threading
import time
from threading import Thread
import random
 
# Dictionary that stores messages for all of the currently running processes.
messages = {}

# Questions: 
# 1. What do unit tests look like for this assignment?
# 2. How is this going to be graded? Is it just the design document?
# 3. Why do we need separate consumer and producer threads?
# 4. Working within your implementation, where would we implement the 1-10 random number part of the design specification?
# 5. What connections are made within your implementation? Are those connections just within machines?
# 6. How would we go about making connections between machines?

def consumer(conn, port):
	print("consumer accepted connection" + str(conn)+"\n")
	sleepVal = 0.0500
	while True:
		time.sleep(sleepVal)
		data = conn.recv(1024)
		print("msg received\n")
		dataVal = data.decode('ascii')
		print("msg received:", dataVal)
		messages[port].append(dataVal)
 

def producer(portVal, tickSize):
	host= "127.0.0.1"
	port = int(portVal)
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

	# if we tick n times in a second, our sleepVal must be 1/n
	sleepVal = 1 / tickSize

	#sema acquire
	try:
		s.connect((host,port))
		print("Client-side connection success to port val:" + str(portVal) + "\n")
 
		while True:
			codeVal = str(code)
			time.sleep(sleepVal)
			s.send(codeVal.encode('ascii'))
			print("msg sent", codeVal)

			# Check if empty or not empty

			# generate rand number

			# Do the appropriate thing

	except socket.error as e:
		print ("Error connecting producer: %s" % e)
 

# def init_machine(config):
# 	HOST = str(config[0])
# 	PORT = int(config[1])
# 	print("starting server | port val:", PORT)
# 	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 	s.bind((HOST, PORT))
# 	s.listen()
# 	while True:
# 		conn, addr = s.accept()
# 		start_new_thread(consumer, (conn,))
 

def machine(config, allPorts):
	config.append(os.getpid())
	global code
	#print(config)

	# starting the server

	HOST = str(config[0])
	PORT = int(config[1])
	print("starting server | port val:", PORT)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, PORT))
	s.listen()
	#add delay to initialize the server-side logic on all processes
	time.sleep(5)
	
	# create a producer thread for as many as exist in config
	# prod_thread = Thread(target=producer, args=(config[2], config[-2],))
	# prod_thread.start()

	# figure out what ports are not the current port
	ports = [port for port in allPorts if port != PORT]

	sockets = []
	# for each port:
	# create a socket that will connect to that port, and add it to the list of sockets
	# while True with our ticksize delay:
	# we either unpack a message from the queue, or roll 1-10 and act accordingly
	# note that we can use sockets[1].send() to send a message to the first, sockets[2].send() for the second
	# and both to send to both 


	#sema acquire
	# for port in ports: do the below, and make sure to add socket to list of sockets
	# host= "127.0.0.1"
	# port = int(portVal)

	for port in ports:
		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

		try:
			s.connect((HOST,port))
			sockets.append(s)
			print("Client-side connection success to port val:" + str(port) + "\n")
	
			# while True:
			# 	codeVal = str(code)
			# 	time.sleep(sleepVal)
			# 	s.send(codeVal.encode('ascii'))
			# 	print("msg sent", codeVal)

				# Check if empty or not empty

				# generate rand number

				# Do the appropriate thing

		except socket.error as e:
			print ("Error connecting producer: %s" % e)


	# if we tick n times in a second, our sleepVal must be 1/n
	tickSize = int(config[2])
	sleepVal = 1 / tickSize

	count = 0
	while count < 2:
		conn, addr = s.accept()
		start_new_thread(consumer, (conn, PORT,))
		count += 1

	logClock = 0
	while True:
		code = random.randint(1,10)
		if len(messages[port]) > 0:
			msg = int(messages[port].pop(0))
			logClock = max(logClock, msg) + 1
			with open(f"log{PORT}.txt", "a") as f:
				response = f"Message received! Global time: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
				response += f"Message queue length: {len(messages[PORT])}\n"
				response += f"Logical clock time: {logClock} \n\n"
				f.write(response)

		elif code == 1 or code == 2:
			sockets[code - 1].send(str(logClock).encode('ascii'))
			logClock += 1
			with open(f"log{PORT}.txt", "a") as f:
				response = f"Message sent to port {ports[code - 1]}! " 
				response += f"Global time: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
				response += f"Logical clock time: {logClock} \n\n"
				f.write(response)

		elif code == 3:
			sockets[0].send(str(logClock).encode('ascii'))
			sockets[1].send(str(logClock).encode('ascii'))
			logClock += 1
			with open(f"log{PORT}.txt", "a") as f:
				response = f"Message sent to ports {ports[0]} and {ports[1]}! " 
				response += f"Global time: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
				response += f"Logical clock time: {logClock} \n\n"
				f.write(response)
		
		else:
			logClock += 1
			with open(f"log{PORT}.txt", "a") as f:
				response = f"Internal event! " 
				response += f"Global time: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
				response += f"Logical clock time: {logClock} \n\n"
				f.write(response)

		time.sleep(sleepVal)




if __name__ == '__main__':

	localHost= "127.0.0.1"
	ports = [2056, 3056, 4056]

	for port in ports:
		messages[port] = []

	randTimes = [random.randint(1, 6) for _ in range(3)]
	config1=[localHost, ports[0], randTimes[0]]
	p1 = Process(target=machine, args=(config1,ports,))
	config2=[localHost, ports[1], randTimes[1]]
	p2 = Process(target=machine, args=(config2,ports,))
	config3=[localHost, ports[2], randTimes[2]]
	p3 = Process(target=machine, args=(config3,ports,))


	p1.start()
	p2.start()
	p3.start()


	p1.join()
	p2.join()
	p3.join()