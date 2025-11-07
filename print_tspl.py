"""
Simple TSPL printing script for TSC TTP-244 Pro
Using COM7 at 9600 baud, 8N1
"""

from tsc_printer import TSCPrinter
import time

def print_label():
    """Print a simple label using TSPL commands"""
    
    print("Connecting to COM7 at 9600 baud...")
    printer = TSCPrinter(port="COM7", baudrate=9600)
    
    if not printer.connect():
        print("Failed to connect to printer")
        return
    
    print("Connected!")
    print("\nSending TSPL commands...")
    
    try:
        # Clear buffer
        printer.send_command("CLS")
        time.sleep(0.1)
        
        # Set label size (adjust to your label size)
        # Format: SIZE width_mm, height_mm, gap_mm
        printer.send_command("SIZE 110 mm, 80 mm, 2 mm")
        time.sleep(0.1)
        
        # Set print speed (0-14, default 4)
        printer.send_command("SPEED 4")
        time.sleep(0.1)
        
        # Set print density (0-15, default 8)
        printer.send_command("DENSITY 8")
        time.sleep(0.1)
        
        # Set direction (0=normal, 1=180° rotated)
        printer.send_command("DIRECTION 0")
        time.sleep(0.1)
        
        # Print text
        # Format: TEXT x, y, "font", rotation, x_mult, y_mult, "text"
        # x, y in dots (203 DPI = ~8 dots/mm)
        printer.send_command('TEXT 50,50,"3",0,1,1,"Hello World"')
        time.sleep(0.1)
        
        # Print QR code next to "Hello World"
        # Format: QRCODE x, y, error_level, cell_size, rotation, mask, model, "data"
        # error_level: L=Low, M=Medium, Q=Quartile, H=High
        # cell_size: 1-10 (size of each QR code cell)
        # rotation: 0, 90, 180, 270
        printer.send_command('QRCODE 300,50,M,4,A,0,M2,S3,"Hello World"')
        time.sleep(0.1)
        
        printer.send_command('TEXT 50,100,"3",0,2,2,"TSC TTP-244 Pro"')
        time.sleep(0.1)
        
        # Print barcode (optional)
        # Format: BARCODE x, y, "type", height, readable, rotation, narrow, wide, "data"
        printer.send_command('BARCODE 50,150,"128",50,"B",0,2,4,"123456789012"')
        time.sleep(0.1)
        
        # Print the label
        # Format: PRINT quantity, copies
        printer.send_command("PRINT 1,1")
        
        print("Print command sent!")
        print("\nThe label should print now.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        printer.disconnect()
        print("\nDisconnected.")


def print_simple_text(text):
    """Print simple text label"""
    printer = TSCPrinter(port="COM7", baudrate=9600)
    
    if not printer.connect():
        print("Failed to connect")
        return
    
    try:
        printer.send_command("CLS")
        time.sleep(0.1)
        printer.send_command("SIZE 110 mm, 80 mm, 2 mm")
        time.sleep(0.1)
        printer.send_command('TEXT 50,50,"3",0,2,2,"' + text + '"')
        time.sleep(0.1)
        printer.send_command("PRINT 1,1")
    finally:
        printer.disconnect()


if __name__ == "__main__":
    print("=" * 60)
    print("TSC TTP-244 Pro TSPL Printing")
    print("COM7 @ 9600 baud, 8N1")
    print("=" * 60)
    print()
    
    # Print a test label
    print_label()
    
    # Uncomment to print custom text:
    # print_simple_text("Your Custom Text Here")

