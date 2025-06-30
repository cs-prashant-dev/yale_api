from django.http import HttpResponse, FileResponse, Http404
from django.shortcuts import render
from exporter import ecobee_device_status
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def index(request):
    return render(request, 'index.html')

def export_ecobee(request):
    output_file = ecobee_device_status.get_ecobee_device_status()
    if output_file and os.path.exists(output_file):
        try:
            file = open(output_file, 'rb')
            response = FileResponse(file, as_attachment=True, filename=output_file)
            logging.info(f"File '{output_file}' sent successfully.")
            return response
        except Exception as file_error:
            logging.error(f"Error reading or sending the file: {file_error}")
            return HttpResponse("Error sending the file.", status=500)
    else:
        return HttpResponse("Failed to export Ecobee data", status=500)
