import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import datetime
import random
import re

class RoomSelection:
    """Room selection page for hotel booking"""
    
    def __init__(self, master, hotel_data, colors, profile_system, go_back_callback, open_booking_detail_callback):
        self.master = master
        self.hotel_data = hotel_data
        self.colors = colors
        self.profile_system = profile_system
        self.go_back_callback = go_back_callback
        self.open_booking_detail_callback = open_booking_detail_callback
        
        # Room selection variables
        self.room_buttons = {}  # Store room selection buttons
        self.selected_room_id = None  # Currently selected room ID
        self.selected_room_price = None  # Selected room price
        self.selected_room_type = None  # Selected room type/name
        self.selected_room_data = None  # Full room data
        
        # Date selection variables
        self.room_checkin_var = tk.StringVar()
        self.room_checkout_var = tk.StringVar()
        
        # Price calculation variables
        self.calculated_total_price = 0  # Total calculated price
        self.calculated_nights = 1  # Number of nights
        
        # Counter for generating unique room IDs
        self.room_counter = 0
        
        # Create the UI
        self.create_widgets()
    
    def create_widgets(self):
        """Create the complete room selection interface"""
        # Create main container
        self.main_container = tk.Frame(self.master, bg='#f5f7fa')
        self.main_container.pack(fill="both", expand=True)
        
        # Create scrollable area inside main container
        self.canvas = tk.Canvas(self.main_container, bg='#f5f7fa', highlightthickness=0)
        scrollbar = tk.Scrollbar(self.main_container, orient="vertical", command=self.canvas.yview)
        
        # Create the scrollable frame
        self.scrollable_frame = tk.Frame(self.canvas, bg='#f5f7fa')
        
        # Configure scrolling
        self.scrollable_frame.bind("<Configure>", 
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create header
        self.create_header()
        
        # Main content container
        main_container = tk.Frame(self.scrollable_frame, bg='#f5f7fa')
        main_container.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Center wrapper
        center_wrapper = tk.Frame(main_container, bg='#f5f7fa')
        center_wrapper.pack(expand=True)
        
        content_frame = tk.Frame(center_wrapper, bg='#f5f7fa')
        content_frame.pack()
        
        # Two-column layout
        left_column = tk.Frame(content_frame, bg='#f5f7fa')
        left_column.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        right_column = tk.Frame(content_frame, bg='#f5f7fa', width=350)
        right_column.pack(side='right', fill='y', padx=(15, 0))
        right_column.pack_propagate(False)
        
        # Left column components
        self.create_hotel_info_left(left_column)
        self.create_room_selection_section(left_column)
        self.create_hotel_amenities(left_column)
        
        # Right column components
        self.create_booking_summary(right_column)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enable mousewheel scrolling
        self.bind_mousewheel()
        
        # Force update to ensure display
        self.master.update()
    
    def create_header(self):
        """Create page header with back button and title"""
        header_frame = tk.Frame(self.scrollable_frame, bg='#f5f7fa')
        header_frame.pack(fill='x', padx=15, pady=(15, 10))
        
        # Back button to return to hotel list
        back_button = tk.Button(header_frame, text="← Back to Hotels", 
                               font=('Arial', 11, 'bold'),
                               bg=self.colors["primary"], fg='white',
                               relief='flat', cursor='hand2',
                               command=self.go_back_callback)
        back_button.pack(anchor='w', pady=(0, 10))
        
        # Page title
        tk.Label(header_frame, text="Select Your Room", 
                font=('Arial', 20, 'bold'), bg='#f5f7fa', fg='#1e3d59').pack(anchor='w')
        
        # Hotel name subtitle
        tk.Label(header_frame, text=self.hotel_data['name'], 
                font=('Arial', 12), bg='#f5f7fa', fg='#555555').pack(anchor='w', pady=(5, 0))
    
    def create_hotel_info_left(self, parent):
        """Create hotel information section"""
        hotel_frame = tk.Frame(parent, bg='white', relief='flat', bd=0)
        hotel_frame.pack(fill='x', pady=(0, 20))
        
        card = tk.Frame(hotel_frame, bg='white', relief='raised', bd=1)
        card.pack(fill='x', padx=0, pady=0)
        
        info_frame = tk.Frame(card, bg='white')
        info_frame.pack(fill='x', padx=25, pady=25)
        
        title_frame = tk.Frame(info_frame, bg='white')
        title_frame.pack(fill='x', pady=(0, 15))
        
        # Hotel name
        tk.Label(title_frame, text=self.hotel_data['name'], 
                font=('Arial', 22, 'bold'), bg='white', fg='#1e3d59').pack(side='left')
        
        # Rating badge
        rating_badge = tk.Frame(title_frame, bg='#ff8c66', padx=10, pady=3)
        rating_badge.pack(side='right', padx=(10, 0))
        tk.Label(rating_badge, text=f"⭐ {self.hotel_data['rating']}", 
                font=('Arial', 12, 'bold'), bg='#ff8c66', fg='white').pack()
        
        # Hotel address
        address_frame = tk.Frame(info_frame, bg='white')
        address_frame.pack(fill='x', pady=(0, 20))
        
        address = self.hotel_data.get('booking_details', {}).get('address', 'Address not available')
        tk.Label(address_frame, text=f"📍 {address}", 
                font=('Arial', 11), bg='white', fg='#555555', wraplength=600, justify='left').pack(anchor='w')
    
    def create_room_selection_section(self, parent):
        """Create room selection section with available rooms"""
        rooms_frame = tk.Frame(parent, bg='white', relief='flat', bd=0)
        rooms_frame.pack(fill='x', pady=(0, 20))
        
        title_frame = tk.Frame(rooms_frame, bg='white')
        title_frame.pack(fill='x', padx=0, pady=(0, 15))
        tk.Label(title_frame, text="Available Rooms", 
                font=('Arial', 18, 'bold'), bg='white', fg='#1e3d59').pack(side='left')
        
        # Try different possible locations for room data
        rooms_data = []
        
        # Check multiple possible locations for room data
        if 'rooms' in self.hotel_data:
            rooms_data = self.hotel_data['rooms']
        elif 'booking_details' in self.hotel_data and 'rooms' in self.hotel_data['booking_details']:
            rooms_data = self.hotel_data['booking_details']['rooms']
        elif 'room_types' in self.hotel_data:
            rooms_data = self.hotel_data['room_types']
        elif 'available_rooms' in self.hotel_data:
            rooms_data = self.hotel_data['available_rooms']
        elif 'accommodation' in self.hotel_data:
            rooms_data = self.hotel_data['accommodation']
        
        # If no rooms found, create default room data
        if not rooms_data:
            print(f"DEBUG: No room data found in hotel data. Creating default rooms.")
            print(f"Hotel data keys: {self.hotel_data.keys()}")
            rooms_data = self.create_default_rooms()
        
        print(f"DEBUG: Found {len(rooms_data)} rooms to display")
        
        if rooms_data:
            for i, room_data in enumerate(rooms_data):
                self.create_room_card(rooms_frame, room_data, i)
        else:
            # Show message if no rooms available
            no_rooms_frame = tk.Frame(rooms_frame, bg='white')
            no_rooms_frame.pack(fill='x', pady=20)
            tk.Label(no_rooms_frame, text="No rooms available for this hotel", 
                    font=('Arial', 14), bg='white', fg='#e74c3c').pack()
    
    def create_default_rooms(self):
        """Create default room data when none is provided"""
        default_rooms = [
            {
                'name': 'Standard Room',
                'type': 'standard',
                'description': 'Comfortable room with all basic amenities',
                'original_price': 300,
                'discount_price': 250,
                'total_price': 275,
                'stock_info': 'Only 2 rooms left',
                'features': [
                    ("✅", "Free WiFi"),
                    ("✅", "Air conditioning"),
                    ("✅", "Private bathroom"),
                    ("✅", "Flat-screen TV"),
                    ("✅", "Mini fridge"),
                    ("✅", "24-hour room service")
                ]
            },
            {
                'name': 'Deluxe Room',
                'type': 'deluxe',
                'description': 'Spacious room with premium amenities',
                'original_price': 450,
                'discount_price': 380,
                'total_price': 418,
                'stock_info': 'Limited availability',
                'features': [
                    ("✅", "Free WiFi (High Speed)"),
                    ("✅", "Air conditioning"),
                    ("✅", "Private bathroom with tub"),
                    ("✅", "55\" Smart TV"),
                    ("✅", "Mini bar"),
                    ("✅", "Work desk"),
                    ("✅", "City view"),
                    ("✅", "Premium toiletries")
                ]
            },
            {
                'name': 'Executive Suite',
                'type': 'suite',
                'description': 'Luxury suite with separate living area',
                'original_price': 650,
                'discount_price': 550,
                'total_price': 605,
                'stock_info': 'Last room available',
                'features': [
                    ("✅", "Free WiFi (Ultra High Speed)"),
                    ("✅", "Separate living room"),
                    ("✅", "King size bed"),
                    ("✅", "Jacuzzi bathtub"),
                    ("✅", "65\" Smart TV"),
                    ("✅", "Complimentary minibar"),
                    ("✅", "Panoramic city view"),
                    ("✅", "Butler service"),
                    ("✅", "Welcome drinks")
                ]
            }
        ]
        return default_rooms
    
    def create_room_card(self, parent, room_data, card_index):
        """Create individual room selection card"""
        card = tk.Frame(parent, bg='white', relief='raised', bd=1)
        card.pack(fill='x', pady=(0, 15))
        
        card_content = tk.Frame(card, bg='white')
        card_content.pack(fill='x', padx=25, pady=20)
        
        # Get room name with fallback
        room_name = room_data.get('name', f'Room {card_index + 1}')
        room_description = room_data.get('description', 'Comfortable accommodation with all basic amenities')
        
        # Header with room name
        header_frame = tk.Frame(card_content, bg='white')
        header_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(header_frame, text=room_name, 
                font=('Arial', 16, 'bold'), bg='white', fg='#1e3d59').pack(side='left')
        
        # Add "Best Value" badge for premium rooms
        if (room_data.get('type') == 'premium' or 
            'Deluxe' in room_name or 
            'Premium' in room_name or 
            'Suite' in room_name):
            badge = tk.Frame(header_frame, bg='#27ae60', padx=8, pady=2)
            badge.pack(side='left', padx=(10, 0))
            tk.Label(badge, text="BEST VALUE", 
                    font=('Arial', 9, 'bold'), bg='#27ae60', fg='white').pack()
        
        # Room content in two columns
        content_frame = tk.Frame(card_content, bg='white')
        content_frame.pack(fill='x')
        
        left_frame = tk.Frame(content_frame, bg='white')
        left_frame.pack(side='left', fill='x', expand=True)
        
        right_frame = tk.Frame(content_frame, bg='white')
        right_frame.pack(side='right', padx=(20, 0))
        
        # Left: Room features
        self.create_room_features(left_frame, room_data, room_description)
        
        # Right: Price and selection button
        self.create_price_options(right_frame, room_data, room_name, card_index)
    
    def create_room_features(self, left_frame, room_data, description):
        """Create room features section"""
        features_frame = tk.Frame(left_frame, bg='white')
        features_frame.pack(anchor='w', pady=(0, 15))
        
        tk.Label(features_frame, text=description, 
                font=('Arial', 11, 'bold'), bg='white', fg='#2c3e50').pack(anchor='w', pady=(0, 8))
        
        # Display room features with icons - handle missing features
        features = room_data.get('features', [])
        
        if not features:
            # Default features if none provided
            default_features = [
                ("✅", "Free WiFi"),
                ("✅", "Air conditioning"),
                ("✅", "Private bathroom"),
                ("✅", "Flat-screen TV"),
                ("✅", "Daily housekeeping")
            ]
            features = default_features
        
        for icon, feature in features:
            feature_item = tk.Frame(features_frame, bg='white')
            feature_item.pack(anchor='w', pady=3)
            tk.Label(feature_item, text=icon, 
                    font=('Arial', 11), bg='white', 
                    fg='#27ae60' if icon == "✅" else ('#e74c3c' if icon == "🚫" else '#7f8c8d')
                    ).pack(side='left', padx=(0, 8))
            tk.Label(feature_item, text=feature, 
                    font=('Arial', 11), bg='white', fg='#2c3e50').pack(side='left')
    
    def create_price_options(self, right_frame, room_data, room_name, card_index):
        """Create price and selection button section"""
        price_container = tk.Frame(right_frame, bg='white')
        price_container.pack(pady=(0, 10))
        
        tk.Label(price_container, text="Today's Price", 
                font=('Arial', 11, 'bold'), bg='white', fg='#2c3e50').pack(anchor='w', pady=(0, 5))
        
        # Get prices with fallbacks
        original_price = room_data.get('original_price', 200)
        discount_price = room_data.get('discount_price', 180)
        total_price = room_data.get('total_price', 198)
        
        # Format prices as RM values
        original_price_str = f"RM {original_price}"
        discount_price_str = f"RM {discount_price}"
        total_price_str = f"RM {total_price}"
        
        # Price comparison (original vs discount)
        price_compare_frame = tk.Frame(price_container, bg='white')
        price_compare_frame.pack(anchor='w', pady=(0, 5))
        
        # Original price (strikethrough)
        original_frame = tk.Frame(price_compare_frame, bg='white')
        original_frame.pack(side='left')
        
        # Create a label with strikethrough effect
        original_label = tk.Label(original_frame, text=original_price_str,
                                 font=('Arial', 11), bg='white', fg='#95a5a6')
        original_label.pack()
        
        # Add strikethrough effect
        original_label.config(font=('Arial', 11, 'overstrike'))
        
        # Discount price (highlighted)
        discount_frame = tk.Frame(price_compare_frame, bg='white')
        discount_frame.pack(side='left', padx=(10, 0))
        tk.Label(discount_frame, text=discount_price_str, 
                font=('Arial', 18, 'bold'), bg='white', fg='#e74c3c').pack()
        
        # Price note
        tk.Label(price_container, text=f"Per room per night", 
                font=('Arial', 9), bg='white', fg='#7f8c8d').pack(anchor='w', pady=(2, 0))
        
        # Total price including taxes
        total_frame = tk.Frame(price_container, bg='white')
        total_frame.pack(anchor='w', pady=(10, 0))
        tk.Label(total_frame, text=f"Total (Incl. taxes & fees):", 
                font=('Arial', 11), bg='white', fg='#2c3e50').pack(side='left')
        tk.Label(total_frame, text=total_price_str, 
                font=('Arial', 12, 'bold'), bg='white', fg='#1e3d59').pack(side='left')
        
        # Stock/availability info
        stock_frame = tk.Frame(price_container, bg='white')
        stock_frame.pack(anchor='w', pady=(8, 0))
        tk.Label(stock_frame, text="🔥", 
                font=('Arial', 11), bg='white', fg='#e74c3c').pack(side='left')
        stock_info = room_data.get('stock_info', 'Limited availability')
        tk.Label(stock_frame, text=f" {stock_info}", 
                font=('Arial', 10, 'bold'), bg='white', fg='#e74c3c').pack(side='left')
        
        # Generate a unique room ID
        room_id = f"{room_data.get('type', 'standard')}_{room_name}_{self.room_counter}"
        self.room_counter += 1
        
        # Check if this room is currently selected
        is_selected = self.selected_room_id == room_id
        
        # Create selection button
        select_btn = tk.Button(price_container, 
                            text="✓ Selected" if is_selected else "Select",
                            bg=self.colors["success"] if is_selected else self.colors["primary"],
                            fg='white', 
                            font=('Arial', 12, 'bold'),
                            relief='flat', padx=20, pady=8,
                            cursor='hand2',
                            command=lambda rid=room_id, rdata=room_data: self.select_room(rid, rdata))
        select_btn.pack(pady=(15, 0))
        
        # Store the button reference
        self.room_buttons[room_id] = select_btn
        
        # Add hover effect for unselected buttons
        if not is_selected:
            select_btn.bind("<Enter>", lambda e, b=select_btn: b.config(bg='#2c3e50'))
            select_btn.bind("<Leave>", lambda e, b=select_btn: b.config(bg=self.colors["primary"]))
    
    def select_room(self, room_id, room_data):
        """Handle room selection/deselection"""
        if self.selected_room_id == room_id:
            # Deselect the room
            current_btn = self.room_buttons[room_id]
            current_btn.config(text="Select", 
                            bg=self.colors["primary"],
                            state="normal")
            current_btn.bind("<Enter>", lambda e, b=current_btn: b.config(bg='#2c3e50'))
            current_btn.bind("<Leave>", lambda e, b=current_btn: b.config(bg=self.colors["primary"]))
            
            self.selected_room_id = None
            self.selected_room_price = None
            self.selected_room_type = None
            self.selected_room_data = None
            
            if hasattr(self, 'room_selection_label'):
                self.room_selection_label.config(
                    text="No room selected",
                    fg='#e74c3c'
                )
            
            self.update_price_display(None, None)
            return
        
        # Deselect other rooms
        for rid, btn in self.room_buttons.items():
            if rid != room_id:
                btn.config(text="Select", 
                        bg=self.colors["primary"],
                        state="normal")
                btn.unbind("<Enter>")
                btn.unbind("<Leave>")
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg='#2c3e50'))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.colors["primary"]))
        
        # Select current room
        current_btn = self.room_buttons[room_id]
        current_btn.config(text="✓ Selected", 
                        bg=self.colors["success"],
                        state="normal")
        current_btn.unbind("<Enter>")
        current_btn.unbind("<Leave>")
        
        self.selected_room_id = room_id
        self.selected_room_price = room_data.get('discount_price', 180)
        self.selected_room_type = room_data.get('name', 'Room')
        self.selected_room_data = room_data
        
        if hasattr(self, 'room_selection_label'):
            price = room_data.get('discount_price', 180)
            self.room_selection_label.config(
                text=f"{room_data.get('name', 'Room')} - RM {price}",
                fg=self.colors["success"]
            )
        
        self.update_price_display(room_data.get('discount_price', 180), room_data.get('total_price', 198))
    
    def create_booking_summary(self, parent):
        """Create booking summary sidebar"""
        summary_container = tk.Frame(parent, bg='white', relief='raised', bd=1)
        summary_container.pack(fill='both', expand=True)
        
        # Header with dark background
        header_frame = tk.Frame(summary_container, bg='#1e3d59')
        header_frame.pack(fill='x', pady=0)
        tk.Label(header_frame, text="Booking Summary", 
                font=('Arial', 16, 'bold'), bg='#1e3d59', fg='white',
                padx=20, pady=15).pack()
        
        # Summary content
        summary_content = tk.Frame(summary_container, bg='white')
        summary_content.pack(fill='both', expand=True, padx=25, pady=25)
        
        # Hotel information
        hotel_info_frame = tk.Frame(summary_content, bg='white')
        hotel_info_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(hotel_info_frame, text="Hotel:", 
                font=('Arial', 12, 'bold'), bg='white', fg='#2c3e50').pack(anchor='w', pady=(0, 5))
        tk.Label(hotel_info_frame, text=self.hotel_data['name'], 
                font=('Arial', 11), bg='white', fg='#555555',
                wraplength=300, justify='left').pack(anchor='w')
        
        # Date selection section
        date_frame = tk.Frame(summary_content, bg='white')
        date_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(date_frame, text="Stay Dates:", 
                font=('Arial', 12, 'bold'), bg='white', fg='#2c3e50').pack(anchor='w', pady=(0, 10))
        
        # Check-in date selection
        checkin_frame = tk.Frame(date_frame, bg='white')
        checkin_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(checkin_frame, text="Check-in", bg='white', 
                font=('Arial', 11, 'bold'), fg='#2c3e50').pack(anchor='w', pady=(0, 5))
        
        checkin_entry = tk.Entry(checkin_frame, font=('Arial', 11), 
                                textvariable=self.room_checkin_var, state='readonly',
                                relief='sunken', bd=1, width=15)
        checkin_entry.pack(side='left', fill='x', expand=True)
        
        # Calendar button for check-in date
        tk.Button(checkin_frame, text="📅", font=('Arial', 11),
                command=lambda: self.show_calendar("checkin"), bg='#1e3d59', fg='white',
                relief='flat', width=3, padx=5).pack(side='right', padx=(5, 0))
        
        # Check-out date selection
        checkout_frame = tk.Frame(date_frame, bg='white')
        checkout_frame.pack(fill='x')
        
        tk.Label(checkout_frame, text="Check-out", bg='white', 
                font=('Arial', 11, 'bold'), fg='#2c3e50').pack(anchor='w', pady=(0, 5))
        
        checkout_entry = tk.Entry(checkout_frame, font=('Arial', 11), 
                                textvariable=self.room_checkout_var, state='readonly',
                                relief='sunken', bd=1, width=15)
        checkout_entry.pack(side='left', fill='x', expand=True)
        
        # Calendar button for check-out date
        tk.Button(checkout_frame, text="📅", font=('Arial', 11),
                command=lambda: self.show_calendar("checkout"), bg='#1e3d59', fg='white',
                relief='flat', width=3, padx=5).pack(side='right', padx=(5, 0))
        
        # Room selection display
        room_selection_frame = tk.Frame(summary_content, bg='white')
        room_selection_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(room_selection_frame, text="Selected Room:", 
                font=('Arial', 12, 'bold'), bg='white', fg='#2c3e50').pack(anchor='w', pady=(0, 5))
        
        self.room_selection_label = tk.Label(room_selection_frame, text="No room selected", 
                                font=('Arial', 11), bg='white', fg='#e74c3c')
        self.room_selection_label.pack(anchor='w')
        
        # Price breakdown section
        self.price_frame = tk.Frame(summary_content, bg='#f8f9fa', relief='sunken', bd=1, padx=15, pady=15)
        self.price_frame.pack(fill='x')
        
        tk.Label(self.price_frame, text="Estimated Price", 
                font=('Arial', 13, 'bold'), bg='#f8f9fa', fg='#1e3d59').pack(anchor='w', pady=(0, 10))
        
        self.price_details_frame = tk.Frame(self.price_frame, bg='#f8f9fa')
        self.price_details_frame.pack(fill='x', pady=10)
        
        self.price_details_label = tk.Label(self.price_details_frame, 
                                        text="Select a room to see price details",
                                        font=('Arial', 11), 
                                        bg='#f8f9fa', 
                                        fg='#7f8c8d',
                                        justify='center')
        self.price_details_label.pack()
        
        self.price_separator = ttk.Separator(self.price_frame, orient='horizontal')
        self.price_separator.pack_forget()  # Initially hidden
        
        self.total_frame = tk.Frame(self.price_frame, bg='#f8f9fa')
        self.total_frame.pack_forget()  # Initially hidden
        
        # Next/Proceed button
        next_btn = tk.Button(summary_content, text="Next →", 
                        bg='#4CAF50', fg='white',  
                        font=('Arial', 14, 'bold'),
                        command=self.check_and_proceed, relief='flat',
                        cursor='hand2', padx=20, pady=12)
        next_btn.pack(fill='x', pady=(20, 0))
        
        # Add hover effects to button
        next_btn.bind("<Enter>", lambda e: next_btn.config(bg='#66BB6A'))
        next_btn.bind("<Leave>", lambda e: next_btn.config(bg='#4CAF50'))
    
    def update_price_display(self, room_price, total_price):
        """Update price breakdown display based on selected room and dates"""
        if not hasattr(self, 'price_frame'):
            return
        
        # Clear previous price details
        for widget in self.price_details_frame.winfo_children():
            widget.destroy()
        
        if room_price is None:
            # No room selected
            self.price_details_label = tk.Label(self.price_details_frame, 
                                            text="Select a room to see price details",
                                            font=('Arial', 11), 
                                            bg='#f8f9fa', 
                                            fg='#7f8c8d',
                                            justify='center')
            self.price_details_label.pack()
            self.price_separator.pack_forget()
            self.total_frame.pack_forget()
        else:
            # Extract numeric price from string (e.g., "RM 200")
            try:
                if isinstance(room_price, str):
                    room_price_num = float(str(room_price).replace('RM', '').replace(' ', '').strip())
                else:
                    room_price_num = float(room_price)
            except ValueError:
                room_price_num = 180  # Default price
            
            # Calculate number of nights based on selected dates
            nights = 1  # Default to 1 night
            try:
                if self.room_checkin_var.get() and self.room_checkout_var.get():
                    checkin_str = self.room_checkin_var.get()
                    checkout_str = self.room_checkout_var.get()
                    
                    checkin_date = datetime.datetime.strptime(checkin_str, '%d/%m/%Y')
                    checkout_date = datetime.datetime.strptime(checkout_str, '%d/%m/%Y')
                    
                    nights = (checkout_date - checkin_date).days
                    if nights < 1:
                        nights = 1
            except Exception:
                nights = 1
            
            # Calculate total costs
            total_room_price = round(room_price_num * nights, 2)
            tax_amount = round(total_room_price * 0.1, 2)  # 10% tax
            service_charge = round(total_room_price * 0.05, 2)  # 5% service charge
            final_total = round(total_room_price + tax_amount + service_charge, 2)
            
            # Display price breakdown
            
            # Per night price
            per_night_frame = tk.Frame(self.price_details_frame, bg='#f8f9fa')
            per_night_frame.pack(fill='x', pady=3)
            tk.Label(per_night_frame, text="Room rate per night", 
                    font=('Arial', 11), bg='#f8f9fa', fg='#555555').pack(side='left')
            tk.Label(per_night_frame, text=f"RM {room_price_num:.2f}", 
                    font=('Arial', 11), bg='#f8f9fa', fg='#555555').pack(side='right')
            
            # Multi-night total if more than 1 night
            if nights > 1:
                nights_frame = tk.Frame(self.price_details_frame, bg='#f8f9fa')
                nights_frame.pack(fill='x', pady=3)
                tk.Label(nights_frame, text=f"× {nights} night{'s' if nights > 1 else ''}", 
                        font=('Arial', 11), bg='#f8f9fa', fg='#555555').pack(side='left')
                tk.Label(nights_frame, text=f"RM {total_room_price:.2f}", 
                        font=('Arial', 11), bg='#f8f9fa', fg='#555555').pack(side='right')
            
            # Taxes and fees
            tax_frame = tk.Frame(self.price_details_frame, bg='#f8f9fa')
            tax_frame.pack(fill='x', pady=3)
            tk.Label(tax_frame, text="Taxes & fees (10%)", 
                    font=('Arial', 11), bg='#f8f9fa', fg='#555555').pack(side='left')
            tk.Label(tax_frame, text=f"RM {tax_amount:.2f}", 
                    font=('Arial', 11), bg='#f8f9fa', fg='#555555').pack(side='right')
            
            # Service charge
            service_frame = tk.Frame(self.price_details_frame, bg='#f8f9fa')
            service_frame.pack(fill='x', pady=3)
            tk.Label(service_frame, text="Service charge (5%)", 
                    font=('Arial', 11), bg='#f8f9fa', fg='#555555').pack(side='left')
            tk.Label(service_frame, text=f"RM {service_charge:.2f}", 
                    font=('Arial', 11), bg='#f8f9fa', fg='#555555').pack(side='right')
            
            # Separator line
            self.price_separator.pack(fill='x', pady=10)
            
            # Final total price display
            self.total_frame.pack(fill='x', pady=(0, 15))
            for widget in self.total_frame.winfo_children():
                widget.destroy()
            
            total_left_frame = tk.Frame(self.total_frame, bg='#f8f9fa')
            total_left_frame.pack(side='left', fill='y')
            
            tk.Label(total_left_frame, text="Total Amount", 
                    font=('Arial', 12, 'bold'), bg='#f8f9fa', fg='#1e3d59').pack(anchor='w')
            
            tk.Label(self.total_frame, text=f"RM {final_total:.2f}", 
                    font=('Arial', 16, 'bold'), bg='#f8f9fa', fg='#e74c3c').pack(side='right')
            
            # Store calculated values
            self.calculated_total_price = final_total
            self.calculated_nights = nights
    
    def show_calendar(self, date_type):
        """Show calendar popup for date selection"""
        cal_window = tk.Toplevel(self.master)
        cal_window.title(f"Select {date_type.capitalize()} Date")
        cal_window.geometry("300x350")
        cal_window.configure(bg='white')
        
        today = datetime.datetime.now()
        
        # Set default date based on date type
        if date_type == "checkin":
            default_day = today.day
            default_month = today.month
            default_year = today.year
        else:  # checkout
            tomorrow = today + datetime.timedelta(days=1)
            default_day = tomorrow.day
            default_month = tomorrow.month
            default_year = tomorrow.year
        
        # Create calendar widget
        cal = Calendar(cal_window, selectmode='day', 
                    year=default_year,
                    month=default_month,
                    day=default_day,
                    mindate=today,  # Can't select past dates
                    disabledforeground='red',
                    foreground='black',
                    background='white',
                    selectbackground=self.colors["secondary"],
                    normalforeground='black',
                    weekendforeground='red',
                    maxdate=today + datetime.timedelta(days=365),  # Max 1 year ahead
                    date_pattern='dd/mm/yyyy')
        cal.pack(pady=20)
        
        def validate_date():
            """Validate and set selected date"""
            selected_date = cal.get_date()
            try:
                selected_datetime = datetime.datetime.strptime(selected_date, '%d/%m/%Y')
                
                # Check if date is in the past
                if selected_datetime.date() < today.date():
                    messagebox.showwarning("Invalid Date", 
                                        "Cannot select a past date. Please select today or a future date.")
                    return
                
                if date_type == "checkin":
                    # Check if checkout date is already set
                    if self.room_checkout_var.get():
                        checkout_str = self.room_checkout_var.get()
                        try:
                            checkout_date = datetime.datetime.strptime(checkout_str, '%d/%m/%Y')
                            if selected_datetime >= checkout_date:
                                messagebox.showwarning("Invalid Date", 
                                                    "Check-in date must be earlier than check-out date.")
                                return
                        except ValueError:
                            pass
                    
                    self.room_checkin_var.set(selected_date)
                    
                elif date_type == "checkout":
                    # Check if check-in date is set first
                    if not self.room_checkin_var.get():
                        messagebox.showwarning("Invalid Date", 
                                            "Please select check-in date first.")
                        return
                    
                    checkin_str = self.room_checkin_var.get()
                    try:
                        checkin_date = datetime.datetime.strptime(checkin_str, '%d/%m/%Y')
                        
                        if selected_datetime <= checkin_date:
                            messagebox.showwarning("Invalid Date", 
                                                "Check-out date must be at least one day after check-in date.")
                            return
                    except ValueError:
                        messagebox.showwarning("Invalid Date", 
                                            "Invalid check-in date format. Please use DD/MM/YYYY format.")
                        return
                    
                    self.room_checkout_var.set(selected_date)
                
                cal_window.destroy()
                
                # Update price display with new dates
                if self.selected_room_price:
                    self.update_price_display(self.selected_room_price, None)
                    
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use DD/MM/YYYY format.")
        
        # Select button
        select_btn = tk.Button(cal_window, text="Select", 
                            command=validate_date,
                            bg=self.colors["secondary"], fg='white',
                            font=('Arial', 11, 'bold'),
                            padx=20, pady=5)
        select_btn.pack(pady=10)
    
    def create_hotel_amenities(self, parent):
        """Create hotel amenities section"""
        amenities_frame = tk.Frame(parent, bg='white', relief='flat', bd=0)
        amenities_frame.pack(fill='x', pady=(0, 20))
        
        card = tk.Frame(amenities_frame, bg='white', relief='raised', bd=1)
        card.pack(fill='x')
        
        content_frame = tk.Frame(card, bg='white')
        content_frame.pack(fill='x', padx=25, pady=25)
        
        tk.Label(content_frame, text="Hotel Amenities", 
                font=('Arial', 18, 'bold'), bg='white', fg='#1e3d59').pack(anchor='w', pady=(0, 20))
        
        # Two-column layout for amenities
        columns_frame = tk.Frame(content_frame, bg='white')
        columns_frame.pack(fill='x')
        
        # Get amenities from hotel data or use defaults
        amenities = self.hotel_data.get('amenities', 
                    ['Free WiFi', 'Air conditioning', 'Swimming pool', 'Fitness center',
                     'Restaurant', '24-hour front desk', 'Room service', 'Laundry service',
                     'Spa', 'Business center', 'Concierge service', 'Valet parking'])
        
        # Split amenities into two columns
        mid_point = len(amenities) // 2
        left_amenities = amenities[:mid_point]
        right_amenities = amenities[mid_point:]
        
        # Left column
        left_column = tk.Frame(columns_frame, bg='white')
        left_column.pack(side='left', fill='x', expand=True, padx=(0, 15))
        
        for amenity in left_amenities:
            amenity_item = tk.Frame(left_column, bg='white')
            amenity_item.pack(fill='x', pady=5)
            tk.Label(amenity_item, text="✓", 
                    font=('Arial', 11), bg='white', fg='#27ae60').pack(side='left', padx=(0, 10))
            tk.Label(amenity_item, text=amenity, 
                    font=('Arial', 11), bg='white', fg='#2c3e50').pack(side='left')
        
        # Right column
        right_column = tk.Frame(columns_frame, bg='white')
        right_column.pack(side='right', fill='x', expand=True)
        
        for amenity in right_amenities:
            amenity_item = tk.Frame(right_column, bg='white')
            amenity_item.pack(fill='x', pady=5)
            tk.Label(amenity_item, text="✓", 
                    font=('Arial', 11), bg='white', fg='#27ae60').pack(side='left', padx=(0, 10))
            tk.Label(amenity_item, text=amenity, 
                    font=('Arial', 11), bg='white', fg='#2c3e50').pack(side='left')
    
    def check_and_proceed(self):
        """Validate selections and proceed to booking confirmation"""
        # Check if room is selected
        if not self.selected_room_type:
            messagebox.showwarning("No Room Selected", 
                                "Please select a room first before proceeding.")
            return
        
        # Check if dates are selected
        if not self.room_checkin_var.get() or not self.room_checkout_var.get():
            messagebox.showwarning("Missing Dates", 
                                "Please select both check-in and check-out dates.")
            return
        
        # Validate date format and logic
        try:
            checkin_date = datetime.datetime.strptime(self.room_checkin_var.get(), '%d/%m/%Y')
            checkout_date = datetime.datetime.strptime(self.room_checkout_var.get(), '%d/%m/%Y')
            
            # Check if checkout is after checkin
            if checkout_date <= checkin_date:
                messagebox.showwarning("Invalid Dates", 
                                    "Check-out date must be after check-in date.")
                return
            
            # Check minimum stay
            days_diff = (checkout_date - checkin_date).days
            if days_diff < 1:
                messagebox.showwarning("Invalid Dates", 
                                    "Minimum stay is one night.")
                return
                
        except ValueError:
            messagebox.showwarning("Invalid Date Format", 
                                "Please use DD/MM/YYYY format for dates.")
            return
        
        # Collect booking data and open confirmation
        booking_data = self.collect_booking_data()
        
        # Open booking confirmation page
        self.open_booking_detail_callback(booking_data)
        
        # Close this window after successful booking
        self.destroy_window()

    def destroy_window(self):
        """Destroy the room selection window"""
        # Unbind mousewheel events
        self.canvas.unbind("<MouseWheel>")
        self.scrollable_frame.unbind("<MouseWheel>")
        
        # Destroy the main container
        if hasattr(self, 'main_container'):
            self.main_container.destroy()
    
    def collect_booking_data(self):
        """Collect all booking information into a dictionary"""
        # Calculate number of nights
        try:
            checkin_date = datetime.datetime.strptime(self.room_checkin_var.get(), "%d/%m/%Y")
            checkout_date = datetime.datetime.strptime(self.room_checkout_var.get(), "%d/%m/%Y")
            num_nights = (checkout_date - checkin_date).days
            if num_nights <= 0:
                num_nights = 1
        except:
            num_nights = 1
        
        # Get room price
        room_price = self.selected_room_price
        if isinstance(room_price, str):
            # Extract numeric value from string like "RM 250"
            try:
                room_price_num = float(re.search(r'(\d+)', str(room_price).replace('RM', '').strip()).group(1))
            except:
                room_price_num = 180
        else:
            room_price_num = float(room_price) if room_price else 180
        
        # Calculate costs
        base_price = room_price_num * num_nights
        tax_fee = round(base_price * 0.1, 2)  # 10% tax
        service_charge = round(base_price * 0.05, 2)  # 5% service charge
        total_price = round(base_price + tax_fee + service_charge, 2)
        
        # Generate booking ID
        booking_id = f"HOTEL{random.randint(100000, 999999)}"
        
        # Get user information from profile
        user_email = "guest@example.com"
        user_name = "Guest User"
        user_phone = ""
        
        if self.profile_system:
            try:
                profile_data = self.profile_system.profile_data
                user_email = profile_data["personal_info"]["email"] or user_email
                user_name = profile_data["personal_info"]["full_name"] or user_name
                user_phone = profile_data["personal_info"]["phone"] or user_phone
            except:
                pass
        
        # Build complete booking data dictionary
        booking_data = {
            "booking_id": booking_id,
            "hotel_name": self.hotel_data.get('name', 'Unknown Hotel'),
            "check_in": self.room_checkin_var.get(),
            "check_out": self.room_checkout_var.get(),
            "room_type": self.selected_room_type,
            "num_nights": num_nights,
            "guests": "2 Adults",  # Default guest count
            "room_rate": f" {room_price_num:.2f} per night",
            "base_price": f" {base_price:.2f}",
            "tax_fee": f" {tax_fee:.2f}",
            "service_charge": f" {service_charge:.2f}",
            "total_price": f" {total_price:.2f}",
            "location": self.hotel_data.get('location', ''),
            "hotel_rating": self.hotel_data.get('rating', 'N/A'),
            "hotel_stars": self.hotel_data.get('stars', ''),
            "booking_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_email": user_email,
            "user_name": user_name,
            "user_phone": user_phone,
            "hotel_address": self.hotel_data.get('booking_details', {}).get('address', 'Address not available'),
            "room_features": self.selected_room_data.get('features', []) if self.selected_room_data else []
        }
        
        return booking_data
    
    def bind_mousewheel(self):
        """Enable mousewheel scrolling for the page"""
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"