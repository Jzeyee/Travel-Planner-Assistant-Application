import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import sys
import os
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class BookingDetailApp:
    def __init__(self, root, booking_data, email, booking_type="attraction", callback=None):
        self.root = root
        self.booking_data = booking_data
        self.email = email
        self.booking_type = booking_type
        self.callback = callback
        self.root.attributes('-fullscreen', True)

        
        # 获取实际的booking_type
        actual_booking_type = booking_data.get('booking_type', booking_type)
        
        # Check if flight booking for special handling
        self.is_flight_booking = actual_booking_type == "flight"
        
        # Validate incoming data
        self.validate_incoming_data()
        
        # Set window title
        booking_id = self.booking_data.get('booking_id', 'N/A')
        self.root.title(f"Booking Confirmation - #{booking_id}")
        
        # Window size
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f8ff")
        
        # Center window
        self.center_window()
        
        # Color scheme
        self.colors = {
            "primary": "#1e3d59",
            "secondary": "#ff6e40",
            "accent": "#ff8c66",
            "light": "#f0f8ff",
            "dark": "#1e3d59",
            "success": "#4CAF50",
            "warning": "#ff6e40",
            "card_bg": "#ffffff",
            "text_light": "#7a7a7a",
            "border": "#e0e0e0",
        }
        
        # Booking type colors
        self.type_colors = {
            "attraction": "#4CAF50",
            "hotel": "#2196F3", 
            "flight": "#9C27B0",
            "car_rental": "#FF9800"
        }
        
        # Create header
        self.create_header()
        
        # Create main content with two sections
        self.create_main_content()
        
        # Create footer with consistent buttons for ALL booking types
        self.create_footer()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def validate_incoming_data(self):
        """Validate and normalize incoming data from previous module"""
        # Ensure required fields exist
        required_fields = ['booking_id', 'total_price']
        
        for field in required_fields:
            if field not in self.booking_data:
                self.booking_data[field] = 'N/A'
        
        # Normalize price format
        if 'total_price' in self.booking_data:
            price = self.booking_data['total_price']
            if isinstance(price, (int, float)):
                self.booking_data['total_price'] = f"{price:.2f}"
        
        # Set default status if not provided
        if 'status' not in self.booking_data:
            self.booking_data['status'] = 'pending'
        
        # Add timestamp if not present
        if 'created_at' not in self.booking_data:
            self.booking_data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Generate booking ID if not present
        if self.booking_data.get('booking_id') in ['N/A', None, '']:
            self.booking_data['booking_id'] = self.generate_booking_id()
        
        # 关键修复：始终使用从detail_page传递过来的booking_type
        # 如果数据中有booking_type，就使用它
        if 'booking_type' not in self.booking_data:
            # 如果booking_type不在数据中，尝试从其他字段推断
            if 'type' in self.booking_data:
                # 映射detail_page的'type'到booking_detail的booking_type
                type_mapping = {
                    'hotel': 'hotel',
                    'flight': 'flight',
                    'car': 'car_rental',
                    'attraction': 'attraction',
                    'general': 'attraction'
                }
                detail_type = self.booking_data['type']
                self.booking_data['booking_type'] = type_mapping.get(detail_type, 'attraction')
            elif 'category' in self.booking_data:
                # 映射category到booking_type
                category_mapping = {
                    'hotel': 'hotel',
                    'flight': 'flight',
                    'car': 'car_rental',
                    'attraction': 'attraction',
                    'general': 'attraction'
                }
                category = self.booking_data['category']
                self.booking_data['booking_type'] = category_mapping.get(category, 'attraction')
            else:
                # 最后使用参数
                self.booking_data['booking_type'] = self.booking_type
        
        # Update is_flight_booking based on corrected booking_type
        self.is_flight_booking = self.booking_data.get('booking_type', '') == "flight"
        
        # For flight bookings, ensure passenger-related fields exist
        if self.is_flight_booking:
            if 'tickets' not in self.booking_data:
                self.booking_data['tickets'] = 1
            if 'adults' not in self.booking_data:
                self.booking_data['adults'] = 1
            if 'children' not in self.booking_data:
                self.booking_data['children'] = 0
    
    def generate_booking_id(self):
        """Generate a unique booking ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"BK{timestamp}"
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_header(self):
        """Create simple header"""
        header = tk.Frame(self.root, bg=self.colors["primary"], height=80)
        header.pack(fill="x")
        
        # Back button
        back_btn = tk.Button(header, text="← Back",
                           font=("Arial", 11),
                           bg=self.colors["primary"], fg="white",
                           relief="flat", cursor="hand2",
                           command=self.go_back)
        back_btn.place(x=20, y=20)
        
        # Get the actual booking type from data (not parameter)
        display_type = self.booking_data.get('booking_type', self.booking_type)
        type_name = display_type.replace('_', ' ').title()
        
        # Title with booking type
        tk.Label(header, text=f"{type_name} Booking Confirmation",
                font=("Arial", 20, "bold"),
                bg=self.colors["primary"], fg="white").pack(pady=20)
    
    def create_main_content(self):
        """Create main content with booking summary and information form"""
        main_container = tk.Frame(self.root, bg=self.colors["light"])
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Two column layout
        left_column = tk.Frame(main_container, bg=self.colors["light"], width=400)
        left_column.pack(side="left", fill="both", padx=(0, 20))
        
        right_column = tk.Frame(main_container, bg=self.colors["light"])
        right_column.pack(side="left", fill="both", expand=True)
        
        # Left: Booking Summary
        self.create_booking_summary(left_column)
        
        # Right: Information Form
        self.create_information_form(right_column)
    
    def create_booking_summary(self, parent):
        """Create booking summary section using data from previous module"""
        container = tk.Frame(parent, bg="white", padx=20, pady=20,
                           relief="solid", borderwidth=1)
        container.pack(fill="both", expand=True)
        
        # Get the actual booking type from data
        actual_type = self.booking_data.get('booking_type', self.booking_type)
        
        # Title with booking type
        type_icon = self.get_type_icon(actual_type)
        type_name = actual_type.replace('_', ' ').title()
        
        tk.Label(container, text=f"{type_icon} {type_name} Booking",
                font=("Arial", 18, "bold"),
                bg="white", fg=self.type_colors.get(actual_type, self.colors["primary"])).pack(anchor="w", pady=(0, 20))
        
        # Booking ID and Status
        id_frame = tk.Frame(container, bg="white")
        id_frame.pack(fill="x", pady=(0, 20))
        
        booking_id = self.booking_data.get('booking_id', 'N/A')
        tk.Label(id_frame, text=f"Booking ID: #{booking_id}",
                font=("Arial", 14, "bold"),
                bg="white", fg=self.colors["dark"]).pack(side="left")
        
        # Show status from data
        status = self.booking_data.get('status', 'pending')
        status_display = self.get_status_display(status)
        
        tk.Label(id_frame, text=status_display[0],
                font=("Arial", 12),
                bg=status_display[1], fg=status_display[2],
                padx=10, pady=3).pack(side="right")
        
        # Booking details - use actual data from booking_data
        details = self.extract_booking_details()
        
        for label, value in details:
            row = tk.Frame(container, bg="white")
            row.pack(fill="x", pady=8)
            
            tk.Label(row, text=f"{label}:", font=("Arial", 12),
                    bg="white", fg=self.colors["text_light"], width=15, anchor="w").pack(side="left")
            tk.Label(row, text=value, font=("Arial", 12, "bold"),
                    bg="white", fg=self.colors["dark"]).pack(side="left", padx=(10, 0))
        
        # Divider
        tk.Frame(container, height=2, bg=self.colors["border"]).pack(fill="x", pady=20)
        
        # Price summary - calculate from actual data
        price_items = self.calculate_price_summary()
        
        for label, value in price_items:
            price_row = tk.Frame(container, bg="white")
            price_row.pack(fill="x", pady=5)
            
            tk.Label(price_row, text=label, font=("Arial", 12),
                    bg="white", fg=self.colors["dark"]).pack(side="left")
            tk.Label(price_row, text=value, font=("Arial", 12),
                    bg="white", fg=self.colors["dark"]).pack(side="right")
        
        # Calculate final total
        total_amount = self.get_total_amount()
        
        # Total frame
        total_frame = tk.Frame(container, bg="#e8f5e9", padx=15, pady=10)
        total_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(total_frame, text="Total Amount:", font=("Arial", 14, "bold"),
                bg="#e8f5e9", fg=self.colors["success"]).pack(side="left")
        
        # Display total amount
        tk.Label(total_frame, text=f"RM {total_amount:,.2f}",
                font=("Arial", 16, "bold"),
                bg="#e8f5e9", fg=self.colors["success"]).pack(side="right")
        
        # Store for reference
        self.booking_data['display_total'] = total_amount
    
    def get_status_display(self, status):
        """Get display information for status"""
        status_map = {
            'pending': ('🔄 Pending Payment', '#fff3e0', '#FF9800'),
            'confirmed': ('✅ Confirmed', '#e8f5e9', '#4CAF50'),
            'cancelled': ('❌ Cancelled', '#ffebee', '#f44336'),
            'completed': ('✓ Completed', '#e3f2fd', '#2196F3'),
            'paid': ('💰 Paid', '#e8f5e9', '#4CAF50')
        }
        return status_map.get(status, status_map['pending'])
    
    def extract_booking_details(self):
        """Extract booking details from the incoming data"""
        details = []
        
        # Get main item name
        item_name = self.get_item_name()
        if item_name:
            details.append(("Item", item_name))
        
        # Define mapping of data fields with their display names
        common_fields = {
            # Date and time fields
            'date': 'Date',
            'booking_date': 'Booking Date',
            'travel_date': 'Travel Date',
            'visit_date': 'Visit Date',
            'check_in': 'Check-in',
            'check_out': 'Check-out',
            'check_in_date': 'Check-in Date',
            'check_out_date': 'Check-out Date',
            'departure_date': 'Departure',
            'arrival_date': 'Arrival',
            'departure_time': 'Departure Time',
            'arrival_time': 'Arrival Time',
            'pickup_date': 'Pick-up',
            'dropoff_date': 'Drop-off',
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'time_slot': 'Time Slot',
            'time': 'Time',
            'flight_date': 'Flight Date',
            
            # Quantity fields
            'guests': 'Guests',
            'adults': 'Adults',
            'children': 'Children',
            'infants': 'Infants',
            'tickets': 'Tickets',
            'passengers': 'Passengers',
            'quantity': 'Quantity',
            'rooms': 'Rooms',
            'nights': 'Nights',
            'days': 'Days',
            'rental_days': 'Rental Days',
            'duration': 'Duration',
            'hours': 'Hours',
            
            # Location and route fields
            'location': 'Location',
            'address': 'Address',
            'city': 'City',
            'country': 'Country',
            'destination': 'Destination',
            'origin': 'Origin',
            'from': 'From',
            'to': 'To',
            'pickup_location': 'Pick-up Location',
            'dropoff_location': 'Drop-off Location',
            'departure_city': 'Departure City',
            'arrival_city': 'Arrival City',
            'departure_airport': 'Departure Airport',
            'arrival_airport': 'Arrival Airport',
            
            # Type and class fields
            'room_type': 'Room Type',
            'room_types': 'Room Type',
            'room_category': 'Room Category',
            'flight_class': 'Class',
            'cabin_class': 'Cabin Class',
            'car_type': 'Car Type',
            'vehicle_type': 'Vehicle Type',
            'vehicle_category': 'Vehicle Category',
            'ticket_type': 'Ticket Type',
            'passenger_class': 'Class',
            
            # Identification fields
            'flight_number': 'Flight Number',
            'airline': 'Airline',
            'car_model': 'Car Model',
            'car_name': 'Car Name',
            'car_brand': 'Car Brand',
            'vehicle_model': 'Vehicle Model',
            'vehicle_name': 'Vehicle Name',
            'seats': 'Seats',
            'seat_numbers': 'Seat Numbers',
            'seat_selection': 'Seat Selection',
            
            # Other details
            'description': 'Description',
            'amenities': 'Amenities',
            'features': 'Features',
            'inclusions': 'Inclusions',
            'exclusions': 'Exclusions',
            'terms': 'Terms',
            'conditions': 'Conditions',
            'baggage_allowance': 'Baggage Allowance'
        }
        
        # Check for common details
        for field, label in common_fields.items():
            if field in self.booking_data:
                value = self.booking_data[field]
                if value and str(value).strip() and str(value).strip().lower() != 'none':
                    # Format dates if they look like dates
                    if any(date_keyword in field.lower() for date_keyword in ['date', 'time', 'check', 'pickup', 'dropoff']):
                        value = self.format_date_value(value)
                    
                    # Format price-related values
                    if any(price_keyword in field.lower() for price_keyword in ['price', 'rate', 'fare', 'cost', 'amount']):
                        value = self.format_price_value(value)
                    
                    # Handle lists (e.g., room_types, amenities)
                    if isinstance(value, list):
                        if value:
                            value = ', '.join(str(item) for item in value[:3])
                            if len(self.booking_data[field]) > 3:
                                value += f" (+{len(self.booking_data[field])-3} more)"
                        else:
                            continue  # Skip empty lists
                    
                    details.append((label, str(value)))
        
        # Add booking date from creation timestamp
        if 'created_at' in self.booking_data:
            booking_date = self.booking_data['created_at'].split()[0]
            details.append(("Booking Date", self.format_date_value(booking_date)))
        
        # Add customer info if available
        customer_fields = ['customer_name', 'customer_email', 'customer_phone']
        for field in customer_fields:
            if field in self.booking_data and self.booking_data[field]:
                label = field.replace('customer_', '').replace('_', ' ').title()
                details.append((label, str(self.booking_data[field])))
        
        return details[:6]  # Limit to 6 most important details
    
    def format_date_value(self, value):
        """Format date values consistently"""
        try:
            # Try to parse common date formats
            if isinstance(value, str):
                # Remove timezone info if present
                value = value.split('+')[0].split('Z')[0].strip()
                
                # Try different date formats
                date_formats = [
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d",
                    "%d/%m/%Y %H:%M:%S",
                    "%d/%m/%Y",
                    "%m/%d/%Y %H:%M:%S",
                    "%m/%d/%Y",
                    "%B %d, %Y %H:%M:%S",
                    "%B %d, %Y"
                ]
                
                for fmt in date_formats:
                    try:
                        date_obj = datetime.strptime(value, fmt)
                        return date_obj.strftime("%d %b %Y")
                    except ValueError:
                        continue
        except Exception:
            pass
        
        return str(value)
    
    def format_price_value(self, value):
        """Format price values consistently"""
        try:
            if isinstance(value, (int, float)):
                return f"RM {value:,.2f}"
            elif isinstance(value, str):
                # Remove currency symbols and convert to float
                cleaned = value.replace('RM', '').replace('$', '').replace(',', '').strip()
                try:
                    return f"RM {float(cleaned):,.2f}"
                except ValueError:
                    return str(value)
        except (ValueError, TypeError):
            pass
        
        return str(value)
    
    def calculate_price_summary(self):
        """Calculate price summary with detailed breakdown"""
        price_items = []
        
        # Get base price and quantity from data
        base_price = self.get_base_price()
        quantity = self.get_quantity()
        unit_label = self.get_unit_label()
        
        # FLIGHT BOOKING SPECIAL HANDLING
        if self.is_flight_booking:
            # Use flight-specific fields
            unit_price_per_passenger = self.booking_data.get('unit_price_per_passenger', base_price)
            passenger_count = self.booking_data.get('passenger_count', quantity)
            total_amount = self.booking_data.get('total_amount', 
                                               self.booking_data.get('total_price', 0))
            
            # Ensure we have the right values
            if unit_price_per_passenger is None:
                unit_price_per_passenger = base_price
            
            if passenger_count is None:
                passenger_count = quantity
            
            # Calculate total if not provided
            if total_amount == 0 and unit_price_per_passenger and passenger_count:
                total_amount = unit_price_per_passenger * passenger_count
            
            # Format prices
            try:
                unit_price_per_passenger = float(unit_price_per_passenger)
                passenger_count = int(passenger_count)
                total_amount = float(total_amount)
            except (ValueError, TypeError):
                unit_price_per_passenger = 0
                passenger_count = 0
                total_amount = 0
            
            # Show calculation breakdown
            price_items.append(("Unit Price (Passenger)", f"RM {unit_price_per_passenger:,.2f}"))
            
            if passenger_count > 1:
                subtotal = unit_price_per_passenger * passenger_count
                price_items.append((f"x {passenger_count} Passenger", f"RM {subtotal:,.2f}"))
        
        # Non-flight booking or fallback
        elif base_price is not None and quantity is not None and quantity > 1:
            subtotal = base_price * quantity
            price_items.append((f"Unit Price ({unit_label})", f"RM {base_price:.2f}"))
            price_items.append((f"× {quantity} {unit_label}", f"RM {subtotal:.2f}"))
        elif base_price is not None:
            price_items.append((f"{unit_label} Price", f"RM {base_price:.2f}"))
        
        # Add taxes and fees from data
        taxes_fees = self.get_taxes_and_fees()
        if taxes_fees > 0:
            price_items.append(("Taxes & Fees", f"RM {taxes_fees:.2f}"))
        
        # Add discounts if any
        discount = self.get_discount_amount()
        if discount > 0:
            price_items.append(("Discount", f"-RM {discount:.2f}"))
        
        return price_items
    
    def get_base_price(self):
        """Extract base price from booking data"""
        # For flight bookings, check flight-specific fields first
        if self.is_flight_booking:
            flight_price_fields = [
                'unit_price_per_passenger', 'unit_price', 'ticket_price', 
                'base_price', 'base_fare', 'fare'
            ]
            
            for field in flight_price_fields:
                if field in self.booking_data:
                    try:
                        value = self.booking_data[field]
                        if isinstance(value, (int, float)):
                            return float(value)
                        elif isinstance(value, str):
                            cleaned = value.replace('RM', '').replace('$', '').replace(',', '').strip()
                            return float(cleaned)
                    except (ValueError, TypeError):
                        continue
        
        base_price_fields = [
            'price', 'unit_price', 'ticket_price', 'room_rate', 
            'base_fare', 'daily_rate', 'rate', 'cost', 'amount'
        ]
        
        for field in base_price_fields:
            if field in self.booking_data:
                try:
                    value = self.booking_data[field]
                    if isinstance(value, (int, float)):
                        return float(value)
                    elif isinstance(value, str):
                        cleaned = value.replace('RM', '').replace('$', '').replace(',', '').strip()
                        return float(cleaned)
                except (ValueError, TypeError):
                    continue
        
        return None
    
    def get_quantity(self):
        """Extract quantity from booking data"""
        # For flight bookings, check flight-specific fields first
        if self.is_flight_booking:
            flight_quantity_fields = [
                'passenger_count', 'tickets', 'passengers'
            ]
            
            for field in flight_quantity_fields:
                if field in self.booking_data:
                    try:
                        value = self.booking_data[field]
                        if isinstance(value, (int, float)):
                            return int(value)
                        elif isinstance(value, str):
                            return int(float(value))
                    except (ValueError, TypeError):
                        continue
        
        quantity_fields = [
            'quantity', 'tickets', 'guests', 'passengers', 'rooms', 'nights', 'days', 'rental_days'
        ]
        
        for field in quantity_fields:
            if field in self.booking_data:
                try:
                    value = self.booking_data[field]
                    if isinstance(value, (int, float)):
                        return int(value)
                    elif isinstance(value, str):
                        return int(float(value))
                except (ValueError, TypeError):
                    continue
        
        # Default to 1 if not specified
        return 1
    
    def get_unit_label(self):
        """Get appropriate unit label based on booking type"""
        # Use the actual booking type from data
        actual_type = self.booking_data.get('booking_type', self.booking_type)
        
        if actual_type == "flight":
            return "Passenger"
        elif actual_type == "hotel":
            nights = self.booking_data.get('nights', 1)
            return "Night" if nights == 1 else "Nights"
        elif actual_type == "car_rental":
            days = self.booking_data.get('rental_days', 1)
            return "Day" if days == 1 else "Days"
        else:
            return "Ticket" if actual_type == "attraction" else "Unit"
    
    def get_taxes_and_fees(self):
        """Extract taxes and fees from booking data"""
        tax_fields = ['tax', 'taxes', 'service_fee', 'booking_fee']
        
        total_tax = 0.0
        
        for field in tax_fields:
            if field in self.booking_data:
                try:
                    value = self.booking_data[field]
                    if isinstance(value, (int, float)):
                        total_tax += float(value)
                    elif isinstance(value, str):
                        cleaned = value.replace('RM', '').replace('$', '').replace(',', '').strip()
                        total_tax += float(cleaned)
                except (ValueError, TypeError):
                    continue
        
        return max(0, total_tax)
    
    def get_discount_amount(self):
        """Extract discount amount from booking data"""
        discount_fields = ['discount', 'discount_amount', 'promo_discount']
        
        for field in discount_fields:
            if field in self.booking_data:
                try:
                    value = self.booking_data[field]
                    if isinstance(value, (int, float)):
                        return float(value)
                    elif isinstance(value, str):
                        cleaned = value.replace('RM', '').replace('$', '').replace(',', '').strip()
                        return float(cleaned)
                except (ValueError, TypeError):
                    continue
        
        return 0.0
    
    def get_total_amount(self):
        """Get total amount as float with proper extraction"""
        # FLIGHT BOOKING SPECIAL HANDLING
        if self.is_flight_booking:
            # Try flight-specific total fields first
            flight_total_fields = ['total_amount', 'total_price']
            
            for field in flight_total_fields:
                if field in self.booking_data:
                    try:
                        value = self.booking_data[field]
                        if isinstance(value, (int, float)):
                            return float(value)
                        elif isinstance(value, str):
                            cleaned = value.replace('RM', '').replace('$', '').replace(',', '').strip()
                            return float(cleaned)
                    except (ValueError, TypeError):
                        continue
            
            # Calculate from unit price and passenger count if available
            unit_price = self.get_base_price()
            passenger_count = self.get_quantity()
            
            if unit_price is not None and passenger_count is not None:
                return float(unit_price * passenger_count)
        
        # Original logic for non-flight bookings
        if 'total_price' in self.booking_data:
            total_str = self.booking_data['total_price']
            try:
                if isinstance(total_str, (int, float)):
                    return float(total_str)
                elif isinstance(total_str, str):
                    cleaned = total_str.replace('RM', '').replace('$', '').replace(',', '').strip()
                    return float(cleaned)
            except (ValueError, TypeError):
                pass
        
        return 0.00
    
    def get_item_name(self):
        """Get item name from booking data"""
        # Get actual booking type from data
        actual_type = self.booking_data.get('booking_type', self.booking_type)
        
        # Check for specific type fields first
        if actual_type == "car_rental":
            car_fields = ['car_model', 'car_name', 'vehicle_model', 'vehicle_name']
            for field in car_fields:
                if field in self.booking_data:
                    value = self.booking_data[field]
                    if value:
                        return str(value)
        
        elif actual_type == "hotel":
            hotel_fields = ['hotel_name', 'item_name', 'name']
            for field in hotel_fields:
                if field in self.booking_data:
                    value = self.booking_data[field]
                    if value:
                        return str(value)
        
        elif actual_type == "flight":
            flight_fields = ['flight_number', 'airline', 'item_name', 'name']
            for field in flight_fields:
                if field in self.booking_data:
                    value = self.booking_data[field]
                    if value:
                        return str(value)
        
        # Check for general name fields
        name_fields = [
            'attraction_name', 'hotel_name', 'flight_number',
            'car_model', 'car_name', 'item_name', 'name'
        ]
        
        for field in name_fields:
            if field in self.booking_data:
                value = self.booking_data[field]
                if value:
                    return str(value)
        
        # Default name based on booking type
        return f"{actual_type.replace('_', ' ').title()} Booking"
    
    def create_information_form(self, parent):
        """Create user information form with pre-filled data if available"""
        container = tk.Frame(parent, bg="white", padx=20, pady=20,
                           relief="solid", borderwidth=1)
        container.pack(fill="both", expand=True)
        
        # Use actual booking type from data
        actual_type = self.booking_data.get('booking_type', self.booking_type)
        
        if actual_type == "flight":
            self.create_flight_passenger_form(container)
        else:
            self.create_regular_form(container)
    
    def create_regular_form(self, parent):
        """Create regular form for non-flight bookings"""
        tk.Label(parent, text="📝 Complete Your Booking",
                font=("Arial", 18, "bold"),
                bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(0, 20))
        
        form_container = tk.Frame(parent, bg="white")
        form_container.pack(fill="both", expand=True)
        
        self.form_data = {}
        form_fields = [
            ("Full Name", "text"),
            ("Email", "text"),
            ("Phone Number", "text"),
            ("Special Requests", "text"),
        ]
        
        for i, (label, field_type) in enumerate(form_fields):
            label_widget = tk.Label(form_container, text=f"{label}:", font=("Arial", 12),
                                  bg="white", fg=self.colors["dark"])
            label_widget.grid(row=i, column=0, sticky="w", pady=10, padx=(0, 10))
            
            if field_type == "text":
                entry = tk.Entry(form_container, font=("Arial", 12),
                               bg="#f9f9f9", relief="solid", borderwidth=1)
                entry.grid(row=i, column=1, sticky="ew", pady=10, padx=(0, 10))
                
                self.prefill_form_field(label, entry)
                self.form_data[label] = entry
        
        form_container.grid_columnconfigure(1, weight=1)
        
        tk.Frame(parent, height=2, bg=self.colors["border"]).pack(fill="x", pady=20)
        
        info_frame = tk.Frame(parent, bg="#f0f8ff", padx=15, pady=15)
        info_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(info_frame, text="ℹ️ Important:",
                font=("Arial", 12, "bold"),
                bg="#f0f8ff", fg=self.colors["primary"]).pack(anchor="w", pady=(0, 10))
        
        info_text = self.get_info_text()
        tk.Label(info_frame, text=info_text, font=("Arial", 11),
                bg="#f0f8ff", fg=self.colors["dark"],
                wraplength=400, justify="left").pack(anchor="w")
    
    def create_flight_passenger_form(self, parent):
        """Create flight passenger form"""
        tk.Label(parent, text="✈️ Passenger Information",
                font=("Arial", 18, "bold"),
                bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(0, 15))
        
        total_passengers = self.booking_data.get('tickets', 1)
        adults = self.booking_data.get('adults', 1)
        children = self.booking_data.get('children', 0)
        
        info_text = f"Total Passengers: {total_passengers} ({adults} Adult(s), {children} Child(ren))"
        tk.Label(parent, text=info_text,
                font=("Arial", 12),
                bg="white", fg=self.colors["secondary"]).pack(anchor="w", pady=(0, 10))
        
        canvas_frame = tk.Frame(parent, bg="white")
        canvas_frame.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        headers_frame = tk.Frame(scrollable_frame, bg="#f0f8ff")
        headers_frame.pack(fill="x", pady=(0, 10))
        
        headers = ["No.", "Type", "Full Name *", "Passport No. *"]
        widths = [40, 80, 180, 150]
        
        for i, header in enumerate(headers):
            tk.Label(headers_frame, text=header,
                    font=("Arial", 11, "bold"),
                    bg="#f0f8ff", fg=self.colors["primary"],
                    padx=5, pady=8, width=widths[i]//10).pack(side="left")
        
        self.passenger_entries = []
        
        for i in range(total_passengers):
            passenger_frame = tk.Frame(scrollable_frame, bg="white")
            passenger_frame.pack(fill="x", pady=5)
            
            tk.Label(passenger_frame, text=f"{i+1}.",
                    font=("Arial", 11),
                    bg="white", fg=self.colors["dark"],
                    width=4).pack(side="left", padx=(5, 0))
            
            passenger_type = "Adult" if i < adults else "Child"
            type_label = tk.Label(passenger_frame, text=passenger_type,
                                font=("Arial", 11),
                                bg="white", fg=self.colors["dark"],
                                width=8)
            type_label.pack(side="left", padx=5)
            
            name_entry = tk.Entry(passenger_frame,
                                font=("Arial", 11),
                                bg="#f9f9f9", relief="solid", borderwidth=1,
                                width=25)
            name_entry.pack(side="left", padx=5)
            
            passport_entry = tk.Entry(passenger_frame,
                                    font=("Arial", 11),
                                    bg="#f9f9f9", relief="solid", borderwidth=1,
                                    width=20)
            passport_entry.pack(side="left", padx=5)
            
            self.passenger_entries.append({
                "number": i+1,
                "type": passenger_type,
                "name_entry": name_entry,
                "passport_entry": passport_entry
            })
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tk.Frame(parent, height=2, bg=self.colors["border"]).pack(fill="x", pady=20)
        
        tk.Label(parent, text="📞 Contact Information",
                font=("Arial", 14, "bold"),
                bg="white", fg=self.colors["primary"]).pack(anchor="w", pady=(0, 15))
        
        contact_frame = tk.Frame(parent, bg="white")
        contact_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(contact_frame, text="Email *:", font=("Arial", 12),
                bg="white", fg=self.colors["dark"], width=8, anchor="w").pack(side="left")
        self.email_entry = tk.Entry(contact_frame, font=("Arial", 12),
                                  bg="#f9f9f9", relief="solid", borderwidth=1, width=30)
        self.email_entry.pack(side="left", padx=(10, 0))
        self.email_entry.insert(0, self.email)
        
        tk.Label(contact_frame, text="Phone *:", font=("Arial", 12),
                bg="white", fg=self.colors["dark"], width=8, anchor="w").pack(side="left", padx=(20, 0))
        self.phone_entry = tk.Entry(contact_frame, font=("Arial", 12),
                                  bg="#f9f9f9", relief="solid", borderwidth=1, width=30)
        self.phone_entry.pack(side="left", padx=(10, 0))
        
        tk.Label(parent, text="Special Requests:", font=("Arial", 12),
                bg="white", fg=self.colors["dark"]).pack(anchor="w", pady=(15, 5))
        self.special_requests_entry = tk.Text(parent, font=("Arial", 11),
                                            bg="#f9f9f9", relief="solid", borderwidth=1,
                                            height=3, width=50)
        self.special_requests_entry.pack(fill="x", pady=(0, 10))
    
    def prefill_form_field(self, label, entry_widget):
        """Pre-fill form field with existing data"""
        field_mapping = {
            "Full Name": ['customer_name', 'name', 'full_name', 'user_name'],
            "Email": ['email', 'user_email', 'contact_email'],
            "Phone Number": ['phone', 'phone_number', 'contact_phone', 'mobile'],
            "Special Requests": ['special_requests', 'requests', 'notes', 'remarks', 'comments']
        }
        
        if label in field_mapping:
            for field in field_mapping[label]:
                if field in self.booking_data:
                    value = self.booking_data[field]
                    if value:
                        entry_widget.insert(0, str(value))
                        if label == "Email" and self.booking_data.get('status') in ['confirmed', 'completed', 'paid']:
                            entry_widget.config(state="readonly")
                        break
    
    def get_type_icon(self, booking_type=None):
        """Get icon for booking type"""
        if booking_type is None:
            booking_type = self.booking_data.get('booking_type', self.booking_type)
            
        icons = {
            "attraction": "🎫",
            "hotel": "🏨",
            "flight": "✈️",
            "car_rental": "🚗",
            "tour": "🚌",
            "restaurant": "🍽️",
            "event": "🎭"
        }
        return icons.get(booking_type, "📋")
    
    def get_info_text(self):
        """Get information text based on booking status"""
        status = self.booking_data.get('status', 'pending')
        
        if status == 'pending':
            return "Please ensure all information is correct before proceeding to payment."
        elif status == 'confirmed' or status == 'paid':
            # Use actual booking type from data
            actual_type = self.booking_data.get('booking_type', self.booking_type)
            item_type = actual_type.replace('_', ' ')
            return f"Your {item_type} booking has been confirmed! You will receive an email confirmation shortly."
        elif status == 'completed':
            return "This booking has been completed. Thank you for choosing our service!"
        elif status == 'cancelled':
            return "This booking has been cancelled. Any refunds will be processed within 5-7 business days."
        return ""
    
    def create_footer(self):
        """Create footer with ONLY Cancel and Confirm & Pay buttons for ALL booking types"""
        footer = tk.Frame(self.root, bg=self.colors["light"], height=80)
        footer.pack(fill="x", side="bottom")
        
        button_frame = tk.Frame(footer, bg=self.colors["light"])
        button_frame.pack(pady=15)
        
        # Show only Cancel and Confirm & Pay buttons regardless of status
        tk.Button(button_frame, text="Cancel Booking",
                 font=("Arial", 12),
                 bg="#f5f5f5", fg=self.colors["dark"],
                 relief="solid", cursor="hand2",
                 command=self.cancel_booking,
                 padx=25, pady=8).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Confirm & Pay",
                 font=("Arial", 12, "bold"),
                 bg=self.colors["primary"], fg="white",
                 relief="solid", cursor="hand2",
                 command=self.confirm_payment,
                 padx=30, pady=8).pack(side="left", padx=5)
    
    def confirm_payment(self):
        """Validate information and proceed to payment"""
        if self.is_flight_booking:
            return self.validate_flight_passengers_and_proceed()
        else:
            return self.validate_regular_booking_and_proceed()
    
    def validate_flight_passengers_and_proceed(self):
        """Validate flight passenger information and proceed to payment"""
        missing_passengers = []
        for passenger in self.passenger_entries:
            name = passenger["name_entry"].get().strip()
            passport = passenger["passport_entry"].get().strip()
            
            if not name:
                missing_passengers.append(f"Passenger {passenger['number']} (name)")
            if not passport:
                missing_passengers.append(f"Passenger {passenger['number']} (passport)")
        
        if missing_passengers:
            messagebox.showwarning("Missing Information", 
                                 "Please fill in for:\n" + "\n".join(missing_passengers))
            return
        
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        
        if not email or "@" not in email:
            messagebox.showwarning("Invalid Email", "Please enter a valid email address")
            return
        
        if not phone:
            messagebox.showwarning("Missing Phone", "Please enter phone number")
            return
        
        passenger_data_list = []
        for passenger in self.passenger_entries:
            passenger_data = {
                "passenger_number": passenger['number'],
                "passenger_type": passenger['type'],
                "full_name": passenger["name_entry"].get().strip(),
                "passport_number": passenger["passport_entry"].get().strip()
            }
            passenger_data_list.append(passenger_data)
        
        self.booking_data['passengers'] = passenger_data_list
        self.booking_data['email'] = email
        self.booking_data['phone'] = phone
        self.booking_data['customer_name'] = passenger_data_list[0]["full_name"]
        self.booking_data['special_requests'] = self.special_requests_entry.get("1.0", tk.END).strip()
        
        payment_data = {
            "booking_id": self.booking_data['booking_id'],
            "booking_type": self.booking_data.get('booking_type', self.booking_type),
            "item_name": self.get_item_name(),
            "total_price": float(self.get_total_amount()),
            "status": "pending",
            "created_at": self.booking_data.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "booking_data": self.booking_data,
            "customer_info": {
                'name': passenger_data_list[0]["full_name"],
                'email': email,
                'phone': phone
            }
        }
        
        for key, value in self.booking_data.items():
            if key not in payment_data:
                payment_data[key] = value
        
        self.root.destroy()
        
        try:
            from payment import show_payment_window
        except ImportError as e:
            messagebox.showwarning("Payment Module", 
                                 f"Payment module not found: {str(e)}")
            return
        
        def after_payment(updated_booking=None):
            if updated_booking:
                messagebox.showinfo("Payment Complete", 
                                  f"Flight booking completed successfully!\n"
                                  f"Booking #{updated_booking.get('booking_id')} confirmed.")
            else:
                messagebox.showinfo("Payment Complete", 
                                  f"Flight booking completed successfully!\n"
                                  f"Booking #{self.booking_data['booking_id']} confirmed.")
            
            if self.callback:
                self.callback(self.booking_data)
        
        show_payment_window(
            email, 
            payment_data, 
            after_payment
        )
    
    def validate_regular_booking_and_proceed(self):
        """Validate regular booking information and proceed to payment"""
        required_fields = ["Full Name", "Email", "Phone Number"]
        missing_fields = []
        
        for field in required_fields:
            widget = self.form_data.get(field)
            if isinstance(widget, tk.Entry):
                if not widget.get().strip():
                    missing_fields.append(field)
        
        if missing_fields:
            messagebox.showwarning("Missing Information", 
                                 f"Please fill in: {', '.join(missing_fields)}")
            return False
        
        user_info = {}
        for label, widget in self.form_data.items():
            if isinstance(widget, tk.Entry):
                user_info[label] = widget.get()
        
        self.booking_data['customer_name'] = user_info.get('Full Name', '')
        self.booking_data['email'] = user_info.get('Email', '')
        self.booking_data['phone'] = user_info.get('Phone Number', '')
        self.booking_data['special_requests'] = user_info.get('Special Requests', '')
        
        payment_data = {
            "booking_id": self.booking_data['booking_id'],
            "booking_type": self.booking_data.get('booking_type', self.booking_type),
            "item_name": self.get_item_name(),
            "total_price": float(self.get_total_amount()),
            "status": "pending",
            "created_at": self.booking_data.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "booking_data": self.booking_data,
            "customer_info": {
                'name': user_info.get('Full Name', ''),
                'email': user_info.get('Email', ''),
                'phone': user_info.get('Phone Number', '')
            }
        }
        
        for key, value in self.booking_data.items():
            if key not in payment_data:
                payment_data[key] = value
        
        self.root.destroy()
        
        try:
            from payment import show_payment_window
        except ImportError as e:
            messagebox.showwarning("Payment Module", 
                                 f"Payment module not found: {str(e)}")
            return
        
        def after_payment(updated_booking=None):
            if updated_booking:
                messagebox.showinfo("Payment Complete", 
                                  f"Booking completed successfully!\n"
                                  f"Booking #{updated_booking.get('booking_id')} confirmed.")
            else:
                messagebox.showinfo("Payment Complete", 
                                  f"Booking completed successfully!\n"
                                  f"Booking #{self.booking_data['booking_id']} confirmed.")
            
            if self.callback:
                self.callback(self.booking_data)
        
        show_payment_window(
            user_info.get('Email', self.email), 
            payment_data, 
            after_payment
        )
        
        return True
    
    def cancel_booking(self):
        """Cancel booking"""
        if messagebox.askyesno("Cancel Booking", 
                              "Are you sure you want to cancel this booking?"):
            self.booking_data['status'] = 'cancelled'
            messagebox.showinfo("Cancelled", "Booking has been cancelled.")
            self.root.destroy()
    
    def go_back(self):
        """Go back to previous screen"""
        self.root.destroy()
    
    def on_close(self):
        """Handle window close event"""
        self.root.destroy()


def show_booking_detail_window(booking_data, email="", booking_type="attraction", callback=None):
    """Main function to show booking detail window
    
    Args:
        booking_data: Dictionary containing booking information
        email: Customer email address
        booking_type: Type of booking (attraction, hotel, flight, car_rental)
        callback: Callback function to execute after booking is complete
    """
    root = tk.Tk()
    app = BookingDetailApp(root, booking_data, email, booking_type, callback)
    root.mainloop()


def main():
    """Main entry point when script is run directly"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Booking Detail Application')
    parser.add_argument('--data', type=str, help='Path to booking data JSON file')
    args = parser.parse_args()
    
    # Load booking data from file
    if args.data and os.path.exists(args.data):
        try:
            with open(args.data, 'r', encoding='utf-8') as f:
                booking_data = json.load(f)
            
            # Determine booking type from data
            booking_type = booking_data.get('booking_type', 'attraction')
            
            # Get email from data
            email = booking_data.get('user_email', booking_data.get('email', ''))
            
            root = tk.Tk()
            app = BookingDetailApp(root, booking_data, email, booking_type)
            root.mainloop()
            
            # Clean up temp file
            try:
                os.remove(args.data)
            except:
                pass
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load booking data: {str(e)}")
    else:
        messagebox.showerror("Error", "No booking data file provided")


if __name__ == "__main__":
    main()