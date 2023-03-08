from multiprocessing import Process
import os, socket, time, random, re
from _thread import *
from threading import Thread

def consumer(conn):
	'''Listens for incoming messages and adds them to the messages queue.'''

	print("consumer accepted connection" + str(conn)+"\n")
	sleepVal = 0.0500

	# Constantly listen for messages, with minimal sleep in between (system time).
	while True:
		time.sleep(sleepVal)
		data = conn.recv(1024)
		dataVal = data.decode('ascii')

		# Only add messages to queue if non-empty.
		if dataVal != "":

			# Test that incoming messages are possible logical clock values.
			assert(int(dataVal) >= 0)

			messages.append(dataVal)
 

def init_machine(config):
	'''Initialize the machine by starting a consumer thread for connecting ports.'''

	# Extract host and port from config.
	HOST = str(config[0])

	# Extract port and examine it for validity.
	PORT = int(config[1])
	assert(PORT >= 0 and PORT <= 65535)

	# Run the server and accept incoming connection requests.
	print("starting server | port val:", PORT)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, PORT))
	s.listen()
	
	while True:
		conn, _ = s.accept()
		start_new_thread(consumer, (conn,))
 

def machine(config, allPorts):
	'''Simulate a machine running given a port config; run within a process.'''

	config.append(os.getpid())

	# Messages queue that is shared throughout the process.
	global messages
	messages = []

	# Initialize the server at this port, and wait for the others to complete.
	init_thread = Thread(target=init_machine, args=(config,))
	init_thread.start()
	time.sleep(5)
	
	HOST = str(config[0])
	PORT = int(config[1])

	# Form a socket connection to all other machines, add these to the sockets list.
	ports = [int(port) for port in allPorts if port != PORT]
	sockets = []
	for port in ports:
		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		try:
			s.connect((HOST,port))
			sockets.append(s)
			print("Client-side connection success to port val:" + str(port) + "\n")

		except socket.error as e:
			print ("Error connecting producer: %s" % e)

	# Test that a socket connection has been formed with all other machines.
	assert(len(sockets) == len(ports))

	# If we tick n times in a second, our sleepVal must be 1/n.
	assert(int(config[2]) >= 1)
	tickSize = int(config[2])
	sleepVal = 1 / tickSize
	print(f"Process {os.getpid()} running at {tickSize} ticks per second.")

	logClock = 0

	# Store information about the clock ticks in arrays that can be plotted.
	currTime = 0
	sizePerSecond = []
	clockPerSecond = []

	with open(f"log{PORT}.txt", "w") as f:
		with open (f"output{PORT}.txt", "w") as k: 
			with open (f"output{PORT}_queue.txt", "w") as l: 
				with open (f"output{PORT}_seconds.txt", "w") as z:
					while True:
						# Generate a random code 1-10.
						code = random.randint(1, 10)

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

						currTime += 1

						# Record one second passed and reset currTime.
						if currTime == tickSize:
							sizePerSecond.append(len(messages))
							clockPerSecond.append(logClock)
							currTime = 0

						# Plot after a minute.
						if len(sizePerSecond) > 60:
							for i in range(1, 61):
								z.write(f"{i}\n")
								l.write(f"{sizePerSecond[i - 1]}\n")
								k.write(f"{clockPerSecond[i - 1]}\n")
							return

						time.sleep(sleepVal)


def assertConfig(config):
	'''Check that an input config is valid.'''

	# Validate host address using https://www.geeksforgeeks.org/python-program-to-validate-an-ip-address/.
	ipRegex = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
	assert(re.match(ipRegex, config[0]))

	# Check that port is in valid range, and that tick size is at least 1.
	assert(int(config[1]) >= 0 and int(config[1]) <= 65535)
	assert(int(config[2]) >= 1)


if __name__ == '__main__':

	localHost= "127.0.0.1"
	ports = [2056, 3056, 4056]

	# Define clock speed for each of the 3 processes.
	randTimes = [random.randint(1, 6) for _ in range(3)]

	config1=[localHost, ports[0], randTimes[0]]
	assertConfig(config1)
	p1 = Process(target=machine, args=(config1,ports,))

	config2=[localHost, ports[1], randTimes[1]]
	assertConfig(config2)
	p2 = Process(target=machine, args=(config2,ports,))

	config3=[localHost, ports[2], randTimes[2]]
	assertConfig(config3)
	p3 = Process(target=machine, args=(config3,ports,))


	p1.start()
	p2.start()
	p3.start()


	p1.join()
	p2.join()
	p3.join()