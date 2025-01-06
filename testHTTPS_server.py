import socket
import ssl
import json
import _thread
import machine

class HTTPSServer:
    def __init__(self, port=443):
        self.port = port
        self.routes = {}
        
    def route(self, path, methods=None):
        if methods is None:
            methods = ['GET']
            
        def decorator(handler):
            self.routes[path] = {'handler': handler, 'methods': methods}
            return handler
        return decorator

    def handle_request(self, client_sock):
        try:
            request = client_sock.recv(1024).decode()
            # Parse request
            request_line = request.split('\r\n')[0]
            method, path, _ = request_line.split(' ')
            
            # Find handler
            route_info = self.routes.get(path)
            if route_info and method in route_info['methods']:
                response_data, status_code, headers = route_info['handler'](request)
                
                # Construct response
                status_line = f'HTTP/1.1 {status_code} OK\r\n'
                header_lines = ''.join([f'{k}: {v}\r\n' for k, v in headers.items()])
                response = f'{status_line}{header_lines}\r\n{response_data}'
                
                client_sock.send(response.encode())
            else:
                # 404 response
                response = 'HTTP/1.1 404 Not Found\r\n\r\nNot Found'
                client_sock.send(response.encode())
                
        except Exception as e:
            print(f"Error handling request: {e}")
        finally:
            client_sock.close()

    def run(self):
        sock = socket.socket()
        sock.bind(('0.0.0.0', self.port))
        sock.listen(5)
        
        # Load certificate and private key
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain('cert.pem', 'key.pem')
        
        print(f'HTTPS server running on port {self.port}')
        
        while True:
            try:
                client, addr = sock.accept()
                ssl_client = context.wrap_socket(client, server_side=True)
                _thread.start_new_thread(self.handle_request, (ssl_client,))
            except Exception as e:
                print(f"Error accepting connection: {e}")

# Usage example
server = HTTPSServer()

@server.route('/api/temperature', methods=['GET'])
def get_temperature(request):
    adc = machine.ADC(4)
    conversion_factor = 3.3 / (65535)
    sensor_value = adc.read_u16() * conversion_factor
    temperature = 27 - (sensor_value - 0.706) / 0.001721
    
    return json.dumps({"temperature": temperature}), 200, {"Content-Type": "application/json"}

# Start server
if __name__ == '__main__':
    server.run()