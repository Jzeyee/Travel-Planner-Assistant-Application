import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
import re
from datetime import datetime, timedelta
import hashlib
import random
import string
import sys

class ModernButton(tk.Button):
    """Custom modern button with hover effects"""
    def __init__(self, master=None, **kwargs):
        self.bg_color = kwargs.pop('bg_color', '#4361ee')
        self.hover_color = kwargs.pop('hover_color', '#5a75f0')
        self.active_color = kwargs.pop('active_color', '#2a4d6e')
        self.text_color = kwargs.pop('text_color', 'white')
        
        kwargs['bg'] = self.bg_color
        kwargs['fg'] = self.text_color
        kwargs['borderwidth'] = 0
        kwargs['relief'] = 'flat'
        kwargs['cursor'] = 'hand2'
        kwargs['activebackground'] = self.active_color
        kwargs['activeforeground'] = self.text_color
        
        super().__init__(master, **kwargs)
        
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        
    def on_enter(self, e):
        self['bg'] = self.hover_color
    
    def on_leave(self, e):
        self['bg'] = self.bg_color

class InputField(tk.Frame):
    """Custom modern input field with label and icon"""
    def __init__(self, master=None, label="", is_password=False, icon=None, **kwargs):
        super().__init__(master, bg=kwargs.pop('bg', '#ffffff'), **kwargs)
        
        self.label_text = label
        self.is_password = is_password
        self.icon = icon
        
        self.setup_ui()
    
    def setup_ui(self):
        # Label
        self.label = tk.Label(self, text=self.label_text, bg=self['bg'], 
                             font=("Segoe UI", 11), fg='#2c3e50')
        self.label.pack(anchor="w", pady=(0, 8))
        
        # Input container
        self.input_frame = tk.Frame(self, bg='#f8f9fa', relief='solid', 
                                   borderwidth=1, highlightthickness=0)
        self.input_frame.pack(fill="x")
        
        # Icon
        if self.icon:
            icon_label = tk.Label(self.input_frame, text=self.icon, bg='#f8f9fa',
                                 font=("Segoe UI", 14), fg='#7f8c8d')
            icon_label.pack(side="left", padx=(12, 0), pady=12)
        
        # Entry field
        self.entry = tk.Entry(self.input_frame, font=("Segoe UI", 13), 
                             bg='#f8f9fa', relief='flat', highlightthickness=0)
        self.entry.pack(fill="x", padx=12, pady=12, expand=True)
        
        # Eye button for passwords
        if self.is_password:
            self.show_password = False
            self.entry.config(show="•")
            self.eye_btn = tk.Button(self.input_frame, text="👁", bg='#f8f9fa',
                                    borderwidth=0, cursor="hand2",
                                    command=self.toggle_password)
            self.eye_btn.pack(side="right", padx=(5, 20))
    
    def toggle_password(self):
        self.show_password = not self.show_password
        self.entry.config(show='' if self.show_password else '•')
        self.eye_btn.config(text="👁️" if self.show_password else "👁")
    
    def get(self):
        return self.entry.get()
    
    def delete(self, first, last):
        return self.entry.delete(first, last)
    
    def insert(self, index, string):
        return self.entry.insert(index, string)

class OTPEntry(tk.Frame):
    """Custom OTP entry field with 6 boxes"""
    def __init__(self, master=None, **kwargs):
        super().__init__(master, bg=kwargs.pop('bg', '#ffffff'), **kwargs)
        
        self.otp_entries = []
        self.setup_ui()
    
    def setup_ui(self):
        # Create 6 entry boxes for OTP
        for i in range(6):
            entry = tk.Entry(self, width=3, font=("Segoe UI", 20), 
                           justify="center", relief="solid", borderwidth=2,
                           bg='#f8f9fa', highlightthickness=0)
            entry.grid(row=0, column=i, padx=5, ipady=10)
            
            # Add validation to allow only digits
            entry.config(validate="key", validatecommand=(self.register(self.validate_digit), '%P'))
            
            # Bind tab and backspace for better UX
            entry.bind('<KeyRelease>', lambda e, idx=i: self.on_key_release(e, idx))
            entry.bind('<BackSpace>', lambda e, idx=i: self.on_backspace(e, idx))
            
            self.otp_entries.append(entry)
        
        # Focus first entry
        self.otp_entries[0].focus()
    
    def validate_digit(self, text):
        """Validate that only digits are entered"""
        if text == "" or (text.isdigit() and len(text) <= 1):
            return True
        return False
    
    def on_key_release(self, event, index):
        """Move to next field when a digit is entered"""
        if event.char.isdigit() and index < 5:
            self.otp_entries[index + 1].focus()
    
    def on_backspace(self, event, index):
        """Move to previous field on backspace if current is empty"""
        if event.keysym == 'BackSpace' and index > 0 and not self.otp_entries[index].get():
            self.otp_entries[index - 1].focus()
    
    def get_otp(self):
        """Get the complete OTP"""
        return ''.join([entry.get() for entry in self.otp_entries])
    
    def clear(self):
        """Clear all OTP fields"""
        for entry in self.otp_entries:
            entry.delete(0, tk.END)
        self.otp_entries[0].focus()

class WelcomeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Traney ✈️")
        self.root.attributes('-fullscreen', True)
        
        # Modern Colors
        self.bg = "#f8fafc"
        self.primary = "#4361ee"
        self.secondary = "#3a0ca3"
        self.accent = "#f72585"
        self.success = "#06d6a0"
        self.card_bg = "#ffffff"
        self.text_primary = "#1a1a2e"
        self.text_secondary = "#6c757d"
        self.light_gray = "#e9ecef"
        self.medium_gray = "#ced4da"
        self.dark_gray = "#495057"
        
        # Gradients
        self.login_gradient = ["#667eea", "#764ba2"]
        self.signup_gradient = ["#f093fb", "#f5576c"]
        self.welcome_gradient = ["#1a2980", "#26d0ce"]
        
        # Files
        self.users_file = "traney_users.json"
        self.users_data = {} 
        self.pending_otps = {}
        self.reset_email = None
        self.current_step = 1  # For forgot password flow
        
        # Configure styles
        self.setup_styles()
        
        self.show_welcome_page()
        
        # Bindings
        self.root.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.root.bind('<Escape>', lambda e: self.root.quit() if self.root.attributes('-fullscreen') else None)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        
        # Modern checkbutton style
        style.configure('Modern.TCheckbutton', background=self.card_bg, 
                       font=('Segoe UI', 11))
        
        # Modern radiobutton style
        style.configure('Modern.TRadiobutton', background=self.card_bg,
                       font=('Segoe UI', 11))
    
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit Traney?"):
            self.root.destroy()
    
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def toggle_fullscreen(self):
        self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen'))
    
    def create_gradient_bg(self, parent, colors):
        """Create gradient background"""
        canvas = tk.Canvas(parent, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        
        # Get screen dimensions
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        if width <= 1 or height <= 1:
            width = 1920
            height = 1080
        
        # Create gradient
        for i in range(height):
            ratio = i / height
            # Convert hex colors to RGB
            c1 = self.hex_to_rgb(colors[0])
            c2 = self.hex_to_rgb(colors[1])
            
            # Interpolate between colors
            r = int(c1[0] * (1 - ratio) + c2[0] * ratio)
            g = int(c1[1] * (1 - ratio) + c2[1] * ratio)
            b = int(c1[2] * (1 - ratio) + c2[2] * ratio)
            
            color = f'#{r:02x}{g:02x}{b:02x}'
            canvas.create_line(0, i, width, i, fill=color)
        
        return canvas
    
    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def show_welcome_page(self):
        self.clear_window()
        
        # Gradient background
        bg_canvas = self.create_gradient_bg(self.root, self.welcome_gradient)
        
        # Content container with shadow effect
        content_container = tk.Frame(self.root, bg='white')
        content_container.place(relx=0.5, rely=0.5, anchor="center", width=850, height=800)
        
        # Add subtle shadow effect using darker border
        shadow_frame = tk.Frame(self.root, bg=self.medium_gray)
        shadow_frame.place(relx=0.5, rely=0.5, anchor="center", width=860, height=810)
        
        content = tk.Frame(shadow_frame, bg='white', relief='flat', borderwidth=2)
        content.place(relx=0.5, rely=0.5, anchor="center", width=850, height=800)
        
        # Add some rounded corners effect with padding
        content_inner = tk.Frame(content, bg='white')
        content_inner.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Logo and title
        logo_frame = tk.Frame(content_inner, bg='white')
        logo_frame.pack(pady=(0, 30))
        
        # Logo with airplane icon
        tk.Label(logo_frame, text="✈️", font=("Segoe UI", 72), 
                bg='white', fg=self.primary).pack()
        
        # Title with gradient text effect
        title_frame = tk.Frame(logo_frame, bg='white')
        title_frame.pack()
        
        tk.Label(title_frame, text="Traney", font=("Segoe UI", 48, "bold"), 
                bg='white', fg=self.primary).pack(side="left")
        tk.Label(title_frame, text=".", font=("Segoe UI", 48, "bold"), 
                bg='white', fg=self.accent).pack(side="left")
        
        tk.Label(content_inner, text="Your Smart Travel Companion", 
                font=("Segoe UI", 18), bg='white', fg=self.text_secondary).pack(pady=(0, 40))
        
        # Features in a modern grid
        features_frame = tk.Frame(content_inner, bg='white')
        features_frame.pack(pady=(0, 50))
        
        features = [
            ("✈️", "Real-time Flight Updates"),
            ("📅", "Smart Itinerary Planning"), 
            ("🏨", "Hotel & Activity Booking"),
            ("💰", "Travel Expense Tracking")
        ]
        
        for i, (icon, text) in enumerate(features):
            frame = tk.Frame(features_frame, bg='white')
            frame.grid(row=i//2, column=i%2, padx=30, pady=15, sticky='w')
            
            # Icon with background
            icon_bg = tk.Frame(frame, bg='#e3f2fd', width=40, height=40)
            icon_bg.pack_propagate(False)
            icon_bg.pack(side="left", padx=(0, 15))
            tk.Label(icon_bg, text=icon, font=("Segoe UI", 18), 
                    bg='#e3f2fd', fg=self.primary).pack(expand=True)
            
            # Text
            tk.Label(frame, text=text, font=("Segoe UI", 14),
                    bg='white', fg=self.text_primary).pack(side="left")
        
        # Action buttons
        btn_frame = tk.Frame(content_inner, bg='white')
        btn_frame.pack(pady=(20, 0))
        
        ModernButton(btn_frame, text="LOGIN", font=("Segoe UI", 14, "bold"),
                    bg_color=self.primary, hover_color="#5a75f0",
                    width=20, height=2, command=self.show_login_page
                    ).pack(side="left", padx=10, pady=10)
        
        ModernButton(btn_frame, text="SIGN UP", font=("Segoe UI", 14, "bold"),
                    bg_color=self.accent, hover_color="#f83e94",
                    width=20, height=2, command=self.show_signup_page
                    ).pack(side="left", padx=10, pady=10)
        
        # Full screen toggle
        ModernButton(self.root, text="⛶ Exit Fullscreen", 
                    command=self.toggle_fullscreen,
                    font=("Segoe UI", 12), bg_color=self.dark_gray,
                    hover_color='#343a40', text_color='white'
                    ).place(relx=1.0, x=-20, y=20, anchor="ne")
    
    def show_login_page(self):
        self.clear_window()
        
        # Gradient background
        bg_canvas = self.create_gradient_bg(self.root, self.login_gradient)
        
        # Back button
        ModernButton(self.root, text="← Back", command=self.show_welcome_page,
                    font=("Segoe UI", 12), bg_color='#ffffff',
                    hover_color='#f0f0f0', text_color=self.primary
                    ).place(x=20, y=20)
        
        # Login card with shadow effect
        card_shadow = tk.Frame(self.root, bg=self.medium_gray)
        card_shadow.place(relx=0.5, rely=0.5, anchor="center", width=520, height=750)
        
        card = tk.Frame(self.root, bg=self.card_bg, relief='flat', borderwidth=2)
        card.place(relx=0.5, rely=0.5, anchor="center", width=500, height=730)
        
        # Header with solid color
        header = tk.Frame(card, bg=self.primary, height=200)
        header.pack(fill="x")
        
        # Header content
        header_content = tk.Frame(header, bg=self.primary)
        header_content.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(header_content, text="Sign in to your account",
                font=("Segoe UI", 14), bg=self.primary, fg="#e9ecef").pack()
        tk.Label(header_content, text="✈️ Welcome Back!", font=("Segoe UI", 24, "bold"),
                bg=self.primary, fg="white").pack()

        
        # Form
        form = tk.Frame(card, bg=self.card_bg)
        form.pack(fill="both", expand=True, padx=40, pady=15)
        
        # Email field
        self.email_field = InputField(form, label="Email Address", 
                                     icon="📧", bg=self.card_bg)
        self.email_field.pack(fill="x", pady=(0, 15))
        
        # Password field
        self.pass_field = InputField(form, label="Password", 
                                    is_password=True, icon="🔒", bg=self.card_bg)
        self.pass_field.pack(fill="x", pady=(0, 15))
        
        # Options row
        options = tk.Frame(form, bg=self.card_bg)
        options.pack(fill="x", pady=(0, 15))
        
        self.remember_var = tk.BooleanVar()
        check = tk.Checkbutton(options, text="Remember me", variable=self.remember_var,
                              bg=self.card_bg, font=("Segoe UI", 11),
                              selectcolor=self.card_bg, activebackground=self.card_bg)
        check.pack(side="left")
        
        # Forgot Password link
        forgot_label = tk.Label(options, text="Forgot Password?", fg=self.accent,
                bg=self.card_bg, cursor="hand2",
                font=("Segoe UI", 11, "underline"))
        forgot_label.pack(side="right")
        forgot_label.bind("<Button-1>", lambda e: self.show_forgot_password())
        
        # Login button
        ModernButton(form, text="SIGN IN", font=("Segoe UI", 14, "bold"),
                    bg_color=self.primary, hover_color="#5a75f0",
                    width=30, height=2, command=self.perform_login
                    ).pack(pady=(0, 30))
        
        # Signup link
        signup_frame = tk.Frame(form, bg=self.card_bg)
        signup_frame.pack()
        
        tk.Label(signup_frame, text="Don't have an account? ", 
                bg=self.card_bg, font=("Segoe UI", 12)).pack(side="left")
        
        signup_label = tk.Label(signup_frame, text="Sign Up Now", fg=self.accent, 
                bg=self.card_bg, cursor="hand2", 
                font=("Segoe UI", 12, "bold"))
        signup_label.pack(side="left")
        signup_label.bind("<Button-1>", lambda e: self.show_signup_page())
    
    def show_signup_page(self):
        self.clear_window()
        
        # Gradient background
        bg_canvas = self.create_gradient_bg(self.root, self.signup_gradient)
        
        # Back button
        ModernButton(self.root, text="← Back", command=self.show_welcome_page,
                    font=("Segoe UI", 12), bg_color='#ffffff',
                    hover_color='#f0f0f0', text_color=self.accent
                    ).place(x=20, y=20)
        
        # Signup card with shadow
        card_shadow = tk.Frame(self.root, bg=self.medium_gray)
        card_shadow.place(relx=0.5, rely=0.5, anchor="center", width=620, height=780)
        
        card = tk.Frame(self.root, bg=self.card_bg, relief='flat', borderwidth=2)
        card.place(relx=0.5, rely=0.5, anchor="center", width=600, height=770)
        
        # Header with solid color
        header = tk.Frame(card, bg=self.accent, height=100)
        header.pack(fill="x")
        
        # Header content
        header_content = tk.Frame(header, bg=self.accent)
        header_content.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(header_content, text="Create your free account",
                font=("Segoe UI", 14), bg=self.accent, fg="#e9ecef").pack()
        tk.Label(header_content, text="✈️ Join Traney", font=("Segoe UI", 28, "bold"),
                bg=self.accent, fg="white").pack()
        
        # Form (not scrollable)
        form = tk.Frame(card, bg=self.card_bg)
        form.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Fields
        fields = [
            ("👤", "Full Name", False),
            ("📧", "Email Address", False),
            ("🔒", "Password", True),
            ("🔑", "Confirm Password", True)
        ]
        
        self.signup_entries = {}
        for icon, label, is_pass in fields:
            field = InputField(form, label=label, is_password=is_pass,
                              icon=icon, bg=self.card_bg)
            field.pack(fill="x", pady=(0, 15))
            self.signup_entries[label] = field
        
        # Terms with modern checkbox
        terms_frame = tk.Frame(form, bg=self.card_bg)
        terms_frame.pack(fill="x", pady=(0, 15))
        
        self.terms_var = tk.BooleanVar()
        check = tk.Checkbutton(terms_frame, variable=self.terms_var,
                              bg=self.card_bg, font=("Segoe UI", 15),
                              selectcolor=self.card_bg, activebackground=self.card_bg)
        check.pack(side="left")
        
        tk.Label(terms_frame, text="I agree to the ", bg=self.card_bg,
                font=("Segoe UI", 11)).pack(side="left")
        
        terms_link = tk.Label(terms_frame, text="Terms & Conditions", 
                             fg=self.primary, bg=self.card_bg,
                             cursor="hand2", font=("Segoe UI", 11, "underline"))
        terms_link.pack(side="left")
        
        # Signup button
        ModernButton(form, text="CREATE ACCOUNT", font=("Segoe UI", 14, "bold"),
                    bg_color=self.accent, hover_color="#f83e94",
                    width=20, height=2, command=self.perform_signup
                    ).pack(pady=(0, 15))
        
        # Login link
        login_frame = tk.Frame(form, bg=self.card_bg)
        login_frame.pack()
        
        tk.Label(login_frame, text="Already have an account? ", 
                bg=self.card_bg, font=("Segoe UI", 12)).pack(side="left")
        
        login_label = tk.Label(login_frame, text="Login Here", fg=self.primary, 
                bg=self.card_bg, cursor="hand2", 
                font=("Segoe UI", 12, "bold"))
        login_label.pack(side="left")
        login_label.bind("<Button-1>", lambda e: self.show_login_page())

    def show_forgot_password(self):
        """Show forgot password dialog with OTP verification"""
        self.forgot_dialog = tk.Toplevel(self.root)
        self.forgot_dialog.title("Reset Password")
        self.forgot_dialog.geometry("500x700")
        self.forgot_dialog.configure(bg=self.card_bg)
        self.forgot_dialog.resizable(False, False)
        
        # Make dialog modal
        self.forgot_dialog.transient(self.root)
        self.forgot_dialog.grab_set()
        
        # Center dialog
        self.forgot_dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (500 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (600 // 2)
        self.forgot_dialog.geometry(f"500x700+{x}+{y}")
        
        # Header
        header_frame = tk.Frame(self.forgot_dialog, bg=self.primary, height=80)
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="🔐 Reset Password", font=("Segoe UI", 20, "bold"),
                bg=self.primary, fg="white").pack(expand=True, pady=20)
        
        # Content frame
        self.forgot_content = tk.Frame(self.forgot_dialog, bg=self.card_bg)
        self.forgot_content.pack(fill="both", expand=True, padx=40, pady=30)
        
        # Show step 1 (email input)
        self.show_forgot_step1()
    
    def show_forgot_step1(self):
        """Step 1: Email input"""
        self.current_step = 1
        
        # Clear content
        for widget in self.forgot_content.winfo_children():
            widget.destroy()
        
        # Instructions
        tk.Label(self.forgot_content, text="Enter your email address", 
                font=("Segoe UI", 16, "bold"), bg=self.card_bg, fg=self.primary).pack(pady=(0, 20))
        
        tk.Label(self.forgot_content, text="We'll send a verification code to this email", 
                font=("Segoe UI", 12), bg=self.card_bg, fg=self.text_secondary).pack(pady=(0, 30))
        
        # Email entry
        email_frame = tk.Frame(self.forgot_content, bg='#f8f9fa', relief='solid', borderwidth=1)
        email_frame.pack(pady=(0, 20))
        self.reset_email_entry = tk.Entry(email_frame, font=("Segoe UI", 14), bg='#f8f9fa', 
                                         relief='flat', width=30)
        self.reset_email_entry.pack(padx=15, pady=12)
        
        # Error message label
        self.step1_error = tk.Label(self.forgot_content, text="", 
                                   font=("Segoe UI", 11), bg=self.card_bg, fg="#e74c3c")
        self.step1_error.pack(pady=(0, 30))
        
        # Buttons
        btn_frame = tk.Frame(self.forgot_content, bg=self.card_bg)
        btn_frame.pack(pady=(20, 0))
        
        ModernButton(btn_frame, text="SEND OTP", 
                    font=("Segoe UI", 12, "bold"),
                    bg_color=self.accent, hover_color="#f83e94",
                    command=self.send_otp
                    ).pack(side="left", padx=5)
        
        ModernButton(btn_frame, text="CANCEL", 
                    font=("Segoe UI", 12),
                    bg_color=self.light_gray, hover_color=self.medium_gray,
                    text_color=self.text_primary,
                    command=self.forgot_dialog.destroy
                    ).pack(side="left", padx=5)
    
    def show_forgot_step2(self):
        """Step 2: OTP verification"""
        self.current_step = 2
        
        # Clear content
        for widget in self.forgot_content.winfo_children():
            widget.destroy()
        
        # Instructions
        tk.Label(self.forgot_content, text="Enter verification code", 
                font=("Segoe UI", 16, "bold"), bg=self.card_bg, fg=self.primary).pack(pady=(0, 20))
        
        tk.Label(self.forgot_content, text=f"Sent to: {self.reset_email}", 
                font=("Segoe UI", 12), bg=self.card_bg, fg=self.text_secondary).pack(pady=(0, 10))
        
        tk.Label(self.forgot_content, text="Check your email for the 6-digit code", 
                font=("Segoe UI", 12), bg=self.card_bg, fg=self.text_secondary).pack(pady=(0, 30))
        
        # OTP entry
        self.otp_entry = OTPEntry(self.forgot_content, bg=self.card_bg)
        self.otp_entry.pack(pady=(0, 20))
        
        # Timer label
        self.timer_label = tk.Label(self.forgot_content, text="", 
                                   font=("Segoe UI", 12), bg=self.card_bg, fg=self.success)
        self.timer_label.pack(pady=(0, 10))
        
        # Error message label
        self.step2_error = tk.Label(self.forgot_content, text="", 
                                   font=("Segoe UI", 11), bg=self.card_bg, fg="#e74c3c")
        self.step2_error.pack(pady=(0, 20))
        
        # Buttons
        btn_frame = tk.Frame(self.forgot_content, bg=self.card_bg)
        btn_frame.pack(pady=(20, 0))
        
        ModernButton(btn_frame, text="VERIFY OTP", 
                    font=("Segoe UI", 12, "bold"),
                    bg_color=self.accent, hover_color="#f83e94",
                    command=self.verify_otp
                    ).pack(side="left", padx=5)
        
        ModernButton(btn_frame, text="RESEND OTP", 
                    font=("Segoe UI", 12),
                    bg_color=self.light_gray, hover_color=self.medium_gray,
                    text_color=self.text_primary,
                    command=self.resend_otp
                    ).pack(side="left", padx=5)
        
        ModernButton(btn_frame, text="BACK", 
                    font=("Segoe UI", 12),
                    bg_color=self.light_gray, hover_color=self.medium_gray,
                    text_color=self.text_primary,
                    command=self.show_forgot_step1
                    ).pack(side="left", padx=5)
        
        # Start timer
        self.start_otp_timer()
    
    def show_forgot_step3(self):
        """Step 3: New password"""
        self.current_step = 3
        
        # Clear content
        for widget in self.forgot_content.winfo_children():
            widget.destroy()
        
        # Instructions
        tk.Label(self.forgot_content, text="Create new password", 
                font=("Segoe UI", 16, "bold"), bg=self.card_bg, fg=self.primary).pack(pady=(0, 20))
        
        tk.Label(self.forgot_content, text="Create a strong password for your account", 
                font=("Segoe UI", 12), bg=self.card_bg, fg=self.text_secondary).pack(pady=(0, 30))
        
        # New password field
        tk.Label(self.forgot_content, text="New Password", bg=self.card_bg, 
                font=("Segoe UI", 12)).pack(anchor="w", pady=(0, 5))
        
        new_pass_frame = tk.Frame(self.forgot_content, bg='#f8f9fa', relief='solid', borderwidth=1)
        new_pass_frame.pack(fill="x", pady=(0, 15))
        self.new_pass_entry = tk.Entry(new_pass_frame, font=("Segoe UI", 14), 
                                      show="•", relief='flat', bg='#f8f9fa')
        self.new_pass_entry.pack(fill="x", padx=15, pady=12)
        
        # Confirm password field
        tk.Label(self.forgot_content, text="Confirm Password", bg=self.card_bg,
                font=("Segoe UI", 12)).pack(anchor="w", pady=(0, 5))
        
        confirm_pass_frame = tk.Frame(self.forgot_content, bg='#f8f9fa', relief='solid', borderwidth=1)
        confirm_pass_frame.pack(fill="x", pady=(0, 30))
        self.confirm_pass_entry = tk.Entry(confirm_pass_frame, font=("Segoe UI", 14), 
                                         show="•", relief='flat', bg='#f8f9fa')
        self.confirm_pass_entry.pack(fill="x", padx=15, pady=12)
        
        # Error message label
        self.step3_error = tk.Label(self.forgot_content, text="", 
                                   font=("Segoe UI", 11), bg=self.card_bg, fg="#e74c3c")
        self.step3_error.pack(pady=(0, 20))
        
        # Buttons
        btn_frame = tk.Frame(self.forgot_content, bg=self.card_bg)
        btn_frame.pack(pady=(20, 0))
        
        ModernButton(btn_frame, text="RESET PASSWORD", 
                    font=("Segoe UI", 12, "bold"),
                    bg_color=self.success, hover_color="#05c895",
                    command=self.reset_password
                    ).pack(side="left", padx=5)
        
        ModernButton(btn_frame, text="BACK", 
                    font=("Segoe UI", 12),
                    bg_color=self.light_gray, hover_color=self.medium_gray,
                    text_color=self.text_primary,
                    command=self.show_forgot_step2
                    ).pack(side="left", padx=5)
    
    def send_otp(self):
        """Send OTP to email"""
        email = self.reset_email_entry.get().strip()
        
        # Clear previous error
        self.step1_error.config(text="")
        
        # Validation
        if not email:
            self.step1_error.config(text="Please enter your email address")
            return
        
        if not self.validate_email(email):
            self.step1_error.config(text="Please enter a valid email address")
            return
        
        if not self.user_exists(email):
            self.step1_error.config(text="Email not found. Please check and try again.")
            return
        
        # Store email
        self.reset_email = email
        
        # Generate OTP
        otp = self.generate_otp()
        expiry = datetime.now() + timedelta(minutes=5)
        
        # Store OTP
        self.pending_otps[email] = {
            "otp": otp,
            "expiry": expiry
        }
        
        # Show OTP in popup for demo
        messagebox.showinfo("OTP Sent", 
                          f"A 6-digit verification code has been sent to:\n\n{email}\n\n"
                          f"Demo OTP: {otp}\n"
                          f"Valid for 5 minutes")
        
        # Move to step 2
        self.show_forgot_step2()
    
    def start_otp_timer(self):
        """Start OTP countdown timer"""
        if self.reset_email not in self.pending_otps:
            return
        
        expiry = self.pending_otps[self.reset_email]["expiry"]
        
        def update_timer():
            remaining = expiry - datetime.now()
            if remaining.total_seconds() <= 0:
                self.timer_label.config(text="OTP expired", fg="#e74c3c")
                return
            
            mins = int(remaining.total_seconds() // 60)
            secs = int(remaining.total_seconds() % 60)
            self.timer_label.config(text=f"Expires in: {mins:02d}:{secs:02d}", fg=self.success)
            self.timer_label.after(1000, update_timer)
        
        update_timer()
    
    def verify_otp(self):
        """Verify the entered OTP"""
        entered_otp = self.otp_entry.get_otp()
        
        # Clear previous error
        self.step2_error.config(text="")
        
        # Validation
        if len(entered_otp) != 6:
            self.step2_error.config(text="Please enter a 6-digit code")
            return
        
        if self.reset_email not in self.pending_otps:
            self.step2_error.config(text="OTP not found. Please request a new one.")
            return
        
        stored = self.pending_otps[self.reset_email]
        
        # Check expiry
        if datetime.now() > stored["expiry"]:
            self.step2_error.config(text="OTP has expired. Please request a new one.")
            return
        
        # Check OTP
        if entered_otp != stored["otp"]:
            self.step2_error.config(text="Invalid OTP. Please try again.")
            self.otp_entry.clear()
            return
        
        # OTP verified successfully
        messagebox.showinfo("Success", "OTP verified successfully!")
        self.show_forgot_step3()
    
    def resend_otp(self):
        """Resend OTP"""
        if not self.reset_email:
            return
        
        # Generate new OTP
        otp = self.generate_otp()
        expiry = datetime.now() + timedelta(minutes=5)
        
        # Store new OTP
        self.pending_otps[self.reset_email] = {
            "otp": otp,
            "expiry": expiry
        }
        
        # Clear OTP field
        self.otp_entry.clear()
        
        # Show new OTP in popup
        messagebox.showinfo("New OTP Sent", 
                          f"A new 6-digit verification code has been sent to:\n\n{self.reset_email}\n\n"
                          f"New OTP: {otp}\n"
                          f"Valid for 5 minutes")
        
        # Restart timer
        self.start_otp_timer()
        
        # Clear error
        self.step2_error.config(text="")
    
    def reset_password(self):
        """Reset user password"""
        new_pass = self.new_pass_entry.get()
        confirm_pass = self.confirm_pass_entry.get()
        
        # Clear previous error
        self.step3_error.config(text="")
        
        # Validation
        if not new_pass or not confirm_pass:
            self.step3_error.config(text="Please fill in all password fields")
            return
        
        if len(new_pass) < 8:
            self.step3_error.config(text="Password must be at least 8 characters")
            return
        
        if new_pass != confirm_pass:
            self.step3_error.config(text="Passwords don't match")
            return
        
        # Reset password
        if self.reset_user_password(self.reset_email, new_pass):
            messagebox.showinfo("Success", "Your password has been reset successfully!")
            self.forgot_dialog.destroy()
            self.show_login_page()
        else:
            self.step3_error.config(text="Failed to reset password. Please try again.")
    
    # Helper methods
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def generate_otp(self, length=6):
        """Generate OTP verification code"""
        return ''.join(random.choices(string.digits, k=length))
    
    def hash_password(self, password):
        """Hash password"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def user_exists(self, email):
        """Check if user exists"""
        if not os.path.exists(self.users_file):
            return False
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users = json.load(f)
                return email in users
        except:
            return False
    
    def create_account_simple(self, name, email, password):
        """Create new account"""
        try:
            users = {}
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    users = json.load(f)
            
            if email in users:
                return False
            
            # Create complete user data structure compatible with profile.py
            users[email] = {
                "personal_info": {
                    "full_name": name,
                    "email": email,
                    "phone": "",
                    "address": "",
                    "nationality": "",
                    "date_of_birth": ""
                },
                "password": self.hash_password(password),
                "created_at": datetime.now().isoformat(),
                "bookings": []  # Initialize empty bookings list
            }
            
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users, f, indent=4, ensure_ascii=False)
            
            return True
        except Exception as e:
            return False
    
    def perform_signup(self):
        """Handle user registration"""
        name = self.signup_entries["Full Name"].get().strip()
        email = self.signup_entries["Email Address"].get().strip()
        password = self.signup_entries["Password"].get()
        confirm = self.signup_entries["Confirm Password"].get()
        
        # Validate input
        if not all([name, email, password, confirm]):
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        if not self.validate_email(email):
            messagebox.showerror("Error", "Invalid email")
            return
        
        if len(password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords don't match")
            return
        
        if not self.terms_var.get():
            messagebox.showerror("Error", "Please accept terms & conditions")
            return
        
        if self.user_exists(email):
            messagebox.showerror("Error", "Email already exists")
            return
        
        # Create account
        if self.create_account_simple(name, email, password):
            messagebox.showinfo("Success", "Account created successfully!")
            self.show_login_page()
        else:
            messagebox.showerror("Error", "Failed to create account")
    
    def validate_login_simple(self, email, password):
        """Simple login validation"""
        if not os.path.exists(self.users_file):
            return False
        
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users = json.load(f)
            
            if email not in users:
                return False
            
            # Validate password
            stored_hash = users[email].get("password")
            input_hash = self.hash_password(password)
            password_match = stored_hash == input_hash
            
            return password_match
            
        except Exception as e:
            return False
    
    def get_user_data(self, email):
        """Get user data"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users = json.load(f)
                return users.get(email)
        except Exception as e:
            return None
    
    def reset_user_password(self, email, new_password):
        """Reset user password"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users = json.load(f)
            
            if email not in users:
                return False
            
            users[email]["password"] = self.hash_password(new_password)
            
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users, f, indent=4, ensure_ascii=False)
            return True
        except:
            return False
    
    def perform_login(self):
        """Handle user login"""
        # Get input data
        email = self.email_field.get().strip()
        password = self.pass_field.get()
        
        # Validate input
        if not email or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        if not self.validate_email(email):
            messagebox.showerror("Error", "Please enter a valid email address")
            return
        
        # Check if user file exists
        if not os.path.exists(self.users_file):
            messagebox.showerror("Error", "No user database found. Please sign up first.")
            return
        
        # Validate login credentials
        is_valid = self.validate_login_simple(email, password)
        
        if is_valid:
            # Get user data
            user_data = self.get_user_data(email)
            
            if user_data:
                # Ensure correct data structure
                if 'personal_info' not in user_data:
                    user_data = {
                        "personal_info": {
                            "full_name": user_data.get('name', 'User'),
                            "email": email,
                            "phone": "",
                            "address": "",
                            "nationality": "",
                            "date_of_birth": ""
                        },
                        "password": user_data.get('password', ''),
                        "created_at": user_data.get('created_at', datetime.now().isoformat()),
                        "bookings": []
                    }
                
                user_name = user_data['personal_info']['full_name']
                
                # Save user data to session file
                session_data = {
                    'email': email,
                    'user_name': user_name,
                    'full_profile': user_data
                }
                
                try:
                    with open('user_session.json', 'w', encoding='utf-8') as f:
                        json.dump(session_data, f, indent=2, ensure_ascii=False)
                except Exception as e:
                    pass
                
                # Destroy current window
                self.root.destroy()
                
                # Open HomeApp
                try:
                    from home import HomeApp
                    
                    home_root = tk.Tk()
                    
                    try:
                        # Try different parameter combinations for HomeApp
                        try:
                            app = HomeApp(home_root, email, user_name)
                        except TypeError as e:
                            error_msg = str(e)
                            
                            if "__init__() takes 2 positional arguments" in error_msg:
                                app = HomeApp(home_root)
                            elif "__init__() takes from 2 to 4 positional arguments" in error_msg:
                                try:
                                    app = HomeApp(home_root, email)
                                except:
                                    app = HomeApp(home_root, email, user_name)
                            else:
                                # Try 4 parameters
                                app = HomeApp(home_root, email, user_name, user_data)
                    
                    except Exception as e:
                        messagebox.showerror("Error", f"Cannot create home screen: {str(e)}")
                        sys.exit(1)
                    
                    home_root.mainloop()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Cannot open home screen: {str(e)}")
                    sys.exit(1)
            else:
                messagebox.showerror("Error", "User data not found")
        else:
            messagebox.showerror("Error", "Invalid email or password!")

if __name__ == "__main__":
    root = tk.Tk()
    app = WelcomeApp(root)
    root.mainloop()