"""
TSC Printer Interface Module
Handles serial communication with TSC TTP-244 Pro printer
"""

import serial
import time

class TSCPrinter:
    """Interface for TSC label printers using TSPL commands"""
    
    def __init__(self, port="COM7", baudrate=9600, timeout=2):
        """
        Initialize printer connection parameters
        
        Args:
            port: Serial port (e.g., 'COM7' on Windows)
            baudrate: Communication speed (default 9600)
            timeout: Serial timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None
        
    def connect(self):
        """
        Establish connection to printer
        
        Returns:
            bool: True if connected successfully, False otherwise
        """
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )
            time.sleep(0.5)  # Give printer time to initialize
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """Close printer connection"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
    
    def send_command(self, command):
        """
        Send TSPL command to printer
        
        Args:
            command: TSPL command string
            
        Returns:
            bool: True if sent successfully
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            print("Printer not connected")
            return False
        
        try:
            # Add line ending and encode
            cmd_bytes = (command + '\r\n').encode('utf-8')
            self.serial_conn.write(cmd_bytes)
            return True
        except Exception as e:
            print(f"Send error: {e}")
            return False
    
    def is_connected(self):
        """Check if printer is connected"""
        return self.serial_conn and self.serial_conn.is_open