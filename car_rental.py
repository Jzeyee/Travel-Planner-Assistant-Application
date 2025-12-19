import tkinter as tk
from tkinter import ttk, messagebox, font as tkFont
from PIL import Image, ImageTk, ImageDraw
import random
import os
import json
import subprocess
import sys
from datetime import datetime
from typing import List, Dict
from profile import Profile

class CarRentalApp:
    def __init__(self, root, email):
        self.root = root
        self.email = email
        self.root.title("Traney - Car Rental")
        self.root.attributes('-fullscreen', True)
        self.root.minsize(1024, 600)
        
        # Load user info from session
        self.load_user_session()
        
        # Profile menu status
        self.is_menu_open = False
        
        # Image cache
        self.image_cache = {}
        
        # Create custom fonts
        self.create_custom_fonts()
        
        # Color scheme matching attractions module
        self.colors = {
            "primary": "#1e3d59",
            "secondary": "#ff6e40",
            "accent": "#ff8c66",
            "light": "#f8fafc",
            "dark": "#1e3d59",
            "success": "#10b981",
            "warning": "#f59e0b",
            "danger": "#ef4444",
            "card_bg": "#ffffff",
            "sidebar_bg": "#ffffff",
            "nav_bg": "#1e3d59",
            "nav_active": "#ff8c66",
            "text_light": "#64748b",
            "border": "#e2e8f0",
            "footer_bg": "#1e3d59",
            "footer_text": "#b0c4de",
            "electric": "#48bb78",
        }
        
        # Data
        self.cars = self.load_cars()
        self.filtered_cars = self.cars.copy()
        
        # Filter variables
        self.min_price_var = tk.IntVar(value=50)
        self.max_price_var = tk.IntVar(value=500)
        self.car_type_var = tk.StringVar(value="all")
        self.rating_var = tk.DoubleVar(value=4.0)
        
        # Setup UI
        self.setup_ui()
        self.show_car_rental_page()
        
        # Initialize Profile
        self.profile_system = Profile(self.root, self.profile_btn, use_custom_menu=True)
        
        # Bind keys
        self.root.bind("<Escape>", self.toggle_fullscreen)
        self.root.bind("<F11>", self.toggle_fullscreen)

    def create_custom_fonts(self):
        """Create custom fonts"""
        self.menu_font = tkFont.Font(family="Arial", size=11)
        self.menu_bold_font = tkFont.Font(family="Arial", size=11, weight="bold")

    def load_user_session(self):
        """Load user information from session file"""
        session_file = 'user_session.json'
        if os.path.exists(session_file):
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                    self.email = session_data.get('email', 'user@example.com')
                    self.user_name = session_data.get('user_name', 'Guest User')
            except:
                self.email = 'user@example.com'
                self.user_name = 'Guest User'
        else:
            self.email = 'user@example.com'
            self.user_name = 'Guest User'

    def load_cars(self) -> List[Dict]:
        """Load car rental data"""
        cars = [
            {
                "id": 1,
                "name": "Perodua Myvi",
                "model": "Perodua Myvi 1.5",
                "category": "Economy",
                "year": 2023,
                "transmission": "Automatic",
                "fuel_type": "Petrol",
                "seats": 5,
                "doors": 5,
                "luggage": 2,
                "daily_rate": 88,
                "price": 88,
                "weekly_rate": 550,
                "rating": 4.2,
                "reviews": 1240,
                "available": 12,
                "image_file": "perodua_myvi.jpg",
                "features": ["Air Conditioning", "Bluetooth", "Backup Camera", "Keyless Entry"],
                "insurance": "Basic",
                "mileage": "Unlimited",
                "pickup_locations": ["Kuala Lumpur", "Penang", "Johor Bahru"],
                "color": "Silver",
                "engine": "1.5L",
                "is_featured": True,
                "is_electric": False,
                "discount": 10
            },
            {
                "id": 2,
                "name": "Honda City",
                "model": "Honda City 1.5",
                "category": "Economy",
                "year": 2023,
                "transmission": "Automatic",
                "fuel_type": "Petrol",
                "seats": 5,
                "doors": 4,
                "luggage": 3,
                "daily_rate": 120,
                "price": 120,
                "weekly_rate": 750,
                "rating": 4.4,
                "reviews": 890,
                "available": 8,
                "image_file": "honda_city.jpg",
                "features": ["Air Conditioning", "Touchscreen", "Apple CarPlay", "Safety Sense"],
                "insurance": "Standard",
                "mileage": "Unlimited",
                "pickup_locations": ["Kuala Lumpur", "Penang"],
                "color": "White",
                "engine": "1.5L",
                "is_featured": False,
                "is_electric": False,
                "discount": 0
            },
            {
                "id": 3,
                "name": "Honda CR-V",
                "model": "Honda CR-V 1.5 Turbo",
                "category": "SUV",
                "year": 2023,
                "transmission": "Automatic",
                "fuel_type": "Petrol",
                "seats": 7,
                "doors": 5,
                "luggage": 4,
                "daily_rate": 220,
                "price": 220,
                "weekly_rate": 1400,
                "rating": 4.6,
                "reviews": 670,
                "available": 6,
                "image_file": "honda_crv.jpg",
                "features": ["Sunroof", "Leather Seats", "Navigation", "Blind Spot Monitor"],
                "insurance": "Premium",
                "mileage": "Unlimited",
                "pickup_locations": ["Kuala Lumpur", "Penang"],
                "color": "Grey",
                "engine": "1.5L Turbo",
                "is_featured": True,
                "is_electric": False,
                "discount": 15
            },
            {
                "id": 4,
                "name": "Mercedes-Benz C-Class",
                "model": "Mercedes C200",
                "category": "Luxury",
                "year": 2023,
                "transmission": "Automatic",
                "fuel_type": "Petrol",
                "seats": 5,
                "doors": 4,
                "luggage": 2,
                "daily_rate": 450,
                "price": 450,
                "weekly_rate": 2800,
                "rating": 4.8,
                "reviews": 210,
                "available": 3,
                "image_file": "mercedes_cclass.jpg",
                "features": ["Panoramic Roof", "Massage Seats", "Burmester Audio", "Driver Assist"],
                "insurance": "Premium Plus",
                "mileage": "300 km/day",
                "pickup_locations": ["Kuala Lumpur"],
                "color": "Black",
                "engine": "2.0L Turbo",
                "is_featured": True,
                "is_electric": False,
                "discount": 10
            },
            {
                "id": 5,
                "name": "Tesla Model 3",
                "model": "Tesla Model 3 Long Range",
                "category": "Electric",
                "year": 2023,
                "transmission": "Automatic",
                "fuel_type": "Electric",
                "seats": 5,
                "doors": 4,
                "luggage": 2,
                "daily_rate": 380,
                "price": 380,
                "weekly_rate": 2400,
                "rating": 4.8,
                "reviews": 340,
                "available": 5,
                "image_file": "tesla_model3.jpg",
                "features": ["Autopilot", "Glass Roof", "Premium Audio", "Supercharging"],
                "insurance": "Standard",
                "mileage": "Unlimited",
                "pickup_locations": ["Kuala Lumpur", "Penang"],
                "color": "White",
                "engine": "Electric",
                "range_km": 568,
                "charge_time": "30 min (Supercharger)",
                "is_featured": True,
                "is_electric": True,
                "discount": 12
            },
            {
                "id": 6,
                "name": "BYD Atto 3",
                "model": "BYD Atto 3 Extended",
                "category": "Electric",
                "year": 2023,
                "transmission": "Automatic",
                "fuel_type": "Electric",
                "seats": 5,
                "doors": 5,
                "luggage": 3,
                "daily_rate": 220,
                "price": 220,
                "weekly_rate": 1400,
                "rating": 4.5,
                "reviews": 120,
                "available": 8,
                "image_file": "byd_atto3.jpg",
                "features": ["Rotating Screen", "Panoramic Roof", "Voice Control", "V2L"],
                "insurance": "Standard",
                "mileage": "Unlimited",
                "pickup_locations": ["Kuala Lumpur"],
                "color": "Blue",
                "engine": "Electric",
                "range_km": 420,
                "charge_time": "45 min (DC Fast)",
                "is_featured": False,
                "is_electric": True,
                "discount": 8
            },
        ]
        
        for car in cars:
            car["popularity"] = random.uniform(3.5, 5.0)
            if car["discount"] > 0:
                car["original_rate"] = int(car["daily_rate"] / (1 - car["discount"]/100))
                car["original_price"] = int(car["price"] / (1 - car["discount"]/100))
            else:
                car["original_rate"] = car["daily_rate"]
                car["original_price"] = car["price"]
            
            if "range_km" not in car:
                car["range_km"] = "N/A"
            if "charge_time" not in car:
                car["charge_time"] = "N/A"
        
        return cars
    
    def setup_ui(self):
        """Setup main UI components"""
        # Header
        self.create_header()
        
        # Main content area
        self.create_main_content()
        
        # Status bar
        self.create_status_bar()
        
        # Footer
        self.create_footer()
    
    def create_header(self):
        """Create top navigation bar"""
        header = tk.Frame(self.root, bg='#1e3d59', height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        logo_frame = tk.Frame(header, bg='#1e3d59')
        logo_frame.pack(side='left', padx=30)
        logo_frame.bind("<Button-1>", lambda e: self.navigate_to_page("home.py"))
        
        tk.Label(logo_frame, text="🚗", font=("Arial", 28), bg='#1e3d59', fg="white").pack(side='left')
        
        logo_text = tk.Frame(logo_frame, bg='#1e3d59')
        logo_text.pack(side='left', padx=8)
        tk.Label(logo_text, text="Traney", font=("Arial", 22, "bold"), bg='#1e3d59', fg="white").pack()
        
        nav_frame = tk.Frame(header, bg='#1e3d59')
        nav_frame.pack(side='left', padx=30)
        
        nav_items = [
            ("🏠", "Home", "home.py"),
            ("🏨", "Hotel", "hotel.py"),
            ("✈️", "Flight", "flight.py"),
            ("🏛️", "Attractions", "attraction.py"),
            ("🚗", "Car Rental", "rental.py"),
            ("🗺️", "Travel Plan", "travel_plan.py"),
            ("🎒", "Packing List", "packing.py")
        ]
        
        self.nav_buttons = {}
        
        for icon, text, script in nav_items:
            btn_frame = tk.Frame(nav_frame, bg='#1e3d59')
            btn_frame.pack(side='left', padx=2)
            
            is_current = text == "Car Rental"
            
            btn = tk.Button(btn_frame, text=f"{icon} {text}", 
                        font=("Arial", 11, "bold" if is_current else "normal"),
                        bg='#1e3d59',
                        fg='#ff8c66' if is_current else '#b0c4de',
                        relief="flat", cursor="hand2",
                        padx=12, pady=8,
                        command=lambda s=script: self.navigate_to_page(s))
            btn.pack()
            
            self.nav_buttons[text] = btn_frame
            
            if is_current:
                underline = tk.Frame(btn_frame, bg='#ff8c66', height=3)
                underline.pack(fill='x', pady=(2, 0))
            
            if not is_current:
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg='#2a4d6e'))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg='#1e3d59'))
        
        right_frame = tk.Frame(header, bg='#1e3d59')
        right_frame.pack(side='right', padx=3)

        search_frame = tk.Frame(right_frame, bg="white", height=42)
        search_frame.pack(side='left')
        search_frame.pack_propagate(False)
        
        self.search_entry = tk.Entry(search_frame, font=("Arial", 11), bg="white",
                                    relief="flat", width=25)
        self.search_entry.pack(side='left', fill='both', expand=True, padx=(12, 0))
        self.search_entry.insert(0, "Search cars...")
        self.search_entry.config(fg="gray")
        
        def clear_placeholder(e):
            if self.search_entry.get() == "Search cars...":
                self.search_entry.delete(0, 'end')
                self.search_entry.config(fg="black")
        
        def add_placeholder(e):
            if not self.search_entry.get():
                self.search_entry.insert(0, "Search cars...")
                self.search_entry.config(fg="gray")
        
        self.search_entry.bind("<FocusIn>", clear_placeholder)
        self.search_entry.bind("<FocusOut>", add_placeholder)
        self.search_entry.bind("<KeyRelease>", self.filter_cars)
        
        profile_frame = tk.Frame(right_frame, bg='#1e3d59')
        profile_frame.pack(side='left')

        self.profile_btn = tk.Button(
            profile_frame, 
            text="👤", 
            font=("Segoe UI", 22), 
            bg='#1e3d59',
            fg="white", 
            relief="flat", 
            cursor="hand2", 
            padx=15, 
            pady=5,
            highlightthickness=0,
            bd=0,
            takefocus=0,
            activebackground='#2a4d6e',
            activeforeground='white',
            command=self.toggle_profile_menu
        )
        self.profile_btn.pack()

        fullscreen_btn = tk.Button(right_frame, text="⛶", font=("Arial", 18), 
                                bg='#1e3d59', fg="white",
                                relief="flat", cursor="hand2",
                                borderwidth=0, highlightthickness=0,
                                command=self.toggle_fullscreen)
        fullscreen_btn.pack(side='left', padx=(10, 0))
    
    def toggle_profile_menu(self):
        """Toggle dropdown menu show/hide"""
        if self.is_menu_open:
            self.hide_profile_menu()
        else:
            self.show_profile_menu()

    def show_profile_menu(self):
        """Show dropdown menu"""
        if self.is_menu_open:
            return
            
        self.is_menu_open = True
        
        self.profile_menu = tk.Toplevel(self.root)
        self.profile_menu.title("")
        self.profile_menu.overrideredirect(True)
        self.profile_menu.configure(bg='white')
        
        self.profile_menu.attributes('-topmost', True)
        
        button_x = self.profile_btn.winfo_rootx()
        button_y = self.profile_btn.winfo_rooty()
        button_height = self.profile_btn.winfo_height()
        
        menu_width = 250
        menu_height = 350
        
        x = button_x - menu_width + self.profile_btn.winfo_width()
        y = button_y + button_height
        
        self.profile_menu.geometry(f"{menu_width}x{menu_height}+{x}+{y}")
        
        self.create_menu_content()
        
        self.profile_menu.bind("<FocusOut>", lambda e: self.hide_profile_menu())
        self.root.bind("<Button-1>", lambda e: self.check_click_outside(e))

    def create_menu_content(self):
        """Create menu content connected to profile.py"""
        main_container = tk.Frame(self.profile_menu, bg='white', 
                                highlightbackground='#e0e0e0', highlightthickness=1)
        main_container.pack(fill='both', expand=True, padx=0, pady=0)
        
        user_info_frame = tk.Frame(main_container, bg='#f8f9fa')
        user_info_frame.pack(fill='x', padx=0, pady=0)
        
        avatar_frame = tk.Frame(user_info_frame, bg='#f8f9fa')
        avatar_frame.pack(fill='x', padx=20, pady=15)
        
        avatar_label = tk.Label(avatar_frame, text="👤", 
                              font=('Arial', 20), bg='#f8f9fa', fg='#ff8c66')
        avatar_label.pack(side='left', padx=(0, 12))
        
        info_frame = tk.Frame(avatar_frame, bg='#f8f9fa')
        info_frame.pack(side='left', fill='both', expand=True)
        
        tk.Label(info_frame, text=self.user_name, 
                font=('Arial', 12, 'bold'), bg='#f8f9fa', fg='#333333').pack(anchor='w')
        tk.Label(info_frame, text=self.email, 
                font=('Arial', 10), bg='#f8f9fa', fg='#666666').pack(anchor='w', pady=(2, 0))
        
        separator1 = tk.Frame(main_container, bg='#f0f0f0', height=1)
        separator1.pack(fill='x', pady=(0, 5))
        
        menu_options_frame = tk.Frame(main_container, bg='white')
        menu_options_frame.pack(fill='both', expand=True, padx=0, pady=10)
        
        menu_items = [
            ("📝 My Profile", self.profile_system.view_profile),
            ("ℹ️ About", self.profile_system.show_about),
            ("🚪 Logout", self.profile_system.logout)
        ]
        
        for text, command_func in menu_items:
            item_frame = tk.Frame(menu_options_frame, bg='white')
            item_frame.pack(fill='x', padx=20, pady=5)
            
            item_btn = tk.Button(item_frame, text=f"   {text}", 
                               font=self.menu_font,
                               bg='white', fg='#333333',
                               relief='flat', cursor='hand2',
                               anchor='w',
                               padx=0, pady=8,
                               command=lambda cmd=command_func: self.execute_profile_command(cmd))
            
            item_btn.pack(fill='x')
            
            item_btn.bind("<Enter>", lambda e, b=item_btn: b.config(bg='#f5f5f5', fg='#ff8c66'))
            item_btn.bind("<Leave>", lambda e, b=item_btn: b.config(bg='white', fg='#333333'))
        
        session_frame = tk.Frame(main_container, bg='#f8f9fa')
        session_frame.pack(fill='x', padx=0, pady=(5, 0))
        
        session_content = tk.Frame(session_frame, bg='#f8f9fa')
        session_content.pack(fill='x', padx=20, pady=10)
        
        session_time = datetime.now().strftime("%H:%M")
        session_date = datetime.now().strftime("%Y-%m-%d")
        
        tk.Label(session_content, text=f"Logged in: {session_time}", 
                font=('Arial', 9), bg='#f8f9fa', fg='#666666').pack(anchor='w')
        tk.Label(session_content, text=f"Date: {session_date}", 
                font=('Arial', 9), bg='#f8f9fa', fg='#666666').pack(anchor='w', pady=(2, 0))

    def execute_profile_command(self, command_func):
        """Execute profile command and close menu"""
        self.hide_profile_menu()
        command_func()

    def hide_profile_menu(self):
        """Hide dropdown menu"""
        if hasattr(self, 'profile_menu') and self.profile_menu:
            self.profile_menu.destroy()
            self.profile_menu = None
        self.is_menu_open = False

    def check_click_outside(self, event):
        """Check if clicked outside menu"""
        if self.is_menu_open and hasattr(self, 'profile_menu') and self.profile_menu:
            menu_x = self.profile_menu.winfo_rootx()
            menu_y = self.profile_menu.winfo_rooty()
            menu_width = self.profile_menu.winfo_width()
            menu_height = self.profile_menu.winfo_height()
            
            click_x = event.x_root
            click_y = event.y_root
            
            button_x = self.profile_btn.winfo_rootx()
            button_y = self.profile_btn.winfo_rooty()
            button_width = self.profile_btn.winfo_width()
            button_height = self.profile_btn.winfo_height()
            
            button_clicked = (button_x <= click_x <= button_x + button_width and 
                            button_y <= click_y <= button_y + button_height)
            
            menu_clicked = (menu_x <= click_x <= menu_x + menu_width and 
                          menu_y <= click_y <= menu_y + menu_height)
            
            if not menu_clicked and not button_clicked:
                self.hide_profile_menu()

    def create_main_content(self):
        """Create main content area with scrollbar"""
        self.main_container = tk.Frame(self.root, bg=self.colors["light"])
        self.main_container.pack(fill="both", expand=True)
        
        self.canvas = tk.Canvas(self.main_container, bg=self.colors["light"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.content_frame = tk.Frame(self.canvas, bg=self.colors["light"])
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        
        self.content_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
    
    def create_status_bar(self):
        """Create status bar"""
        status = tk.Frame(self.root, bg=self.colors["light"], height=24)
        status.pack(fill="x")
        status.pack_propagate(False)
        
        self.status_label = tk.Label(status, text="Ready", 
                                    font=("Segoe UI", 9),
                                    bg=self.colors["light"], fg=self.colors["text_light"])
        self.status_label.pack(side="left", padx=10)
        
        self.count_label = tk.Label(status, text="",
                                   font=("Segoe UI", 9),
                                   bg=self.colors["light"], fg=self.colors["primary"])
        self.count_label.pack(side="right", padx=10)
    
    def create_footer(self):
        """Create footer"""
        footer = tk.Frame(self.root, bg=self.colors["footer_bg"], height=40)
        footer.pack(fill="x")
        footer.pack_propagate(False)
        
        tk.Label(footer, text="© 2024 Traney Travel Services",
                font=("Segoe UI", 10),
                bg=self.colors["footer_bg"], fg=self.colors["footer_text"]).pack(expand=True)
    
    def show_car_rental_page(self):
        """Show main car rental page"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        title_frame = tk.Frame(self.content_frame, bg=self.colors["light"], height=80)
        title_frame.pack(fill="x", pady=(0, 20))
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, text="Car Rental", 
                font=("Segoe UI", 24, "bold"),
                bg=self.colors["light"], fg=self.colors["primary"]).place(relx=0.5, rely=0.5, anchor="center")
        
        columns = tk.Frame(self.content_frame, bg=self.colors["light"])
        columns.pack(fill="both", expand=True, padx=30)
        
        sidebar = tk.Frame(columns, bg=self.colors["sidebar_bg"], width=280)
        sidebar.pack(side="left", fill="y", padx=(0, 20))
        sidebar.pack_propagate(False)
        self.create_sidebar_filters(sidebar)
        
        content = tk.Frame(columns, bg=self.colors["light"])
        content.pack(side="left", fill="both", expand=True)
        self.create_cars_content(content)
        
        self.set_status(f"Showing {len(self.cars)} cars", "success")
        self.count_label.config(text=f"{len(self.filtered_cars)} items")
    
    def create_sidebar_filters(self, parent):
        """Create filter sidebar"""
        tk.Frame(parent, bg=self.colors["primary"], height=50).pack(fill="x")
        tk.Label(parent, text="🔍 FILTERS", font=("Segoe UI", 12, "bold"),
                bg=self.colors["primary"], fg="white").place(relx=0.5, rely=25, anchor="center")
        
        filter_frame = tk.Frame(parent, bg=self.colors["sidebar_bg"])
        filter_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(filter_frame, text="Price Range (RM/day)", font=("Segoe UI", 11, "bold"),
                bg=self.colors["sidebar_bg"], fg=self.colors["primary"]).pack(anchor="w")
        
        self.price_display = tk.Label(filter_frame, 
                                     text=f"RM {self.min_price_var.get()} - RM {self.max_price_var.get()}",
                                     font=("Segoe UI", 10, "bold"),
                                     bg=self.colors["sidebar_bg"], fg=self.colors["secondary"])
        self.price_display.pack(anchor="w", pady=(5, 10))
        
        min_frame = tk.Frame(filter_frame, bg=self.colors["sidebar_bg"])
        min_frame.pack(fill="x", pady=(0, 5))
        tk.Label(min_frame, text="Min:", font=("Segoe UI", 10),
                bg=self.colors["sidebar_bg"], fg=self.colors["text_light"]).pack(side="left")
        
        tk.Scale(min_frame, from_=50, to=500, variable=self.min_price_var,
                orient="horizontal", length=200, showvalue=False,
                bg=self.colors["sidebar_bg"], command=self.on_price_change).pack(side="right", fill="x", expand=True)
        
        max_frame = tk.Frame(filter_frame, bg=self.colors["sidebar_bg"])
        max_frame.pack(fill="x", pady=(0, 15))
        tk.Label(max_frame, text="Max:", font=("Segoe UI", 10),
                bg=self.colors["sidebar_bg"], fg=self.colors["text_light"]).pack(side="left")
        
        tk.Scale(max_frame, from_=50, to=500, variable=self.max_price_var,
                orient="horizontal", length=200, showvalue=False,
                bg=self.colors["sidebar_bg"], command=self.on_price_change).pack(side="right", fill="x", expand=True)
        
        tk.Label(filter_frame, text="Car Type", font=("Segoe UI", 11, "bold"),
                bg=self.colors["sidebar_bg"], fg=self.colors["primary"]).pack(anchor="w", pady=(10, 0))
        
        car_types = [
            ("🚗 All Types", "all"),
            ("💰 Economy", "Economy"),
            ("🚙 SUV", "SUV"),
            ("💎 Luxury", "Luxury"),
            ("⚡ Electric", "Electric"),
        ]
        
        for text, value in car_types:
            tk.Radiobutton(filter_frame, text=text, variable=self.car_type_var,
                          value=value, font=("Segoe UI", 10), bg=self.colors["sidebar_bg"],
                          command=self.filter_cars).pack(anchor="w", pady=2)
        
        tk.Label(filter_frame, text="Minimum Rating", font=("Segoe UI", 11, "bold"),
                bg=self.colors["sidebar_bg"], fg=self.colors["primary"]).pack(anchor="w", pady=(10, 0))
        
        stars_frame = tk.Frame(filter_frame, bg=self.colors["sidebar_bg"])
        stars_frame.pack(pady=(5, 15))
        
        for i in range(1, 6):
            star = tk.Label(stars_frame, text="☆", font=("Segoe UI", 20),
                           bg=self.colors["sidebar_bg"], fg="#e2e8f0", cursor="hand2")
            star.pack(side="left", padx=2)
            star.bind("<Button-1>", lambda e, r=i: self.set_star_rating(r))
        
        tk.Button(filter_frame, text="🔄 Reset Filters",
                 font=("Segoe UI", 11),
                 bg=self.colors["light"], fg=self.colors["primary"],
                 relief="flat", cursor="hand2",
                 command=self.reset_filters,
                 padx=15, pady=8).pack(fill="x", pady=(20, 5))
        
        tk.Button(filter_frame, text="💾 Save Preferences",
                 font=("Segoe UI", 11),
                 bg=self.colors["primary"], fg="white",
                 relief="flat", cursor="hand2",
                 command=self.save_preferences,
                 padx=15, pady=8).pack(fill="x")
    
    def create_cars_content(self, parent):
        """Create cars content with tabs"""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill="both", expand=True)
        
        all_frame = tk.Frame(notebook, bg=self.colors["light"])
        notebook.add(all_frame, text="🚗 All Cars")
        self.create_cars_grid(all_frame, self.filtered_cars)
        
        economy_frame = tk.Frame(notebook, bg=self.colors["light"])
        notebook.add(economy_frame, text="💰 Economy")
        economy = [c for c in self.cars if c["category"] == "Economy"]
        self.create_cars_grid(economy_frame, economy)
        
        suv_frame = tk.Frame(notebook, bg=self.colors["light"])
        notebook.add(suv_frame, text="🚙 SUV")
        suvs = [c for c in self.cars if c["category"] == "SUV"]
        self.create_cars_grid(suv_frame, suvs)
        
        electric_frame = tk.Frame(notebook, bg=self.colors["light"])
        notebook.add(electric_frame, text="⚡ Electric")
        electrics = [c for c in self.cars if c["category"] == "Electric"]
        self.create_cars_grid(electric_frame, electrics)
        
        luxury_frame = tk.Frame(notebook, bg=self.colors["light"])
        notebook.add(luxury_frame, text="💎 Luxury")
        luxury = [c for c in self.cars if c["category"] == "Luxury"]
        self.create_cars_grid(luxury_frame, luxury)
    
    def create_cars_grid(self, parent, cars):
        """Create grid of car cards"""
        header = tk.Frame(parent, bg=self.colors["light"])
        header.pack(fill="x", pady=(0, 20))
        
        tk.Label(header, text=f"{len(cars)} Cars Available",
                font=("Segoe UI", 16, "bold"),
                bg=self.colors["light"], fg=self.colors["primary"]).pack(side="left")
        
        grid_frame = tk.Frame(parent, bg=self.colors["light"])
        grid_frame.pack(fill="both", expand=True)
        
        if not cars:
            tk.Label(grid_frame, text="No cars found",
                    font=("Segoe UI", 14),
                    bg=self.colors["light"], fg=self.colors["text_light"]).pack(expand=True)
            return
        
        row, col = 0, 0
        for car in cars:
            card = self.create_car_card(grid_frame, car)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            grid_frame.grid_columnconfigure(col, weight=1)
            
            col += 1
            if col == 3:
                col = 0
                row += 1
        
        for i in range(row + 1):
            grid_frame.grid_rowconfigure(i, weight=0)
    
    def create_car_card(self, parent, car):
        """Create a single car card"""
        card = tk.Frame(parent, bg="white",
                       highlightbackground=self.colors["border"],
                       highlightthickness=1)
        
        photo = self.get_car_image(car)
        img_label = tk.Label(card, image=photo, bg="white")
        img_label.image = photo
        img_label.pack(fill="x")
        
        if car.get("is_featured"):
            tk.Label(card, text="⭐ Featured", font=("Segoe UI", 8, "bold"),
                    bg=self.colors["warning"], fg="white", padx=6, pady=2).place(x=10, y=10)
        
        if car["is_electric"]:
            tk.Label(card, text="⚡ Electric", font=("Segoe UI", 8, "bold"),
                    bg=self.colors["electric"], fg="white", padx=6, pady=2).place(x=10, y=35)
        
        if car["discount"] > 0:
            tk.Label(card, text=f"🔥 {car['discount']}% OFF", font=("Segoe UI", 8, "bold"),
                    bg=self.colors["danger"], fg="white", padx=6, pady=2).place(x=280, y=10)
        
        availability_color = self.colors["success"] if car["available"] > 0 else self.colors["danger"]
        availability_text = f"{car['available']} Available" if car["available"] > 0 else "Sold Out"
        tk.Label(card, text=availability_text, font=("Segoe UI", 9, "bold"),
                bg="white", fg=availability_color).place(x=280, y=35)
        
        content = tk.Frame(card, bg="white", padx=15, pady=15)
        content.pack(fill="both", expand=True)
        
        tk.Label(content, text=car["name"], font=("Segoe UI", 14, "bold"),
                bg="white", fg=self.colors["dark"], wraplength=280).pack(anchor="w")
        
        tk.Label(content, text=car["model"], font=("Segoe UI", 10),
                bg="white", fg=self.colors["text_light"]).pack(anchor="w", pady=(2, 10))
        
        rating_frame = tk.Frame(content, bg="white")
        rating_frame.pack(anchor="w", pady=(0, 10))
        
        stars_frame = tk.Frame(rating_frame, bg="white")
        stars_frame.pack(side="left")
        
        rating = car["rating"]
        for i in range(5):
            star = "★" if i < int(rating) else "☆"
            color = self.colors["secondary"] if i < int(rating) else "#e2e8f0"
            tk.Label(stars_frame, text=star, font=("Segoe UI", 12),
                    bg="white", fg=color).pack(side="left")
        
        tk.Label(rating_frame, text=f" {rating:.1f}", font=("Segoe UI", 11, "bold"),
                bg="white", fg=self.colors["dark"]).pack(side="left", padx=(5, 10))
        
        tk.Label(rating_frame, text=f"({car['reviews']:,})", font=("Segoe UI", 10),
                bg="white", fg=self.colors["text_light"]).pack(side="left")
        
        info_frame = tk.Frame(content, bg="white")
        info_frame.pack(fill="x", pady=(10, 0))
        
        if car["discount"] > 0:
            tk.Label(info_frame, text=f"RM {car['original_rate']}", 
                    font=("Segoe UI", 11, "overstrike"),
                    bg="white", fg=self.colors["text_light"]).pack(side="left", padx=(0, 5))
        
        tk.Label(info_frame, text=f"RM {car['daily_rate']}/day", font=("Segoe UI", 16, "bold"),
                bg="white", fg=self.colors["secondary"]).pack(side="left")
        
        category_icons = {
            "Economy": "💰",
            "SUV": "🚙",
            "Luxury": "💎",
            "Electric": "⚡"
        }
        tk.Label(info_frame, text=category_icons.get(car["category"], "🚗"),
                font=("Segoe UI", 14),
                bg="white", fg=self.colors["primary"]).pack(side="right")
        
        tk.Button(content, text="View Details",
                 font=("Segoe UI", 11),
                 bg=self.colors["secondary"], fg=self.colors["light"],
                 relief="flat", cursor="hand2",
                 command=lambda c=car: self.show_detail_page(c),
                 padx=15, pady=8).pack(fill="x", pady=(15, 0))
        
        return card
    
    def get_car_image(self, car_data):
        """Get car image with caching"""
        if not hasattr(self, 'image_cache'):
            self.image_cache = {}
        
        car_name = car_data.get('name', '')
        cache_key = car_name
        
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
        
        filename = car_data.get('image_file', 'car.jpg')
        image_path = os.path.join("images/cars", filename)
        
        if not os.path.exists(image_path):
            generic_files = ["car.jpg", "car1.jpg", "car2.jpg", "car3.jpg", "car4.jpg"]
            for file in generic_files:
                alt_path = os.path.join("images/cars", file)
                if os.path.exists(alt_path):
                    image_path = alt_path
                    break
            else:
                for file in generic_files:
                    alt_path = os.path.join("images", file)
                    if os.path.exists(alt_path):
                        image_path = alt_path
                        break
        
        try:
            img = Image.open(image_path)
            img = img.resize((350, 180), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.image_cache[cache_key] = photo
            return photo
        except Exception as e:
            return self.create_car_placeholder_image()
    
    def create_car_placeholder_image(self):
        """Create a placeholder image for cars when image is not available"""
        img = Image.new('RGB', (350, 180), color='#3498db')
        draw = ImageDraw.Draw(img)
        
        draw.ellipse((140, 40, 210, 110), fill='white', outline='white', width=2)
        draw.ellipse((160, 60, 190, 90), fill='#2c3e50')
        draw.ellipse((230, 40, 300, 110), fill='white', outline='white', width=2)
        draw.ellipse((250, 60, 280, 90), fill='#2c3e50')
        
        draw.rectangle((110, 75, 330, 130), fill='white', outline='white', width=2)
        draw.rectangle((130, 80, 310, 120), fill='#2c3e50')
        
        from PIL import ImageFont
        try:
            font = ImageFont.truetype("arial.ttf", 16)
            draw.text((175, 140), "Car Image", fill='white', anchor="mm", font=font)
        except:
            draw.text((175, 140), "Car Image", fill='white', anchor="mm")
        
        return ImageTk.PhotoImage(img)
    
    def on_price_change(self, value):
        """Handle price filter change"""
        min_price = self.min_price_var.get()
        max_price = self.max_price_var.get()
        
        if min_price > max_price:
            self.min_price_var.set(max_price)
            min_price = max_price
        
        self.price_display.config(text=f"RM {min_price} - RM {max_price}")
        self.filter_cars()
    
    def set_star_rating(self, rating):
        """Set star rating filter"""
        self.rating_var.set(rating)
        self.filter_cars()
    
    def filter_cars(self, *args):
        """Filter cars based on criteria"""
        min_price = self.min_price_var.get()
        max_price = self.max_price_var.get()
        car_type = self.car_type_var.get()
        min_rating = self.rating_var.get()
        search_text = self.search_entry.get().lower()
        
        filtered = []
        for car in self.cars:
            if not (min_price <= car["daily_rate"] <= max_price):
                continue
            
            if car_type != "all" and car["category"] != car_type:
                continue
            
            if car["rating"] < min_rating:
                continue
            
            if search_text and search_text != "search cars...":
                search_match = (search_text in car["name"].lower() or
                              search_text in car["model"].lower() or
                              search_text in car["category"].lower())
                if not search_match:
                    continue
            
            filtered.append(car)
        
        filtered.sort(key=lambda x: x.get("popularity", 0), reverse=True)
        
        self.filtered_cars = filtered
        self.show_car_rental_page()
        
        self.set_status(f"Found {len(filtered)} cars", "success")
        self.count_label.config(text=f"{len(filtered)} items")
    
    def reset_filters(self):
        """Reset all filters"""
        self.min_price_var.set(50)
        self.max_price_var.set(500)
        self.car_type_var.set("all")
        self.rating_var.set(4.0)
        self.search_entry.delete(0, 'end')
        self.search_entry.insert(0, "Search cars...")
        self.search_entry.config(fg="gray")
        
        self.price_display.config(text=f"RM {self.min_price_var.get()} - RM {self.max_price_var.get()}")
        self.filter_cars()
        self.set_status("All filters reset", "success")
    
    def save_preferences(self):
        """Save user preferences"""
        preferences = {
            "price_range": (self.min_price_var.get(), self.max_price_var.get()),
            "car_type": self.car_type_var.get(),
            "min_rating": self.rating_var.get()
        }
        
        self.set_status("Preferences saved", "success")
    
    def show_detail_page(self, car):
        """Open car_detail.py when clicking View Details"""
        try:
            self.root.destroy()
            
            import car_detail
            root = tk.Tk()
            app = car_detail.CarDetailApp(root, car, self.email)
            root.mainloop()
            
        except ImportError:
            self.create_car_detail_module()
            
            root = tk.Tk()
            app = CarRentalApp(root, self.email)
            root.mainloop()
            
        except Exception as e:
            root = tk.Tk()
            app = CarRentalApp(root, self.email)
            root.mainloop()
    
    def create_car_detail_module(self):
        """Create car_detail.py file if it doesn't exist"""
        car_detail_code = '''# car_detail.py - Car Detail Module
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import os

class CarDetailApp:
    def __init__(self, root, car, email):
        self.root = root
        self.car = car
        self.email = email
        self.root.title(f"Traney - {car['name']}")
        self.root.geometry("1000x700")
        
        self.colors = {
            "primary": "#1e3d59",
            "secondary": "#ff6e40",
            "light": "#f8fafc",
            "dark": "#1e3d59",
            "nav_bg": "#1e3d59",
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        header = tk.Frame(self.root, bg=self.colors["nav_bg"], height=60)
        header.pack(fill="x")
        
        tk.Button(header, text="← Back", font=("Segoe UI", 12),
                 bg=self.colors["nav_bg"], fg="white", relief="flat",
                 command=self.go_back).pack(side="left", padx=20)
        
        tk.Label(header, text=f"{self.car['name']} Details",
                font=("Segoe UI", 20, "bold"),
                bg=self.colors["nav_bg"], fg="white").pack(side="left", padx=20)
        
        main_frame = tk.Frame(self.root, bg=self.colors["light"])
        main_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        left_frame = tk.Frame(main_frame, bg=self.colors["light"], width=400)
        left_frame.pack(side="left", fill="y")
        left_frame.pack_propagate(False)
        
        photo = self.load_image(self.car["image_file"], (380, 250))
        img_label = tk.Label(left_frame, image=photo, bg="white")
        img_label.image = photo
        img_label.pack(fill="both", expand=True)
        
        right_frame = tk.Frame(main_frame, bg=self.colors["light"])
        right_frame.pack(side="left", fill="both", expand=True, padx=(30, 0))
        
        tk.Label(right_frame, text=self.car["name"], 
                font=("Segoe UI", 24, "bold"),
                bg=self.colors["light"], fg=self.colors["dark"]).pack(anchor="w")
        
        tk.Label(right_frame, text=self.car["model"],
                font=("Segoe UI", 16),
                bg=self.colors["light"], fg="#64748b").pack(anchor="w", pady=(0, 20))
        
        price = self.car.get("price", self.car.get("daily_rate", 0))
        price_frame = tk.Frame(right_frame, bg=self.colors["light"])
        price_frame.pack(anchor="w", pady=(0, 20))
        
        if "discount" in self.car and self.car["discount"] > 0:
            original_price = self.car.get("original_price", self.car.get("original_rate", price))
            tk.Label(price_frame, text=f"RM {original_price}", 
                    font=("Segoe UI", 14, "overstrike"),
                    bg=self.colors["light"], fg="#64748b").pack(side="left", padx=(0, 10))
        
        tk.Label(price_frame, text=f"RM {price}/day", 
                font=("Segoe UI", 28, "bold"),
                bg=self.colors["light"], fg=self.colors["secondary"]).pack(side="left")
        
        tk.Label(right_frame, text="Specifications", 
                font=("Segoe UI", 18, "bold"),
                bg=self.colors["light"], fg=self.colors["dark"]).pack(anchor="w", pady=(10, 10))
        
        specs = [
            ("Category:", self.car.get("category", "N/A")),
            ("Transmission:", self.car.get("transmission", "N/A")),
            ("Fuel Type:", self.car.get("fuel_type", "N/A")),
            ("Seats:", str(self.car.get("seats", "N/A"))),
            ("Luggage:", f"{self.car.get('luggage', 'N/A')} bags"),
            ("Engine:", self.car.get("engine", "N/A")),
            ("Color:", self.car.get("color", "N/A")),
        ]
        
        for label, value in specs:
            spec_frame = tk.Frame(right_frame, bg=self.colors["light"])
            spec_frame.pack(fill="x", pady=5)
            
            tk.Label(spec_frame, text=label, font=("Segoe UI", 12),
                    bg=self.colors["light"], fg="#64748b", width=12, anchor="w").pack(side="left")
            tk.Label(spec_frame, text=value, font=("Segoe UI", 12, "bold"),
                    bg=self.colors["light"], fg=self.colors["dark"]).pack(side="left")
        
        tk.Label(right_frame, text="Features", 
                font=("Segoe UI", 18, "bold"),
                bg=self.colors["light"], fg=self.colors["dark"]).pack(anchor="w", pady=(20, 10))
        
        features_frame = tk.Frame(right_frame, bg=self.colors["light"])
        features_frame.pack(fill="x")
        
        features = self.car.get("features", [])
        if features:
            for feature in features:
                tk.Label(features_frame, text=f"• {feature}", 
                        font=("Segoe UI", 12),
                        bg=self.colors["light"], fg=self.colors["dark"]).pack(anchor="w", pady=2)
        else:
            tk.Label(features_frame, text="No features listed", 
                    font=("Segoe UI", 12),
                    bg=self.colors["light"], fg="#64748b").pack(anchor="w")
        
        tk.Button(right_frame, text="Book Now", 
                 font=("Segoe UI", 16, "bold"),
                 bg=self.colors["secondary"], fg="white",
                 relief="flat", cursor="hand2",
                 command=self.book_car,
                 padx=30, pady=12).pack(side="right", pady=(30, 0))
    
    def load_image(self, filename, size):
        try:
            image_path = os.path.join("images/cars", filename)
            if not os.path.exists(image_path):
                alt_path = os.path.join("images", os.path.basename(filename))
                if os.path.exists(alt_path):
                    image_path = alt_path
                else:
                    raise FileNotFoundError(f"Image not found: {filename}")
            
            image = Image.open(image_path)
            image = image.convert('RGB')
            image = image.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            placeholder = Image.new('RGB', size, (245, 247, 250))
            draw = ImageDraw.Draw(placeholder)
            draw.rectangle([0, 0, size[0]-1, size[1]-1], outline=(229, 231, 235), width=1)
            draw.text((size[0]//2, size[1]//2), "Car Image", 
                     fill=(156, 163, 175), anchor="mm", align="center")
            return ImageTk.PhotoImage(placeholder)
    
    def book_car(self):
        price = self.car.get("price", self.car.get("daily_rate", 0))
        messagebox.showinfo("Booking", f"Booking {self.car['name']} for RM {price}/day")
    
    def go_back(self):
        self.root.destroy()
        import car_rental
        root = tk.Tk()
        app = car_rental.CarRentalApp(root, self.email)
        root.mainloop()
'''
        
        with open("car_detail.py", "w", encoding="utf-8") as f:
            f.write(car_detail_code)
    
    def navigate_to_page(self, script_file):
        """Navigate to other pages"""
        if script_file == "rental.py":
            return
        
        if os.path.exists(script_file):
            try:
                session_data = {
                    'email': self.email,
                    'user_name': self.user_name
                }
                with open('user_session.json', 'w') as f:
                    json.dump(session_data, f)
                
                self.root.destroy()
                subprocess.Popen(["python", script_file])
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open {script_file}: {str(e)}")
        else:
            messagebox.showinfo("Coming Soon", f"The {script_file.split('.')[0]} module is under development!")
    
    def set_status(self, message: str, status_type: str = "info"):
        colors = {"info": self.colors["text_light"], "success": self.colors["success"],
                 "warning": self.colors["warning"], "error": self.colors["danger"]}
        self.status_label.config(text=message, fg=colors.get(status_type, self.colors["text_light"]))
    
    def toggle_fullscreen(self, event=None):
        is_fullscreen = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not is_fullscreen)
        return "break"
    
    def on_mousewheel(self, event):
        if event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        else:
            self.canvas.yview_scroll(1, "units")


def main():
    """Main function for independent execution"""
    root = tk.Tk()
    
    if len(sys.argv) > 2:
        email = sys.argv[1]
        user_name = sys.argv[2]
        app = CarRentalApp(root, email)
    else:
        app = CarRentalApp(root, "user@example.com")
    
    root.mainloop()

if __name__ == "__main__":
    main()