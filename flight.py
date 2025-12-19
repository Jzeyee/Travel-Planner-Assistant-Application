import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import os, json, datetime, sys
from flight_detail import FlightDetailPage
from booking_detail import BookingDetailApp
from profile import Profile

class Flight:
    """Main Flight Booking Application"""
    def __init__(self, root, email="user@example.com"):
        # Initialize main window
        self.root = root
        self.email = email
        
        # Try to load user information from session
        if not email:
            self.load_user_session()
        else:
            self.user_name = "Guest User"
        
        self.root.title("Traney - Flight Booking")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#f0f8ff')
        
        # Fullscreen bindings
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        self.root.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.fullscreen_state = True
        
        # Profile menu state
        self.is_menu_open = False
        self.profile_menu = None
        
        # Load data
        self.user_data = self.load_user_data()
        self.flight_data = self.get_default_flight_data()
        
        # Current state variables
        self.current_page = "main"
        self.selected_flight_data = None
        self.selected_seats = []
        self.passenger_info = {}
        
        # Passenger counts
        self.adult_count = 1
        self.child_count = 0
        self.infant_count = 0
        
        # Color scheme
        self.colors = {
            "primary": "#1e3d59", "secondary": "#ff6e40", "accent": "#ff8c66",
            "light": "#f0f8ff", "dark": "#1e3d59", "success": "#4CAF50",
            "warning": "#ff6e40", "card_bg": "#ffffff", "header_bg": "#1e3d59",
            "sidebar_bg": "#ffffff", "highlight": "#ff8c66", "nav_bg": "#1e3d59",
            "nav_active": "#ff8c66", "nav_inactive": "#b0c4de", "text_light": "#b0c4de",
            "border": "#e0e0e0", "footer_bg": "#1e3d59"
        }
        
        # Fonts
        self.create_custom_fonts()
        
        # Clear previous widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create UI
        self.create_header()
        
        # Initialize Profile here
        self.profile_system = Profile(self.root, self.profile_btn, use_custom_menu=True)
        
        self.main_container = tk.Frame(self.root, bg=self.colors["light"])
        self.main_container.pack(fill="both", expand=True)
        
        # Initialize variables
        self.init_variables()
        
        self.init_main_page()
        self.bind_mousewheel_to_all()

    def create_custom_fonts(self):
        """Create custom fonts"""
        # Create font with strikethrough
        self.strike_font = tk.font.Font(family="Arial", size=14, overstrike=True)
        self.normal_font = tk.font.Font(family="Arial", size=14)
        self.bold_font = tk.font.Font(family="Arial", size=20, weight="bold")
        self.price_font = tk.font.Font(family="Arial", size=20, weight="bold")
        self.title_font = tk.font.Font(family="Arial", size=24, weight="bold")
        self.subtitle_font = tk.font.Font(family="Arial", size=16, weight="bold")
        self.menu_font = tk.font.Font(family="Arial", size=11)
        self.menu_bold_font = tk.font.Font(family="Arial", size=11, weight="bold")

    def lighten_color(self, color, amount=20):
        """Lighten color function"""
        if color.startswith('#'):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            
            r = min(255, r + amount)
            g = min(255, g + amount)
            b = min(255, b + amount)
            
            return f'#{r:02x}{g:02x}{b:02x}'
        return color

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

    def init_variables(self):
        """Initialize tkinter variables"""
        self.leaving_var = tk.StringVar(value="Kuala Lumpur, Malaysia")
        self.going_var = tk.StringVar(value="Select destination")
        self.departure_var = tk.StringVar()
        self.return_var = tk.StringVar()
        self.flight_type_var = tk.StringVar(value="Return")
        self.class_var = tk.StringVar(value="Economy")
        
        # Filter variables
        self.airline_var = tk.StringVar(value="All")
        self.stops_var = tk.StringVar(value="All")
        self.time_var = tk.StringVar(value="All")
        self.sort_var = tk.StringVar(value="Price (Low to High)")
        self.price_range_var = tk.IntVar(value=2000)
        
        # Destination cities from flight data
        self.cities = self.flight_data.get("cities", ["Select destination", "Singapore", "Bangkok", "Tokyo", "Seoul"])
        
        self.current_displayed_flights = []

    def parse_price(self, price_str):
        """Parse price string to float"""
        try:
            return float(price_str.replace('RM ', '').replace(',', ''))
        except:
            return 0.0

    def get_default_flight_data(self):
        """Return optimized flight data structure"""
        # Base flight template for all flights
        base_flights = [
            {
                "id": "MAS001", "airline": "Malaysia Airlines", "route": "Kuala Lumpur → Tokyo, Japan",
                "duration": "7h 15m", "time": "08:00 - 16:15", "stops": "Non-stop", "aircraft": "Boeing 777",
                "rating": "4.5", "price": "RM 1,250", "original_price": "RM 1,500", "deal": "Best Deal",
                "amenities": ["In-flight entertainment", "Meal service", "30kg baggage", "Seat selection"],
                "airline_info": "National carrier of Malaysia with excellent service",
                "review_rating": "8.7/10", "review_comment": "Comfortable flight with great service"
            },
            {
                "id": "SIA001", "airline": "Singapore Airlines", "route": "Kuala Lumpur → Singapore, Singapore",
                "duration": "1h 05m", "time": "14:30 - 15:35", "stops": "Non-stop", "aircraft": "Airbus A320",
                "rating": "4.8", "price": "RM 350", "original_price": "RM 420", "deal": "Popular",
                "amenities": ["Complimentary meals", "Entertainment system", "25kg baggage", "Priority boarding"],
                "airline_info": "World-class airline known for exceptional service",
                "review_rating": "9.2/10", "review_comment": "Excellent service as always"
            },
            {
                "id": "AK001", "airline": "AirAsia", "route": "Kuala Lumpur → Bangkok, Thailand",
                "duration": "2h 15m", "time": "19:00 - 21:15", "stops": "Non-stop", "aircraft": "Airbus A320",
                "rating": "4.2", "price": "RM 280", "original_price": "RM 320", "deal": "Cheapest",
                "amenities": ["Value fares", "Online check-in", "15kg baggage", "Food purchase"],
                "airline_info": "Low-cost carrier with extensive regional network",
                "review_rating": "7.8/10", "review_comment": "Great value for money"
            }
        ]
        
        # Generate flights for different cities using templates
        city_templates = {
            "Tokyo": {"base_price": 1250, "duration": "7h 15m", "airlines": ["Malaysia Airlines", "Japan Airlines"]},
            "Bangkok": {"base_price": 480, "duration": "2h 15m", "airlines": ["Thai Airways", "AirAsia"]},
            "Singapore": {"base_price": 350, "duration": "1h 05m", "airlines": ["Singapore Airlines", "AirAsia"]},
            "Hong Kong": {"base_price": 890, "duration": "3h 50m", "airlines": ["Cathay Pacific", "AirAsia"]},
            "Taipei": {"base_price": 1120, "duration": "4h 30m", "airlines": ["EVA Air", "China Airlines"]},
            "Shanghai": {"base_price": 980, "duration": "5h 15m", "airlines": ["China Eastern", "AirAsia X"]},
            "Beijing": {"base_price": 1050, "duration": "6h 05m", "airlines": ["Air China", "Malaysia Airlines"]},
            "Penang": {"base_price": 120, "duration": "1h 00m", "airlines": ["AirAsia", "Malaysia Airlines"]}
        }
        
        destination_flights = {}
        for city, template in city_templates.items():
            city_flights = []
            for i, airline in enumerate(template["airlines"]):
                price = template["base_price"] + (i * 200)
                flight = {
                    "id": f"{airline[:2]}{i+1:03d}",
                    "airline": airline,
                    "route": f"Kuala Lumpur → {city}",
                    "duration": template["duration"],
                    "time": f"{8+i*3}:00 - {8+i*3+int(template['duration'].split('h')[0])}:15",
                    "stops": "Non-stop",
                    "aircraft": "Boeing 787" if price > 1000 else "Airbus A320",
                    "rating": str(4.5 - i*0.2),
                    "price": f"RM {price:,}" if price >= 1000 else f"RM {price}",
                    "original_price": f"RM {price + 200:,}" if price >= 1000 else f"RM {price + 200}",
                    "deal": "Premium Service" if i == 0 else "Best Value",
                    "amenities": base_flights[0]["amenities"] if i == 0 else base_flights[2]["amenities"]
                }
                city_flights.append(flight)
            destination_flights[city] = city_flights
        
        return {
            "cities": list(city_templates.keys()),
            "recommended_flights": base_flights,
            "destination_flights": destination_flights,
            "category_flights": {
                "budget": [f for f in base_flights if self.parse_price(f["price"]) < 500],
                "business": [base_flights[1]],
                "direct": [base_flights[0]]
            }
        }

    def create_header(self):
        """Create top navigation bar - consistent with Home page"""
        header = tk.Frame(self.root, bg='#1e3d59', height=70)
        header.pack(fill='x')
        header.pack_propagate(False)  # Maintain fixed height
        
        # Logo section (click to return to home)
        logo_frame = tk.Frame(header, bg='#1e3d59')
        logo_frame.pack(side='left', padx=30)
        logo_frame.bind("<Button-1>", lambda e: self.navigate_to_page("home.py"))
        
        tk.Label(logo_frame, text="✈️", font=("Arial", 28), bg='#1e3d59', fg="white").pack(side='left')
        
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
            ("🏛️", "Attractions", "attraction.py"),
            ("🚗", "Car Rental", "car_rental.py"),
            ("🗺️", "Travel Plan", "travel_plan.py"),
            ("🎒", "Packing List", "packing.py")
        ]
        
        self.nav_buttons = {}  # Store button references
        
        for icon, text, script in nav_items:
            btn_frame = tk.Frame(nav_frame, bg='#1e3d59')
            btn_frame.pack(side='left', padx=2)
            
            is_current = text == "Flight"  # Current page is Flight
            
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
            btn.bind("<Enter>", lambda e, b=btn, t=text: 
                    b.config(bg='#2a4d6e') if t != "Flight" else None)
            btn.bind("<Leave>", lambda e, b=btn, t=text: 
                    b.config(bg='#1e3d59') if t != "Flight" else None)
        
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
        self.search_entry.insert(0, "Search...")
        self.search_entry.config(fg="gray")  # Gray placeholder text
        
        # Placeholder text handling
        def clear_placeholder(e):
            if self.search_entry.get() == "Search...":
                self.search_entry.delete(0, 'end')
                self.search_entry.config(fg="black")
        
        def add_placeholder(e):
            if not self.search_entry.get():
                self.search_entry.insert(0, "Search...")
                self.search_entry.config(fg="gray")
        
        self.search_entry.bind("<FocusIn>", clear_placeholder)
        self.search_entry.bind("<FocusOut>", add_placeholder)
        
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

        # Fullscreen toggle button
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
        
        # Create menu window
        self.profile_menu = tk.Toplevel(self.root)
        self.profile_menu.title("")
        self.profile_menu.overrideredirect(True)  # Remove window border
        self.profile_menu.configure(bg='white')
        
        # Add shadow effect
        self.profile_menu.attributes('-topmost', True)
        
        # Calculate menu position
        button_x = self.profile_btn.winfo_rootx()
        button_y = self.profile_btn.winfo_rooty()
        button_height = self.profile_btn.winfo_height()
        
        menu_width = 250
        menu_height = 350  # Reduced height because one menu item was removed
        
        x = button_x - menu_width + self.profile_btn.winfo_width()
        y = button_y + button_height
        
        self.profile_menu.geometry(f"{menu_width}x{menu_height}+{x}+{y}")
        
        # Create menu content
        self.create_menu_content()
        
        # Bind click outside to close menu
        self.profile_menu.bind("<FocusOut>", lambda e: self.hide_profile_menu())
        self.root.bind("<Button-1>", lambda e: self.check_click_outside(e))

    def create_menu_content(self):
        """Create menu content connected to profile.py - REMOVED "My Bookings" """
        # Main container
        main_container = tk.Frame(self.profile_menu, bg='white', 
                                highlightbackground='#e0e0e0', highlightthickness=1)
        main_container.pack(fill='both', expand=True, padx=0, pady=0)
        
        # Top user info area
        user_info_frame = tk.Frame(main_container, bg='#f8f9fa')
        user_info_frame.pack(fill='x', padx=0, pady=0)
        
        # Avatar and username
        avatar_frame = tk.Frame(user_info_frame, bg='#f8f9fa')
        avatar_frame.pack(fill='x', padx=20, pady=15)
        
        # Avatar
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
        
        # Separator
        separator1 = tk.Frame(main_container, bg='#f0f0f0', height=1)
        separator1.pack(fill='x', pady=(0, 5))
        
        # Menu options area - removed "My Bookings"
        menu_options_frame = tk.Frame(main_container, bg='white')
        menu_options_frame.pack(fill='both', expand=True, padx=0, pady=10)
        
        # Menu options - removed "My Bookings", only three items remain
        menu_items = [
            ("📝 My Profile", self.profile_system.view_profile),
            ("ℹ️ About", self.profile_system.show_about),
            ("🚪 Logout", self.profile_system.logout)
        ]
        
        for i, (text, command_func) in enumerate(menu_items):
            item_frame = tk.Frame(menu_options_frame, bg='white')
            item_frame.pack(fill='x', padx=20, pady=5)
            
            # Create menu item - using lambda to ensure correct parameter passing
            item_btn = tk.Button(item_frame, text=f"   {text}", 
                               font=self.menu_font,
                               bg='white', fg='#333333',
                               relief='flat', cursor='hand2',
                               anchor='w',
                               padx=0, pady=8,
                               command=lambda cmd=command_func: self.execute_profile_command(cmd))
            
            item_btn.pack(fill='x')
            
            # Hover effects
            item_btn.bind("<Enter>", lambda e, b=item_btn: b.config(bg='#f5f5f5', fg='#ff8c66'))
            item_btn.bind("<Leave>", lambda e, b=item_btn: b.config(bg='white', fg='#333333'))
        
        # Logout session information
        session_frame = tk.Frame(main_container, bg='#f8f9fa')
        session_frame.pack(fill='x', padx=0, pady=(5, 0))
        
        session_content = tk.Frame(session_frame, bg='#f8f9fa')
        session_content.pack(fill='x', padx=20, pady=10)
        
        # Current session information
        session_time = datetime.datetime.now().strftime("%H:%M")
        session_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
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
        if self.profile_menu:
            self.profile_menu.destroy()
            self.profile_menu = None
        self.is_menu_open = False

    def check_click_outside(self, event):
        """Check if click is outside menu"""
        if self.is_menu_open and self.profile_menu:
            # Check if click position is within menu window
            menu_x = self.profile_menu.winfo_rootx()
            menu_y = self.profile_menu.winfo_rooty()
            menu_width = self.profile_menu.winfo_width()
            menu_height = self.profile_menu.winfo_height()
            
            click_x = event.x_root
            click_y = event.y_root
            
            # Check if profile button was clicked
            button_x = self.profile_btn.winfo_rootx()
            button_y = self.profile_btn.winfo_rooty()
            button_width = self.profile_btn.winfo_width()
            button_height = self.profile_btn.winfo_height()
            
            button_clicked = (button_x <= click_x <= button_x + button_width and 
                            button_y <= click_y <= button_y + button_height)
            
            # Check if click is inside menu
            menu_clicked = (menu_x <= click_x <= menu_x + menu_width and 
                          menu_y <= click_y <= menu_y + menu_height)
            
            if not menu_clicked and not button_clicked:
                self.hide_profile_menu()

    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        current_state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_state)

    def load_user_data(self):
        """Load user data from JSON file"""
        try:
            if os.path.exists('user_data.json'):
                with open('user_data.json', 'r') as f:
                    return json.load(f)
            return {}
        except:
            return {}

    def get_all_flights(self):
        """Get all flights from flight data"""
        all_flights = self.flight_data["recommended_flights"].copy()
        for flights in self.flight_data["destination_flights"].values():
            all_flights.extend(flights)
        for flights in self.flight_data["category_flights"].values():
            all_flights.extend(flights)
        return list({f['id']: f for f in all_flights}.values())  # Remove duplicates

    def init_main_page(self):
        """Initialize main page"""
        self.current_page = "main"
        for widget in self.main_container.winfo_children():
            widget.destroy()
        self.show_flights_page()
    
    def show_flights_page(self):
        """Show the flights page with search form and filters"""
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        self.create_search_section()
        self.create_content_section()
        self.create_footer(self.main_container)
    
    def create_search_section(self):
        """Create search section"""
        search_section = tk.Frame(self.main_container, bg=self.colors["light"])
        search_section.pack(fill="x", pady=(20, 30), padx=30)
        
        search_container = tk.Frame(search_section, bg=self.colors["primary"], padx=40, pady=30)
        search_container.pack(fill="x", padx=40, pady=12)
        
        tk.Label(search_container, text="✈️ Find Your Perfect Flight", 
                font=("Arial", 16, "bold"), bg=self.colors["primary"], fg="white").pack(pady=(0, 20))
        
        # Create form rows
        self.create_form_row1(search_container)
        self.create_form_row2(search_container)
        self.create_form_row3(search_container)

    def create_form_row1(self, parent):
        """Create first row of form (locations)"""
        row = tk.Frame(parent, bg=self.colors["primary"])
        row.pack(pady=(0, 15))
        
        # Leaving from (fixed)
        self.create_form_field(row, "Leaving From", "Kuala Lumpur, Malaysia", 
                              fixed=True, padx=(0, 25))
        
        # Going to (dropdown)
        self.create_form_field(row, "Going To", self.cities, 
                              variable=self.going_var, padx=(25, 0))

    def create_form_row2(self, parent):
        """Create second row of form (centered dates only)"""
        row = tk.Frame(parent, bg=self.colors["primary"])
        row.pack(pady=(0, 15))
        
        # Container to center both date fields
        container = tk.Frame(row, bg=self.colors["primary"])
        container.pack()
        
        # Departure date (centered with return date)
        self.create_date_field(container, "Departure Date", self.departure_var, 
                              lambda: self.show_calendar("departure"), padx=(0, 20))
        
        # Return date
        self.create_date_field(container, "Return Date", self.return_var,
                              lambda: self.show_calendar("return"), padx=(20, 0))

    def create_form_row3(self, parent):
        """Create third row (centered search button only)"""
        row = tk.Frame(parent, bg=self.colors["primary"])
        row.pack(pady=(10, 0))
        
        # Center the search button
        tk.Button(row, text="🔍 Search Flights", font=("Arial", 14, "bold"),
                 bg=self.colors["secondary"], fg="white", relief="flat",
                 cursor="hand2", command=self.search_flights,
                 padx=35, pady=12).pack()

    def create_form_field(self, parent, label, value, variable=None, fixed=False, padx=0):
        """Create a form field (label + input)"""
        col = tk.Frame(parent, bg=self.colors["primary"])
        col.pack(side="left", padx=padx)
        
        tk.Label(col, text=label, font=("Arial", 12, "bold"),
                bg=self.colors["primary"], fg="#e0f0ff").pack(pady=(0, 8))
        
        field = tk.Frame(col, bg="white", relief="solid", borderwidth=1, height=40, width=220)
        field.pack()
        field.pack_propagate(False)
        
        if fixed:
            tk.Label(field, text=value, font=("Arial", 12), bg="white",
                    fg=self.colors["primary"], anchor="w", padx=15, pady=10).pack(fill="both", expand=True)
        else:
            combobox = ttk.Combobox(field, textvariable=variable, values=value,
                                   font=("Arial", 12), state="readonly")
            combobox.set(value[0] if isinstance(value, list) else value)
            combobox.pack(fill="both", expand=True, padx=15, pady=8)
            if label == "Going To":
                self.going_combobox = combobox

    def create_counter(self, parent, label, count, increase_cmd, decrease_cmd):
        """Create a counter widget"""
        tk.Label(parent, text=label, font=("Arial", 11),
                bg=self.colors["primary"], fg="#e0f0ff").pack()
        
        control = tk.Frame(parent, bg=self.colors["primary"])
        control.pack(pady=(5, 0))
        
        tk.Button(control, text="➖", font=("Arial", 11), bg="#e74c3c", fg="white",
                 relief="flat", cursor="hand2", command=decrease_cmd, width=2).pack(side="left", padx=(0, 8))
        
        display = tk.Label(control, text=str(count), font=("Arial", 12, "bold"),
                          bg="white", fg=self.colors["primary"], width=3, 
                          padx=5, relief="solid", borderwidth=1)
        display.pack(side="left")
        
        tk.Button(control, text="➕", font=("Arial", 11), bg="#27ae60", fg="white",
                 relief="flat", cursor="hand2", command=increase_cmd, width=2).pack(side="left", padx=(8, 0))
        
        # Store reference to display
        if label == "Adults":
            self.adult_display = display
        elif label == "Children":
            self.child_display = display

    def create_date_field(self, parent, label, variable, command, padx=0):
        """Create a date field with calendar button"""
        col = tk.Frame(parent, bg=self.colors["primary"])
        col.pack(side="left", padx=padx)
        
        tk.Label(col, text=label, font=("Arial", 12, "bold"),
                bg=self.colors["primary"], fg="#e0f0ff").pack(pady=(0, 8))
        
        field = tk.Frame(col, bg="white", relief="solid", borderwidth=1, height=40, width=180)
        field.pack()
        field.pack_propagate(False)
        
        control = tk.Frame(field, bg="white")
        control.pack(fill="both", expand=True, padx=15, pady=8)
        
        entry = tk.Entry(control, textvariable=variable, font=("Arial", 12),
                        bg="white", fg=self.colors["primary"], relief="flat",
                        borderwidth=0, width=10, state="readonly")
        entry.pack(side="left", fill="both", expand=True)
        
        tk.Button(control, text="📅", font=("Arial", 14), bg=self.colors["primary"],
                 fg="white", relief="flat", cursor="hand2", command=command,
                 width=2, height=1, padx=6).pack(side="left", padx=(10, 0))
        
        # Store reference to display
        if label == "Departure Date":
            self.departure_display = entry
        elif label == "Return Date":
            self.return_display = entry

    def create_content_section(self):
        """Create main content section"""
        content_frame = tk.Frame(self.main_container, bg=self.colors["light"])
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left sidebar for filters
        left_frame = tk.Frame(content_frame, bg=self.colors["light"], width=280)
        left_frame.pack(side="left", fill="y", padx=(0, 20))
        self.create_sidebar_filters(left_frame)
        
        # Right content area
        right_frame = tk.Frame(content_frame, bg=self.colors["light"])
        right_frame.pack(side="left", fill="both", expand=True)
        self.create_main_content(right_frame)

    def create_sidebar_filters(self, parent):
        """Create sidebar with flight filters"""
        # Create scrollable sidebar
        canvas = tk.Canvas(parent, bg=self.colors["sidebar_bg"], highlightthickness=0, width=280)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        
        scrollable_frame = tk.Frame(canvas, bg=self.colors["sidebar_bg"])
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        sidebar = tk.Frame(scrollable_frame, bg=self.colors["sidebar_bg"], width=260,
                          relief="flat", highlightbackground=self.colors["border"], highlightthickness=1)
        sidebar.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Filter header
        header = tk.Frame(sidebar, bg=self.colors["primary"], height=45)
        header.pack(fill="x", pady=(0, 15))
        header.pack_propagate(False)
        tk.Label(header, text="🔍 FILTERS", font=("Arial", 13, "bold"),
                bg=self.colors["primary"], fg="white").pack(expand=True)
        
        content = tk.Frame(sidebar, bg=self.colors["sidebar_bg"])
        content.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Create filter sections
        self.create_filter_section(content, "Airlines", self.airline_var,
                                 ["All", "Malaysia Airlines", "Singapore Airlines", "AirAsia", "Thai Airways", "Japan Airlines"])
        
        self.create_filter_section(content, "Stops", self.stops_var,
                                 [("All", "All"), ("Non-stop", "Non-stop"), 
                                  ("1 Stop", "1 Stop"), ("2+ Stops", "2+ Stops")])
        
        self.create_filter_section(content, "Departure Time", self.time_var,
                                 ["All", "Morning (6am-12pm)", "Afternoon (12pm-6pm)",
                                  "Evening (6pm-12am)", "Night (12am-6am)"])
        
        # Price range filter
        tk.Label(content, text="Price Range (RM)", font=("Arial", 12, "bold"),
                bg=self.colors["sidebar_bg"], fg=self.colors["primary"]).pack(anchor="w", pady=(10, 8))
        
        price_frame = tk.Frame(content, bg=self.colors["sidebar_bg"])
        price_frame.pack(fill="x", pady=(0, 15))
        
        self.price_label = tk.Label(price_frame, text=f"Max: RM {self.price_range_var.get()}",
                                   font=("Arial", 11, "bold"), bg=self.colors["sidebar_bg"], 
                                   fg=self.colors["secondary"])
        self.price_label.pack(anchor="w")
        
        tk.Scale(price_frame, from_=0, to=5000, variable=self.price_range_var,
                orient="horizontal", length=200, showvalue=False,
                bg=self.colors["sidebar_bg"], troughcolor=self.colors["light"],
                command=self.on_price_range_change).pack(fill="x", pady=5)
        
        # Reset filters button
        tk.Button(content, text="🔄 Reset All Filters", font=("Arial", 12),
                 bg=self.colors["primary"], fg="white", relief="flat",
                 cursor="hand2", command=self.reset_filters, height=2).pack(fill="x", pady=(20, 10))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_filter_section(self, parent, title, variable, options):
        """Create a filter section with radio buttons"""
        tk.Label(parent, text=title, font=("Arial", 12, "bold"),
                bg=self.colors["sidebar_bg"], fg=self.colors["primary"]).pack(anchor="w", pady=(10, 8))
        
        frame = tk.Frame(parent, bg=self.colors["sidebar_bg"])
        frame.pack(fill="x", pady=(0, 15))
        
        for option in options:
            if isinstance(option, tuple):
                text, value = option
            else:
                text = value = option
            
            tk.Radiobutton(frame, text=text, variable=variable, value=value,
                          font=("Arial", 11), bg=self.colors["sidebar_bg"],
                          fg=self.colors["dark"], selectcolor=self.colors["light"],
                          activebackground=self.colors["sidebar_bg"],
                          command=self.apply_filters).pack(anchor="w", pady=2)

    def create_main_content(self, parent):
        """Create main content area with tabs"""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill="both", expand=True)
        
        # Style the notebook
        style = ttk.Style()
        style.configure("TNotebook", background=self.colors["light"])
        style.configure("TNotebook.Tab", font=("Arial", 11, "bold"), padding=[15, 5])
        
        # Define tabs
        tabs = [
            ("✈️ All Flights", self.create_flights_grid),
            ("⭐ Recommended", lambda p: self.create_flight_section(p, "recommended_flights", "Top Recommendations")),
            ("💰 Budget", lambda p: self.create_flight_section(p, "budget", "Budget Flights", "category_flights")),
            ("💼 Business", lambda p: self.create_flight_section(p, "business", "Business Class", "category_flights")),
            ("⚡ Non-stop", lambda p: self.create_flight_section(p, "direct", "Non-stop Flights", "category_flights"))
        ]
        
        for tab_text, tab_func in tabs:
            frame = tk.Frame(notebook, bg=self.colors["light"])
            notebook.add(frame, text=tab_text)
            tab_func(frame)

    def create_flights_grid(self, parent):
        """Create flights grid with sorting options"""
        # Header with results and sort
        header = tk.Frame(parent, bg=self.colors["light"])
        header.pack(fill="x", pady=(0, 20))
        
        self.results_label = tk.Label(header, text="Search for flights...",
                                     font=("Arial", 14, "bold"), bg=self.colors["light"],
                                     fg=self.colors["primary"])
        self.results_label.pack(side="left")
        
        sort_frame = tk.Frame(header, bg=self.colors["light"])
        sort_frame.pack(side="right")
        
        tk.Label(sort_frame, text="Sort by:", font=("Arial", 12),
                bg=self.colors["light"], fg=self.colors["dark"]).pack(side="left", padx=(0, 10))
        
        self.sort_combo = ttk.Combobox(sort_frame, textvariable=self.sort_var,
                                      values=["Price (Low to High)", "Price (High to Low)",
                                              "Duration (Short to Long)", "Duration (Long to Short)"],
                                      state="readonly", font=("Arial", 11), width=20)
        self.sort_combo.pack(side="left")
        self.sort_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())
        
        # Scrollable flight list
        self.canvas = tk.Canvas(parent, bg=self.colors["light"], highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors["light"])
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.grid_frame = self.scrollable_frame
        self.show_recommended_flights()
        
        self.canvas.pack(side="left", fill="both", expand=True, padx=(0, 5))
        scrollbar.pack(side="right", fill="y")

    def create_flight_section(self, parent, data_key, title, parent_key="flight_data"):
        """Create a generic flight section"""
        container = tk.Frame(parent, bg=self.colors["light"])
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        tk.Label(container, text=title, font=("Arial", 20, "bold"),
                bg=self.colors["light"], fg=self.colors["primary"]).pack(anchor="w", pady=(0, 10))
        
        # Get flights data
        if parent_key == "flight_data":
            flights = self.flight_data.get(data_key, [])
        else:
            flights = self.flight_data.get(parent_key, {}).get(data_key, [])
        
        if not flights:
            tk.Label(container, text=f"No {title.lower()} available",
                    font=("Arial", 14), bg=self.colors["light"],
                    fg=self.colors["text_light"]).pack(pady=50)
            return
        
        # Create scrollable flight list
        canvas_frame = tk.Frame(container, bg=self.colors["light"])
        canvas_frame.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(canvas_frame, bg=self.colors["light"], highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        
        scrollable_frame = tk.Frame(canvas, bg=self.colors["light"])
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for flight in flights:
            card = self.create_flight_card(scrollable_frame, flight)
            card.pack(fill="x", pady=10)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(0, 5))
        scrollbar.pack(side="right", fill="y")

    def create_flight_card(self, parent, flight_data, is_promo=False):
        """Create a flight card for display"""
        card_bg = "#ffffff" if not is_promo else "#f8f9ff"
        card = tk.Frame(parent, bg=card_bg, relief="flat",
                       highlightbackground=self.colors["border"], highlightthickness=1,
                       padx=20, pady=20)
        
        # Top section
        top_frame = tk.Frame(card, bg=card_bg)
        top_frame.pack(fill="x", pady=(0, 15))
        
        # Airline info
        airline_frame = tk.Frame(top_frame, bg=card_bg)
        airline_frame.pack(side="left")
        
        # Get airline icon
        airline_icons = {
            "Malaysia": "🇲🇾", "Singapore": "🇸🇬", "AirAsia": "🔴",
            "Thai": "🇹🇭", "Japan": "🇯🇵", "Cathay": "🇭🇰"
        }
        icon = "✈️"
        for key in airline_icons:
            if key in flight_data['airline']:
                icon = airline_icons[key]
                break
        
        tk.Label(airline_frame, text=icon, font=("Arial", 16),
                bg=card_bg, fg=self.colors["primary"]).pack(side="left", padx=(0, 8))
        tk.Label(airline_frame, text=flight_data['airline'], font=("Arial", 14, "bold"),
                bg=card_bg, fg=self.colors["primary"]).pack(side="left")
        
        # Right side: Rating and deal badge
        right_frame = tk.Frame(top_frame, bg=card_bg)
        right_frame.pack(side="right")
        
        if flight_data.get('deal'):
            deal_colors = {
                "Best": "#e74c3c", "Popular": "#3498db", "Cheapest": "#27ae60",
                "Premium": "#9b59b6", "Morning": "#f39c12"
            }
            deal_color = "#e74c3c"
            for key in deal_colors:
                if key in flight_data['deal']:
                    deal_color = deal_colors[key]
                    break
            
            tk.Label(right_frame, text=flight_data['deal'], font=("Arial", 9, "bold"),
                    bg=deal_color, fg="white", padx=8, pady=3).pack(side="right", padx=(5, 0))
        
        rating_frame = tk.Frame(right_frame, bg=card_bg)
        rating_frame.pack(side="right")
        tk.Label(rating_frame, text="⭐", font=("Arial", 12), bg=card_bg).pack(side="left")
        tk.Label(rating_frame, text=flight_data['rating'], font=("Arial", 12, "bold"),
                bg=card_bg, fg=self.colors["secondary"]).pack(side="left", padx=2)
        
        # Route and times
        time_str = flight_data['time'].split(' - ')
        departure_time, arrival_time = time_str[0] if time_str else "08:00", time_str[1] if len(time_str) > 1 else "16:00"
        
        route_frame = tk.Frame(card, bg=card_bg)
        route_frame.pack(fill="x", pady=(0, 15))
        
        route_main = tk.Frame(route_frame, bg=card_bg)
        route_main.pack(fill="x", pady=(5, 0))
        
        # Departure
        self.create_time_display(route_main, departure_time, "Departure", side="left", padx=10)
        
        # Middle flight path
        middle_frame = tk.Frame(route_main, bg=card_bg)
        middle_frame.pack(side="left", fill="x", expand=True, padx=10)
        
        canvas = tk.Canvas(middle_frame, height=30, bg=card_bg, highlightthickness=0)
        canvas.pack(fill="x", pady=5)
        width = canvas.winfo_reqwidth() or 150
        canvas.create_line(0, 15, width, 15, fill=self.colors["border"], dash=(5, 3))
        canvas.create_text(width/2, 15, text="✈️", font=("Arial", 12))
        
        tk.Label(middle_frame, text=f"⏱️ {flight_data['duration']}", font=("Arial", 11),
                bg=card_bg, fg=self.colors["dark"]).pack()
        
        # Arrival
        self.create_time_display(route_main, arrival_time, "Arrival", side="left", padx=10)
        
        # Flight details (removed passenger info)
        details = [
            ("🛫", f"Stops: {flight_data['stops']}", 
             self.colors["success"] if "Non-stop" in flight_data['stops'] else self.colors["warning"]),
            ("✈️", f"Aircraft: {flight_data['aircraft']}", self.colors["text_light"]),
            ("🎫", f"Class: {self.class_var.get()}", self.colors["accent"]),
        ]
        
        info_frame = tk.Frame(card, bg=card_bg)
        info_frame.pack(fill="x", pady=(15, 20))
        
        for i, (icon, text, color) in enumerate(details):
            frame = tk.Frame(info_frame, bg=card_bg)
            frame.grid(row=i//2, column=i%2, padx=10, pady=5, sticky="w")
            tk.Label(frame, text=icon, font=("Arial", 12), bg=card_bg, fg=color).pack(side="left", padx=(0, 5))
            tk.Label(frame, text=text, font=("Arial", 11), bg=card_bg, fg=self.colors["dark"]).pack(side="left")
        
        # Bottom section: Price and button
        bottom_frame = tk.Frame(card, bg=card_bg)
        bottom_frame.pack(fill="x", pady=(10, 0))
        
        price_frame = tk.Frame(bottom_frame, bg=card_bg)
        price_frame.pack(side="left")
        
        # Original price if discounted
        if flight_data.get('original_price') and flight_data['price'] != flight_data['original_price']:
            original = flight_data['original_price'].replace('RM ', '').replace(',', '')
            current = flight_data['price'].replace('RM ', '').replace(',', '')
            try:
                discount = int((1 - float(current) / float(original)) * 100)
                
                original_frame = tk.Frame(price_frame, bg=card_bg)
                original_frame.pack(anchor="w", pady=(0, 2))
                
                tk.Label(original_frame, text=f"RM {original}", font=("Arial", 12),
                        bg=card_bg, fg=self.colors["text_light"]).pack(side="left")
                
                tk.Label(original_frame, text=f"-{discount}%", font=("Arial", 10, "bold"),
                        bg=self.colors["success"], fg="white", padx=5, pady=1).pack(side="left", padx=5)
            except:
                pass
        
        # Current price
        tk.Label(price_frame, text=flight_data['price'], font=("Arial", 24, "bold"),
                bg=card_bg, fg=self.colors["secondary"]).pack(anchor="w")
        
        # Price per person
        try:
            per_person = self.parse_price(flight_data['price']) / self.adult_count
            tk.Label(price_frame, text=f"≈ RM {per_person:.0f} per person", font=("Arial", 10),
                    bg=card_bg, fg=self.colors["text_light"]).pack(anchor="w", pady=(2, 0))
        except:
            pass
        
        # Action button
        button_frame = tk.Frame(bottom_frame, bg=card_bg)
        button_frame.pack(side="right")
        
        tk.Button(button_frame, text="View Details →", font=("Arial", 12, "bold"),
                 bg=self.colors["primary"], fg="white", relief="flat", cursor="hand2",
                 padx=25, pady=10, command=lambda f=flight_data: self.show_flight_details(f)).pack()
        
        return card

    def create_time_display(self, parent, time, label, side="left", padx=0):
        """Create time display widget"""
        frame = tk.Frame(parent, bg=parent.cget("bg"))
        frame.pack(side=side, padx=padx)
        
        tk.Label(frame, text=time, font=("Arial", 18, "bold"),
                bg=frame.cget("bg"), fg=self.colors["dark"]).pack()
        tk.Label(frame, text=label, font=("Arial", 10),
                bg=frame.cget("bg"), fg=self.colors["text_light"]).pack()

    # Passenger counter methods
    def increase_adult(self):
        if self.adult_count < 9:
            self.adult_count += 1
            self.adult_display.config(text=str(self.adult_count))

    def decrease_adult(self):
        if self.adult_count > 1:
            self.adult_count -= 1
            self.adult_display.config(text=str(self.adult_count))

    def increase_child(self):
        if self.child_count < 8:
            self.child_count += 1
            self.child_display.config(text=str(self.child_count))

    def decrease_child(self):
        if self.child_count > 0:
            self.child_count -= 1
            self.child_display.config(text=str(self.child_count))

    # Calendar methods
    def show_calendar(self, date_type):
        """Show calendar popup for date selection"""
        cal_window = tk.Toplevel(self.root)
        cal_window.title("Select Date")
        cal_window.geometry("300x320")
        cal_window.configure(bg='white')
        cal_window.transient(self.root)
        cal_window.grab_set()
        
        today = datetime.date.today()
        
        # Set minimum date
        if date_type == "departure":
            mindate = today
        elif self.departure_var.get():
            try:
                mindate = datetime.datetime.strptime(self.departure_var.get(), "%d-%m-%Y").date()
            except:
                mindate = today
        else:
            mindate = today
        
        # Create calendar
        cal = Calendar(cal_window, selectmode='day', mindate=mindate, date_pattern='dd-mm-yyyy')
        cal.pack(pady=20, padx=10)
        
        def set_date():
            selected_date = cal.get_date()
            if self.validate_date(date_type, selected_date):
                if date_type == "departure":
                    self.departure_var.set(selected_date)
                    if self.return_var.get():
                        try:
                            return_date = datetime.datetime.strptime(self.return_var.get(), "%d-%m-%Y").date()
                            departure_date = datetime.datetime.strptime(selected_date, "%d-%m-%Y").date()
                            if return_date <= departure_date:
                                self.return_var.set("")
                        except:
                            pass
                else:
                    self.return_var.set(selected_date)
                cal_window.destroy()
        
        # Buttons
        btn_frame = tk.Frame(cal_window, bg='white')
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Confirm", command=set_date, bg='#27ae60',
                 fg='white', font=('Arial', 12, 'bold'), relief='flat', padx=20).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Cancel", command=cal_window.destroy, bg='#95a5a6',
                 fg='white', font=('Arial', 12, 'bold'), relief='flat', padx=20).pack(side='left', padx=5)
        
        # Center window
        x = (self.root.winfo_screenwidth() // 2) - 150
        y = (self.root.winfo_screenheight() // 2) - 160
        cal_window.geometry(f"+{x}+{y}")

    def validate_date(self, date_type, selected_date_str):
        """Validate selected date"""
        try:
            selected_date = datetime.datetime.strptime(selected_date_str, "%d-%m-%Y").date()
            today = datetime.date.today()
            
            if selected_date < today:
                messagebox.showwarning("Invalid Date", "Cannot select past dates.")
                return False
            
            if date_type == "return" and self.departure_var.get():
                departure_date = datetime.datetime.strptime(self.departure_var.get(), "%d-%m-%Y").date()
                if selected_date <= departure_date:
                    messagebox.showwarning("Invalid Date", "Return date must be after departure date.")
                    return False
            
            return True
        except ValueError:
            messagebox.showerror("Date Error", "Invalid date format.")
            return False

    # Filter methods
    def on_price_range_change(self, value):
        self.price_label.config(text=f"Max: RM {int(float(value))}")
        self.apply_filters()

    def reset_filters(self):
        self.airline_var.set("All")
        self.stops_var.set("All")
        self.time_var.set("All")
        self.price_range_var.set(2000)
        self.sort_var.set("Price (Low to High)")
        self.price_label.config(text=f"Max: RM {self.price_range_var.get()}")
        self.apply_filters()

    def apply_filters(self):
        if not self.current_displayed_flights:
            return
        
        filtered_flights = []
        for flight in self.current_displayed_flights:
            # Airline filter
            if self.airline_var.get() != "All" and self.airline_var.get() not in flight['airline']:
                continue
            
            # Stops filter
            if self.stops_var.get() != "All" and self.stops_var.get() not in flight['stops']:
                continue
            
            # Price filter
            price = self.parse_price(flight['price'])
            if price > self.price_range_var.get():
                continue
            
            # Time filter
            if self.time_var.get() != "All":
                try:
                    time_str = flight['time'].split(' - ')[0]
                    hour = int(time_str.split(':')[0])
                    time_ranges = {
                        "Morning (6am-12pm)": (6, 12),
                        "Afternoon (12pm-6pm)": (12, 18),
                        "Evening (6pm-12am)": (18, 24),
                        "Night (12am-6am)": (0, 6)
                    }
                    if self.time_var.get() in time_ranges:
                        start, end = time_ranges[self.time_var.get()]
                        if not (start <= hour < end):
                            continue
                except:
                    pass
            
            filtered_flights.append(flight)
        
        # Sort filtered flights
        sort_by = self.sort_var.get()
        if sort_by.startswith("Price"):
            reverse = "High" in sort_by
            filtered_flights.sort(key=lambda x: self.parse_price(x['price']), reverse=reverse)
        elif sort_by.startswith("Duration"):
            reverse = "Long" in sort_by
            filtered_flights.sort(key=lambda x: self.parse_duration(x['duration']), reverse=reverse)
        
        self.display_flights(filtered_flights)

    def parse_duration(self, duration_str):
        """Parse duration string to minutes"""
        try:
            total = 0
            if 'h' in duration_str:
                hours = int(duration_str.split('h')[0].strip())
                total += hours * 60
            if 'm' in duration_str:
                minutes_part = duration_str.split('h')[1] if 'h' in duration_str else duration_str
                minutes = int(minutes_part.replace('m', '').strip())
                total += minutes
            return total
        except:
            return 0

    def display_flights(self, flights):
        if not hasattr(self, 'grid_frame'):
            return
            
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        
        if not flights:
            tk.Label(self.grid_frame, text="No flights found matching your criteria.",
                    font=("Arial", 14), bg=self.colors["light"], fg=self.colors["text_light"]).pack(pady=50)
            return
        
        if hasattr(self, 'results_label'):
            self.results_label.config(text=f"Found {len(flights)} flight(s)")
        
        for flight in flights:
            card = self.create_flight_card(self.grid_frame, flight)
            card.pack(fill="x", pady=10)

    def show_recommended_flights(self):
        all_flights = self.get_all_flights()
        self.current_displayed_flights = all_flights
        self.display_flights(all_flights)
        if hasattr(self, 'results_label'):
            self.results_label.config(text="All Available Flights")

    def navigate_to_page(self, script_file):
        """Navigate to other page - fixed version to ensure window closes"""
        if script_file == "flight.py":
            return
        
        try:
            # Save current user info to session
            session_data = {
                'email': self.email,
                'user_name': self.user_name
            }
            with open('user_session.json', 'w') as f:
                json.dump(session_data, f)
            
            # Immediately destroy all child widgets
            for widget in self.root.winfo_children():
                try:
                    widget.destroy()
                except:
                    pass
            
            # Force close main window
            self.root.quit()
            self.root.destroy()
            
            # Check if target file exists
            if not os.path.exists(script_file):
                # Create new Tkinter instance to show error
                error_root = tk.Tk()
                error_root.withdraw()
                messagebox.showerror("Error", f"File not found: {script_file}")
                error_root.destroy()
                # Restart flight app
                os.system(f"python flight.py")
                return
            
            # Use os.system to start new app (this runs in new process)
            python_executable = sys.executable
            
            # Use different commands based on OS
            if sys.platform == "win32":
                # Windows: use start command to launch in new window
                os.system(f'start "" "{python_executable}" "{script_file}"')
            elif sys.platform == "darwin":
                # macOS
                os.system(f'open -a Terminal "{python_executable}" "{script_file}"')
            else:
                # Linux/Unix
                os.system(f'"{python_executable}" "{script_file}" &')
            
            # Force exit current Python process
            sys.exit(0)
            
        except Exception as e:
            # If error occurs, create new error window
            try:
                error_root = tk.Tk()
                error_root.withdraw()
                messagebox.showerror("Error", f"Cannot open {script_file}: {str(e)}")
                error_root.destroy()
            except:
                pass

    def search_flights(self):
        """Validate and perform flight search"""
        # Validate inputs
        if self.going_var.get() == "Select destination":
            messagebox.showwarning("Input Error", "Please select destination city.")
            self.going_combobox.focus_set()
            return
        
        if not self.departure_var.get():
            messagebox.showwarning("Input Error", "Please select departure date.")
            return
        
        try:
            dep_date = datetime.datetime.strptime(self.departure_var.get(), "%d-%m-%Y").date()
            if dep_date < datetime.date.today():
                messagebox.showwarning("Invalid Date", "Departure date cannot be in the past.")
                return
        except:
            messagebox.showerror("Date Error", "Invalid departure date format.")
            return
        
        if self.flight_type_var.get() == "Return" and not self.return_var.get():
            messagebox.showwarning("Input Error", "Please select return date for return flights.")
            return
        
        total_passengers = self.adult_count + self.child_count
        if total_passengers == 0:
            messagebox.showwarning("Input Error", "Please select at least one passenger.")
            return
        
        if total_passengers > 9:
            messagebox.showwarning("Input Error", "Maximum 9 passengers allowed.")
            return
        
        # Perform search
        self.perform_search("Kuala Lumpur, Malaysia", self.going_var.get())

    def perform_search(self, leaving, going):
        going_city = going.split(',')[0].strip().lower()
        
        # Search for flights to selected city
        filtered_flights = []
        for city, flights in self.flight_data["destination_flights"].items():
            if city.lower() == going_city:
                filtered_flights.extend(flights)
                break
        
        # If not found, search in routes
        if not filtered_flights:
            for flight in self.get_all_flights():
                if going_city in flight['route'].lower():
                    filtered_flights.append(flight)
        
        # If still not found, show all flights
        if not filtered_flights:
            messagebox.showinfo("Search Results", f"No flights found for {going}. Showing all flights.")
            filtered_flights = self.get_all_flights()
        
        self.current_displayed_flights = filtered_flights
        self.display_flights(filtered_flights)
        
        if hasattr(self, 'results_label'):
            self.results_label.config(text=f"Found {len(filtered_flights)} flight(s) to {going}")

    def show_flight_details(self, flight_data):
        """Open flight detail module"""
        self.selected_flight_data = flight_data
        
        # Prepare flight info
        departure_date = self.departure_var.get() or datetime.date.today().strftime("%d-%m-%Y")
        return_date = self.return_var.get() if self.flight_type_var.get() == "Return" else ""
        
        time_parts = flight_data['time'].split(' - ')
        departure_time = time_parts[0] if time_parts else "08:00"
        arrival_time = time_parts[1] if len(time_parts) > 1 else "16:00"
        
        flight_info = {
            "airline": flight_data['airline'],
            "route": flight_data['route'],
            "departure_date": departure_date,
            "departure_time": departure_time,
            "arrival_time": arrival_time,
            "return_date": return_date,
            "duration": flight_data['duration'],
            "stops": flight_data['stops'],
            "aircraft": flight_data['aircraft'],
            "rating": flight_data['rating'],
            "price": flight_data['price'],
            "flight_type": self.flight_type_var.get(),
            "class": self.class_var.get(),
            "tickets": {"adults": self.adult_count, "children": self.child_count},
            "from_city": self.leaving_var.get(),
            "to_city": self.going_var.get() if self.going_var.get() != "Select destination" else "Any Destination"
        }
        
        # Open detail window
        try:
            detail_window = tk.Toplevel(self.root)
            detail_window.title(f"Flight Details - {flight_data['airline']}")
            detail_window.geometry("1200x800")
            detail_window.configure(bg=self.colors["light"])
            
            # Center window
            x = (self.root.winfo_screenwidth() // 2) - 600
            y = (self.root.winfo_screenheight() // 2) - 400
            detail_window.geometry(f"+{x}+{y}")
            
            # Create detail page
            detail_page = FlightDetailPage(
                detail_window, flight_info, self.adult_count, self.child_count,
                self.departure_var, self.return_var, self.flight_type_var,
                self.class_var, self.going_var, self.colors, self.email,
                self.profile_system, lambda: self.close_detail_window(detail_window),
                self.open_booking_detail_window
            )
            
            detail_window.transient(self.root)
            detail_window.grab_set()
            
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open flight details: {str(e)}")

    def close_detail_window(self, window):
        window.destroy()
        window.grab_release()

    def restore_main_page(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.current_page = "main"
        self.create_header()
        
        # Reinitialize profile system
        self.profile_system = Profile(self.root, self.profile_btn, use_custom_menu=True)
        
        self.main_container = tk.Frame(self.root, bg=self.colors["light"])
        self.main_container.pack(fill="both", expand=True)
        self.show_flights_page()
        self.bind_mousewheel_to_all()

    def open_booking_detail_window(self, booking_data):
        """Open booking detail window"""
        try:
            self.save_booking_to_file(booking_data)
            booking_window = tk.Toplevel(self.root)
            booking_window.title("Flight Booking Confirmation")
            booking_window.geometry("900x700")
            
            # Get user info
            user_email = self.email
            user_name = self.user_name
            if self.profile_system:
                profile_data = self.profile_system.profile_data
                user_email = profile_data["personal_info"]["email"] or user_email
                user_name = profile_data["personal_info"]["full_name"] or user_name
            
            booking_data['email'] = user_email
            booking_data['customer_name'] = user_name
            
            BookingDetailApp(booking_window, booking_data, user_email, "flight")
            booking_window.protocol("WM_DELETE_WINDOW", lambda: booking_window.destroy())
            
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open booking details: {str(e)}")

    def save_booking_to_file(self, booking_data):
        """Save booking to JSON file"""
        try:
            bookings_file = "bookings.json"
            bookings = []
            
            if os.path.exists(bookings_file):
                with open(bookings_file, 'r', encoding='utf-8') as f:
                    bookings = json.load(f)
            
            flight_booking = {
                "id": booking_data.get("booking_id", f"FL{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"),
                "booking_type": "flight",
                "item_name": booking_data.get("item_name", f"{booking_data['airline']} - {booking_data['route']}"),
                "airline": booking_data["airline"],
                "route": booking_data["route"],
                "departure_date": booking_data["departure_date"],
                "departure_time": booking_data["departure_time"],
                "arrival_time": booking_data["arrival_time"],
                "tickets": booking_data["tickets"],
                "class": booking_data["class"],
                "seats": booking_data.get("seats", []),
                "status": "Confirmed",
                "price": self.parse_price(booking_data["total_price"]),
                "booking_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "email": booking_data.get("email", ""),
                "user_name": booking_data.get("customer_name", "")
            }
            
            bookings.append(flight_booking)
            
            with open(bookings_file, 'w', encoding='utf-8') as f:
                json.dump(bookings, f, indent=2, ensure_ascii=False)
            
            return True
        except:
            return False

    def create_footer(self, parent):
        footer = tk.Frame(parent, bg=self.colors["footer_bg"], height=40)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        tk.Label(footer, text="© 2024 Traney Travel Services. All rights reserved.",
                font=("Arial", 9), bg=self.colors["footer_bg"], fg="white").pack(side="left", padx=15)

    def bind_mousewheel_to_all(self):
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)
        
    def _on_mousewheel(self, event):
        widget = event.widget
        while widget and not isinstance(widget, tk.Canvas):
            widget = widget.master
        
        if widget and isinstance(widget, tk.Canvas):
            widget.yview_scroll(int(-1*(event.delta/120)), "units")
        
        return "break"


if __name__ == "__main__":
    session_file = 'user_session.json'
    user_email = "user@example.com"
    if os.path.exists(session_file):
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
                user_email = session_data.get('email', "user@example.com")
        except:
            pass
    
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    app = Flight(root, user_email)
    root.mainloop()