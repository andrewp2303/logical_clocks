from multiprocessing import Process
import os
import socket
from _thread import *
import threading
import time
from threading import Thread
import random

# TODO:
# 1. Create unit tests.
# 2. Work out if "consumer" thread is working 100% properly.
# 3. Add additional print statements / log statements to make our analysis easier.

# Questions: 
# 1. What do unit tests look like for this assignment?
# 2. How is this going to be graded? Is it just the design document?
# 3. Why do we need separate consumer and producer threads?
# 4. Working within your implementation, where would we implement the 1-10 random number part of the design specification?
# 5. What connections are made within your implementation? Are those connections just within machines?
# 6. How would we go about making connections between machines?

def consumer(conn):
	print("consumer accepted connection" + str(conn)+"\n")
	sleepVal = 0.0500

	# Constantly listen for messages, with minimal sleep in between.
	while True:
		time.sleep(sleepVal)
		data = conn.recv(1024)
		dataVal = data.decode('ascii')

		# Only add messages to queue if non-empty.
		if dataVal != "":
			messages.append(dataVal)
 

def init_machine(config):

	# Extract host and port from config.
	HOST = str(config[0])
	PORT = int(config[1])

	# Run the server and accept incoming connection requests.
	print("starting server | port val:", PORT)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, PORT))
	s.listen()
	while True:
		conn, addr = s.accept()
		start_new_thread(consumer, (conn,))
 

def machine(config, allPorts):
	config.append(os.getpid())

	# Messages queue that is shared throughout the process.
	global messages
	messages = []

	# Initialize the server at this port, and wait for the others to complete.
	init_thread = Thread(target=init_machine, args=(config,))
	init_thread.start()
	time.sleep(5)
	
	# Extract host and port from config.
	HOST = str(config[0])
	PORT = int(config[1])

	# Determine all ports that are not the current port
	ports = [int(port) for port in allPorts if port != PORT]

	# List of potential sockets to send messages to.
	sockets = []

	# Connect to all ports except the process's port.
	for port in ports:
		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		try:
			s.connect((HOST,port))
			sockets.append(s)
			print("Client-side connection success to port val:" + str(port) + "\n")

		except socket.error as e:
			print ("Error connecting producer: %s" % e)


	# If we tick n times in a second, our sleepVal must be 1/n
	tickSize = int(config[2])
	sleepVal = 1 / tickSize
	print(f"Process {os.getpid()} running at {tickSize} ticks per second.")

	logClock = 0
	with open(f"log{PORT}.txt", "w") as f:
		while True:

			# Generate a random code 1-10.
			code = random.randint(1,10)

			# Pop a message from the queue if there are messages.
			if len(messages) > 0:
				msg = int(messages.pop(0))
				logClock = max(logClock, msg) + 1
				response = f"Message received! Global time: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
				response += f"Message queue length: {len(messages)}\n"
				response += f"Logical clock time: {logClock} \n\n"
				f.write(response)

			# Send a message to one of the other machines.
			elif code == 1 or code == 2:
				sockets[code - 1].send(str(logClock).encode('ascii'))
				logClock += 1
				response = f"Message sent to port {ports[code - 1]}! " 
				response += f"Global time: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
				response += f"Logical clock time: {logClock} \n\n"
				f.write(response)

			# Send a message to both other machines.
			elif code == 3:
				sockets[0].send(str(logClock).encode('ascii'))
				sockets[1].send(str(logClock).encode('ascii'))
				logClock += 1
				response = f"Message sent to ports {ports[0]} and {ports[1]}! " 
				response += f"Global time: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
				response += f"Logical clock time: {logClock} \n\n"
				f.write(response)
			
			# Register an internal event.
			else:
				logClock += 1
				response = f"Internal event! " 
				response += f"Global time: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
				response += f"Logical clock time: {logClock} \n\n"
				f.write(response)

			time.sleep(sleepVal)




if __name__ == '__main__':

	localHost= "127.0.0.1"
	ports = [2056, 3056, 4056]

	# Define clock speed for each of the 3 processes.
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