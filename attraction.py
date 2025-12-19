import tkinter as tk
from tkinter import ttk, messagebox, font as tkFont
from PIL import Image, ImageTk, ImageDraw
import io
import random
import os
import time
import json
import subprocess
import sys
from datetime import datetime
from typing import List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor
from profile import Profile

class AttractionApp:
    def __init__(self, root, email):
        self.root = root
        self.email = email
        self.root.title("Traney - Attractions")
        self.root.attributes('-fullscreen', True)
        self.root.minsize(1024, 600)
        
        # Load user information from session
        self.load_user_session()
        
        # Profile menu status
        self.is_menu_open = False
        
        # Create custom fonts
        self.create_custom_fonts()
        
        # Color scheme
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
            "nav_active": "#ff6e40",
            "text_light": "#64748b",
            "border": "#e2e8f0",
            "footer_bg": "#1e3d59",
            "footer_text": "#b0c4de",
        }
        
        # Data
        self.attractions = self.load_attractions()
        self.filtered_attractions = self.attractions.copy()
        
        # Image cache
        self.image_cache = {}
        self.cache_size = 50
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Filter variables
        self.min_price_var = tk.IntVar(value=0)
        self.max_price_var = tk.IntVar(value=500)
        self.rating_var = tk.DoubleVar(value=4.0)
        self.sort_var = tk.StringVar(value="popularity")
        self.search_var = tk.StringVar()
        self.view_mode = tk.StringVar(value="grid")
        
        # Category filter variables
        self.category_vars = {}
        
        # Setup UI
        self.setup_ui()
        self.show_attractions_page()
        
        # Initialize Profile here - Important!
        self.profile_system = Profile(self.root, self.profile_btn, use_custom_menu=True)
        
        # Bind keys
        self.root.bind("<Escape>", self.toggle_fullscreen)
        self.root.bind("<F11>", self.toggle_fullscreen)

    def create_custom_fonts(self):
        """Create custom fonts"""
        self.menu_font = tkFont.Font(family="Arial", size=11)  # Use tkFont
        self.menu_bold_font = tkFont.Font(family="Arial", size=11, weight="bold")  # Use tkFont

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

    def load_attractions(self) -> List[Dict]:
        """Load attractions data with 15 international locations - ALL WITH PRICES"""
        attractions = [
            # Malaysian attractions - All with prices
            {
                "id": 1, 
                "name": "Petronas Twin Towers", 
                "location": "Kuala Lumpur, Malaysia",
                "description": "Iconic twin skyscrapers with skybridge.", 
                "category": "Landmark",
                "price": 80, 
                "rating": 4.6, 
                "reviews": 23400, 
                "duration": "2 hours",
                "image_file": "images/attractions/PTT.jpg",
                "color": "#355c7d", 
                "tags": ["Modern", "Architecture"], 
                "is_trending": True,
                "best_time": "9 AM - 9 PM",
                "phone": "+60 3-2331 8080",
                "website": "www.petronastwintowers.com.my",
                "opening_hours": "9:00 AM - 9:00 PM",
                "address": "Kuala Lumpur City Centre, 50088 Kuala Lumpur"
            },
            {
                "id": 2, 
                "name": "Batu Caves", 
                "location": "Selangor, Malaysia",
                "description": "Limestone hill with cave temples.", 
                "category": "Religious",
                "price": 25,  # Changed from 0 to 25
                "rating": 4.4, 
                "reviews": 18900, 
                "duration": "2-3 hours",
                "image_file": "images/attractions/BC.jpg",
                "color": "#f8b195", 
                "tags": ["Temple", "Hindu"], 
                "is_trending": False,
                "best_time": "6 AM - 9 PM",
                "phone": "+60 3-2287 9422",
                "website": "www.batucaves.org",
                "opening_hours": "6:00 AM - 9:00 PM",
                "address": "Gombak, 68100 Batu Caves, Selangor"
            },
            {
                "id": 3, 
                "name": "Langkawi Sky Bridge", 
                "location": "Langkawi, Malaysia",
                "description": "Curved pedestrian bridge with stunning views.", 
                "category": "Viewpoint",
                "price": 85, 
                "rating": 4.5, 
                "reviews": 12700, 
                "duration": "2-3 hours",
                "image_file": "images/attractions/LSB.jpg",
                "color": "#6c5b7b", 
                "tags": ["Scenic", "Bridge"], 
                "is_trending": True,
                "best_time": "10 AM - 6 PM",
                "phone": "+60 4-959 4225",
                "website": "www.panoramalangkawi.com",
                "opening_hours": "10:00 AM - 6:00 PM",
                "address": "Langkawi, 07000 Kedah"
            },
            {
                "id": 4, 
                "name": "Perhentian Islands", 
                "location": "Terengganu, Malaysia",
                "description": "Tropical paradise with crystal clear waters.", 
                "category": "Beach",
                "price": 120,  # Changed from 0 to 120 (boat tour)
                "rating": 4.8, 
                "reviews": 9800, 
                "duration": "Full day",
                "image_file": "images/attractions/PI.jpg",
                "color": "#f67280", 
                "tags": ["Beach", "Snorkeling"], 
                "is_trending": True,
                "best_time": "March - October",
                "phone": "+60 9-626 2020",
                "website": "www.perhentianislands.com",
                "opening_hours": "24 hours",
                "address": "Besut, Terengganu"
            },
            {
                "id": 5, 
                "name": "Penang Hill", 
                "location": "Penang, Malaysia",
                "description": "Hill resort with panoramic views.", 
                "category": "Viewpoint",
                "price": 30, 
                "rating": 4.3, 
                "reviews": 15600, 
                "duration": "3-4 hours",
                "image_file": "images/attractions/PH.jpg",
                "color": "#355c7d", 
                "tags": ["Hill Station", "Funicular"], 
                "is_trending": False,
                "best_time": "6:30 AM - 11 PM",
                "phone": "+60 4-828 8880",
                "website": "www.penanghill.gov.my",
                "opening_hours": "6:30 AM - 11:00 PM",
                "address": "Bukit Bendera, 11300 Penang"
            },
            {
                "id": 6, 
                "name": "Taman Negara", 
                "location": "Pahang, Malaysia",
                "description": "Ancient tropical rainforest.", 
                "category": "Nature",
                "price": 45,  # Changed from 5 to 45
                "rating": 4.6, 
                "reviews": 7800, 
                "duration": "Full day",
                "image_file": "images/attractions/TN.jpg",
                "color": "#99b898", 
                "tags": ["Rainforest", "Wildlife"], 
                "is_trending": False,
                "best_time": "February - September",
                "phone": "+60 9-266 1122",
                "website": "www.tamannegara.org",
                "opening_hours": "7:00 AM - 6:00 PM",
                "address": "Kuala Tahan, 27000 Jerantut, Pahang"
            },
            {
                "id": 7, 
                "name": "Cameron Highlands", 
                "location": "Pahang, Malaysia",
                "description": "Hill station with tea plantations.", 
                "category": "Nature",
                "price": 60,  # Changed from 0 to 60 (tour package)
                "rating": 4.4, 
                "reviews": 11200, 
                "duration": "2-3 days",
                "image_file": "images/attractions/CM.jpg",
                "color": "#99b898", 
                "tags": ["Tea Plantation"], 
                "is_trending": False,
                "best_time": "Year-round",
                "phone": "+60 5-491 1100",
                "website": "www.cameronhighlands.com",
                "opening_hours": "24 hours",
                "address": "Cameron Highlands, 39000 Pahang"
            },
            {
                "id": 8, 
                "name": "Malacca Historical Sites", 
                "location": "Malacca, Malaysia",
                "description": "UNESCO World Heritage city.", 
                "category": "Historical",
                "price": 35,  # Changed from 0 to 35 (guided tour)
                "rating": 4.5, 
                "reviews": 13400, 
                "duration": "Full day",
                "image_file": "images/attractions/MHS.jpg",
                "color": "#c06c84", 
                "tags": ["UNESCO", "Colonial"], 
                "is_trending": True,
                "best_time": "9 AM - 5 PM",
                "phone": "+60 6-283 6538",
                "website": "www.melaka.gov.my",
                "opening_hours": "9:00 AM - 5:00 PM",
                "address": "Malacca City, 75000 Malacca"
            },
            
            # International attractions - All with prices
            {
                "id": 9, 
                "name": "Eiffel Tower", 
                "location": "Paris, France",
                "description": "Iconic iron lattice tower on the Champ de Mars.", 
                "category": "Landmark",
                "price": 25, 
                "rating": 4.7, 
                "reviews": 215000, 
                "duration": "2-3 hours",
                "image_file": "images/attractions/EF.jpg",
                "color": "#4a6572", 
                "tags": ["Iconic", "Romantic"], 
                "is_trending": True,
                "best_time": "9 AM - 11 PM",
                "phone": "+33 892 70 12 39",
                "website": "www.toureiffel.paris",
                "opening_hours": "9:00 AM - 11:00 PM",
                "address": "Champ de Mars, 5 Avenue Anatole France, Paris"
            },
            {
                "id": 10, 
                "name": "Great Wall of China", 
                "location": "Beijing, China",
                "description": "Ancient fortification stretching over 13,000 miles.", 
                "category": "Historical",
                "price": 45, 
                "rating": 4.8, 
                "reviews": 89000, 
                "duration": "3-4 hours",
                "image_file": "images/attractions/GWOC.jpg",
                "color": "#8d6e63", 
                "tags": ["UNESCO", "Ancient"], 
                "is_trending": True,
                "best_time": "April - October",
                "phone": "+86 10 6162 6028",
                "website": "www.thegreatwall.com.cn",
                "opening_hours": "7:30 AM - 6:00 PM",
                "address": "Huairou District, Beijing"
            },
            {
                "id": 11, 
                "name": "Statue of Liberty", 
                "location": "New York, USA",
                "description": "Colossal neoclassical sculpture on Liberty Island.", 
                "category": "Landmark",
                "price": 24, 
                "rating": 4.5, 
                "reviews": 112000, 
                "duration": "2-3 hours",
                "image_file": "images/attractions/SOL.jpg",
                "color": "#1976d2", 
                "tags": ["Iconic", "Freedom"], 
                "is_trending": False,
                "best_time": "8:30 AM - 4:00 PM",
                "phone": "+1 212-363-3200",
                "website": "www.nps.gov/stli",
                "opening_hours": "8:30 AM - 4:00 PM",
                "address": "Liberty Island, New York, NY 10004"
            },
            {
                "id": 12, 
                "name": "Taj Mahal", 
                "location": "Agra, India",
                "description": "White marble mausoleum built by Mughal emperor Shah Jahan.", 
                "category": "Historical",
                "price": 15, 
                "rating": 4.9, 
                "reviews": 156000, 
                "duration": "3 hours",
                "image_file": "images/attractions/TajMahal.jpg",
                "color": "#f0f0f0", 
                "tags": ["UNESCO", "Mughal"], 
                "is_trending": True,
                "best_time": "6 AM - 7 PM",
                "phone": "+91 562 222 7261",
                "website": "www.tajmahal.gov.in",
                "opening_hours": "6:00 AM - 7:00 PM",
                "address": "Dharmapuri, Forest Colony, Tajganj, Agra"
            },
            {
                "id": 13, 
                "name": "Sydney Opera House", 
                "location": "Sydney, Australia",
                "description": "Multi-venue performing arts centre with unique architecture.", 
                "category": "Landmark",
                "price": 35, 
                "rating": 4.6, 
                "reviews": 78000, 
                "duration": "1-2 hours",
                "image_file": "images/attractions/SOH.jpg",
                "color": "#ffcc80", 
                "tags": ["Modern", "Architecture"], 
                "is_trending": False,
                "best_time": "9 AM - 5 PM",
                "phone": "+61 2 9250 7111",
                "website": "www.sydneyoperahouse.com",
                "opening_hours": "9:00 AM - 5:00 PM",
                "address": "Bennelong Point, Sydney NSW 2000"
            },
            {
                "id": 14, 
                "name": "Colosseum", 
                "location": "Rome, Italy",
                "description": "Ancient amphitheatre, the largest ever built.", 
                "category": "Historical",
                "price": 18, 
                "rating": 4.7, 
                "reviews": 134000, 
                "duration": "2-3 hours",
                "image_file": "images/attractions/Colosseum.jpg",
                "color": "#a1887f", 
                "tags": ["Roman", "Ancient"], 
                "is_trending": True,
                "best_time": "8:30 AM - 7:15 PM",
                "phone": "+39 06 3996 7700",
                "website": "www.parcocolosseo.it",
                "opening_hours": "8:30 AM - 7:15 PM",
                "address": "Piazza del Colosseo, 1, Rome"
            },
            {
                "id": 15, 
                "name": "Mount Fuji", 
                "location": "Shizuoka, Japan",
                "description": "Active volcano and Japan's highest mountain.", 
                "category": "Nature",
                "price": 75,  # Changed from 0 to 75 (guided climb)
                "rating": 4.8, 
                "reviews": 92000, 
                "duration": "Full day",
                "image_file": "images/attractions/MF.jpg",
                "color": "#e0e0e0", 
                "tags": ["Volcano", "Sacred"], 
                "is_trending": True,
                "best_time": "July - September",
                "phone": "+81 555-72-1111",
                "website": "www.fujisan-climb.jp",
                "opening_hours": "24 hours (climbing season)",
                "address": "Kitayama, Fujinomiya, Shizuoka"
            }
        ]
        
        # Add calculated fields for all attractions
        for attr in attractions:
            attr["popularity"] = random.uniform(3.5, 5.0)
            attr["distance_km"] = random.randint(5, 500)  # Increased range for international
            attr["is_featured"] = attr["id"] in [1, 4, 8, 9, 12]  # Featured attractions
            
            # Ensure all required fields exist
            required_fields = ["best_time", "phone", "website", "opening_hours", "address"]
            for field in required_fields:
                if field not in attr:
                    attr[field] = "Not specified"
        
        return attractions

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
        """Create top navigation bar - Matching car_rental.py style"""
        header = tk.Frame(self.root, bg='#1e3d59', height=70)
        header.pack(fill='x')
        header.pack_propagate(False)  # Maintain fixed height
        
        # Logo section (click to return to homepage)
        logo_frame = tk.Frame(header, bg='#1e3d59')
        logo_frame.pack(side='left', padx=30)
        logo_frame.bind("<Button-1>", lambda e: self.navigate_to_page("home.py"))
        
        tk.Label(logo_frame, text="🏛️", font=("Arial", 28), bg='#1e3d59', fg="white").pack(side='left')
        
        logo_text = tk.Frame(logo_frame, bg='#1e3d59')
        logo_text.pack(side='left', padx=8)
        tk.Label(logo_text, text="Traney", font=("Arial", 22, "bold"), bg='#1e3d59', fg="white").pack()
        
        # Navigation menu
        nav_frame = tk.Frame(header, bg='#1e3d59')
        nav_frame.pack(side='left', padx=30)
        
        # Navigation items: (icon, text, script file)
        nav_items = [
            ("🏠", "Home", "home.py"),
            ("🏨", "Hotel", "hotel.py"),
            ("✈️", "Flight", "flight.py"),
            ("🏛️", "Attractions", "attraction.py"),  # Current page is Attractions
            ("🚗", "Car Rental", "car_rental.py"),
            ("🗺️", "Travel Plan", "travel_plan.py"),
            ("🎒", "Packing List", "packing.py")
        ]
        
        self.nav_buttons = {}  # Store button references
        
        for icon, text, script in nav_items:
            btn_frame = tk.Frame(nav_frame, bg='#1e3d59')
            btn_frame.pack(side='left', padx=2)
            
            is_current = text == "Attractions"  # Current page is Attractions
            
            btn = tk.Button(btn_frame, text=f"{icon} {text}", 
                        font=("Arial", 11, "bold" if is_current else "normal"),
                        bg='#1e3d59',
                        fg='#ff8c66' if is_current else '#b0c4de',
                        relief="flat", cursor="hand2",
                        padx=12, pady=8,
                        command=lambda s=script: self.navigate_to_page(s))
            btn.pack()
            
            self.nav_buttons[text] = btn_frame
            
            # Add underline for current active page
            if is_current:
                underline = tk.Frame(btn_frame, bg='#ff8c66', height=3)
                underline.pack(fill='x', pady=(2, 0))
            
            # Hover effects for navigation buttons
            if not is_current:
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg='#2a4d6e'))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg='#1e3d59'))
        
        # Right section: search, profile, fullscreen
        right_frame = tk.Frame(header, bg='#1e3d59')
        right_frame.pack(side='right', padx=3)

        # Search bar
        search_frame = tk.Frame(right_frame, bg="white", height=42)
        search_frame.pack(side='left')
        search_frame.pack_propagate(False)
        
        self.search_entry = tk.Entry(search_frame, font=("Arial", 11), bg="white",
                                    relief="flat", width=25)
        self.search_entry.pack(side='left', fill='both', expand=True, padx=(12, 0))
        self.search_entry.insert(0, "Search attractions...")
        self.search_entry.config(fg="gray")  # Gray placeholder text
        
        # Placeholder text handling
        def clear_placeholder(e):
            if self.search_entry.get() == "Search attractions...":
                self.search_entry.delete(0, 'end')
                self.search_entry.config(fg="black")
        
        def add_placeholder(e):
            if not self.search_entry.get():
                self.search_entry.insert(0, "Search attractions...")
                self.search_entry.config(fg="gray")
        
        self.search_entry.bind("<FocusIn>", clear_placeholder)
        self.search_entry.bind("<FocusOut>", add_placeholder)
        self.search_entry.bind("<KeyRelease>", self.on_search_change)
        
        # Profile button
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
        """Toggle profile menu visibility"""
        if self.is_menu_open:
            self.hide_profile_menu()
        else:
            self.show_profile_menu()

    def show_profile_menu(self):
        """Display profile menu"""
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
        
        # Create menu content
        self.create_menu_content()
        
        self.profile_menu.bind("<FocusOut>", lambda e: self.hide_profile_menu())
        self.root.bind("<Button-1>", lambda e: self.check_click_outside(e))

    def create_menu_content(self):
        """Create profile menu content"""
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
        
        # User information
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
        
        for i, (text, command_func) in enumerate(menu_items):
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

            # Hover effects for menu items
            item_btn.bind("<Enter>", lambda e, b=item_btn: b.config(bg='#f5f5f5', fg='#ff8c66'))
            item_btn.bind("<Leave>", lambda e, b=item_btn: b.config(bg='white', fg='#333333'))
        
        # Session information
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
        """Execute profile menu command"""
        self.hide_profile_menu()
        command_func()

    def hide_profile_menu(self):
        """Hide profile menu"""
        if hasattr(self, 'profile_menu') and self.profile_menu:
            self.profile_menu.destroy()
            self.profile_menu = None
        self.is_menu_open = False

    def check_click_outside(self, event):
        """Check if click is outside menu"""
        if self.is_menu_open and hasattr(self, 'profile_menu') and self.profile_menu:
            # Check if click position is within menu window
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
        
        # Canvas for scrolling
        self.canvas = tk.Canvas(self.main_container, bg=self.colors["light"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Content frame
        self.content_frame = tk.Frame(self.canvas, bg=self.colors["light"])
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        
        # Bind events
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
    
    # ==================== MAIN PAGES ====================
    def show_attractions_page(self):
        """Show main attractions page"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Simple title
        title_frame = tk.Frame(self.content_frame, bg=self.colors["light"], height=80)
        title_frame.pack(fill="x", pady=(0, 20))
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, text="Attractions", 
                font=("Segoe UI", 24, "bold"),
                bg=self.colors["light"], fg=self.colors["primary"]).place(relx=0.5, rely=0.5, anchor="center")
        
        # Two column layout
        columns = tk.Frame(self.content_frame, bg=self.colors["light"])
        columns.pack(fill="both", expand=True, padx=30)
        
        # Left sidebar - Filters
        sidebar = tk.Frame(columns, bg=self.colors["sidebar_bg"], width=280)
        sidebar.pack(side="left", fill="y", padx=(0, 20))
        sidebar.pack_propagate(False)
        self.create_sidebar_filters(sidebar)
        
        # Right content - Attractions
        content = tk.Frame(columns, bg=self.colors["light"])
        content.pack(side="left", fill="both", expand=True)
        self.create_attractions_content(content)
        
        # Update status
        self.set_status(f"Showing {len(self.attractions)} attractions", "success")
        self.count_label.config(text=f"{len(self.filtered_attractions)} items")
    
    def create_sidebar_filters(self, parent):
        """Create filter sidebar"""
        # Header
        tk.Frame(parent, bg=self.colors["primary"], height=50).pack(fill="x")
        tk.Label(parent, text="🔍 FILTERS", font=("Segoe UI", 12, "bold"),
                bg=self.colors["primary"], fg="white").place(relx=0.5, rely=25, anchor="center")
        
        # Filter content
        filter_frame = tk.Frame(parent, bg=self.colors["sidebar_bg"])
        filter_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Price range - Updated for no free attractions
        tk.Label(filter_frame, text="Price Range (RM)", font=("Segoe UI", 11, "bold"),
                bg=self.colors["sidebar_bg"], fg=self.colors["primary"]).pack(anchor="w")
        
        self.price_display = tk.Label(filter_frame, 
                                     text=f"RM {self.min_price_var.get()} - RM {self.max_price_var.get()}",
                                     font=("Segoe UI", 10, "bold"),
                                     bg=self.colors["sidebar_bg"], fg=self.colors["secondary"])
        self.price_display.pack(anchor="w", pady=(5, 10))
        
        # Min price
        min_frame = tk.Frame(filter_frame, bg=self.colors["sidebar_bg"])
        min_frame.pack(fill="x", pady=(0, 5))
        tk.Label(min_frame, text="Min:", font=("Segoe UI", 10),
                bg=self.colors["sidebar_bg"], fg=self.colors["text_light"]).pack(side="left")
        
        tk.Scale(min_frame, from_=0, to=500, variable=self.min_price_var,
                orient="horizontal", length=200, showvalue=False,
                bg=self.colors["sidebar_bg"], command=self.on_price_change).pack(side="right", fill="x", expand=True)
        
        # Max price
        max_frame = tk.Frame(filter_frame, bg=self.colors["sidebar_bg"])
        max_frame.pack(fill="x", pady=(0, 15))
        tk.Label(max_frame, text="Max:", font=("Segoe UI", 10),
                bg=self.colors["sidebar_bg"], fg=self.colors["text_light"]).pack(side="left")
        
        tk.Scale(max_frame, from_=0, to=500, variable=self.max_price_var,
                orient="horizontal", length=200, showvalue=False,
                bg=self.colors["sidebar_bg"], command=self.on_price_change).pack(side="right", fill="x", expand=True)
        
        # Categories
        tk.Label(filter_frame, text="Categories", font=("Segoe UI", 11, "bold"),
                bg=self.colors["sidebar_bg"], fg=self.colors["primary"]).pack(anchor="w", pady=(10, 0))
        
        categories = ["Historical", "Nature", "Landmark", "Beach", "Adventure", "Religious", "Viewpoint"]
        
        for cat in categories:
            var = tk.BooleanVar(value=True)
            self.category_vars[cat] = var
            tk.Checkbutton(filter_frame, text=cat, variable=var,
                          font=("Segoe UI", 10), bg=self.colors["sidebar_bg"],
                          command=self.filter_attractions).pack(anchor="w", pady=2)
        
        # Rating
        tk.Label(filter_frame, text="Minimum Rating", font=("Segoe UI", 11, "bold"),
                bg=self.colors["sidebar_bg"], fg=self.colors["primary"]).pack(anchor="w", pady=(10, 0))
        
        stars_frame = tk.Frame(filter_frame, bg=self.colors["sidebar_bg"])
        stars_frame.pack(pady=(5, 15))
        
        for i in range(1, 6):
            star = tk.Label(stars_frame, text="☆", font=("Segoe UI", 20),
                           bg=self.colors["sidebar_bg"], fg="#e2e8f0", cursor="hand2")
            star.pack(side="left", padx=2)
            star.bind("<Button-1>", lambda e, r=i: self.set_star_rating(r))
        
        # Action buttons
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
    
    def create_attractions_content(self, parent):
        """Create attractions content with tabs matching car rental style"""
        # Create notebook (tabs)
        notebook = ttk.Notebook(parent)
        notebook.pack(fill="both", expand=True)
        
        # All attractions tab
        all_frame = tk.Frame(notebook, bg=self.colors["light"])
        notebook.add(all_frame, text="🌍 All Attractions")
        self.create_attractions_grid(all_frame, self.filtered_attractions)
        
        # Trending tab
        trend_frame = tk.Frame(notebook, bg=self.colors["light"])
        notebook.add(trend_frame, text="📈 Trending")
        trending = [a for a in self.attractions if a.get("is_trending", False)]
        self.create_attractions_grid(trend_frame, trending)
        
        # Nature tab
        nature_frame = tk.Frame(notebook, bg=self.colors["light"])
        notebook.add(nature_frame, text="🏞️ Nature")
        nature = [a for a in self.attractions if a["category"] == "Nature"]
        self.create_attractions_grid(nature_frame, nature)
        
        # Beach tab
        beach_frame = tk.Frame(notebook, bg=self.colors["light"])
        notebook.add(beach_frame, text="🏖️ Beach")
        beach = [a for a in self.attractions if a["category"] == "Beach"]
        self.create_attractions_grid(beach_frame, beach)
        
        # International tab
        intl_frame = tk.Frame(notebook, bg=self.colors["light"])
        notebook.add(intl_frame, text="🌐 International")
        international = [a for a in self.attractions if a["id"] >= 9]  # IDs 9-15 are international
        self.create_attractions_grid(intl_frame, international)
    
    def create_attractions_grid(self, parent, attractions):
        """Create grid of attraction cards matching car rental style"""
        # Header
        header = tk.Frame(parent, bg=self.colors["light"])
        header.pack(fill="x", pady=(0, 20))
        
        tk.Label(header, text=f"{len(attractions)} Attractions",
                font=("Segoe UI", 16, "bold"),
                bg=self.colors["light"], fg=self.colors["primary"]).pack(side="left")
        
        # Grid container
        grid_frame = tk.Frame(parent, bg=self.colors["light"])
        grid_frame.pack(fill="both", expand=True)
        
        # Display attractions
        if not attractions:
            tk.Label(grid_frame, text="No attractions found",
                    font=("Segoe UI", 14),
                    bg=self.colors["light"], fg=self.colors["text_light"]).pack(expand=True)
            return
        
        # Create 3-column grid
        row, col = 0, 0
        for attraction in attractions:
            card = self.create_attraction_card(grid_frame, attraction)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            grid_frame.grid_columnconfigure(col, weight=1)
            
            col += 1
            if col == 3:
                col = 0
                row += 1
        
        # Configure grid rows
        for i in range(row + 1):
            grid_frame.grid_rowconfigure(i, weight=0)
    
    def create_attraction_card(self, parent, attraction):
        """Create a single attraction card matching car rental style"""
        card = tk.Frame(parent, bg="white",
                       highlightbackground=self.colors["border"],
                       highlightthickness=1)
        
        # Image
        photo = self.load_image(attraction["image_file"], (350, 180))
        img_label = tk.Label(card, image=photo, bg="white")
        img_label.image = photo
        img_label.pack(fill="x")
        
        # Badges matching car rental style
        if attraction.get("is_featured"):
            tk.Label(card, text="⭐ Featured", font=("Segoe UI", 8, "bold"),
                    bg=self.colors["warning"], fg="white", padx=6, pady=2).place(x=10, y=10)
        
        # Country flag indicator for international attractions
        if attraction["id"] >= 9:  # International attractions
            country = attraction["location"].split(", ")[-1]
            flag_text = self.get_country_flag(country)
            tk.Label(card, text=flag_text, font=("Segoe UI", 12),
                    bg="white", fg=self.colors["primary"]).place(x=280, y=10)
        
        # Content
        content = tk.Frame(card, bg="white", padx=15, pady=15)
        content.pack(fill="both", expand=True)
        
        # Title and location
        tk.Label(content, text=attraction["name"], font=("Segoe UI", 14, "bold"),
                bg="white", fg=self.colors["dark"], wraplength=280).pack(anchor="w")
        
        tk.Label(content, text=f"📍 {attraction['location']}", font=("Segoe UI", 10),
                bg="white", fg=self.colors["text_light"]).pack(anchor="w", pady=(2, 10))
        
        # Rating stars matching car rental style
        rating_frame = tk.Frame(content, bg="white")
        rating_frame.pack(anchor="w", pady=(0, 10))
        
        stars_frame = tk.Frame(rating_frame, bg="white")
        stars_frame.pack(side="left")
        
        rating = attraction["rating"]
        for i in range(5):
            star = "★" if i < int(rating) else "☆"
            color = self.colors["secondary"] if i < int(rating) else "#e2e8f0"
            tk.Label(stars_frame, text=star, font=("Segoe UI", 12),
                    bg="white", fg=color).pack(side="left")
        
        tk.Label(rating_frame, text=f" {rating:.1f}", font=("Segoe UI", 11, "bold"),
                bg="white", fg=self.colors["dark"]).pack(side="left", padx=(5, 10))
        
        tk.Label(rating_frame, text=f"({attraction['reviews']:,})", font=("Segoe UI", 10),
                bg="white", fg=self.colors["text_light"]).pack(side="left")
        
        # Price and duration - REMOVED FREE CHECK
        info_frame = tk.Frame(content, bg="white")
        info_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(info_frame, text=f"RM {attraction['price']}", font=("Segoe UI", 16, "bold"),
                bg="white", fg=self.colors["secondary"]).pack(side="left")
        
        tk.Label(info_frame, text=f"⏱️ {attraction['duration']}", font=("Segoe UI", 10),
                bg="white", fg=self.colors["text_light"]).pack(side="right")
        
        # View Details button - Matching car rental style
        tk.Button(content, text="View Details",
                 font=("Segoe UI", 11),
                 bg=self.colors["secondary"], fg=self.colors["light"],
                 relief="flat", cursor="hand2",
                 command=lambda a=attraction: self.show_detail_page(a),
                 padx=15, pady=8).pack(fill="x", pady=(15, 0))
        
        return card
    
    def get_country_flag(self, country):
        """Get emoji flag for country"""
        flag_map = {
            "France": "🇫🇷",
            "China": "🇨🇳",
            "USA": "🇺🇸",
            "India": "🇮🇳",
            "Australia": "🇦🇺",
            "Italy": "🇮🇹",
            "Japan": "🇯🇵",
            "Malaysia": "🇲🇾"
        }
        return flag_map.get(country, "🌐")
    
    # ==================== IMAGE HANDLING ====================
    def load_image(self, file_path: str, size: Tuple[int, int] = (300, 200)) -> ImageTk.PhotoImage:
        """Load image from local file with enhanced error handling"""
        cache_key = f"{file_path}_{size[0]}_{size[1]}"
        if cache_key in self.image_cache:
            self.image_cache[cache_key]["last_used"] = time.time()
            return self.image_cache[cache_key]["image"]
        
        try:
            # Try to load from local file
            if os.path.exists(file_path):
                image = Image.open(file_path)
            else:
                # If file doesn't exist, check in images/attractions folder
                filename = os.path.basename(file_path)
                alternative_path = f"images/attractions/{filename}"
                
                if os.path.exists(alternative_path):
                    image = Image.open(alternative_path)
                else:
                    # Try to find the file with different path combinations
                    search_paths = [
                        file_path,
                        alternative_path,
                        f"./{filename}",
                        f"./attractions/{filename}",
                    ]
                    
                    found = False
                    for path in search_paths:
                        if os.path.exists(path):
                            image = Image.open(path)
                            found = True
                            break
                    
                    if not found:
                        raise FileNotFoundError(f"Image file not found: {file_path}")
            
            image = image.convert('RGB')
            image = image.resize(size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.image_cache[cache_key] = {"image": photo, "last_used": time.time()}
            return photo
            
        except Exception as e:
            print(f"Error loading image {file_path}: {e}")
            # Create placeholder image
            placeholder = Image.new('RGB', size, (245, 247, 250))
            draw = ImageDraw.Draw(placeholder)
            draw.rectangle([0, 0, size[0]-1, size[1]-1], outline=(229, 231, 235), width=1)
            draw.text((size[0]//2, size[1]//2), "Image\nNot Found", 
                     fill=(156, 163, 175), anchor="mm", align="center")
            photo = ImageTk.PhotoImage(placeholder)
            
            # Cache the placeholder too
            self.image_cache[cache_key] = {"image": photo, "last_used": time.time()}
            return photo
    
    # ==================== FILTER FUNCTIONS ====================
    def on_price_change(self, value):
        """Handle price filter change"""
        min_price = self.min_price_var.get()
        max_price = self.max_price_var.get()
        
        if min_price > max_price:
            self.min_price_var.set(max_price)
            min_price = max_price
        
        self.price_display.config(text=f"RM {min_price} - RM {max_price}")
        self.filter_attractions()
    
    def set_star_rating(self, rating):
        """Set star rating filter"""
        self.rating_var.set(rating)
        self.filter_attractions()
    
    def on_search_change(self, event):
        """Handle search input"""
        if hasattr(self, '_search_timer'):
            self.root.after_cancel(self._search_timer)
        self._search_timer = self.root.after(300, self.filter_attractions)
    
    def filter_attractions(self, *args):
        """Filter attractions based on criteria"""
        # Get filter values
        min_price = self.min_price_var.get()
        max_price = self.max_price_var.get()
        min_rating = self.rating_var.get()
        search_text = self.search_entry.get().lower()
        
        # Get selected categories
        selected_categories = [cat for cat, var in self.category_vars.items() if var.get()]
        
        # Apply filters
        filtered = []
        for attr in self.attractions:
            # Price filter
            if not (min_price <= attr["price"] <= max_price):
                continue
            
            # Rating filter
            if attr["rating"] < min_rating:
                continue
            
            # Category filter
            if attr["category"] not in selected_categories:
                continue
            
            # Search filter
            if search_text and search_text != "search attractions...":
                search_match = (search_text in attr["name"].lower() or
                              search_text in attr["location"].lower() or
                              search_text in attr["description"].lower() or
                              search_text in attr["category"].lower() or
                              search_text in " ".join(attr.get("tags", [])).lower())
                if not search_match:
                    continue
            
            filtered.append(attr)
        
        # Sort
        sort_by = self.sort_var.get()
        if sort_by == "popularity":
            filtered.sort(key=lambda x: x.get("popularity", 0), reverse=True)
        elif sort_by == "rating_desc":
            filtered.sort(key=lambda x: x["rating"], reverse=True)
        elif sort_by == "price_asc":
            filtered.sort(key=lambda x: x["price"])
        elif sort_by == "price_desc":
            filtered.sort(key=lambda x: x["price"], reverse=True)
        
        self.filtered_attractions = filtered
        self.show_attractions_page()  # Refresh display
        
        # Update status
        self.set_status(f"Found {len(filtered)} attractions", "success")
        self.count_label.config(text=f"{len(filtered)} items")
    
    def reset_filters(self):
        """Reset all filters"""
        self.min_price_var.set(0)
        self.max_price_var.set(500)  # Updated max price
        self.rating_var.set(4.0)
        self.sort_var.set("popularity")
        self.search_entry.delete(0, 'end')
        self.search_entry.insert(0, "Search attractions...")
        self.search_entry.config(fg="gray")
        
        for var in self.category_vars.values():
            var.set(True)
        
        self.price_display.config(text=f"RM {self.min_price_var.get()} - RM {self.max_price_var.get()}")
        self.filter_attractions()
        self.set_status("All filters reset", "success")
    
    def save_preferences(self):
        """Save user preferences - NO POPUP"""
        preferences = {
            "price_range": (self.min_price_var.get(), self.max_price_var.get()),
            "min_rating": self.rating_var.get(),
            "categories": [cat for cat, var in self.category_vars.items() if var.get()]
        }
        
        # Just update status, no popup
        self.set_status("Preferences saved", "success")
    
    # ==================== NAVIGATION FUNCTIONS ====================
    def navigate_to_page(self, script_file):
        """Navigate to different page/module"""
        if script_file == "attraction.py":  # Already on attractions page
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
    
    # ==================== DETAIL PAGE NAVIGATION ====================
    def show_detail_page(self, attraction):
        """Open attraction_detail.py when clicking View Details - NO POPUP"""
        try:
            # Ensure attraction has all required fields for detail page
            required_fields = ["best_time", "phone", "website", "opening_hours", "address"]
            for field in required_fields:
                if field not in attraction:
                    attraction[field] = "Not specified"
            
            # Close current window
            self.root.destroy()
            
            # Import and open attraction_detail.py
            import attraction_detail
            root = tk.Tk()
            app = attraction_detail.AttractionDetailApp(root, attraction, self.email)
            root.mainloop()
            
        except ImportError as e:
            # If attraction_detail.py doesn't exist, reopen attractions page
            print(f"Error: {e}")
            
            # Reopen attractions page
            root = tk.Tk()
            app = AttractionApp(root, self.email)
            root.mainloop()
            
        except Exception as e:
            # Handle any other errors
            print(f"Error opening detail page: {e}")
            
            # Reopen attractions page
            root = tk.Tk()
            app = AttractionApp(root, self.email)
            root.mainloop()
    
    # ==================== UTILITY FUNCTIONS ====================
    def set_status(self, message: str, status_type: str = "info"):
        """Set status bar message"""
        colors = {"info": self.colors["text_light"], "success": self.colors["success"],
                 "warning": self.colors["warning"], "error": self.colors["danger"]}
        self.status_label.config(text=message, fg=colors.get(status_type, self.colors["text_light"]))
    
    def toggle_fullscreen(self, event=None):
        """Toggle full screen mode"""
        is_fullscreen = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not is_fullscreen)
        return "break"
    
    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        if event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        else:
            self.canvas.yview_scroll(1, "units")

def main():
    root = tk.Tk()
    if len(sys.argv) > 2:
        email = sys.argv[1]
        user_name = sys.argv[2]
        app = AttractionApp(root, email)
    else:
        app = AttractionApp(root, "user@example.com")
    
    root.mainloop()

if __name__ == "__main__":
    main()