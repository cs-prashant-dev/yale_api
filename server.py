from http.server import SimpleHTTPRequestHandler, HTTPServer
import json
PORT = 8000
import ecobee_device_status
import os
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # Serve the index.html page
            try:
                with open('index.html', 'rb') as file:
                    content = file.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(content)
            except FileNotFoundError:
                self.send_error(404, "index.html not found")
        elif self.path == '/export-ecobee':
            output_file = ecobee_device_status.get_ecobee_device_status()
            if output_file and os.path.exists(output_file):
                # Send file as response
                self.send_response(200)
                self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                self.send_header('Content-Disposition', f'attachment; filename="{output_file}"')
                self.end_headers()
                try:
                    with open(output_file, 'rb') as file:
                        self.wfile.write(file.read())
                        logging.info(f"File '{output_file}' sent successfully.")
                except Exception as file_error:
                    logging.error(f"Error reading or sending the file: {file_error}")
                    self.send_error(500, "Error sending the file.")
            else:
                self.send_error(500, "Failed to export Ecobee data")
        else:
            self.send_error(404, "Page Not Found")

if __name__ == '__main__':
    server = HTTPServer(('localhost', PORT), MyHandler)
    print(f"Server running on http://localhost:{PORT}")
    server.serve_forever()
