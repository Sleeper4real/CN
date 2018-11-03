import socket # Include library

ServerSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
HostIP = socket.gethostname()
PortNumber = 15566

ServerSocket.bind( ( HostIP, PortNumber ) ) 
ServerSocket.listen( 5 )
while True :
	Client, Address = ServerSocket.accept()
	Message = Client.recv( 1024 )
	print “Got connection from ”, Address
	print “Msg from client : ”, Message
	Client.send( “Thank you for connecting” )
	Client.close()