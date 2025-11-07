"""
GUI Application for Scanner-Based Label Printing
Scanner input is automatically captured and can be printed
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from tsc_printer import TSCPrinter
import threading
import time

class ScannerPrinterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TSC TTP-244 Pro - Scanner Printer")
        self.root.geometry("600x500")
        
        # Printer settings
        self.port = "COM10"
        self.baudrate = 9600
        
        # Storage for multiple barcodes
        self.scanned_barcodes = []
        self.max_barcodes = 20

        # carton counter
        self.carton_counter = self.load_carton_counter()

        # Override flags
        self.override_carton_id = False
        self.override_date = False

        # Create UI
        self.create_widgets()
        
        # # Bind Enter key to print button
        # self.root.bind('<Return>', lambda e: self.print_label())
        
        # Focus on scanner input for automatic capture
        self.scanner_input.focus_set()
        
    def create_widgets(self):
        """Create all UI widgets"""
        
        # Title
        title_label = tk.Label(
            self.root, 
            text="TSC TTP-244 Pro Label Printer", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(self.root, text="Printer Settings", padding=10)
        settings_frame.pack(fill="x", padx=10, pady=5)
        
        # Port selection
        port_frame = tk.Frame(settings_frame)
        port_frame.pack(fill="x", pady=5)
        tk.Label(port_frame, text="COM Port:").pack(side="left", padx=5)
        self.port_entry = tk.Entry(port_frame, width=10)
        self.port_entry.insert(0, self.port)
        self.port_entry.pack(side="left", padx=5)
        
        # Baudrate selection
        baudrate_frame = tk.Frame(settings_frame)
        baudrate_frame.pack(fill="x", pady=5)
        tk.Label(baudrate_frame, text="Baudrate:").pack(side="left", padx=5)
        self.baudrate_entry = tk.Entry(baudrate_frame, width=10)
        self.baudrate_entry.insert(0, str(self.baudrate))
        self.baudrate_entry.pack(side="left", padx=5)
        
        # Test connection button
        test_btn = tk.Button(
            settings_frame, 
            text="Test Connection", 
            command=self.test_connection,
            bg="#4CAF50",
            fg="white"
        )
        test_btn.pack(pady=5)
        
        # Override section
        override_frame = tk.Frame(settings_frame)
        override_frame.pack(fill="x", pady=10)
        
        # Carton ID override
        tk.Label(override_frame, text="Override Carton ID:", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5,2))
        carton_row = tk.Frame(override_frame)
        carton_row.pack(fill="x", pady=2)
        
        self.override_carton_entry = tk.Entry(carton_row, width=15)
        self.override_carton_entry.pack(side="left", padx=5)
        
        self.use_carton_override = tk.BooleanVar(value=False)
        tk.Checkbutton(
            carton_row, 
            text="Use override", 
            variable=self.use_carton_override,
            command=self.toggle_carton_override
        ).pack(side="left")
        
        tk.Label(override_frame, text="(Format: YYWW-XXX, e.g., 2544-001)", font=("Arial", 7), fg="gray").pack(anchor="w", padx=5)
        
        # Date override
        tk.Label(override_frame, text="Override Date Packed:", font=("Arial", 9, "bold")).pack(anchor="w", pady=(10,2))
        date_row = tk.Frame(override_frame)
        date_row.pack(fill="x", pady=2)
        
        self.override_date_entry = tk.Entry(date_row, width=20)
        self.override_date_entry.pack(side="left", padx=5)
        
        self.use_date_override = tk.BooleanVar(value=False)
        tk.Checkbutton(
            date_row, 
            text="Use override", 
            variable=self.use_date_override,
            command=self.toggle_date_override
        ).pack(side="left")
        
        tk.Label(override_frame, text="(Format: YYYY-MM-DD HH:MM:SS)", font=("Arial", 7), fg="gray").pack(anchor="w", padx=5)

        # Counter
        self.counter_label = tk.Label(
            self.root,
            text=f"Scanned: 0 / {self.max_barcodes}",
            font=("Arial", 12, "bold"),
            fg="#2196F3"
        )
        self.counter_label.pack(pady=5)

        # Scanner input frame
        input_frame = ttk.LabelFrame(self.root, text="Scanner Input", padding=10)
        input_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Scanner input field (scanned barcode will appear here)
        tk.Label(
            input_frame, 
            text="Scanned Value (auto-captured when scanner reads):", 
            font=("Arial", 10)
        ).pack(anchor="w", pady=5)
        
        self.scanner_input = tk.Entry(
            input_frame, 
            font=("Arial", 14), 
            width=40
        )
        self.scanner_input.pack(fill="x", pady=5)
        self.scanner_input.bind('<KeyRelease>', self.on_scanner_input)
        
        # # Manual input label
        # tk.Label(
        #     input_frame, 
        #     text="Or type manually:", 
        #     font=("Arial", 9)
        # ).pack(anchor="w", pady=(10, 5))
        
        # # Additional text fields for custom label
        # custom_frame = tk.Frame(input_frame)
        # custom_frame.pack(fill="x", pady=5)
        
        # tk.Label(custom_frame, text="Label Title:").pack(side="left", padx=5)
        # self.title_input = tk.Entry(custom_frame, width=30)
        # self.title_input.pack(side="left", padx=5)
        # self.title_input.insert(0, "Product Label")
        
        # NEW: Scanned items list
        tk.Label(input_frame, text="Scanned Items:", font=("Arial", 10)).pack(anchor="w", pady=5)
        
        list_frame = tk.Frame(input_frame)
        list_frame.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.barcode_listbox = tk.Listbox(
            list_frame,
            font=("Courier", 9),
            yscrollcommand=scrollbar.set,
            height=6
        )
        self.barcode_listbox.pack(fill="both", expand=True, side="left")
        scrollbar.config(command=self.barcode_listbox.yview)

        # NEW: Delete button (right-click to delete)
        self.barcode_listbox.bind('<Button-3>', self.delete_selected)
        tk.Label(
            input_frame, 
            text="(Right-click on item to delete)", 
            font=("Arial", 8), 
            fg="gray"
        ).pack(anchor="w")

        # Print button
        self.print_btn = tk.Button(
            input_frame,
            text=f"🖨️ PRINT LABEL",
            command=self.print_label,
            font=("Arial", 12, "bold"),
            bg="#2196F3",
            fg="white",
            height=6,
            state="disabled"
        )
        self.print_btn.pack(pady=5, fill="x")
        
        # Status/log area
        log_frame = ttk.LabelFrame(self.root, text="Status Log", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=8, 
            font=("Courier", 9)
        )
        self.log_text.pack(fill="both", expand=True)
        
        self.log("Application started. Ready to scan and print.")
        self.log(f"Scan items, than click PRINT once ready.")

        # Load carton counter from file (persists between sessions)
    def load_carton_counter(self):
        try:
            with open('carton_counter.txt', 'r') as f:
                return int(f.read().strip())
        except:
            return 1

    # Save carton counter to file
    def save_carton_counter(self):
        try:
            with open('carton_counter.txt', 'w') as f:
                f.write(str(self.carton_counter))
        except Exception as e:
            self.log(f"Warning: Could not save counter - {e}")
    
    # Extract S/N from barcode string
    def extract_serial_number(self, barcode_string):
        """
        Extract S/N from barcode format:
        "EBD S/N: HAA02-2544-336PCB S/No: HB25390000142PCB Rev: HT_EBD_V25EBD FW: 14"
        Returns: "HAA02-2544-336"
        """
        import re
        
        # Pattern: "S/N: " followed by alphanumeric with hyphens
        match = re.search(r'S/N:\s*([A-Z0-9\-]+)(?=PCB)', barcode_string)
        
        if match:
            serial = match.group(1)
            # Remove any trailing non-alphanumeric characters
            serial = re.split(r'[^A-Z0-9\-]', serial)[0]
            return serial
        else:
            # If pattern not found, return original string
            self.log(f"Warning: Could not extract S/N from: {barcode_string}")
            return barcode_string   

    # Toggle methods for overrides
    def toggle_carton_override(self):
        """Enable/disable carton ID override"""
        if self.use_carton_override.get():
            self.override_carton_entry.config(state="normal", bg="white")
            self.log("Carton ID override enabled")
        else:
            self.override_carton_entry.config(state="disabled", bg="#f0f0f0")
            self.log("Carton ID override disabled")
    
    def toggle_date_override(self):
        """Enable/disable date override"""
        if self.use_date_override.get():
            self.override_date_entry.config(state="normal", bg="white")
            self.log("Date override enabled")
        else:
            self.override_date_entry.config(state="disabled", bg="#f0f0f0")
            self.log("Date override disabled")

    def log(self, message):
        """Add message to log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")

    def update_counter(self):
        """Update counter and button state"""
        qr_count = len(self.scanned_barcodes)
        self.counter_label.config(text=f"Scanned: {qr_count}")
        
        if qr_count > 1:
            self.print_btn.config(
                state="normal", 
                bg="#2196F3",
                text=f"🖨️ PRINT LABEL ({qr_count} QR Codes)"
            )
        else:
            self.print_btn.config(
                state="disabled", 
                bg="#cccccc",
                text=f"🖨️ PRINT LABEL (Scan items first)"
            )

    def on_scanner_input(self, event):
        """Handle scanner input (usually ends with Enter)"""
        value = self.scanner_input.get().strip()
        if value and event.keysym == 'Return':
           self.add_barcode()
            # Scanner typically sends Enter after barcode
            # self.log(f"Scanned value detected: {value}")
            # # Auto-print option (uncomment if you want auto-print on scan)
            # self.print_label()

    def add_barcode(self):
        """Add scanned barcode to list"""
        value = self.scanner_input.get().strip()
        
        if not value:
            return
       
        # Extract S/N before storing
        extracted_sn = self.extract_serial_number(value)
        
        self.scanned_barcodes.append(extracted_sn)
        index = len(self.scanned_barcodes)
        
        # Display extracted S/N in listbox
        self.barcode_listbox.insert("end", f"{index:02d}. {extracted_sn}")
        self.barcode_listbox.see("end")
        self.scanner_input.delete(0, "end")
        self.update_counter()

        # Log both original and extracted
        self.log(f"Scanned: {value[:50]}...")  # Show first 50 chars
        self.log(f"Extracted S/N: {extracted_sn} ({index}/{self.max_barcodes})")
        
    def delete_selected(self, event):
        """Delete selected barcode (right-click)"""
        selection = self.barcode_listbox.curselection()
        if not selection:
            return
            
        idx = selection[0]
        deleted = self.scanned_barcodes.pop(idx)

     # Refresh list
        self.barcode_listbox.delete(0, "end")
        for i, barcode in enumerate(self.scanned_barcodes, 1):
            self.barcode_listbox.insert("end", f"{i:02d}. {barcode}")
            
        self.update_counter()
        self.log(f"Deleted: {deleted}")    

    def test_connection(self):
        """Test printer connection"""
        self.port = self.port_entry.get().strip()
        try:
            self.baudrate = int(self.baudrate_entry.get().strip())
        except:
            self.baudrate = 9600
            
        self.log(f"Testing connection to {self.port} at {self.baudrate} baud...")
        
        def test():
            try:
                printer = TSCPrinter(port=self.port, baudrate=self.baudrate)
                if printer.connect():
                    printer.disconnect()
                    self.log("✅ Connection successful!")
                    messagebox.showinfo("Success", f"Connected to {self.port} successfully!")
                else:
                    self.log("❌ Connection failed!")
                    messagebox.showerror("Error", f"Failed to connect to {self.port}")
            except Exception as e:
                self.log(f"❌ Error: {e}")
                messagebox.showerror("Error", f"Connection error: {e}")
                
        threading.Thread(target=test, daemon=True).start()

    def format_carton_id(self):
        """Format: CYYWW-XXX (e.g. C2544-001)"""
        from datetime import datetime
        now = datetime.now()
        year = now.strftime("%y")
        week = now.strftime("%U")
        return f"C{year}{week}-{self.carton_counter:03d}"

    def print_label(self):
        """Print label with scanned/manual input"""
        # scanned_value = self.scanner_input.get().strip()
        # title = self.title_input.get().strip()
        
        # if not scanned_value:
        #     messagebox.showwarning("Warning", "Please enter a scanned value or type manually")
        #     return
        if len(self.scanned_barcodes) == 0:
            messagebox.showwarning("Not ready", "Please scan at least 1 item to print!")
            return

        self.log(f"Printing {self.scanned_barcodes} QR codes...")
        
        # Get settings
        self.port = self.port_entry.get().strip()
        try:
            self.baudrate = int(self.baudrate_entry.get().strip())
        except:
            self.baudrate = 9600

        def print_job():
            try:
                printer = TSCPrinter(port=self.port, baudrate=self.baudrate)
                
                if not printer.connect():
                    self.log("❌ Failed to connect to printer")
                    messagebox.showerror("Error", "Failed to connect to printer")
                    return
                
                self.log("✅ Connected to printer")
                
                # Get carton ID and timestamp
                from datetime import datetime
                # Check for carton ID override
                if self.use_carton_override.get() and self.override_carton_entry.get().strip():
                    carton_id = self.override_carton_entry.get().strip()
                    self.log(f"Using override Carton ID: {carton_id}")
                else:
                    carton_id = self.format_carton_id()
                
                # Check for date override
                if self.use_date_override.get() and self.override_date_entry.get().strip():
                    date_packed = self.override_date_entry.get().strip()
                    self.log(f"Using override Date: {date_packed}")
                else:
                    date_packed = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Clear buffer
                printer.send_command("CLS")
                time.sleep(0.1)
                
                # Set label size (100mm x 150mm)
                printer.send_command("SIZE 100 mm, 150 mm, 2 mm")
                time.sleep(0.1)
                
                # Set print settings
                printer.send_command("SPEED 4")
                time.sleep(0.1)
                printer.send_command("DENSITY 8")
                time.sleep(0.1)
                printer.send_command("DIRECTION 0")
                time.sleep(0.1)
                
                # Print header - Carton ID
                printer.send_command(f'TEXT 50,30,"3",0,1,2,"Carton ID: {carton_id}"')
                time.sleep(0.1)

                # Print header - Date Packed
                printer.send_command(f'TEXT 50,100,"3",0,1,2,"Date Packed: {date_packed}"')
                time.sleep(0.1)

                # Print header - QR Code of Carton ID
                printer.send_command(f'QRCODE 650,20,M,5,A,0,M2,S3,"{carton_id}"')
                time.sleep(0.1)

                # Print horizontal line separator
                printer.send_command('BAR 50,170,750,4')
                time.sleep(0.1)
                
                # Print table of scanned values as TEXT 
                item_count = len(self.scanned_barcodes)

                for i in range(item_count):
                    row = i // 2  
                    col = i % 2
                    x = 50 + (col * 380)    
                    y = 200 + (row * 85) 
                    
                    # Get actual scanned value
                    scanned_value = self.scanned_barcodes[i]
                    item_number = i + 1

                    display_text = f"{item_number:02d}. {scanned_value}"
                    
                    # Print scanned value as TEXT (not QR code)
                    printer.send_command(f'TEXT {x},{y},"3",0,1,1,"{display_text}"')
                    time.sleep(0.05)
                
                # Execute print
                printer.send_command("PRINT 1,1")
                
                self.log("✅ Print command sent successfully!")
                
                # Increment carton counter for next print
                if not self.use_carton_override.get():
                    self.carton_counter += 1
                    self.save_carton_counter()
                    self.log(f"Carton counter incremented to: {self.carton_counter}")
                else:
                    self.log("Carton counter NOT incremented (override used)")
                printer.disconnect()
                
                # ✅ MODIFIED: Show success message
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success", 
                    f"Carton {carton_id} printed!\n{self.max_barcodes} items in table format"
                ))
                
                # Clear scanner input after successful print
                if messagebox.askyesno("Continue?", "Clear and scan another batch?"):
                    self.scanned_barcodes.clear()
                    self.barcode_listbox.delete(0, "end")
                    self.update_counter()
                    self.scanner_input.delete(0, "end")
                    self.scanner_input.focus_set()
                
            except Exception as e:
                error_msg = f"Print error: {e}"
                self.log(f"❌ {error_msg}")
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        # # Print in background thread
        # def print_job():
        #     try:
        #         printer = TSCPrinter(port=self.port, baudrate=self.baudrate)
                
        #         if not printer.connect():
        #             self.log("❌ Failed to connect to printer")
        #             messagebox.showerror("Error", "Failed to connect to printer")
        #             return
                
        #         self.log("✅ Connected to printer")
                
        #         # Clear buffer
        #         printer.send_command("CLS")
        #         time.sleep(0.1)
                
        #         # Set label size
        #         printer.send_command("SIZE 100 mm, 150 mm, 2 mm")
        #         time.sleep(0.1)
                
        #         # Set print settings
        #         printer.send_command("SPEED 4")
        #         time.sleep(0.1)
        #         printer.send_command("DENSITY 8")
        #         time.sleep(0.1)
        #         printer.send_command("DIRECTION 0")
        #         time.sleep(0.1)
                
        #         # Title
        #         printer.send_command(f'TEXT 50,50,"3",0,2,2,"CARTON IDs:{carton_id}"')
        #         printer.send_command(f'TEXT 50,100,"3",0,1,1,"Date Packed:{date_str}"')
        #         time.sleep(0.1)
                
        #         for i in range(self.max_barcodes):
        #             row = i // 4
        #             col = i % 4
        #             x = 50 + (col * 170)
        #             y = 80 + (row * 200)

        #             carton_id = self.format_carton_id(i + 1)

        #             # Print QR code 
        #             printer.send_command(f'QRCODE {x}, {y}, M,4,A,0,M2,S3,"{carton_id}"')
        #             time.sleep(0.5)

        #             # Print scanned value
        #             printer.send_command(f'TEXT {x}, {y+90},"1,0,1,1,"{carton_id}"')
        #             time.sleep(0.5)

        #         # Execute print
        #         printer.send_command("PRINT 1,1")
                
        #         self.log("✅ Print command sent successfully!")
        #         printer.disconnect()
                
        #         # Show success message
        #         self.root.after(0, lambda: messagebox.showinfo(
        #             "Success", f"Label printed!\n{self.max_barcodes} QR codes in CYYWW-XXX format"
        #         ))
                
        #         # Clear scanner input after successful print
        #         if messagebox.askyesno("Continue?", "Clear and scan another batch?"):
        #             self.scanned_barcodes.clear()
        #             self.barcode_listbox.delete(0, "end")
        #             self.update_counter()
        #             self.scanner_input.delete(0, "end")
        #             self.scanner_input.focus_set()
                
        #     except Exception as e:
        #         error_msg = f"Print error: {e}"
        #         self.log(f"❌ {error_msg}")
        #         self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        
        threading.Thread(target=print_job, daemon=True).start()


def main():
    root = tk.Tk()
    app = ScannerPrinterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

