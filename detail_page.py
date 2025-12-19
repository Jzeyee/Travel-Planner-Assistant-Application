import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
from PIL import Image, ImageTk, ImageDraw
import subprocess
from datetime import datetime, timedelta
import time
import calendar as cal

class DetailPage:
    def __init__(self, root, item_data, user_email=None, return_to_home=True):
        self.root = root
        self.item_data = self.validate_item_data(item_data)
        self.user_email = user_email or "guest@example.com"
        self.return_to_home = return_to_home
        
        # Set fullscreen
        self.root.title(f"Traney - {self.item_data['name']}")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg="#f0f8ff")
        
        try:
            self.root.iconbitmap('car_icon.ico')
        except:
            pass
        
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
            "nav_bg": "#1e3d59",
            "border": "#e2e8f0",
            "footer_bg": "#1e3d59",
            "calendar_bg": "#ffffff",
            "calendar_header": "#1e3d59",
            "calendar_today": "#ff6e40",
            "calendar_selected": "#1e3d59",
            "calendar_hover": "#e2e8f0",
            "calendar_weekend": "#ef4444",
            "calendar_past": "#94a3b8",
            "electric": "#48bb78",
        }
        
        # Image cache
        self.image_cache = {}
        
        # Initialize price label
        self.price_label = None
        
        # Create UI
        self.setup_ui()
        
        # Bind ESC key for fullscreen toggle
        self.root.bind("<Escape>", self.toggle_fullscreen)
    
    def validate_item_data(self, item_data):
        """Validate and repair item data"""
        defaults = {
            'id': 'UNKNOWN001',
            'name': 'Unknown Item',
            'location': 'Location not specified',
            'price': 0,
            'discount_price': None,
            'currency': 'RM',
            'rating': 0,
            'reviews': 0,
            'image_file': '',
            'description': 'No description available.',
            'category': 'general',
            'highlights': ['Quality service', 'Great value'],
            'facilities': ['Standard amenities'],
            'tags': [],
        }
        
        validated_data = defaults.copy()
        validated_data.update(item_data)
        
        # Add defaults for flights
        if validated_data['category'] == 'flight':
            validated_data.setdefault('airline', 'Unknown Airline')
            validated_data.setdefault('flight_no', 'N/A')
            validated_data.setdefault('departure', 'Not specified')
            validated_data.setdefault('arrival', 'Not specified')
            validated_data.setdefault('duration', 'N/A')
            validated_data.setdefault('departure_airport', 'N/A')
            validated_data.setdefault('arrival_airport', 'N/A')
            validated_data.setdefault('cabin_class', 'Economy')
            validated_data.setdefault('baggage_allowance', '20kg')
        
        return validated_data
    
    def setup_ui(self):
        """Set up UI components"""
        self.create_header()
        self.create_main_scrollable_container()
        self.create_detail_content()
        self.create_footer()
    
    def create_header(self):
        """Create header"""
        header = tk.Frame(self.root, bg=self.colors["nav_bg"], height=70)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        
        container = tk.Frame(header, bg=self.colors["nav_bg"])
        container.pack(fill="both", expand=True, padx=30)
        
        # Back button
        back_btn = tk.Button(container, text="← Back to Home",
                           font=("Segoe UI", 12, "bold"),
                           bg=self.colors["nav_bg"], fg="white",
                           relief="flat", cursor="hand2",
                           command=self.go_back)
        back_btn.pack(side="left")
        self.add_hover_effect(back_btn, "#2a4d6e", self.colors["nav_bg"])
        
        # Title
        title_label = tk.Label(container, 
                             text=self.item_data["name"][:40] + ("..." if len(self.item_data["name"]) > 40 else ""),
                             font=("Segoe UI", 16, "bold"),
                             bg=self.colors["nav_bg"], fg="white")
        title_label.pack(side="left", padx=20, expand=True)
        
        # Fullscreen toggle button
        fs_btn = tk.Button(container, text="⛶", font=("Segoe UI", 18),
                         bg=self.colors["nav_bg"], fg="white",
                         relief="flat", cursor="hand2",
                         command=self.toggle_fullscreen)
        fs_btn.pack(side="right", padx=(10, 0))
        self.add_hover_effect(fs_btn, "#2a4d6e", self.colors["nav_bg"])
    
    def create_main_scrollable_container(self):
        """Create main container with scrollbar"""
        self.main_container = tk.Frame(self.root, bg=self.colors["light"])
        self.main_container.pack(fill="both", expand=True, side="top")
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self.main_container, bg=self.colors["light"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=self.canvas.yview)
        
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create frame inside canvas
        self.content_frame = tk.Frame(self.canvas, bg=self.colors["light"])
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        
        # Bind scroll events
        self.content_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
    
    def create_detail_content(self):
        """Create detail content"""
        main_content = tk.Frame(self.content_frame, bg=self.colors["light"])
        main_content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Hero image area
        self.create_hero_image(main_content)
        
        # Details section
        self.create_details_section(main_content)
        
        # Booking section
        self.create_booking_section(main_content)
    
    def create_hero_image(self, parent):
        """Create hero image area"""
        hero_frame = tk.Frame(parent, bg="white", height=400)
        hero_frame.pack(fill="x", pady=(0, 20))
        hero_frame.pack_propagate(False)
        
        # Load and display image
        try:
            photo = self.load_image(self.item_data.get("image_file", ""), size=(1200, 400))
            image_label = tk.Label(hero_frame, image=photo, bg="white")
            image_label.image = photo
            image_label.pack(fill="both", expand=True)
        except:
            fallback_frame = tk.Frame(hero_frame, bg=self.item_data.get('color', '#1e3d59'))
            fallback_frame.pack(fill="both", expand=True)
            icon = "🏨" if self.item_data['category'] == 'hotel' else \
                   "✈️" if self.item_data['category'] == 'flight' else \
                   "🚗" if self.item_data['category'] == 'car' else "🏛️"
            tk.Label(fallback_frame, text=icon, font=("Arial", 64),
                    bg=self.item_data.get('color', '#1e3d59'), fg="white").pack(expand=True)
        
        # Overlay for information
        overlay = tk.Frame(hero_frame, bg="#333333", height=80)
        overlay.place(relx=0, rely=1, y=-80, relwidth=1)
        
        # Price
        price = self.item_data.get("price", 0)
        discount_price = self.item_data.get("discount_price")
        final_price = discount_price if discount_price else price
        
        price_text = f"FREE" if final_price == 0 else f"RM {final_price}"
        price_bg = self.colors["success"] if final_price == 0 else self.colors["secondary"]
        tk.Label(overlay, text=price_text, 
                font=("Segoe UI", 14, "bold"),
                bg=price_bg, fg="white",
                padx=15, pady=5).place(relx=0.05, rely=0.5, anchor="w")
        
        # Name
        tk.Label(overlay, text=self.item_data["name"], 
                font=("Segoe UI", 20, "bold"),
                bg="#333333", fg="white").place(relx=0.5, rely=0.5, anchor="center")
        
        # Location/Airline
        category = self.item_data.get('category', 'general')
        if category == 'flight':
            location_text = f"✈️ {self.item_data.get('airline', 'Airline')}"
        else:
            location_text = f"📍 {self.item_data.get('location', 'N/A')}"
        tk.Label(overlay, text=location_text,
                font=("Segoe UI", 12),
                bg="#333333", fg="#ff8c66").place(relx=0.95, rely=0.5, anchor="e")
    
    def create_details_section(self, parent):
        """Create details section"""
        details_container = tk.Frame(parent, bg="white")
        details_container.pack(fill="x", pady=(0, 20))
        
        content = tk.Frame(details_container, bg="white", padx=30, pady=30)
        content.pack(fill="both", expand=True)
        
        # Location and rating
        info_row = tk.Frame(content, bg="white")
        info_row.pack(fill="x", pady=(0, 20))
        
        category = self.item_data.get('category', 'general')
        if category == 'flight':
            # Display flight information
            flight_info = f"✈️ {self.item_data.get('airline', 'Airline')} | Flight {self.item_data.get('flight_no', 'N/A')}"
            tk.Label(info_row, text=flight_info, 
                    font=("Segoe UI", 14),
                    bg="white", fg="#64748b").pack(side="left")
        else:
            tk.Label(info_row, text=f"📍 {self.item_data.get('location', 'N/A')}", 
                    font=("Segoe UI", 14),
                    bg="white", fg="#64748b").pack(side="left")
        
        # Rating
        rating = self.item_data.get("rating", 0)
        if rating > 0:
            rating_frame = tk.Frame(info_row, bg="white")
            rating_frame.pack(side="right")
            
            stars_frame = tk.Frame(rating_frame, bg="white")
            stars_frame.pack(side="left")
            
            for i in range(5):
                star = "★" if i < int(rating) else "☆"
                color = "#ff6e40" if i < int(rating) else "#e2e8f0"
                tk.Label(stars_frame, text=star, font=("Segoe UI", 16),
                        bg="white", fg=color).pack(side="left")
            
            reviews = self.item_data.get("reviews", 0)
            tk.Label(rating_frame, text=f" {rating:.1f} ({reviews:,} reviews)",
                    font=("Segoe UI", 14),
                    bg="white", fg=self.colors["dark"]).pack(side="left", padx=(10, 0))
        
        # Description
        tk.Label(content, text="Description", 
                font=("Segoe UI", 18, "bold"),
                bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(0, 10))
        
        tk.Label(content, text=self.item_data.get("description", "No description available."), 
                font=("Segoe UI", 14),
                bg="white", fg=self.colors["dark"],
                wraplength=1100, justify="left").pack(anchor="w", pady=(0, 20))
        
        # Flight details (if flight)
        if category == 'flight':
            self.create_flight_details(content)
        
        # Highlights
        highlights = self.item_data.get("highlights", [])
        if highlights:
            tk.Label(content, text="Highlights" if category != 'flight' else "Flight Features", 
                    font=("Segoe UI", 18, "bold"),
                    bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(0, 10))
            
            for highlight in highlights[:5]:
                highlight_frame = tk.Frame(content, bg="white")
                highlight_frame.pack(fill="x", pady=5)
                tk.Label(highlight_frame, text="✓", 
                        font=("Segoe UI", 14),
                        bg="white", fg=self.colors["success"]).pack(side="left", padx=(0, 10))
                tk.Label(highlight_frame, text=highlight, 
                        font=("Segoe UI", 14),
                        bg="white", fg=self.colors["dark"]).pack(side="left")
    
    def create_flight_details(self, parent):
        """Create flight details"""
        details_frame = tk.Frame(parent, bg="white")
        details_frame.pack(fill="x", pady=(0, 20))
        
        # Flight itinerary
        tk.Label(details_frame, text="Flight Itinerary", 
                font=("Segoe UI", 16, "bold"),
                bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(0, 10))
        
        # Itinerary card
        itinerary_frame = tk.Frame(details_frame, bg=self.colors["light"], padx=20, pady=15)
        itinerary_frame.pack(fill="x", pady=(0, 10))
        
        # Departure
        departure_frame = tk.Frame(itinerary_frame, bg=self.colors["light"])
        departure_frame.pack(side="left", expand=True)
        
        tk.Label(departure_frame, text="🛫 Departure", 
                font=("Segoe UI", 12, "bold"),
                bg=self.colors["light"], fg=self.colors["primary"]).pack()
        tk.Label(departure_frame, text=self.item_data.get('departure', 'N/A'), 
                font=("Segoe UI", 14),
                bg=self.colors["light"], fg=self.colors["dark"]).pack(pady=(5, 0))
        tk.Label(departure_frame, text=f"From: {self.item_data.get('departure_airport', 'Airport')}", 
                font=("Segoe UI", 11),
                bg=self.colors["light"], fg="#64748b").pack()
        
        # Arrow
        arrow_frame = tk.Frame(itinerary_frame, bg=self.colors["light"])
        arrow_frame.pack(side="left", padx=20)
        tk.Label(arrow_frame, text="➜", 
                font=("Segoe UI", 20),
                bg=self.colors["light"], fg=self.colors["secondary"]).pack()
        
        # Arrival
        arrival_frame = tk.Frame(itinerary_frame, bg=self.colors["light"])
        arrival_frame.pack(side="left", expand=True)
        
        tk.Label(arrival_frame, text="🛬 Arrival", 
                font=("Segoe UI", 12, "bold"),
                bg=self.colors["light"], fg=self.colors["primary"]).pack()
        tk.Label(arrival_frame, text=self.item_data.get('arrival', 'N/A'), 
                font=("Segoe UI", 14),
                bg=self.colors["light"], fg=self.colors["dark"]).pack(pady=(5, 0))
        tk.Label(arrival_frame, text=f"To: {self.item_data.get('arrival_airport', 'Airport')}", 
                font=("Segoe UI", 11),
                bg=self.colors["light"], fg="#64748b").pack()
        
        # Flight information
        info_frame = tk.Frame(details_frame, bg="white")
        info_frame.pack(fill="x", pady=(10, 0))
        
        info_grid = tk.Frame(info_frame, bg="white")
        info_grid.pack()
        
        flight_info = [
            ("⏱️ Duration", self.item_data.get('duration', 'N/A')),
            ("💺 Cabin Class", self.item_data.get('cabin_class', 'Economy')),
            ("🧳 Baggage Allowance", self.item_data.get('baggage_allowance', '20kg'))
        ]
        
        for i, (label, value) in enumerate(flight_info):
            info_card = tk.Frame(info_grid, bg=self.colors["light"], padx=15, pady=10,
                               relief="flat", highlightbackground=self.colors["border"],
                               highlightthickness=1)
            info_card.grid(row=0, column=i, padx=5, sticky="nsew")
            
            tk.Label(info_card, text=label, 
                    font=("Segoe UI", 11),
                    bg=self.colors["light"], fg=self.colors["primary"]).pack(anchor="w")
            tk.Label(info_card, text=value, 
                    font=("Segoe UI", 12, "bold"),
                    bg=self.colors["light"], fg=self.colors["dark"]).pack(anchor="w", pady=(5, 0))
    
    def create_booking_section(self, parent):
        """Create booking section"""
        booking_container = tk.Frame(parent, bg="white", padx=30, pady=30)
        booking_container.pack(fill="x", pady=(0, 20))
        
        tk.Label(booking_container, text="Book Now", 
                font=("Segoe UI", 24, "bold"),
                bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(0, 20))
        
        # Booking form
        form_frame = tk.Frame(booking_container, bg="white")
        form_frame.pack(fill="x")
        
        # Date selection (including flights)
        category = self.item_data.get('category', 'general')
        if category in ['hotel', 'car', 'attraction', 'flight']:
            self.create_date_selection(form_frame, category)
        
        # Quantity selection
        self.create_quantity_selection(form_frame, category)
        
        # Price display
        self.create_price_display(form_frame)
        
        # Action buttons
        self.create_action_buttons(form_frame)
    
    def create_date_selection(self, parent, category):
        """Create date selection"""
        date_frame = tk.Frame(parent, bg="white")
        date_frame.pack(fill="x", pady=(0, 20))
        
        today = datetime.now()
        
        if category == 'hotel':
            # Hotel date selection
            tk.Label(date_frame, text="📅 Dates", 
                    font=("Segoe UI", 14, "bold"),
                    bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(0, 10))
            
            dates_row = tk.Frame(date_frame, bg="white")
            dates_row.pack(fill="x")
            
            # Check-in date
            checkin_frame = tk.Frame(dates_row, bg="white")
            checkin_frame.pack(side="left", padx=(0, 20))
            
            tk.Label(checkin_frame, text="Check-in:", 
                    font=("Segoe UI", 12, "bold"),
                    bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(0, 5))
            
            self.date_var = tk.StringVar(value=today.strftime("%Y-%m-%d"))
            checkin_entry = tk.Entry(checkin_frame, textvariable=self.date_var,
                                    font=("Segoe UI", 12), width=15, state="readonly",
                                    bg=self.colors["light"], relief="solid", borderwidth=1)
            checkin_entry.pack(side="left", padx=(0, 10))
            
            tk.Button(checkin_frame, text="📅",
                    font=("Segoe UI", 12),
                    bg=self.colors["light"], fg=self.colors["primary"],
                    relief="solid", cursor="hand2",
                    command=lambda: self.open_modern_calendar_popup("checkin")).pack(side="left")
            self.add_hover_effect(tk.Button(), "#e2e8f0", self.colors["light"])
            
            # Check-out date
            checkout_frame = tk.Frame(dates_row, bg="white")
            checkout_frame.pack(side="left", padx=(20, 0))
            
            tk.Label(checkout_frame, text="Check-out:", 
                    font=("Segoe UI", 12, "bold"),
                    bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(0, 5))
            
            checkout_date = today + timedelta(days=2)
            self.checkout_var = tk.StringVar(value=checkout_date.strftime("%Y-%m-%d"))
            checkout_entry = tk.Entry(checkout_frame, textvariable=self.checkout_var,
                                     font=("Segoe UI", 12), width=15, state="readonly",
                                     bg=self.colors["light"], relief="solid", borderwidth=1)
            checkout_entry.pack(side="left", padx=(0, 10))
            
            tk.Button(checkout_frame, text="📅",
                    font=("Segoe UI", 12),
                    bg=self.colors["light"], fg=self.colors["primary"],
                    relief="solid", cursor="hand2",
                    command=lambda: self.open_modern_calendar_popup("checkout")).pack(side="left")
            self.add_hover_effect(tk.Button(), "#e2e8f0", self.colors["light"])
            
        else:
            # Single date selection (flights, cars, attractions)
            date_label = "📅 Flight Date" if category == 'flight' else \
                        "📅 Pickup Date" if category == 'car' else \
                        "📅 Visit Date" if category == 'attraction' else \
                        "📅 Date"
            
            tk.Label(date_frame, text=date_label, 
                    font=("Segoe UI", 14, "bold"),
                    bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(0, 10))
            
            date_row = tk.Frame(date_frame, bg="white")
            date_row.pack(fill="x")
            
            self.date_var = tk.StringVar(value=today.strftime("%Y-%m-%d"))
            date_entry = tk.Entry(date_row, textvariable=self.date_var,
                                 font=("Segoe UI", 12), width=15, state="readonly",
                                 bg=self.colors["light"], relief="solid", borderwidth=1)
            date_entry.pack(side="left", padx=(0, 10))
            
            cal_btn = tk.Button(date_row, text="📅 Select Date",
                    font=("Segoe UI", 12),
                    bg=self.colors["light"], fg=self.colors["primary"],
                    relief="solid", cursor="hand2",
                    command=lambda: self.open_modern_calendar_popup("single"))
            cal_btn.pack(side="left")
            self.add_hover_effect(cal_btn, "#e2e8f0", self.colors["light"])
    
    def create_quantity_selection(self, parent, category):
        """Create quantity selection"""
        quantity_frame = tk.Frame(parent, bg="white")
        quantity_frame.pack(fill="x", pady=(0, 20))
        
        quantity_label = "👥 Guests" if category == 'hotel' else \
                        "👥 Passengers" if category == 'flight' else \
                        "🚗 Cars" if category == 'car' else \
                        "👥 Tickets"
        
        tk.Label(quantity_frame, text=quantity_label, 
                font=("Segoe UI", 14, "bold"),
                bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(0, 10))
        
        counter_frame = tk.Frame(quantity_frame, bg="white")
        counter_frame.pack()
        
        self.quantity_var = tk.IntVar(value=1)
        
        # Decrease button
        tk.Button(counter_frame, text="−", font=("Segoe UI", 16),
                 bg=self.colors["light"], fg=self.colors["primary"],
                 relief="solid", width=3, cursor="hand2",
                 command=lambda: self.quantity_var.set(max(1, self.quantity_var.get() - 1))).pack(side="left", padx=(0, 10))
        
        # Quantity display
        tk.Label(counter_frame, textvariable=self.quantity_var,
                font=("Segoe UI", 18, "bold"),
                bg="white", fg=self.colors["primary"],
                width=6).pack(side="left")
        
        # Increase button
        tk.Button(counter_frame, text="+", font=("Segoe UI", 16),
                 bg=self.colors["light"], fg=self.colors["primary"],
                 relief="solid", width=3, cursor="hand2",
                 command=lambda: self.quantity_var.set(self.quantity_var.get() + 1)).pack(side="left", padx=(10, 0))
    
    def create_price_display(self, parent):
        """Create price display"""
        price_frame = tk.Frame(parent, bg=self.colors["light"], padx=20, pady=20)
        price_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(price_frame, text="Total Amount:",
                font=("Segoe UI", 16),
                bg=self.colors["light"], fg=self.colors["primary"]).pack(side="left")
        
        # Calculate initial price
        base_price = self.item_data.get('price', 0)
        discount_price = self.item_data.get('discount_price')
        final_price = discount_price if discount_price else base_price
        
        # Calculate total price
        initial_total = final_price
        
        self.price_label = tk.Label(price_frame,
                                   text=f"RM {initial_total}" if final_price > 0 else "FREE",
                                   font=("Segoe UI", 24, "bold"),
                                   bg=self.colors["light"],
                                   fg=self.colors["secondary"])
        self.price_label.pack(side="right")
        
        # Bind price updates
        self.quantity_var.trace("w", lambda *args: self.update_price())
        if hasattr(self, 'date_var'):
            self.date_var.trace("w", lambda *args: self.update_price())
        if hasattr(self, 'checkout_var'):
            self.checkout_var.trace("w", lambda *args: self.update_price())
    
    def create_action_buttons(self, parent):
        """Create action buttons"""
        action_frame = tk.Frame(parent, bg="white")
        action_frame.pack(fill="x", pady=(20, 0))
        
        # Back button
        tk.Button(action_frame, text="← Back to Home",
                 font=("Segoe UI", 12),
                 bg=self.colors["light"], fg=self.colors["primary"],
                 relief="solid", cursor="hand2",
                 command=self.go_back,
                 padx=30, pady=10).pack(side="left", padx=(0, 20))
        
        # Book Now button
        tk.Button(action_frame, text="📅 Book Now",
                 font=("Segoe UI", 14, "bold"),
                 bg=self.colors["primary"], fg="white",
                 relief="solid", cursor="hand2",
                 command=self.open_booking_detail,
                 padx=40, pady=10).pack(side="right")
    
    def open_modern_calendar_popup(self, date_type):
        """Open modern style calendar popup"""
        popup = tk.Toplevel(self.root)
        popup.title("Select Date")
        popup.geometry("450x500")
        popup.configure(bg=self.colors["calendar_bg"])
        popup.resizable(False, False)
        
        # Make window modal
        popup.transient(self.root)
        popup.grab_set()
        
        # Set window rounded corners (via overlay)
        popup.overrideredirect(False)
        
        # Center window
        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f'{width}x{height}+{x}+{y}')
        
        # Title
        title = "Select Check-in Date" if date_type == "checkin" else \
                "Select Check-out Date" if date_type == "checkout" else \
                "Select Flight Date" if self.item_data.get('category') == 'flight' else \
                "Select Date"
        
        # Title bar
        title_frame = tk.Frame(popup, bg=self.colors["calendar_header"], height=60)
        title_frame.pack(fill="x", side="top")
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text=title, 
                font=("Segoe UI", 16, "bold"),
                bg=self.colors["calendar_header"], fg="white")
        title_label.pack(expand=True, fill="both")
        
        # Close button
        close_btn = tk.Label(title_frame, text="×", 
                font=("Segoe UI", 24),
                bg=self.colors["calendar_header"], fg="white",
                cursor="hand2")
        close_btn.pack(side="right", padx=20)
        close_btn.bind("<Button-1>", lambda e: popup.destroy())
        close_btn.bind("<Enter>", lambda e: close_btn.config(fg="#ff8c66"))
        close_btn.bind("<Leave>", lambda e: close_btn.config(fg="white"))
        
        # Main content area
        content_frame = tk.Frame(popup, bg=self.colors["calendar_bg"], padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)
        
        # Create modern calendar
        self.create_modern_calendar(content_frame, date_type, popup)
    
    def create_modern_calendar(self, parent, date_type, popup):
        """Create modern style calendar"""
        # Get current date
        today = datetime.now().date()
        
        if date_type == "checkin" and hasattr(self, 'date_var'):
            current_date = datetime.strptime(self.date_var.get(), "%Y-%m-%d").date()
        elif date_type == "checkout" and hasattr(self, 'checkout_var'):
            current_date = datetime.strptime(self.checkout_var.get(), "%Y-%m-%d").date()
        else:
            current_date = today
        
        self.cal_year = current_date.year
        self.cal_month = current_date.month
        self.date_type = date_type
        self.cal_popup = popup
        
        # Calendar container
        cal_container = tk.Frame(parent, bg=self.colors["calendar_bg"])
        cal_container.pack(fill="both", expand=True)
        
        # Navigation bar
        nav_frame = tk.Frame(cal_container, bg=self.colors["calendar_bg"])
        nav_frame.pack(fill="x", pady=(0, 15))
        
        # Previous month button
        prev_btn = tk.Button(nav_frame, text="◀", 
                           font=("Segoe UI", 14),
                           bg=self.colors["calendar_bg"], fg=self.colors["primary"],
                           relief="flat", cursor="hand2",
                           command=self.prev_month)
        prev_btn.pack(side="left")
        self.add_hover_effect(prev_btn, self.colors["calendar_hover"], self.colors["calendar_bg"])
        
        # Month year display
        self.month_year_var = tk.StringVar(value=f"{cal.month_name[self.cal_month]} {self.cal_year}")
        month_label = tk.Label(nav_frame, textvariable=self.month_year_var,
                              font=("Segoe UI", 16, "bold"),
                              bg=self.colors["calendar_bg"], fg=self.colors["primary"])
        month_label.pack(side="left", expand=True)
        
        # Next month button
        next_btn = tk.Button(nav_frame, text="▶", 
                           font=("Segoe UI", 14),
                           bg=self.colors["calendar_bg"], fg=self.colors["primary"],
                           relief="flat", cursor="hand2",
                           command=self.next_month)
        next_btn.pack(side="right")
        self.add_hover_effect(next_btn, self.colors["calendar_hover"], self.colors["calendar_bg"])
        
        # Weekday headers
        days_header = tk.Frame(cal_container, bg=self.colors["calendar_bg"])
        days_header.pack(fill="x")
        
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(weekdays):
            day_color = self.colors["calendar_weekend"] if i >= 5 else self.colors["primary"]
            day_label = tk.Label(days_header, text=day, 
                    font=("Segoe UI", 11, "bold"),
                    bg=self.colors["calendar_bg"], fg=day_color,
                    width=8, height=2)
            day_label.grid(row=0, column=i, padx=1, pady=1)
        
        # Date grid container
        self.days_frame = tk.Frame(cal_container, bg=self.colors["calendar_bg"])
        self.days_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        # Populate dates
        self.fill_modern_calendar_dates()
        
        # Action button area
        action_frame = tk.Frame(parent, bg=self.colors["calendar_bg"])
        action_frame.pack(fill="x", pady=(20, 0))
        
        # Today button
        today_btn = tk.Button(action_frame, text="Today",
                            font=("Segoe UI", 12),
                            bg=self.colors["light"], fg=self.colors["primary"],
                            relief="solid", padx=20, pady=8,
                            cursor="hand2",
                            command=lambda: self.select_today(date_type, popup))
        today_btn.pack(side="left", padx=(0, 10))
        self.add_hover_effect(today_btn, self.colors["calendar_hover"], self.colors["light"])
        
        # Confirm button
        confirm_btn = tk.Button(action_frame, text="Select",
                              font=("Segoe UI", 12, "bold"),
                              bg=self.colors["primary"], fg="white",
                              relief="solid", padx=30, pady=8,
                              cursor="hand2",
                              command=lambda: self.select_current_date(date_type, popup))
        confirm_btn.pack(side="right")
        self.add_hover_effect(confirm_btn, "#2a4d6e", self.colors["primary"])
    
    def fill_modern_calendar_dates(self):
        """Populate modern calendar dates"""
        # Clear old date buttons
        for widget in self.days_frame.winfo_children():
            widget.destroy()
        
        today = datetime.now().date()
        
        # Get first weekday and days in month
        first_weekday, month_days = cal.monthrange(self.cal_year, self.cal_month)
        first_weekday = (first_weekday + 1) % 7  # Adjust for Monday as first day
        
        # Get currently selected date
        selected_date = None
        if self.date_type == "checkin" and hasattr(self, 'date_var'):
            try:
                selected_date = datetime.strptime(self.date_var.get(), "%Y-%m-%d").date()
            except:
                pass
        elif self.date_type == "checkout" and hasattr(self, 'checkout_var'):
            try:
                selected_date = datetime.strptime(self.checkout_var.get(), "%Y-%m-%d").date()
            except:
                pass
        elif hasattr(self, 'date_var'):
            try:
                selected_date = datetime.strptime(self.date_var.get(), "%Y-%m-%d").date()
            except:
                pass
        
        row, col = 0, 0
        
        # Fill blanks
        for i in range(first_weekday):
            blank = tk.Label(self.days_frame, text="", 
                           bg=self.colors["calendar_bg"],
                           width=8, height=3)
            blank.grid(row=row, column=col, padx=1, pady=1)
            col += 1
        
        # Create date buttons
        for day in range(1, month_days + 1):
            date_obj = datetime(self.cal_year, self.cal_month, day).date()
            is_today = (date_obj == today)
            is_selected = (selected_date == date_obj)
            is_past = (date_obj < today)
            is_weekend = (col >= 5)  # Saturday or Sunday
            
            # Determine button style
            if is_selected:
                btn_bg = self.colors["calendar_selected"]
                btn_fg = "white"
                btn_font = ("Segoe UI", 11, "bold")
            elif is_today:
                btn_bg = self.colors["calendar_today"]
                btn_fg = "white"
                btn_font = ("Segoe UI", 11, "bold")
            elif is_past:
                btn_bg = self.colors["calendar_bg"]
                btn_fg = self.colors["calendar_past"]
                btn_font = ("Segoe UI", 11)
            elif is_weekend:
                btn_bg = self.colors["calendar_bg"]
                btn_fg = self.colors["calendar_weekend"]
                btn_font = ("Segoe UI", 11, "bold")
            else:
                btn_bg = self.colors["calendar_bg"]
                btn_fg = self.colors["primary"]
                btn_font = ("Segoe UI", 11)
            
            # Create date button
            btn = tk.Button(self.days_frame, text=str(day),
                          font=btn_font,
                          bg=btn_bg, fg=btn_fg,
                          relief="flat", width=8, height=3,
                          cursor="hand2" if not is_past else "arrow",
                          state="normal" if not is_past else "disabled",
                          command=lambda d=date_obj: self.select_modern_date(d) if not is_past else None)
            btn.grid(row=row, column=col, padx=1, pady=1)
            
            # Add hover effect (only for selectable dates)
            if not is_past and not is_selected:
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.colors["calendar_hover"]))
                btn.bind("<Leave>", lambda e, b=btn, bg=btn_bg: b.config(bg=bg))
            
            col += 1
            if col == 7:
                col = 0
                row += 1
    
    def prev_month(self):
        """Switch to previous month"""
        self.cal_month -= 1
        if self.cal_month < 1:
            self.cal_month = 12
            self.cal_year -= 1
        self.month_year_var.set(f"{cal.month_name[self.cal_month]} {self.cal_year}")
        self.fill_modern_calendar_dates()
    
    def next_month(self):
        """Switch to next month"""
        self.cal_month += 1
        if self.cal_month > 12:
            self.cal_month = 1
            self.cal_year += 1
        self.month_year_var.set(f"{cal.month_name[self.cal_month]} {self.cal_year}")
        self.fill_modern_calendar_dates()
    
    def select_modern_date(self, date_obj):
        """Select date in modern calendar"""
        self.selected_modern_date = date_obj
        
        # Update selection state for all buttons
        for widget in self.days_frame.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget("state") != "disabled":
                day_text = widget.cget("text")
                if day_text.isdigit():
                    day = int(day_text)
                    widget_date = datetime(self.cal_year, self.cal_month, day).date()
                    
                    if widget_date == date_obj:
                        widget.config(bg=self.colors["calendar_selected"], fg="white",
                                    font=("Segoe UI", 11, "bold"))
                    else:
                        is_today = (widget_date == datetime.now().date())
                        is_weekend = ((datetime(self.cal_year, self.cal_month, day).weekday() + 1) % 7 >= 5)
                        
                        if is_today:
                            widget.config(bg=self.colors["calendar_today"], fg="white",
                                        font=("Segoe UI", 11, "bold"))
                        elif is_weekend:
                            widget.config(bg=self.colors["calendar_bg"], fg=self.colors["calendar_weekend"],
                                        font=("Segoe UI", 11, "bold"))
                        else:
                            widget.config(bg=self.colors["calendar_bg"], fg=self.colors["primary"],
                                        font=("Segoe UI", 11))
    
    def select_today(self, date_type, popup):
        """Select today"""
        today = datetime.now().date()
        self.select_modern_date(today)
        
        # Auto-close window
        self.confirm_modern_date_selection(today, date_type, popup)
    
    def select_current_date(self, date_type, popup):
        """Confirm selection of currently selected date"""
        if hasattr(self, 'selected_modern_date'):
            self.confirm_modern_date_selection(self.selected_modern_date, date_type, popup)
        else:
            # If no date selected, use today
            today = datetime.now().date()
            self.confirm_modern_date_selection(today, date_type, popup)
    
    def confirm_modern_date_selection(self, date_obj, date_type, popup):
        """Confirm date selection"""
        date_str = date_obj.strftime("%Y-%m-%d")
        
        if date_type == "checkin":
            self.date_var.set(date_str)
        elif date_type == "checkout":
            self.checkout_var.set(date_str)
        else:
            self.date_var.set(date_str)
        
        popup.destroy()
    
    def update_price(self):
        """Update price display"""
        if not self.price_label:
            return
        
        category = self.item_data.get('category', 'general')
        base_price = self.item_data.get('price', 0)
        discount_price = self.item_data.get('discount_price')
        final_price = discount_price if discount_price else base_price
        
        if category == 'hotel' and hasattr(self, 'date_var') and hasattr(self, 'checkout_var'):
            try:
                check_in = datetime.strptime(self.date_var.get(), "%Y-%m-%d")
                check_out = datetime.strptime(self.checkout_var.get(), "%Y-%m-%d")
                nights = (check_out - check_in).days
                if nights <= 0:
                    nights = 1
                total_price = final_price * nights * self.quantity_var.get()
            except:
                total_price = final_price * self.quantity_var.get()
        else:
            total_price = final_price * self.quantity_var.get()
        
        if final_price > 0:
            self.price_label.config(text=f"RM {total_price:.2f}")
        else:
            self.price_label.config(text="FREE")
    
    def load_image(self, filename: str, size: tuple = (300, 200)) -> ImageTk.PhotoImage:
        """Load image from local file"""
        cache_key = f"{filename}_{size[0]}_{size[1]}"
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
        
        try:
            # Determine default image directory based on category
            category = self.item_data.get('category', 'general')
            if category == 'hotel':
                default_dir = "images/hotels"
            elif category == 'flight':
                default_dir = "images/flights"
            elif category == 'car':
                default_dir = "images/cars"
            elif category == 'attraction':
                default_dir = "images/attractions"
            else:
                default_dir = "images"
            
            # Try multiple possible paths
            possible_paths = []
            
            if filename:
                # Original path
                possible_paths.append(filename)
                
                # In category directory
                possible_paths.append(os.path.join(default_dir, filename))
                
                # Only filename in category directory
                possible_paths.append(os.path.join(default_dir, os.path.basename(filename)))
            
            # Generic placeholder images
            generic_files = []
            if category == 'hotel':
                generic_files = ["hotel_recommend.jpg"]
            elif category == 'flight':
                generic_files = ["flight_recommend.jpg"]
            elif category == 'car':
                generic_files = ["car_recommend.jpg"]
            elif category == 'attraction':
                generic_files = ["attraction_recommend.jpg"]
            
            # Add generic file paths
            for file in generic_files:
                possible_paths.append(os.path.join(default_dir, file))
                possible_paths.append(os.path.join("images", file))
            
            # Try all possible paths
            image_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    image_path = path
                    break
            
            if image_path:
                img = Image.open(image_path)
                img = img.resize(size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.image_cache[cache_key] = photo
                return photo
            else:
                # Create category-specific placeholder
                return self.create_category_placeholder_image(size)
                
        except Exception as e:
            # Create category-specific placeholder
            return self.create_category_placeholder_image(size)
    
    def create_category_placeholder_image(self, size):
        """Create category-specific placeholder image"""
        category = self.item_data.get('category', 'general')
        
        # Different colors for different categories
        category_colors = {
            'hotel': '#3498db',       # Blue
            'flight': '#9b59b6',      # Purple
            'car': '#e74c3c',         # Red
            'attraction': '#2ecc71',  # Green
            'general': '#1abc9c'      # Cyan
        }
        
        bg_color = category_colors.get(category, '#3498db')
        
        # Category icons
        category_icons = {
            'hotel': '🏨',
            'flight': '✈️',
            'car': '🚗',
            'attraction': '🏛️',
            'general': '📋'
        }
        
        icon = category_icons.get(category, '📋')
        
        img = Image.new('RGB', size, color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # Add border
        draw.rectangle([0, 0, size[0]-1, size[1]-1], outline='#ffffff', width=2)
        
        # Add icon
        try:
            from PIL import ImageFont
            
            # Try loading font
            try:
                font = ImageFont.truetype("arial.ttf", min(size[0]//8, size[1]//4))
            except:
                font = ImageFont.load_default()
            
            # Calculate text position
            text_bbox = draw.textbbox((0, 0), icon, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = (size[0] - text_width) // 2
            y = (size[1] - text_height) // 2
            
            draw.text((x, y), icon, fill='white', font=font)
        except:
            # If font fails, use simple text
            draw.text((size[0]//2, size[1]//2), icon, 
                     fill='white', anchor="mm", align="center")
        
        # Add category text
        category_text = category.capitalize()
        try:
            from PIL import ImageFont
            try:
                small_font = ImageFont.truetype("arial.ttf", min(size[0]//20, 14))
            except:
                small_font = ImageFont.load_default()
            
            text_bbox = draw.textbbox((0, 0), category_text, font=small_font)
            text_width = text_bbox[2] - text_bbox[0]
            
            x = (size[0] - text_width) // 2
            y = size[1] - 40
            
            draw.text((x, y), category_text, fill='white', font=small_font)
        except:
            pass
        
        photo = ImageTk.PhotoImage(img)
        
        # Cache placeholder image
        cache_key = f"placeholder_{category}_{size[0]}_{size[1]}"
        self.image_cache[cache_key] = photo
        
        return photo
    
    def create_footer(self):
        """Create footer"""
        footer = tk.Frame(self.root, bg=self.colors["footer_bg"], height=50)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        
        tk.Label(footer, text="© 2024 Traney Travel Services", 
                font=("Segoe UI", 10),
                bg=self.colors["footer_bg"], fg="#b0c4de").pack(pady=15)
    
    def open_booking_detail(self):
        """Directly open booking detail page (no confirmation popup)"""
        try:
            # Validate dates
            category = self.item_data.get('category', 'general')
            
            if category in ['hotel', 'car', 'attraction', 'flight']:
                selected_date = datetime.strptime(self.date_var.get(), "%Y-%m-%d")
                if selected_date < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
                    messagebox.showerror("Invalid Date", "Please select a future date.")
                    return
                
                if category == 'hotel':
                    check_in = datetime.strptime(self.date_var.get(), "%Y-%m-%d")
                    check_out = datetime.strptime(self.checkout_var.get(), "%Y-%m-%d")
                    if check_out <= check_in:
                        messagebox.showerror("Invalid Dates", "Check-out date must be after check-in date.")
                        return
            
            # Directly open booking page, no confirmation needed
            self.open_booking_detail_via_subprocess()
            
        except ValueError:
            messagebox.showerror("Invalid Date", "Please select a valid date.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def calculate_total_price(self):
        """Calculate total price"""
        base_price = self.item_data.get('price', 0)
        discount_price = self.item_data.get('discount_price')
        final_price = discount_price if discount_price else base_price
        
        category = self.item_data.get('category', 'general')
        
        if category == 'hotel':
            check_in = datetime.strptime(self.date_var.get(), "%Y-%m-%d")
            check_out = datetime.strptime(self.checkout_var.get(), "%Y-%m-%d")
            nights = (check_out - check_in).days
            if nights <= 0:
                nights = 1
            return final_price * nights * self.quantity_var.get()
        else:
            return final_price * self.quantity_var.get()
    
    def open_booking_detail_via_subprocess(self):
        """Open booking detail via subprocess"""
        try:
            import tempfile
            
            # Prepare complete booking data
            category = self.item_data.get('category', 'general')
            
            booking_data = {
                'booking_id': f"BK{int(time.time()) % 1000000}",
                'type': category,
                'user_email': self.user_email,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                
                # Item information
                'item_name': self.item_data['name'],
                'item_id': self.item_data.get('id', ''),
                'category': category,
                'image_file': self.item_data.get('image_file', ''),
                'description': self.item_data.get('description', ''),
                'location': self.item_data.get('location', ''),
                'rating': self.item_data.get('rating', 0),
                'reviews': self.item_data.get('reviews', 0),
                
                # Booking details
                'quantity': self.quantity_var.get(),
                'total_price': str(self.calculate_total_price()),
                'unit_price': str(self.item_data.get('price', 0)),
                'discount_price': str(self.item_data.get('discount_price', '')),
                'currency': self.item_data.get('currency', 'RM'),
                
                # Add specific information based on category
                'highlights': self.item_data.get('highlights', []),
                'facilities': self.item_data.get('facilities', [])
            }
            
            # Add date information
            if hasattr(self, 'date_var'):
                booking_data['date'] = self.date_var.get()
            
            if category == 'hotel' and hasattr(self, 'checkout_var'):
                booking_data['check_out'] = self.checkout_var.get()
                try:
                    check_in = datetime.strptime(self.date_var.get(), "%Y-%m-%d")
                    check_out = datetime.strptime(self.checkout_var.get(), "%Y-%m-%d")
                    nights = (check_out - check_in).days
                    if nights <= 0:
                        nights = 1
                    booking_data['nights'] = nights
                    booking_data['check_in'] = self.date_var.get()
                except:
                    booking_data['nights'] = 1
                    booking_data['check_in'] = self.date_var.get()
            
            # Flight specific information
            if category == 'flight':
                booking_data.update({
                    'flight_date': self.date_var.get() if hasattr(self, 'date_var') else '',
                    'flight_number': self.item_data.get('flight_no', ''),
                    'airline': self.item_data.get('airline', ''),
                    'departure_time': self.item_data.get('departure', ''),
                    'arrival_time': self.item_data.get('arrival', ''),
                    'departure_airport': self.item_data.get('departure_airport', ''),
                    'arrival_airport': self.item_data.get('arrival_airport', ''),
                    'duration': self.item_data.get('duration', ''),
                    'cabin_class': self.item_data.get('cabin_class', 'Economy'),
                    'baggage_allowance': self.item_data.get('baggage_allowance', '20kg'),
                    'passengers': self.quantity_var.get()
                })
            
            # Hotel specific information
            elif category == 'hotel':
                booking_data.update({
                    'hotel_name': self.item_data['name'],
                    'room_types': self.item_data.get('room_types', ['Standard Room']),
                    'amenities': self.item_data.get('amenities', []),
                    'check_in_time': self.item_data.get('check_in', '14:00'),
                    'check_out_time': self.item_data.get('check_out', '12:00'),
                    'guests': self.quantity_var.get()
                })
            
            # Car rental specific information
            elif category == 'car':
                booking_data.update({
                    'car_model': f"{self.item_data.get('brand', '')} {self.item_data.get('type', '')}",
                    'pickup_date': self.date_var.get() if hasattr(self, 'date_var') else '',
                    'dropoff_date': self.date_var.get() if hasattr(self, 'date_var') else '',
                    'rental_days': '1',
                    'daily_rate': str(self.item_data.get('price', 0)),
                    'car_details': f"{self.item_data.get('seats', '')} seats, {self.item_data.get('transmission', '')} transmission"
                })
            
            # Attraction specific information
            elif category == 'attraction':
                booking_data.update({
                    'attraction_name': self.item_data['name'],
                    'visit_date': self.date_var.get() if hasattr(self, 'date_var') else '',
                    'tickets': self.quantity_var.get(),
                    'duration': self.item_data.get('duration', ''),
                    'best_time': self.item_data.get('best_time', '')
                })
            
            # Save as temporary file
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f"traney_booking_{int(time.time())}.json")
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(booking_data, f, indent=2, ensure_ascii=False)
            
            print(f"Booking data saved to: {temp_file}")
            print(f"Data for booking_detail.py: {json.dumps(booking_data, indent=2)}")
            
            # Close current window
            self.root.destroy()
            
            # Get Python executable path and current directory
            current_dir = os.getcwd()
            python_exe = sys.executable
            booking_detail_path = os.path.join(current_dir, "booking_detail.py")
            
            if os.path.exists(booking_detail_path):
                # Use subprocess to open booking_detail.py and pass data file path
                cmd = [python_exe, booking_detail_path, "--data", temp_file]
                print(f"Executing: {' '.join(cmd)}")
                subprocess.Popen(cmd)
            else:
                messagebox.showerror("Error", f"booking_detail.py not found at: {booking_detail_path}")
                # Return to home.py
                self.return_to_home_app()
                
        except Exception as e:
            print(f"Error opening booking detail: {e}")
            messagebox.showerror("Error", f"Failed to open booking page: {str(e)}")
            # Return to home.py
            self.return_to_home_app()
    
    def go_back(self):
        """Go back"""
        if self.return_to_home:
            self.return_to_home_app()
        else:
            self.root.destroy()
    
    def return_to_home_app(self):
        """Return to home.py"""
        try:
            # Save return information
            if not os.path.exists('temp'):
                os.makedirs('temp')
            
            return_info = {
                'from_detail': True,
                'timestamp': 'returned_from_detail'
            }
            
            return_file = os.path.join('temp', 'return_info.json')
            with open(return_file, 'w', encoding='utf-8') as f:
                json.dump(return_info, f, indent=2, ensure_ascii=False)
            
            # Close current window and launch home.py
            self.root.destroy()
            subprocess.Popen(["python", "home.py"])
            
        except Exception as e:
            print(f"Error returning to home: {e}")
            self.root.destroy()
    
    def add_hover_effect(self, widget, hover_color, normal_color):
        """Add hover effect"""
        widget.bind("<Enter>", lambda e: widget.config(bg=hover_color))
        widget.bind("<Leave>", lambda e: widget.config(bg=normal_color))
    
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen"""
        self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen'))
        return "break"


def load_item_data_from_json(json_file):
    """Load data from JSON file"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None


def main():
    """Main function"""
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        item_data = load_item_data_from_json(json_file)
        
        if item_data:
            root = tk.Tk()
            app = DetailPage(root, item_data, return_to_home=True)
            root.mainloop()
        else:
            print("Failed to load item data.")
    else:
        print("Usage: python detail_page.py data.json")


if __name__ == "__main__":
    main()