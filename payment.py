import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os
import sys
import subprocess
import random

class PaymentApp:
    def __init__(self, root, email, booking=None, callback=None):
        self.root = root
        self.email = email
        self.booking = booking or {}
        self.callback = callback
        self.root.attributes('-fullscreen', True) 
        
        self.root.title("Traney - Payment")
        self.root.geometry("1400x800")
        self.root.configure(bg="#f0f2f5")
        
        # Colors
        self.colors = {
            "primary": "#1e3d59",
            "secondary": "#ff6e40",
            "success": "#4CAF50",
            "light": "#f0f8ff",
            "dark": "#1e3d59",
            "white": "#ffffff",
            "gray": "#95a5a6"
        }
        
        # Initialize all payment fields
        self.card_number = None
        self.card_name = None
        self.expiry = None
        self.cvv = None
        self.bank_account = None
        self.bank_name = None
        self.swift_code = None
        self.mobile_number = None
        self.wallet_type = None
        self.paypal_email = None
        
        # Bank transfer fields
        self.selected_bank = None
        self.user_id = None
        self.password = None
        
        # Current method
        self.current_method = "credit_card"
        
        # Validate booking data
        self.validate_booking_data()
        
        # Setup UI
        self.setup_ui()
        
        # Initialize with card fields
        self.show_payment_fields()
    
    def validate_booking_data(self):
        """Validate booking data"""
        if not self.booking:
            self.booking = {
                "booking_id": f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "booking_type": "attraction",
                "total_price": 0.00,
                "status": "pending"
            }
        
        # Ensure required fields
        if "booking_id" not in self.booking:
            self.booking["booking_id"] = f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        if "booking_type" not in self.booking:
            self.booking["booking_type"] = "attraction"
        
        if "status" not in self.booking:
            self.booking["status"] = "pending"
        
        if "item_name" not in self.booking:
            self.booking["item_name"] = f"{self.booking['booking_type'].replace('_', ' ').title()} Booking"
    
    def setup_ui(self):
        """Setup the payment interface"""
        # Main container
        self.main_container = tk.Frame(self.root, bg=self.colors["light"])
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self.create_header()
        
        # Content
        self.create_content()
    
    def create_header(self):
        """Create header"""
        header = tk.Frame(self.main_container, bg=self.colors["primary"], height=70)
        header.pack(fill="x", pady=(0, 20))
        
        # Back button and title
        back_frame = tk.Frame(header, bg=self.colors["primary"])
        back_frame.pack(side="left", padx=20)
        
        back_btn = tk.Button(back_frame, text="← Back", 
                           font=("Arial", 14),
                           bg=self.colors["primary"], fg="white",
                           relief="flat", cursor="hand2",
                           command=self.confirm_cancel_booking)
        back_btn.pack(side="left", padx=(0, 20))
        
        # Title
        item_name = self.booking.get("item_name", "Booking")
        if len(item_name) > 30:
            item_name = item_name[:27] + "..."
        title_label = tk.Label(header, text=f"💳 Payment - {item_name}", 
                              font=("Arial", 18, "bold"),
                              bg=self.colors["primary"], fg="white")
        title_label.pack(side="left")
    
    def create_content(self):
        """Create payment content"""
        container = tk.Frame(self.main_container, bg=self.colors["light"])
        container.pack(fill="both", expand=True)
        
        # Left panel - payment methods
        left_panel = tk.Frame(container, bg="white", padx=30, pady=30)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        tk.Label(left_panel, text="Payment Method", 
                font=("Arial", 20, "bold"),
                bg="white", fg=self.colors["dark"]).pack(anchor="w", pady=(0, 20))
        
        # Payment methods
        methods = [
            ("💳 Credit / Debit Card", "credit_card"),
            ("🏦 Bank Transfer", "bank_transfer"),
            ("📱 Mobile Wallet", "mobile_wallet"),
            ("🔵 PayPal", "paypal"),
        ]
        
        self.method_var = tk.StringVar(value="credit_card")
        
        # Create radio buttons with proper command binding
        for title, value in methods:
            method_frame = tk.Frame(left_panel, bg="white")
            method_frame.pack(fill="x", pady=8)
            
            # Create a custom radio button using Checkbutton style
            def create_method_button(frame, text, val, var):
                btn = tk.Radiobutton(
                    frame,
                    text=text,
                    variable=var,
                    value=val,
                    bg="white",
                    font=("Arial", 14),
                    indicatoron=0,  # No indicator, looks like button
                    width=25,
                    anchor="w",
                    padx=15,
                    pady=8,
                    relief="raised",
                    command=lambda v=val: self.on_method_selected(v)
                )
                return btn
            
            rb = create_method_button(method_frame, title, value, self.method_var)
            rb.pack(fill="x")
        
        # Payment details label
        self.details_label = tk.Label(left_panel, text="Payment Details", 
                font=("Arial", 16, "bold"),
                bg="white", fg=self.colors["dark"])
        self.details_label.pack(anchor="w", pady=(30, 10))
        
        # Create main container for scrollable area and button
        content_container = tk.Frame(left_panel, bg="white")
        content_container.pack(fill="both", expand=True)
        
        # Create scrollable fields container
        scroll_frame = tk.Frame(content_container, bg="white")
        scroll_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(scroll_frame, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        self.fields_container = tk.Frame(canvas, bg="white")
        
        # Configure canvas scrolling
        self.fields_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Create window in canvas
        canvas_window = canvas.create_window((0, 0), window=self.fields_container, anchor="nw", width=canvas.winfo_reqwidth())
        
        # Update canvas width when container resizes
        def update_canvas_width(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", update_canvas_width)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configure canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mouse wheel scrolling
        def on_mouse_wheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mouse_wheel)
        
        # Pay button (fixed at bottom)
        button_frame = tk.Frame(content_container, bg="white")
        button_frame.pack(fill="x", side="bottom", pady=(10, 0))
        
        pay_btn = tk.Button(button_frame, text="Pay Now",
                          command=self.process_payment,
                          font=("Arial", 14, "bold"),
                          bg=self.colors["primary"], fg="white",
                          padx=30, pady=12,
                          cursor="hand2")
        pay_btn.pack(anchor="e")
        
        # Right panel - booking summary (NOT scrollable)
        right_panel = tk.Frame(container, bg="white", padx=30, pady=30)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        tk.Label(right_panel, text="Booking Summary", 
                font=("Arial", 20, "bold"),
                bg="white", fg=self.colors["dark"]).pack(anchor="w", pady=(0, 20))
        
        # Create booking details frame (not scrollable)
        details_frame = tk.Frame(right_panel, bg="white")
        details_frame.pack(fill="both", expand=False, pady=(0, 30))
        
        # Booking details
        booking_id = self.booking.get("booking_id", "N/A")
        booking_type = self.booking.get("booking_type", "attraction").title()
        item_name = self.booking.get("item_name", "N/A")
        
        details = [
            ("Booking ID:", booking_id),
            ("Type:", booking_type),
            ("Item:", item_name),
        ]
        
        if "date" in self.booking:
            details.append(("Date:", self.booking["date"]))
        if "tickets" in self.booking:
            details.append(("Tickets:", str(self.booking["tickets"])))
        if "check_in" in self.booking:
            details.append(("Check-in:", self.booking["check_in"]))
        if "check_out" in self.booking:
            details.append(("Check-out:", self.booking["check_out"]))
        if "room_type" in self.booking:
            details.append(("Room Type:", self.booking["room_type"]))
        if "guests" in self.booking:
            details.append(("Guests:", str(self.booking["guests"])))
        if "duration" in self.booking:
            details.append(("Duration:", self.booking["duration"]))
        if "location" in self.booking:
            details.append(("Location:", self.booking["location"]))
        if "provider" in self.booking:
            details.append(("Provider:", self.booking["provider"]))
        if "contact" in self.booking:
            details.append(("Contact:", self.booking["contact"]))
        if "notes" in self.booking:
            details.append(("Special Notes:", self.booking["notes"]))
        
        for label, value in details:
            detail_row = tk.Frame(details_frame, bg="white")
            detail_row.pack(fill="x", pady=5)
            
            tk.Label(detail_row, text=label, font=("Arial", 12),
                    bg="white", fg=self.colors["gray"], width=15, anchor="w").pack(side="left")
            tk.Label(detail_row, text=value, font=("Arial", 12, "bold"),
                    bg="white", fg=self.colors["dark"], wraplength=300, justify="left").pack(side="left", padx=(10, 0), fill="x", expand=True)
        
        # Amount breakdown
        breakdown_frame = tk.Frame(right_panel, bg="#f8f9fa", padx=20, pady=20)
        breakdown_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(breakdown_frame, text="Amount", 
                font=("Arial", 16, "bold"),
                bg="#f8f9fa", fg=self.colors["dark"]).pack(anchor="w", pady=(0, 15))
        
        # Calculate total
        try:
            total_price = float(self.booking.get("total_price", 0))
        except (ValueError, TypeError):
            total_price = 0.0
        
        tax = total_price * 0.06
        service_fee = 5.00 if total_price < 500 else 10.00
        total = total_price + tax + service_fee
        
        prices = [
            ("Subtotal:", f"RM {total_price:,.2f}"),
            ("Tax (6%):", f"RM {tax:,.2f}"),
            ("Service Fee:", f"RM {service_fee:,.2f}"),
            ("TOTAL:", f"RM {total:,.2f}")
        ]
        
        for label, value in prices:
            price_frame = tk.Frame(breakdown_frame, bg="#f8f9fa")
            price_frame.pack(fill="x", pady=5)
            
            tk.Label(price_frame, text=label, font=("Arial", 12),
                    bg="#f8f9fa", fg=self.colors["dark"], anchor="w").pack(side="left")
            tk.Label(price_frame, text=value, font=("Arial", 12, "bold"),
                    bg="#f8f9fa", fg=self.colors["dark"] if label != "TOTAL:" else self.colors["primary"]).pack(side="right")
    
    def on_method_selected(self, method):
        """Handle payment method selection"""
        self.current_method = method
        self.show_payment_fields()
    
    def show_payment_fields(self):
        """Show payment fields based on selected method"""
        # Clear existing fields
        for widget in self.fields_container.winfo_children():
            widget.destroy()
        
        method = self.current_method
        
        # Update label
        labels = {
            "credit_card": "Card Details",
            "bank_transfer": "Bank Transfer Details",
            "mobile_wallet": "Mobile Wallet Details",
            "paypal": "PayPal Details"
        }
        self.details_label.config(text=labels.get(method, "Payment Details"))
        
        if method == "credit_card":
            self.create_card_fields()
        elif method == "bank_transfer":
            self.create_bank_fields()
        elif method == "mobile_wallet":
            self.create_mobile_fields()
        elif method == "paypal":
            self.create_paypal_fields()
    
    def create_card_fields(self):
        """Create credit card fields"""
        # Card number
        tk.Label(self.fields_container, text="Card Number", font=("Arial", 12),
                bg="white", fg=self.colors["dark"]).pack(anchor="w", pady=(0, 5))
        
        self.card_number = tk.Entry(self.fields_container, font=("Arial", 12),
                                   bg="#f9f9f9", relief="solid", borderwidth=1)
        self.card_number.pack(fill="x", pady=(0, 15))
        
        # Cardholder name
        tk.Label(self.fields_container, text="Cardholder Name", font=("Arial", 12),
                bg="white", fg=self.colors["dark"]).pack(anchor="w", pady=(0, 5))
        
        self.card_name = tk.Entry(self.fields_container, font=("Arial", 12),
                                 bg="#f9f9f9", relief="solid", borderwidth=1)
        self.card_name.pack(fill="x", pady=(0, 15))
        
        # Expiry and CVV in one row
        row_frame = tk.Frame(self.fields_container, bg="white")
        row_frame.pack(fill="x", pady=(0, 20))
        
        # Expiry
        expiry_frame = tk.Frame(row_frame, bg="white")
        expiry_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        tk.Label(expiry_frame, text="Expiry Date (MM/YY)", font=("Arial", 12),
                bg="white", fg=self.colors["dark"]).pack(anchor="w", pady=(0, 5))
        
        self.expiry = tk.Entry(expiry_frame, font=("Arial", 12),
                              bg="#f9f9f9", relief="solid", borderwidth=1)
        self.expiry.pack(fill="x")
        
        # CVV
        cvv_frame = tk.Frame(row_frame, bg="white")
        cvv_frame.pack(side="right", fill="x", expand=True)
        
        tk.Label(cvv_frame, text="CVV", font=("Arial", 12),
                bg="white", fg=self.colors["dark"]).pack(anchor="w", pady=(0, 5))
        
        self.cvv = tk.Entry(cvv_frame, font=("Arial", 12),
                           bg="#f9f9f9", relief="solid", borderwidth=1, show="*")
        self.cvv.pack(fill="x")
        
        # Security note
        info_frame = tk.Frame(self.fields_container, bg="#f0f8ff", padx=15, pady=10)
        info_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(info_frame, text="🔒 Secure Payment", 
                font=("Arial", 11, "bold"),
                bg="#f0f8ff", fg=self.colors["primary"]).pack(anchor="w")
        
        note = "Your payment information is encrypted and securely processed."
        
        tk.Label(info_frame, text=note, font=("Arial", 10),
                bg="#f0f8ff", fg=self.colors["gray"],
                justify="left").pack(anchor="w", pady=(5, 0))
        
        # Add padding to bottom to ensure all content is visible
        spacer = tk.Frame(self.fields_container, bg="white", height=10)
        spacer.pack(fill="x")
    
    def create_bank_fields(self):
        """Create bank transfer fields with bank selection and login"""
        # Bank selection
        tk.Label(self.fields_container, text="Select Bank", font=("Arial", 12),
                bg="white", fg=self.colors["dark"]).pack(anchor="w", pady=(0, 5))
        
        banks = [
            "Maybank", "CIMB Bank", "Public Bank", "RHB Bank",
            "Hong Leong Bank", "AmBank", "UOB Bank", "Standard Chartered",
            "HSBC Bank", "OCBC Bank", "Bank Islam", "Bank Muamalat"
        ]
        
        self.selected_bank = ttk.Combobox(self.fields_container, 
                                         values=banks,
                                         font=("Arial", 12),
                                         state="readonly")
        self.selected_bank.pack(fill="x", pady=(0, 15))
        
        # Bank login credentials
        tk.Label(self.fields_container, text="Bank User ID", font=("Arial", 12),
                bg="white", fg=self.colors["dark"]).pack(anchor="w", pady=(0, 5))
        
        self.user_id = tk.Entry(self.fields_container, font=("Arial", 12),
                               bg="#f9f9f9", relief="solid", borderwidth=1)
        self.user_id.pack(fill="x", pady=(0, 15))
        
        tk.Label(self.fields_container, text="Password", font=("Arial", 12),
                bg="white", fg=self.colors["dark"]).pack(anchor="w", pady=(0, 5))
        
        self.password = tk.Entry(self.fields_container, font=("Arial", 12),
                                bg="#f9f9f9", relief="solid", borderwidth=1, show="•")
        self.password.pack(fill="x", pady=(0, 15))
        
        # Instructions
        info_frame = tk.Frame(self.fields_container, bg="#f0f8ff", padx=15, pady=10)
        info_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(info_frame, text="ℹ️ Secure Bank Login:", 
                font=("Arial", 11, "bold"),
                bg="#f0f8ff", fg=self.colors["primary"]).pack(anchor="w")
        
        instructions = """1. Select your bank from the list above
2. Enter your bank's online banking credentials
3. You'll be redirected to your bank's secure login page
4. Authorize the payment using your bank's 2FA method
5. You'll be redirected back after payment confirmation"""
        
        tk.Label(info_frame, text=instructions, font=("Arial", 10),
                bg="#f0f8ff", fg=self.colors["gray"],
                justify="left").pack(anchor="w", pady=(5, 0))
        
        # Security warning
        warning_frame = tk.Frame(self.fields_container, bg="#fff3cd", padx=15, pady=10)
        warning_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(warning_frame, text="⚠️ Security Notice:", 
                font=("Arial", 11, "bold"),
                bg="#fff3cd", fg="#856404").pack(anchor="w")
        
        warning = """Your credentials are transmitted securely using bank-grade encryption.
Never share your banking credentials with anyone else."""
        
        tk.Label(warning_frame, text=warning, font=("Arial", 10),
                bg="#fff3cd", fg="#856404",
                justify="left").pack(anchor="w", pady=(5, 0))
        
        # Add padding to bottom to ensure all content is visible
        spacer = tk.Frame(self.fields_container, bg="white", height=10)
        spacer.pack(fill="x")
    
    def create_mobile_fields(self):
        """Create mobile wallet fields"""
        # Mobile number
        tk.Label(self.fields_container, text="Mobile Number", font=("Arial", 12),
                bg="white", fg=self.colors["dark"]).pack(anchor="w", pady=(0, 5))
        
        self.mobile_number = tk.Entry(self.fields_container, font=("Arial", 12),
                                     bg="#f9f9f9", relief="solid", borderwidth=1)
        self.mobile_number.pack(fill="x", pady=(0, 15))
        
        # Wallet type
        tk.Label(self.fields_container, text="Wallet Provider", font=("Arial", 12),
                bg="white", fg=self.colors["dark"]).pack(anchor="w", pady=(0, 5))
        
        self.wallet_type = ttk.Combobox(self.fields_container, 
                                       values=["Touch 'n Go", "GrabPay", "Boost", "ShopeePay", "WeChat Pay", "Alipay"],
                                       font=("Arial", 12),
                                       state="readonly")
        self.wallet_type.pack(fill="x", pady=(0, 15))
        
        # Wallet holder name
        tk.Label(self.fields_container, text="Wallet Holder Name", font=("Arial", 12),
                bg="white", fg=self.colors["dark"]).pack(anchor="w", pady=(0, 5))
        
        self.card_name = tk.Entry(self.fields_container, font=("Arial", 12),
                                 bg="#f9f9f9", relief="solid", borderwidth=1)
        self.card_name.pack(fill="x", pady=(0, 15))
        
        # Instructions
        info_frame = tk.Frame(self.fields_container, bg="#f0f8ff", padx=15, pady=10)
        info_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(info_frame, text="ℹ️ Mobile wallet instructions:", 
                font=("Arial", 11, "bold"),
                bg="#f0f8ff", fg=self.colors["primary"]).pack(anchor="w")
        
        instructions = """1. Select your wallet provider above
2. Enter the mobile number linked to your wallet
3. You'll receive a payment request
4. Complete payment in your wallet app"""
        
        tk.Label(info_frame, text=instructions, font=("Arial", 10),
                bg="#f0f8ff", fg=self.colors["gray"],
                justify="left").pack(anchor="w", pady=(5, 0))
        
        # Add padding to bottom to ensure all content is visible
        spacer = tk.Frame(self.fields_container, bg="white", height=10)
        spacer.pack(fill="x")
    
    def create_paypal_fields(self):
        """Create PayPal fields"""
        # PayPal email
        tk.Label(self.fields_container, text="PayPal Email Address", font=("Arial", 12),
                bg="white", fg=self.colors["dark"]).pack(anchor="w", pady=(0, 5))
        
        self.paypal_email = tk.Entry(self.fields_container, font=("Arial", 12),
                                    bg="#f9f9f9", relief="solid", borderwidth=1)
        self.paypal_email.pack(fill="x", pady=(0, 15))
        
        # Account holder name
        tk.Label(self.fields_container, text="Account Holder Name", font=("Arial", 12),
                bg="white", fg=self.colors["dark"]).pack(anchor="w", pady=(0, 5))
        
        self.card_name = tk.Entry(self.fields_container, font=("Arial", 12),
                                 bg="#f9f9f9", relief="solid", borderwidth=1)
        self.card_name.pack(fill="x", pady=(0, 15))
        
        # Instructions
        info_frame = tk.Frame(self.fields_container, bg="#f0f8ff", padx=15, pady=10)
        info_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(info_frame, text="ℹ️ PayPal instructions:", 
                font=("Arial", 11, "bold"),
                bg="#f0f8ff", fg=self.colors["primary"]).pack(anchor="w")
        
        instructions = """1. You'll be redirected to PayPal
2. Log in to your PayPal account
3. Review and confirm the payment
4. You'll be returned to this page"""
        
        tk.Label(info_frame, text=instructions, font=("Arial", 10),
                bg="#f0f8ff", fg=self.colors["gray"],
                justify="left").pack(anchor="w", pady=(5, 0))
        
        # Add padding to bottom to ensure all content is visible
        spacer = tk.Frame(self.fields_container, bg="white", height=10)
        spacer.pack(fill="x")
    
    def validate_payment_data(self):
        """Validate payment data based on method"""
        method = self.current_method
        
        if method == "credit_card":
            if not self.card_number or not self.card_number.get().strip():
                messagebox.showerror("Error", "Please enter card number")
                return False
            if not self.card_name or not self.card_name.get().strip():
                messagebox.showerror("Error", "Please enter cardholder name")
                return False
            if not self.expiry or not self.expiry.get().strip():
                messagebox.showerror("Error", "Please enter expiry date")
                return False
            if not self.cvv or not self.cvv.get().strip():
                messagebox.showerror("Error", "Please enter CVV")
                return False
                
        elif method == "bank_transfer":
            if not self.selected_bank or not self.selected_bank.get():
                messagebox.showerror("Error", "Please select a bank")
                return False
            if not self.user_id or not self.user_id.get().strip():
                messagebox.showerror("Error", "Please enter Bank User ID")
                return False
            if not self.password or not self.password.get().strip():
                messagebox.showerror("Error", "Please enter password")
                return False
                
        elif method == "mobile_wallet":
            if not self.mobile_number or not self.mobile_number.get().strip():
                messagebox.showerror("Error", "Please enter mobile number")
                return False
            if not self.wallet_type or not self.wallet_type.get():
                messagebox.showerror("Error", "Please select wallet provider")
                return False
            if not self.card_name or not self.card_name.get().strip():
                messagebox.showerror("Error", "Please enter wallet holder name")
                return False
                
        elif method == "paypal":
            if not self.paypal_email or not self.paypal_email.get().strip():
                messagebox.showerror("Error", "Please enter PayPal email address")
                return False
            if not self.card_name or not self.card_name.get().strip():
                messagebox.showerror("Error", "Please enter account holder name")
                return False
            email = self.paypal_email.get().strip()
            if "@" not in email or "." not in email:
                messagebox.showerror("Error", "Please enter a valid email address")
                return False
        
        return True
    
    def process_payment(self):
        """Process payment with validation"""
        if not self.validate_payment_data():
            return
        
        # Collect payment details
        payment_details = self.collect_payment_details()
        
        # Show processing screen
        self.show_processing(payment_details)
    
    def collect_payment_details(self):
        """Collect payment details based on method"""
        method = self.current_method
        now = datetime.now()
        
        payment_details = {
            "payment_method": method,
            "payment_date": now.strftime("%Y-%m-%d %H:%M:%S"),
            "payment_status": "processing",
            "payment_confirmation_id": f"PAY{now.strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
        }
        
        if method == "credit_card":
            try:
                card_num = self.card_number.get().strip() if self.card_number else "****"
                payment_details.update({
                    "card_last4": card_num[-4:] if len(card_num) >= 4 else "****",
                    "cardholder_name": self.card_name.get().strip() if self.card_name else "",
                    "expiry_date": self.expiry.get().strip() if self.expiry else ""
                })
            except:
                pass
                
        elif method == "bank_transfer":
            try:
                bank_name = self.selected_bank.get() if self.selected_bank else "Unknown Bank"
                user_id = self.user_id.get().strip() if self.user_id else ""
                payment_details.update({
                    "bank_name": bank_name,
                    "user_id_masked": self.mask_string(user_id),
                    "payment_authorized": True
                })
            except:
                pass
                
        elif method == "mobile_wallet":
            try:
                payment_details.update({
                    "wallet_provider": self.wallet_type.get() if self.wallet_type else "",
                    "mobile_number": self.mobile_number.get().strip() if self.mobile_number else "",
                    "wallet_holder": self.card_name.get().strip() if self.card_name else ""
                })
            except:
                pass
                
        elif method == "paypal":
            try:
                email = self.paypal_email.get().strip() if self.paypal_email else ""
                payment_details.update({
                    "paypal_email": email,
                    "account_holder": self.card_name.get().strip() if self.card_name else ""
                })
            except:
                pass
        
        return payment_details
    
    def mask_string(self, text, visible_chars=2):
        """Mask sensitive string for display"""
        if len(text) <= visible_chars:
            return "*" * len(text)
        return "*" * (len(text) - visible_chars) + text[-visible_chars:]
    
    def show_processing(self, payment_details):
        """Show processing screen"""
        # Get bank name BEFORE clearing the container
        bank_name = None
        if self.current_method == "bank_transfer" and self.selected_bank:
            try:
                bank_name = self.selected_bank.get()
            except:
                bank_name = "your bank"
        
        # Clear content
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Create processing screen
        processing_frame = tk.Frame(self.main_container, bg=self.colors["light"])
        processing_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Spinner and message
        tk.Label(processing_frame, text="⏳", font=("Arial", 72),
                bg=self.colors["light"], fg=self.colors["primary"]).pack(pady=(0, 20))
        
        tk.Label(processing_frame, text="Processing Payment...", 
                font=("Arial", 20, "bold"),
                bg=self.colors["light"], fg=self.colors["dark"]).pack(pady=10)
        
        method_names = {
            "credit_card": "Credit Card",
            "bank_transfer": "Bank Transfer",
            "mobile_wallet": "Mobile Wallet",
            "paypal": "PayPal"
        }
        
        method_name = method_names.get(self.current_method, "payment")
        
        tk.Label(processing_frame, text=f"Processing {method_name} payment...",
                font=("Arial", 14),
                bg=self.colors["light"], fg=self.colors["gray"]).pack()
        
        # For bank transfer, show bank-specific message
        if self.current_method == "bank_transfer" and bank_name:
            tk.Label(processing_frame, text=f"Connecting to {bank_name}...",
                    font=("Arial", 14),
                    bg=self.colors["light"], fg=self.colors["gray"]).pack()
        
        # Simulate processing delay (3 seconds)
        self.root.after(3000, lambda: self.show_confirmation(payment_details))
    
    def show_confirmation(self, payment_details):
        """Show payment confirmation"""
        # Clear content
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Create confirmation screen
        confirm_frame = tk.Frame(self.main_container, bg="white", padx=50, pady=50)
        confirm_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Success icon
        tk.Label(confirm_frame, text="✅", font=("Arial", 72),
                bg="white", fg=self.colors["success"]).pack(pady=(0, 20))
        
        # Success message
        booking_id = self.booking.get("booking_id", "N/A")
        item_name = self.booking.get("item_name", "your booking")
        
        # Calculate total
        try:
            total_price = float(self.booking.get("total_price", 0))
            tax = total_price * 0.06
            service_fee = 5.00 if total_price < 500 else 10.00
            total = total_price + tax + service_fee
        except:
            total = 0.0
        
        method_names = {
            "credit_card": "Credit/Debit Card",
            "bank_transfer": "Bank Transfer",
            "mobile_wallet": "Mobile Wallet",
            "paypal": "PayPal"
        }
        
        method_name = method_names.get(self.current_method, "your selected method")
        
        tk.Label(confirm_frame, text="Payment Successful!", 
                font=("Arial", 24, "bold"),
                bg="white", fg=self.colors["dark"]).pack(pady=10)
        
        # Confirmation message
        message = f"""✅ Payment of RM {total:,.2f} has been processed successfully!
        
📋 Booking ID: #{booking_id}
💳 Payment Method: {method_name}
📧 Confirmation sent to: {self.email}

Your booking is now confirmed!"""
        
        tk.Label(confirm_frame, text=message,
                font=("Arial", 14),
                bg="white", fg=self.colors["gray"],
                justify="left").pack(pady=20)
        
        # Payment confirmation ID
        confirm_id = payment_details.get("payment_confirmation_id", "N/A")
        
        id_frame = tk.Frame(confirm_frame, bg="#f8f9fa", padx=20, pady=10)
        id_frame.pack(pady=20, fill="x")
        
        tk.Label(id_frame, text="Payment Confirmation ID:",
                font=("Arial", 12, "bold"),
                bg="#f8f9fa", fg=self.colors["dark"]).pack(side="left", padx=(0, 10))
        
        tk.Label(id_frame, text=confirm_id,
                font=("Arial", 12),
                bg="#f8f9fa", fg=self.colors["primary"]).pack(side="left")
        
        # Action buttons
        action_frame = tk.Frame(confirm_frame, bg="white")
        action_frame.pack(pady=30)
        
        # Save booking
        self.save_booking(payment_details)
        
        done_btn = tk.Button(action_frame, text="Done",
                           command=self.finish_and_close,
                           font=("Arial", 12, "bold"),
                           bg=self.colors["primary"], fg="white",
                           padx=30, pady=10,
                           cursor="hand2")
        done_btn.pack()
    
    def save_booking(self, payment_details):
        """Save booking to database"""
        try:
            # Update booking with payment details
            updated_booking = {
                **self.booking,
                **payment_details,
                "status": "confirmed",
                "confirmed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "customer_email": self.email
            }
            
            # Save to JSON file
            os.makedirs("bookings", exist_ok=True)
            booking_id = updated_booking.get('booking_id', 'unknown')
            filename = f"bookings/booking_{booking_id}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(updated_booking, f, indent=2, default=str)
            
            # Execute callback if provided
            if self.callback:
                self.callback(updated_booking)
                
        except Exception as e:
            print(f"Error saving booking: {e}")
    
    def finish_and_close(self):
        """Finish and close the payment window"""
        # Show final message
        messagebox.showinfo("Booking Complete", 
                          "Your booking has been confirmed!\nA confirmation email has been sent.")
        
        # Close the window
        self.root.destroy()
        
        # Jump to home.py
        self.launch_home_page()
    
    def confirm_cancel_booking(self):
        """Confirm booking cancellation"""
        item_name = self.booking.get("item_name", "your booking")
        response = messagebox.askyesno(
            "Cancel Booking",
            f"Are you sure you want to cancel the booking for {item_name}?\n\nThis action cannot be undone."
        )
        
        if response:
            self.cancel_booking()
    
    def cancel_booking(self):
        """Cancel the booking and jump to home.py"""
        try:
            cancelled_booking = {
                **self.booking,
                "status": "cancelled",
                "cancelled_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            
            os.makedirs("bookings", exist_ok=True)
            booking_id = cancelled_booking.get('booking_id', 'unknown')
            filename = f"bookings/booking_{booking_id}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(cancelled_booking, f, indent=2, default=str)
            
            messagebox.showinfo("Booking Cancelled", 
                              "Your booking has been cancelled.")
            
            # Close the payment window
            self.root.destroy()
            
            # Jump to home.py
            self.launch_home_page()
            
        except Exception as e:
            print(f"Error cancelling booking: {e}")
            messagebox.showerror("Error", "Failed to cancel booking.")
    
    def launch_home_page(self):
        """Launch the home.py script"""
        try:
            # Get the current directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            home_script = os.path.join(current_dir, "home.py")
            
            # Check if home.py exists
            if os.path.exists(home_script):
                # Use the same Python executable
                python_executable = sys.executable
                
                # Launch home.py as a new process
                subprocess.Popen([python_executable, home_script])
            else:
                # If home.py doesn't exist, show a message
                print(f"home.py not found at: {home_script}")
                messagebox.showinfo("Home", "Returning to home...")
                
        except Exception as e:
            print(f"Error launching home.py: {e}")


# Main function
def show_payment_window(email, booking_data=None, callback=None):
    """Show payment window"""
    root = tk.Tk()
    app = PaymentApp(root, email, booking_data, callback)
    root.mainloop()


# For standalone testing
if __name__ == "__main__":
    # Test with sample booking data
    test_booking = {
        "booking_id": "HOTEL524967",
        "booking_type": "hotel",
        "item_name": "Grand Palace Hotel Bangkok",
        "total_price": 2300.00,
        "status": "pending",
        "date": "2024-12-15",
        "check_in": "2024-12-15",
        "check_out": "2024-12-18",
        "room_type": "Deluxe Suite",
        "guests": 2,
        "duration": "3 nights",
        "location": "Bangkok, Thailand",
        "provider": "Grand Palace Hotels",
        "contact": "contact@grandpalace.com",
        "notes": "Late check-in requested"
    }
    show_payment_window("customer@example.com", test_booking)