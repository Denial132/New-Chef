import pygame
import os
import random
import json
import sys

# --- Initialize Pygame Engine ---
pygame.init()
pygame.mixer.init()

# --- Music Volume Configuration ---
current_music_volume = 0.5

# --- Load and Play Background Music ---
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

music_path = os.path.join(
    BASE_DIR,
    "assests",
    "Background",
    "Bacground Music.mp3"
)

try:
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.set_volume(current_music_volume)
    pygame.mixer.music.play(-1)
except Exception as e:
    print("Music Loading Error:", e)

# --- Absolute File Path Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FILE_PATH = os.path.join(SCRIPT_DIR, "save.json")

# --- Window Configurations ---
WIDTH, HEIGHT = 1100, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("New Chef: First Edition")

# --- UI Typography Elements ---
header_font = pygame.font.SysFont("Arial", 26, bold=True)
hud_font = pygame.font.SysFont("Arial", 18, bold=True)
controls = pygame.font.SysFont("Arial", 18, bold=True)
small_font = pygame.font.SysFont("Arial", 14, bold=True)

# --- Game Economics & Metrics ---
money = 50
customers_served = 0
day_number = 1
daily_target = 100

shift_duration = 120000  # 2-minute daily shift timer (in ms)
shift_start_time = pygame.time.get_ticks()

# --- Upgrades System Flags ---
fast_grill_upgrade = False
fast_fryer_upgrade = False
fast_drink_upgrade = False
anti_burn_upgrade = False

# --- Ordered List of Game Areas for Navigation ---
game_areas = [
    "Customer Counter",
    "Grill & Stock Delivery",
    "Drink Station",
    "Fries Station",
    "Chef Wardrobe",
    "Ordering Area",
    "Settings Area"
]

# --- Wardrobe Customisation Catalog ---
current_wardrobe_tab = "Aprons"
wardrobe_tabs = ["Aprons", "Hats", "Shirts"]

equipped_outfits = {
    "Aprons": "Standard White Apron",
    "Hats": "Classic Chef Hat",
    "Shirts": "Standard Chef Coat"
}

owned_outfits = [
    "Standard White Apron", 
    "Classic Chef Hat", 
    "Standard Chef Coat"
]

wardrobe_catalog = [
    # --- Aprons (Extra Tip per order) ---
    {"name": "Standard White Apron", "category": "Aprons", "price": 0, "color": (240, 240, 240), "buff_type": "extra_tip", "buff_value": 0, "desc": "No tip bonus"},
    {"name": "Golden Apron", "category": "Aprons", "price": 200, "color": (230, 180, 0), "buff_type": "extra_tip", "buff_value": 2, "desc": "+$2 Extra Tip per order"},
    {"name": "Master Black Apron", "category": "Aprons", "price": 500, "color": (40, 40, 40), "buff_type": "extra_tip", "buff_value": 5, "desc": "+$5 Extra Tip per order"},
    
    # --- Hats (Higher chance of VIP customers) ---
    {"name": "Classic Chef Hat", "category": "Hats", "price": 0, "color": (240, 240, 240), "buff_type": "vip_chance", "buff_value": 0.0, "desc": "Standard VIP chance"},
    {"name": "Golden Crown Hat", "category": "Hats", "price": 150, "color": (230, 180, 0), "buff_type": "vip_chance", "buff_value": 0.10, "desc": "+10% higher VIP chance"},
    {"name": "Black Beanie", "category": "Hats", "price": 300, "color": (40, 40, 40), "buff_type": "vip_chance", "buff_value": 0.20, "desc": "+20% higher VIP chance"},

    # --- Shirts (Percentage higher payment) ---
    {"name": "Standard Chef Coat", "category": "Shirts", "price": 0, "color": (240, 240, 240), "buff_type": "pay_multiplier", "buff_value": 0.0, "desc": "Standard payment rate"},
    {"name": "Golden Vest", "category": "Shirts", "price": 250, "color": (230, 180, 0), "buff_type": "pay_multiplier", "buff_value": 0.05, "desc": "+5% higher payment"},
    {"name": "Executive Dark Shirt", "category": "Shirts", "price": 450, "color": (40, 40, 40), "buff_type": "pay_multiplier", "buff_value": 0.10, "desc": "+10% higher payment"}
]

# --- Food Holding Tray Staging Variables ---
tray_burgers = 0
tray_fries = 0
tray_drinks = 0

# --- Raw Inventory Stock Counts ---
burger_stock = 1
fries_stock = 1
drink_stock = 1

# --- Navigation Setup ---
current_area = "Customer Counter"
running = True
clock = pygame.time.Clock()

# --- Slider State Tracking for Volume Control ---
dragging_slider = False

# --- Customer Order Combinations ---
single_orders = ["Burger", "Fries", "Drink"]
combo_orders = [
    ["Burger", "Fries"],
    ["Burger", "Drink"],
    ["Fries", "Drink"],
    ["Burger", "Fries", "Drink"]
]

# --- Progressive Unlock Prices ---
grill_unlock_costs = [0, 50, 100, 150, 200, 250, 300, 350]
fryer_unlock_costs = [0, 75, 150, 225]
drink_unlock_costs = [0, 175, 275, 375]

# --- Wholesale Ingredient Inventory & Equipment Catalog ---
supplies = [
    ("Burger Supplies", 20), ("Fries Supplies", 15), ("Drink Supplies", 20), ("Cheese Supplies", 10),
    ("Meat Supplies", 30), ("Bun Supplies", 25), ("Sauce Supplies", 5), ("Box Supplies", 5),
    ("Fast Grills", 150), ("Fast Fryers", 150), ("Fast Drinks", 200), ("Anti-Burn Tech", 250)
]

# --- Graphical Grid Placement Constraints ---
button_width, button_height = 204, 120
spacing_x, spacing_y = 20, 20
start_x, start_y = 40, 110

# --- Logistics Delivery Pipeline Tracking ---
delivery_in_progress = False
delivery_time = 5000
delivery_start = 0

pending_burgers = 0
pending_fries = 0
pending_drinks = 0
delivery_message = ""

# --- Customer Spawning & Queue Parameters ---
base_patience = 45000
customer_queue = []
max_queue_length = 3
queue_spawn_time = 6000
last_queue_spawn = pygame.time.get_ticks()

# --- Kitchen Appliance Status Matrices ---
grills_status = [
    {"cooking": False, "ready": False, "burnt": False, "start": 0, "unlocked": True, "time": 3000, "burn": 7000, "cleanliness": 100, "cleaning": False},
    {"cooking": False, "ready": False, "burnt": False, "start": 0, "unlocked": False, "time": 3000, "burn": 7000, "cleanliness": 100, "cleaning": False},
    {"cooking": False, "ready": False, "burnt": False, "start": 0, "unlocked": False, "time": 3000, "burn": 7000, "cleanliness": 100, "cleaning": False},
    {"cooking": False, "ready": False, "burnt": False, "start": 0, "unlocked": False, "time": 3000, "burn": 7000, "cleanliness": 100, "cleaning": False},
    {"cooking": False, "ready": False, "burnt": False, "start": 0, "unlocked": False, "time": 3000, "burn": 7000, "cleanliness": 100, "cleaning": False},
    {"cooking": False, "ready": False, "burnt": False, "start": 0, "unlocked": False, "time": 3000, "burn": 7000, "cleanliness": 100, "cleaning": False},
    {"cooking": False, "ready": False, "burnt": False, "start": 0, "unlocked": False, "time": 3000, "burn": 7000, "cleanliness": 100, "cleaning": False},
    {"cooking": False, "ready": False, "burnt": False, "start": 0, "unlocked": False, "time": 3000, "burn": 7000, "cleanliness": 100, "cleaning": False}
]

fryers_status = [
    {"cooking": False, "ready": False, "burnt": False, "start": 0, "unlocked": True, "time": 4000, "burn": 9000, "cleanliness": 100, "cleaning": False},
    {"cooking": False, "ready": False, "burnt": False, "start": 0, "unlocked": False, "time": 4000, "burn": 9000, "cleanliness": 100, "cleaning": False},
    {"cooking": False, "ready": False, "burnt": False, "start": 0, "unlocked": False, "time": 4000, "burn": 9000, "cleanliness": 100, "cleaning": False},
    {"cooking": False, "ready": False, "burnt": False, "start": 0, "unlocked": False, "time": 4000, "burn": 9000, "cleanliness": 100, "cleaning": False}
]

drinks_status = [
    {"dispensing": False, "ready": False, "start": 0, "unlocked": True, "cleanliness": 100, "cleaning": False},
    {"dispensing": False, "ready": False, "start": 0, "unlocked": False, "cleanliness": 100, "cleaning": False},
    {"dispensing": False, "ready": False, "start": 0, "unlocked": False, "cleanliness": 100, "cleaning": False},
    {"dispensing": False, "ready": False, "start": 0, "unlocked": False, "cleanliness": 100, "cleaning": False}
]

# --- Helper Clothing Buff Function ---
def get_equipped_buff(buff_type):
    for category, item_name in equipped_outfits.items():
        for item in wardrobe_catalog:
            if item["name"] == item_name and item.get("buff_type") == buff_type:
                return item.get("buff_value", 0)
    return 0

# --- Persistent File Storage Save System ---
def save_game():
    global money, customers_served, burger_stock, fries_stock, drink_stock, tray_burgers, tray_fries, tray_drinks
    global fast_grill_upgrade, fast_fryer_upgrade, fast_drink_upgrade, anti_burn_upgrade, day_number, daily_target, equipped_outfits, owned_outfits, current_music_volume
    save_data = {
        "money": money, 
        "customers_served": customers_served,
        "day_number": day_number,
        "daily_target": daily_target,
        "burger_stock": burger_stock, 
        "fries_stock": fries_stock, 
        "drink_stock": drink_stock,
        "tray_burgers": tray_burgers,
        "tray_fries": tray_fries,
        "tray_drinks": tray_drinks,
        "music_volume": current_music_volume,
        "upgrades": {
            "fast_grills": fast_grill_upgrade,
            "fast_fryers": fast_fryer_upgrade,
            "fast_drinks": fast_drink_upgrade,
            "anti_burn": anti_burn_upgrade
        },
        "wardrobe": {
            "equipped": equipped_outfits,
            "owned": owned_outfits
        },
        "grills": [{"unlocked": g["unlocked"], "cleanliness": g["cleanliness"]} for g in grills_status], 
        "fryers": [{"unlocked": f["unlocked"], "cleanliness": f["cleanliness"]} for f in fryers_status],
        "drink_unlocks": [{"unlocked": d["unlocked"], "cleanliness": d["cleanliness"]} for d in drinks_status]
    }
    try:
        with open(SAVE_FILE_PATH, "w") as f:
            json.dump(save_data, f, indent=4)
    except Exception as e:
        print("Save Error:", e)

def load_game():
    global money, customers_served, burger_stock, fries_stock, drink_stock, tray_burgers, tray_fries, tray_drinks
    global fast_grill_upgrade, fast_fryer_upgrade, fast_drink_upgrade, anti_burn_upgrade, day_number, daily_target, equipped_outfits, owned_outfits, current_music_volume
    if os.path.exists(SAVE_FILE_PATH):
        try:
            with open(SAVE_FILE_PATH, "r") as f:
                save_data = json.load(f)
            money = save_data.get("money", 50)
            customers_served = save_data.get("customers_served", 0)
            day_number = save_data.get("day_number", 1)
            daily_target = save_data.get("daily_target", 100)
            burger_stock = save_data.get("burger_stock", 1)
            fries_stock = save_data.get("fries_stock", 1)
            drink_stock = save_data.get("drink_stock", 1)
            tray_burgers = save_data.get("tray_burgers", 0)
            tray_fries = save_data.get("tray_fries", 0)
            tray_drinks = save_data.get("tray_drinks", 0)
            current_music_volume = save_data.get("music_volume", 0.5)
            pygame.mixer.music.set_volume(current_music_volume)
            
            upgrades = save_data.get("upgrades", {})
            fast_grill_upgrade = upgrades.get("fast_grills", False)
            fast_fryer_upgrade = upgrades.get("fast_fryers", False)
            fast_drink_upgrade = upgrades.get("fast_drinks", False)
            anti_burn_upgrade = upgrades.get("anti_burn", False)

            wardrobe = save_data.get("wardrobe", {})
            if isinstance(wardrobe.get("equipped"), dict):
                equipped_outfits.update(wardrobe.get("equipped"))
            owned_outfits = wardrobe.get("owned", owned_outfits)

            saved_grills = save_data.get("grills", [])
            saved_fryers = save_data.get("fryers", [])
            saved_drinks = save_data.get("drink_unlocks", [])

            for idx, gdata in enumerate(saved_grills):
                if idx < len(grills_status) and isinstance(gdata, dict):
                    grills_status[idx]["unlocked"] = gdata.get("unlocked", False)
                    grills_status[idx]["cleanliness"] = gdata.get("cleanliness", 100)

            for idx, fdata in enumerate(saved_fryers):
                if idx < len(fryers_status) and isinstance(fdata, dict):
                    fryers_status[idx]["unlocked"] = fdata.get("unlocked", False)
                    fryers_status[idx]["cleanliness"] = fdata.get("cleanliness", 100)

            for idx, ddata in enumerate(saved_drinks):
                if idx < len(drinks_status):
                    if isinstance(ddata, dict):
                        drinks_status[idx]["unlocked"] = ddata.get("unlocked", False)
                        drinks_status[idx]["cleanliness"] = ddata.get("cleanliness", 100)
                    else:
                        drinks_status[idx]["unlocked"] = ddata
        except Exception as e:
            print("Load Error:", e)
    else:
        save_game()

load_game()

# --- Core Game Engine Process Helpers ---
def spawn_customer():
    if len(customer_queue) < max_queue_length:
        vip_bonus = get_equipped_buff("vip_chance")
        vip_weight = 20 + int(vip_bonus * 100)
        regular_weight = max(10, 60 - int(vip_bonus * 100))
        
        c_type = random.choices(["Regular", "VIP", "Easygoing"], weights=[regular_weight, vip_weight, 20])[0]
        
        if c_type == "VIP":
            patience = base_patience * 0.5
        elif c_type == "Easygoing":
            patience = base_patience * 1.5
        else:
            patience = base_patience

        is_combo = random.random() < 0.4
        if is_combo:
            items = random.choice(combo_orders)
        else:
            items = [random.choice(single_orders)]

        new_customer = {
            "type": c_type,
            "items": items,
            "patience": patience,
            "start_time": pygame.time.get_ticks()
        }
        customer_queue.append(new_customer)

def check_and_fulfill_order(customer):
    global tray_burgers, tray_fries, tray_drinks, money
    
    req_b = customer["items"].count("Burger")
    req_f = customer["items"].count("Fries")
    req_d = customer["items"].count("Drink")

    if tray_burgers >= req_b and tray_fries >= req_f and tray_drinks >= req_d:
        tray_burgers -= req_b
        tray_fries -= req_f
        tray_drinks -= req_d

        base_payout = (req_b * 15) + (req_f * 6) + (req_d * 4)

        if len(customer["items"]) > 1:
            base_payout += 10

        if customer["type"] == "VIP":
            base_payout *= 2

        elapsed = pygame.time.get_ticks() - customer["start_time"]
        patience_pct = max(0.0, 1.0 - (elapsed / customer["patience"]))
        if patience_pct >= 0.8:
            base_payout += 5

        extra_tip = get_equipped_buff("extra_tip")
        base_payout += extra_tip

        pay_mult = get_equipped_buff("pay_multiplier")
        if pay_mult > 0:
            base_payout *= (1.0 + pay_mult)

        money += int(base_payout)
        return True
    return False

def reject_customer():
    global customer_queue
    if len(customer_queue) > 0:
        customer_queue.pop(0)

def evaluate_grill_press(index):
    global money, burger_stock, tray_burgers
    g = grills_status[index]
    if not g["unlocked"]:
        if money >= grill_unlock_costs[index]:
            money -= grill_unlock_costs[index]
            g["unlocked"] = True
    elif g["cleanliness"] <= 0:
        return
    elif g["ready"]:
        g["ready"] = False
        tray_burgers += 1
    elif burger_stock > 0 and not g["cooking"] and not g["burnt"] and not g["cleaning"]:
        burger_stock -= 1
        g["cooking"], g["burnt"], g["start"] = True, False, pygame.time.get_ticks()
        g["cleanliness"] = max(0, g["cleanliness"] - 10)

def evaluate_fryer_press(index):
    global money, fries_stock, tray_fries
    f = fryers_status[index]
    if not f["unlocked"]:
        if money >= fryer_unlock_costs[index]:
            money -= fryer_unlock_costs[index]
            f["unlocked"] = True
    elif f["cleanliness"] <= 0:
        return
    elif f["ready"]:
        f["ready"] = False
        tray_fries += 1
    elif fries_stock > 0 and not f["cooking"] and not f["burnt"] and not f["cleaning"]:
        fries_stock -= 1
        f["cooking"], f["burnt"], f["start"] = True, False, pygame.time.get_ticks()
        f["cleanliness"] = max(0, f["cleanliness"] - 10)

def evaluate_drink_press(index):
    global money, drink_stock, tray_drinks
    d = drinks_status[index]
    if not d["unlocked"]:
        if money >= drink_unlock_costs[index]:
            money -= drink_unlock_costs[index]
            d["unlocked"] = True
    elif d["cleanliness"] <= 0:
        return
    elif d["ready"]:
        d["ready"] = False
        tray_drinks += 1
    elif drink_stock > 0 and not d["dispensing"] and not d["cleaning"]:
        drink_stock -= 1
        d["dispensing"] = True
        d["start"] = pygame.time.get_ticks()
        d["cleanliness"] = max(0, d["cleanliness"] - 10)

def run_timer_matrix(current_time):
    global running, money, last_queue_spawn, customer_queue, shift_start_time, day_number, daily_target

    if current_time - shift_start_time >= shift_duration:
        shift_start_time = current_time
        if money >= daily_target:
            money += 50
            day_number += 1
            daily_target = max(100, daily_target + 20)
            save_game()

    if current_time - last_queue_spawn >= queue_spawn_time:
        spawn_customer()
        last_queue_spawn = current_time

    expired_customers = []
    for idx, c in enumerate(customer_queue):
        if current_time - c["start_time"] >= c["patience"]:
            expired_customers.append(idx)
    for idx in reversed(expired_customers):
        customer_queue.pop(idx)
        money = max(0, money - 5)

    grill_cook_speed = 1500 if fast_grill_upgrade else 3000
    
    for g in grills_status:
        if g["unlocked"]:
            if g["cleaning"]:
                if g["cleanliness"] >= 100:
                    g["cleaning"] = False
                    g["burnt"] = False
            elif g["cooking"]:
                elapsed = current_time - g["start"]
                if not anti_burn_upgrade and elapsed >= g["burn"]: 
                    g["cooking"], g["ready"], g["burnt"] = False, False, True
                    g["cleanliness"] = max(0, g["cleanliness"] - 30)
                elif elapsed >= grill_cook_speed and not g["ready"]: 
                    g["cooking"], g["ready"] = False, True

    fryer_cook_speed = 2000 if fast_fryer_upgrade else 4000
    for f in fryers_status:
        if f["unlocked"]:
            if f["cleaning"]:
                if f["cleanliness"] >= 100:
                    f["cleaning"] = False
                    f["burnt"] = False
            elif f["cooking"]:
                elapsed = current_time - f["start"]
                if not anti_burn_upgrade and elapsed >= f["burn"]: 
                    f["cooking"] = False
                    f["ready"] = False
                    f["burnt"] = True
                    f["cleanliness"] = max(0, f["cleanliness"] - 30)
                elif elapsed >= fryer_cook_speed and not f["ready"]: 
                    f["cooking"] = False
                    f["ready"] = True

    drink_pour_speed = 1000 if fast_drink_upgrade else 2000
    for d in drinks_status:
        if d["unlocked"]:
            if d["cleaning"]:
                if d["cleanliness"] >= 100:
                    d["cleaning"] = False
            elif d["dispensing"]:
                if current_time - d["start"] >= drink_pour_speed:
                    d["dispensing"], d["ready"] = False, True

    global delivery_in_progress, delivery_start, burger_stock, fries_stock, drink_stock, delivery_message, pending_burgers, pending_fries, pending_drinks
    if delivery_in_progress and current_time - delivery_start >= delivery_time:
        delivery_in_progress = False
        burger_stock += pending_burgers
        fries_stock += pending_fries
        drink_stock += pending_drinks
        pending_burgers, pending_fries, pending_drinks = 0, 0, 0
        delivery_message = "Delivery arrived!"

# --- Main Runtime Game Loop ---
while running:
    current_time = pygame.time.get_ticks()
    canvas_rect = pygame.Rect(40, 135, 1020, 490)
    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()

    # --- Continuous Mouse Dragging Check for Rubbing/Cleaning Stations ---
    if mouse_pressed[0]:
        if current_area == "Grill & Stock Delivery":
            for i in range(8):
                row, col = i // 4, i % 4
                g_rect = pygame.Rect(70 + (col * 240), 150 + (row * 145), 220, 120)
                if g_rect.collidepoint(mouse_pos):
                    g = grills_status[i]
                    if g["unlocked"] and not g["cooking"] and g["cleanliness"] < 100:
                        g["cleaning"] = True
                        g["cleanliness"] = min(100, g["cleanliness"] + 2)

        elif current_area == "Fries Station":
            for i in range(4):
                f_rect = pygame.Rect(70 + (i * 245), 180, 220, 240)
                if f_rect.collidepoint(mouse_pos):
                    f = fryers_status[i]
                    if f["unlocked"] and not f["cooking"] and f["cleanliness"] < 100:
                        f["cleaning"] = True
                        f["cleanliness"] = min(100, f["cleanliness"] + 2)

        elif current_area == "Drink Station":
            for i in range(4):
                d_rect = pygame.Rect(70 + (i * 245), 160, 220, 360)
                if d_rect.collidepoint(mouse_pos):
                    d = drinks_status[i]
                    if d["unlocked"] and not d["dispensing"] and d["cleanliness"] < 100:
                        d["cleaning"] = True
                        d["cleanliness"] = min(100, d["cleanliness"] + 2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1: current_area = "Customer Counter"
            elif event.key == pygame.K_2: current_area = "Grill & Stock Delivery"
            elif event.key == pygame.K_3: current_area = "Drink Station"
            elif event.key == pygame.K_4: current_area = "Fries Station"
            elif event.key == pygame.K_5: current_area = "Chef Wardrobe"
            elif event.key == pygame.K_6: current_area = "Ordering Area"
            elif event.key == pygame.K_7: current_area = "Settings Area"
            elif event.key == pygame.K_p: save_game()
            elif event.key == pygame.K_l: load_game()

            if current_area == "Grill & Stock Delivery":
                keys_map = [pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r, pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f]
                for idx, k in enumerate(keys_map):
                    if event.key == k: evaluate_grill_press(idx)
            
            if current_area == "Fries Station":
                keys_map = [pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r]
                for idx, k in enumerate(keys_map):
                    if event.key == k: evaluate_fryer_press(idx)
            
            if current_area == "Drink Station":
                keys_map = [pygame.K_d, pygame.K_f, pygame.K_g, pygame.K_h]
                for idx, k in enumerate(keys_map):
                    if event.key == k: evaluate_drink_press(idx)
            
            if current_area == "Customer Counter":
                if event.key == pygame.K_SPACE and len(customer_queue) > 0:
                    target_customer = customer_queue[0]
                    if check_and_fulfill_order(target_customer):
                        customers_served += 1
                        customer_queue.pop(0)
                elif event.key in [pygame.K_x, pygame.K_BACKSPACE]:
                    reject_customer()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # --- Clickable Bottom Navigation Buttons ---
            nav_box_w, nav_box_h = 135, 38
            nav_start_x = 20
            nav_y = 645
            for idx, area_name in enumerate(game_areas):
                # Arrange buttons horizontally across the bottom bar
                b_rect = pygame.Rect(nav_start_x + idx * (nav_box_w + 6), nav_y, nav_box_w, nav_box_h)
                if b_rect.collidepoint(mouse_pos):
                    current_area = area_name

            if current_area == "Settings Area":
                slider_rect = pygame.Rect(canvas_rect.x + 40, canvas_rect.y + 190, 400, 20)
                fill_width = int(slider_rect.width * current_music_volume)
                handle_x = slider_rect.x + fill_width
                handle_rect = pygame.Rect(handle_x - 8, slider_rect.y - 6, 16, 32)
                handle_grab_rect = handle_rect.inflate(20, 20)
                slider_grab_rect = slider_rect.inflate(0, 20)
                
                if handle_grab_rect.collidepoint(mouse_pos) or slider_grab_rect.collidepoint(mouse_pos):
                    dragging_slider = True
                    rel_x = max(0, min(mouse_pos[0] - slider_rect.x, slider_rect.width))
                    current_music_volume = rel_x / slider_rect.width
                    pygame.mixer.music.set_volume(current_music_volume)

            if current_area == "Ordering Area" and not delivery_in_progress:
                for i, item in enumerate(supplies):
                    name, price = item
                    column, row = i % 4, i // 4
                    x = start_x + column * (button_width + spacing_x)
                    y = start_y + row * (button_height + spacing_y) + 70
                    button_rect = pygame.Rect(x, y, button_width, button_height)
                    
                    locked_items = ["Bun Supplies", "Cheese Supplies", "Box Supplies", "Meat Supplies", "Sauce Supplies"]
                    is_item_locked = name in locked_items

                    if button_rect.collidepoint(mouse_pos) and name != "LOCKED" and not is_item_locked:
                        if money >= price:
                            if name == "Fast Grills" and not fast_grill_upgrade:
                                money -= price
                                fast_grill_upgrade = True
                            elif name == "Fast Fryers" and not fast_fryer_upgrade:
                                money -= price
                                fast_fryer_upgrade = True
                            elif name == "Fast Drinks" and not fast_drink_upgrade:
                                money -= price
                                fast_drink_upgrade = True
                            elif name == "Anti-Burn Tech" and not anti_burn_upgrade:
                                money -= price
                                anti_burn_upgrade = True
                            elif "Supplies" in name:
                                money -= price
                                delivery_in_progress = True
                                delivery_start = pygame.time.get_ticks()
                                delivery_message = "Cargo In Transit..."
                                if name in ["Burger Supplies", "Bun Supplies", "Meat Supplies"]: 
                                    pending_burgers = 3
                                elif name in ["Fries Supplies", "Box Supplies", "Sauce Supplies"]: 
                                    pending_fries = 4
                                elif name in ["Drink Supplies", "Cheese Supplies"]: 
                                    pending_drinks = 3

            if current_area == "Chef Wardrobe":
                tab_w, tab_h = 120, 36
                tab_start_x = canvas_rect.x + 500
                tab_y = canvas_rect.y + 12

                for t_idx, tab_name in enumerate(wardrobe_tabs):
                    t_rect = pygame.Rect(tab_start_x + t_idx * (tab_w + 10), tab_y, tab_w, tab_h)
                    if t_rect.collidepoint(mouse_pos):
                        current_wardrobe_tab = tab_name

                filtered_catalog = [item for item in wardrobe_catalog if item["category"] == current_wardrobe_tab]
                
                card_w, card_h = 270, 310
                gap = 35
                total_w = len(filtered_catalog) * card_w + (len(filtered_catalog) - 1) * gap
                start_x_wardrobe = canvas_rect.x + (canvas_rect.width - total_w) // 2
                start_y_wardrobe = canvas_rect.y + 60

                for idx, item in enumerate(filtered_catalog):
                    card_x = start_x_wardrobe + idx * (card_w + gap)
                    card_rect = pygame.Rect(card_x, start_y_wardrobe, card_w, card_h)
                    
                    if card_rect.collidepoint(mouse_pos):
                        if item["name"] in owned_outfits:
                            equipped_outfits[current_wardrobe_tab] = item["name"]
                        elif money >= item["price"]:
                            money -= item["price"]
                            owned_outfits.append(item["name"])
                            equipped_outfits[current_wardrobe_tab] = item["name"]

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            dragging_slider = False

    if current_area == "Settings Area" and dragging_slider:
        slider_rect = pygame.Rect(canvas_rect.x + 40, canvas_rect.y + 190, 400, 20)
        rel_x = max(0, min(mouse_pos[0] - slider_rect.x, slider_rect.width))
        current_music_volume = rel_x / slider_rect.width
        pygame.mixer.music.set_volume(current_music_volume)

    run_timer_matrix(current_time)

    screen.fill((230, 230, 235))

    if current_area == "Customer Counter":
        pygame.draw.rect(screen, (220, 200, 180), canvas_rect)
        pygame.draw.rect(screen, (0, 0, 0), canvas_rect, 3)
        if len(customer_queue) == 0:
            empty_lbl = header_font.render("No Active Orders In Queue Pool", True, (80, 80, 80))
            screen.blit(empty_lbl, (WIDTH // 2 - empty_lbl.get_width() // 2, 300))
        for idx, c in enumerate(customer_queue):
            c_y = 160 + (idx * 110)
            card_rect = pygame.Rect(80, c_y, 940, 95)
            
            bg_color = (245, 245, 250)
            if c["type"] == "VIP": bg_color = (240, 220, 255)
            elif c["type"] == "Easygoing": bg_color = (220, 245, 220)

            elapsed_time = current_time - c["start_time"]
            p_pct = max(0.0, 1.0 - (elapsed_time / c["patience"]))
            
            if p_pct < 0.4:
                border_color = (255, 0, 0) if (current_time // 250) % 2 == 0 else (100, 100, 110)
                border_thick = 3
            else:
                border_color = (100, 100, 110)
                border_thick = 2

            pygame.draw.rect(screen, bg_color, card_rect)
            pygame.draw.rect(screen, border_color, card_rect, border_thick)
            
            c_lbl = controls.render(f"Position #{idx + 1} | Type: {c['type']}", True, (30, 30, 40))
            screen.blit(c_lbl, (100, c_y + 10))
            
            order_str = " + ".join(c["items"])
            if len(c["items"]) > 1:
                order_str += " (COMBO!)"
            o_lbl = header_font.render(f"Wants: {order_str}", True, (180, 20, 20))
            screen.blit(o_lbl, (100, c_y + 35))

            if idx == 0:
                prompt = controls.render("[ SPACE ] Serve | [ X ] Reject order", True, (0, 120, 0))
                screen.blit(prompt, (450, c_y + 10))

            p_bar_bg = pygame.Rect(680, c_y + 50, 220, 15)
            p_bar_fg = pygame.Rect(680, c_y + 50, int(220 * p_pct), 15)
            pygame.draw.rect(screen, (180, 180, 185), p_bar_bg)
            
            bar_color = (220, 40, 40) if p_pct < 0.4 else (40, 180, 40)
            if p_pct >= 0.8:
                bar_color = (230, 180, 0)
            pygame.draw.rect(screen, bar_color, p_bar_fg)
            
            if p_pct >= 0.8:
                tip_lbl = controls.render("TIP ZONE!", True, (160, 120, 0))
                screen.blit(tip_lbl, (680, c_y + 70))

    elif current_area == "Grill & Stock Delivery":
        g_w, g_h = 220, 120
        key_mapping = ["Q", "W", "E", "R", "A", "S", "D", "F"]
        for i in range(8):
            row, col = i // 4, i % 4
            g_x = 70 + (col * 240)
            g_y = 150 + (row * 145)
            g_rect = pygame.Rect(g_x, g_y, g_w, g_h)
            g = grills_status[i]
            if not g["unlocked"]:
                pygame.draw.rect(screen, (130, 130, 135), g_rect)
                pygame.draw.rect(screen, (0, 0, 0), g_rect, 2)
                lock_lbl = controls.render(f"GRILL {i+1} LOCKED", True, (60, 60, 65))
                screen.blit(lock_lbl, (g_x + 15, g_y + 30))
                cost_lbl = controls.render(f"Unlock: ${grill_unlock_costs[i]}", True, (20, 90, 20))
                screen.blit(cost_lbl, (g_x + 15, g_y + 65))
            else:
                pygame.draw.rect(screen, (80, 80, 85), g_rect)
                pygame.draw.rect(screen, (0, 0, 0), g_rect, 2)
                g_lbl = controls.render(f"Grill {i + 1} [{key_mapping[i]}] Rub to Clean", True, (240, 240, 255))
                screen.blit(g_lbl, (g_x + 10, g_y + 8))
                
                if g["cleaning"]: status_txt = "Scrubbing..."
                elif g["cleanliness"] <= 0: status_txt = "Out of order! Rub here"
                elif g["burnt"]: status_txt = "Burnt! Rub to clean"
                elif g["cleanliness"] <= 20: status_txt = "Dirty! Rub to clean"
                elif g["ready"]: status_txt = "Burger Ready!"
                elif g["cooking"]: status_txt = "Cooking..."
                else: status_txt = "Ready. Press key"
                
                status_lbl = controls.render(status_txt, True, (100, 200, 255) if g["cleaning"] else ((255, 60, 60) if g["burnt"] or g["cleanliness"] <= 20 else ((60, 255, 60) if g["ready"] else (240, 240, 100))))
                screen.blit(status_lbl, (g_x + 10, g_y + 32))

                clean_lbl = small_font.render(f"Cleanliness: {g['cleanliness']}%", True, (200, 200, 210))
                screen.blit(clean_lbl, (g_x + 10, g_y + 58))
                pygame.draw.rect(screen, (40, 40, 45), (g_x + 10, g_y + 76, 200, 8))
                c_color = (40, 180, 70) if g['cleanliness'] > 50 else ((220, 160, 0) if g['cleanliness'] > 25 else (220, 50, 50))
                pygame.draw.rect(screen, c_color, (g_x + 10, g_y + 76, int(200 * (g['cleanliness'] / 100.0)), 8))

                if g["cooking"]:
                    speed = 1500 if fast_grill_upgrade else 3000
                    b_pct = min(1.0, (current_time - g["start"]) / speed)
                    pygame.draw.rect(screen, (40, 40, 45), (g_x + 10, g_y + 92, 200, 12))
                    pygame.draw.rect(screen, (220, 100, 30), (g_x + 10, g_y + 92, int(200 * b_pct), 12))

        if delivery_in_progress or delivery_message != "":
            msg_str = delivery_message if not delivery_in_progress else "Delivery on its way..."
            deliv_lbl = controls.render(msg_str, True, (20, 20, 180))
            screen.blit(deliv_lbl, (70, 460))

    elif current_area == "Drink Station":
        d_w, d_h = 220, 360
        key_mapping = ["D", "F", "G", "H"]
        drink_pour_speed = 1000 if fast_drink_upgrade else 2000
        for i in range(4):
            d_x = 70 + (i * 245)
            d_y = 160
            d_rect = pygame.Rect(d_x, d_y, d_w, d_h)
            d = drinks_status[i]
            if not d["unlocked"]:
                pygame.draw.rect(screen, (140, 140, 145), d_rect)
                pygame.draw.rect(screen, (0, 0, 0), d_rect, 2)
                lock_msg = controls.render(f"Soda {i+1} Locked", True, (60, 60, 65))
                screen.blit(lock_msg, (d_x + 20, d_y + 100))
                unlock_msg = controls.render(f"Press [{key_mapping[i]}]", True, (20, 90, 20))
                screen.blit(unlock_msg, (d_x + 20, d_y + 140))
                cost_msg = controls.render(f"Cost: ${drink_unlock_costs[i]}", True, (20, 90, 20))
                screen.blit(cost_msg, (d_x + 20, d_y + 170))
            else:
                pygame.draw.rect(screen, (160, 210, 230), d_rect)
                pygame.draw.rect(screen, (0, 0, 0), d_rect, 2)
                disp_title = header_font.render(f"Soda {i+1} [{key_mapping[i]}]", True, (20, 20, 30))
                screen.blit(disp_title, (d_x + 15, d_y + 20))
                
                if d["cleaning"]: disp_txt = "Scrubbing..."
                elif d["cleanliness"] <= 0: disp_txt = "Out of order! Rub here"
                elif d["dispensing"]: disp_txt = "Pouring..."
                elif d["ready"]: disp_txt = "Full! Press key"
                else: disp_txt = "Ready. Rub to clean"
                
                disp_lbl = controls.render(disp_txt, True, (0, 0, 150) if d["dispensing"] else ((180, 20, 20) if d["cleanliness"] <= 20 else ((0, 120, 0) if d["ready"] else (40, 40, 45))))
                screen.blit(disp_lbl, (d_x + 15, d_y + 60))

                clean_lbl = small_font.render(f"Cleanliness: {d['cleanliness']}%", True, (40, 40, 50))
                screen.blit(clean_lbl, (d_x + 15, d_y + 100))
                pygame.draw.rect(screen, (40, 40, 45), (d_x + 15, d_y + 125, 190, 10))
                c_color = (40, 180, 70) if d['cleanliness'] > 50 else ((220, 160, 0) if d['cleanliness'] > 25 else (220, 50, 50))
                pygame.draw.rect(screen, c_color, (d_x + 15, d_y + 125, int(190 * (d['cleanliness'] / 100.0)), 10))
                
                if d["dispensing"]:
                    d_pct = min(1.0, (current_time - d["start"]) / drink_pour_speed)
                    pygame.draw.rect(screen, (40, 40, 45), (d_x + 15, d_y + 200, 190, 20))
                    pygame.draw.rect(screen, (30, 144, 255), (d_x + 15, d_y + 200, int(190 * d_pct), 20))

    elif current_area == "Fries Station":
        f_w, f_h = 220, 240
        key_mapping = ["Q", "W", "E", "R"]
        for i in range(4):
            f_x = 70 + (i * 245)
            f_y = 180
            f_rect = pygame.Rect(f_x, f_y, f_w, f_h)
            f = fryers_status[i]
            if not f["unlocked"]:
                pygame.draw.rect(screen, (130, 130, 135), f_rect)
                pygame.draw.rect(screen, (0, 0, 0), f_rect, 2)
                lock_lbl = controls.render(f"Fryer {i+1} Locked", True, (60, 60, 65))
                screen.blit(lock_lbl, (f_x + 20, f_y + 80))
                cost_lbl = controls.render(f"Unlock: ${fryer_unlock_costs[i]}", True, (20, 90, 20))
                screen.blit(cost_lbl, (f_x + 20, f_y + 110))
            else:
                pygame.draw.rect(screen, (210, 200, 120), f_rect)
                pygame.draw.rect(screen, (0, 0, 0), f_rect, 2)
                f_lbl = controls.render(f"Fryer {i + 1} [{key_mapping[i]}] Rub to Clean", True, (40, 40, 45))
                screen.blit(f_lbl, (f_x + 10, f_y + 15))
                
                if f["cleaning"]: status_txt = "Scrubbing..."
                elif f["cleanliness"] <= 0: status_txt = "Out of order! Rub here"
                elif f["burnt"]: status_txt = "Burnt! Rub to clean"
                elif f["cleanliness"] <= 20: status_txt = "Dirty! Rub to clean"
                elif f["ready"]: status_txt = "Done! Take them out"
                elif f["cooking"]: status_txt = "Frying..."
                else: status_txt = "Empty"
                
                status_lbl = controls.render(status_txt, True, (0, 0, 150) if f["cleaning"] else ((180, 20, 20) if f["burnt"] or f["cleanliness"] <= 20 else ((20, 150, 20) if f["ready"] else (50, 50, 55))))
                screen.blit(status_lbl, (f_x + 10, f_y + 45))

                clean_lbl = small_font.render(f"Cleanliness: {f['cleanliness']}%", True, (50, 50, 60))
                screen.blit(clean_lbl, (f_x + 10, f_y + 80))
                pygame.draw.rect(screen, (40, 40, 45), (f_x + 10, f_y + 100, 200, 10))
                c_color = (40, 180, 70) if f['cleanliness'] > 50 else ((220, 160, 0) if f['cleanliness'] > 25 else (220, 50, 50))
                pygame.draw.rect(screen, c_color, (f_x + 10, f_y + 100, int(200 * (f['cleanliness'] / 100.0)), 10))

                if f["cooking"]:
                    speed = 2000 if fast_fryer_upgrade else 4000
                    fr_pct = min(1.0, (current_time - f["start"]) / speed)
                    pygame.draw.rect(screen, (40, 40, 45), (f_x + 10, f_y + 130, 200, 18))
                    pygame.draw.rect(screen, (255, 165, 0), (f_x + 10, f_y + 130, int(200 * fr_pct), 18))

    # --- CHEF WARDROBE SECTION ---
    elif current_area == "Chef Wardrobe":
        pygame.draw.rect(screen, (242, 244, 248), canvas_rect, border_radius=12)
        pygame.draw.rect(screen, (180, 185, 200), canvas_rect, 2, border_radius=12)

        w_title = header_font.render("Chef Outfit Wardrobe", True, (35, 45, 60))
        screen.blit(w_title, (canvas_rect.x + 25, canvas_rect.y + 12))

        tab_w, tab_h = 120, 36
        tab_start_x = canvas_rect.x + 500
        tab_y = canvas_rect.y + 12

        for t_idx, tab_name in enumerate(wardrobe_tabs):
            t_rect = pygame.Rect(tab_start_x + t_idx * (tab_w + 10), tab_y, tab_w, tab_h)
            is_active_tab = (current_wardrobe_tab == tab_name)

            t_bg = (40, 120, 220) if is_active_tab else (215, 220, 230)
            t_fg = (255, 255, 255) if is_active_tab else (60, 70, 85)

            pygame.draw.rect(screen, t_bg, t_rect, border_radius=8)
            if not is_active_tab:
                pygame.draw.rect(screen, (180, 185, 195), t_rect, 1, border_radius=8)

            t_lbl = controls.render(tab_name, True, t_fg)
            lbl_x = t_rect.x + (t_rect.width - t_lbl.get_width()) // 2
            lbl_y = t_rect.y + (t_rect.height - t_lbl.get_height()) // 2
            screen.blit(t_lbl, (lbl_x, lbl_y))

        filtered_catalog = [item for item in wardrobe_catalog if item["category"] == current_wardrobe_tab]

        card_w, card_h = 270, 310
        gap = 35
        total_w = len(filtered_catalog) * card_w + (len(filtered_catalog) - 1) * gap
        start_x_wardrobe = canvas_rect.x + (canvas_rect.width - total_w) // 2
        start_y_wardrobe = canvas_rect.y + 60

        for idx, item in enumerate(filtered_catalog):
            card_x = start_x_wardrobe + idx * (card_w + gap)
            card_rect = pygame.Rect(card_x, start_y_wardrobe, card_w, card_h)

            currently_equipped = equipped_outfits.get(current_wardrobe_tab)
            is_equipped = (item["name"] == currently_equipped)
            is_owned = (item["name"] in owned_outfits)
            is_hovered = card_rect.collidepoint(mouse_pos)

            shadow_rect = card_rect.move(3, 4)
            pygame.draw.rect(screen, (210, 215, 225), shadow_rect, border_radius=12)
            pygame.draw.rect(screen, (255, 255, 255), card_rect, border_radius=12)

            if is_equipped:
                border_color = (230, 175, 20)
                border_thick = 4
            elif is_hovered:
                border_color = (0, 180, 255)
                border_thick = 3
            else:
                border_color = (210, 215, 225)
                border_thick = 2

            pygame.draw.rect(screen, border_color, card_rect, border_thick, border_radius=12)

            name_txt = controls.render(item["name"], True, (30, 35, 45))
            screen.blit(name_txt, (card_x + 16, start_y_wardrobe + 12))

            swatch_rect = pygame.Rect(card_x + 16, start_y_wardrobe + 40, card_w - 32, 105)
            pygame.draw.rect(screen, item["color"], swatch_rect, border_radius=8)
            pygame.draw.rect(screen, (160, 165, 175), swatch_rect, 1, border_radius=8)

            icon_color = (255, 255, 255) if item["color"] != (240, 240, 240) else (40, 40, 40)
            pygame.draw.circle(screen, icon_color, (swatch_rect.centerx, swatch_rect.centery - 6), 22)
            pygame.draw.rect(screen, icon_color, (swatch_rect.centerx - 16, swatch_rect.centery - 6, 32, 20))

            desc_txt = small_font.render(item["desc"], True, (220, 20, 60))
            screen.blit(desc_txt, (card_x + 16, start_y_wardrobe + 155))

            if is_equipped:
                status_str = "EQUIPPED"
                btn_color = (230, 175, 20)
                txt_color = (255, 255, 255)
            elif is_owned:
                status_str = "EQUIP"
                btn_color = (50, 160, 90)
                txt_color = (255, 255, 255)
            else:
                status_str = f"BUY (${item['price']})"
                btn_color = (220, 60, 60) if money < item['price'] else (40, 120, 220)
                txt_color = (255, 255, 255)

            btn_rect = pygame.Rect(card_x + 16, start_y_wardrobe + 245, card_w - 32, 45)
            pygame.draw.rect(screen, btn_color, btn_rect, border_radius=8)
            
            btn_lbl = controls.render(status_str, True, txt_color)
            lbl_x = btn_rect.x + (btn_rect.width - btn_lbl.get_width()) // 2
            lbl_y = btn_rect.y + (btn_rect.height - btn_lbl.get_height()) // 2
            screen.blit(btn_lbl, (lbl_x, lbl_y))

    # --- SETTINGS AREA SECTION ---
    elif current_area == "Settings Area":
        pygame.draw.rect(screen, (242, 244, 248), canvas_rect, border_radius=12)
        pygame.draw.rect(screen, (180, 185, 200), canvas_rect, 2, border_radius=12)

        set_title = header_font.render("Game Settings - Audio Volume", True, (35, 45, 60))
        screen.blit(set_title, (canvas_rect.x + 40, canvas_rect.y + 40))

        vol_label = controls.render(f"Music Volume: {int(current_music_volume * 100)}%", True, (50, 50, 60))
        screen.blit(vol_label, (canvas_rect.x + 40, canvas_rect.y + 140))

        slider_rect = pygame.Rect(canvas_rect.x + 40, canvas_rect.y + 190, 400, 20)
        pygame.draw.rect(screen, (200, 200, 210), slider_rect, border_radius=10)
        
        fill_width = int(slider_rect.width * current_music_volume)
        fill_rect = pygame.Rect(slider_rect.x, slider_rect.y, fill_width, slider_rect.height)
        pygame.draw.rect(screen, (40, 120, 220), fill_rect, border_radius=10)

        handle_x = slider_rect.x + fill_width
        handle_rect = pygame.Rect(handle_x - 8, slider_rect.y - 6, 16, 32)
        pygame.draw.rect(screen, (30, 30, 40), handle_rect, border_radius=4)

        instruct_txt = small_font.render("Click and drag the black handle or slider bar to adjust volume (0% to 100%).", True, (100, 100, 110))
        screen.blit(instruct_txt, (canvas_rect.x + 40, canvas_rect.y + 240))

    elif current_area == "Ordering Area":
        tab_title = header_font.render("Supplier & Upgrades Tablet", True, (30, 30, 35))
        screen.blit(tab_title, (WIDTH // 2 - tab_title.get_width() // 2, 145))
        for i, item in enumerate(supplies):
            name, price = item
            column, row = i % 4, i // 4
            x = start_x + column * (button_width + spacing_x)
            y = start_y + row * (button_height + spacing_y) + 70
            button_rect = pygame.Rect(x, y, button_width, button_height)
            
            locked_items = ["Bun Supplies", "Cheese Supplies", "Box Supplies", "Meat Supplies", "Sauce Supplies"]
            is_item_locked = name in locked_items

            if name == "LOCKED" or is_item_locked:
                pygame.draw.rect(screen, (140, 140, 145), button_rect)
                pygame.draw.rect(screen, (0, 0, 0), button_rect, 2)
                txt = controls.render("LOCKED", True, (70, 70, 75))
                screen.blit(txt, txt.get_rect(center=button_rect.center))
            else:
                is_bought_upgrade = (name == "Fast Grills" and fast_grill_upgrade) or \
                                    (name == "Fast Fryers" and fast_fryer_upgrade) or \
                                    (name == "Fast Drinks" and fast_drink_upgrade) or \
                                    (name == "Anti-Burn Tech" and anti_burn_upgrade)
                
                is_hovered = button_rect.collidepoint(mouse_pos)
                if is_bought_upgrade:
                    bg = (160, 220, 160)
                elif is_hovered:
                    bg = (120, 200, 255)
                else:
                    bg = (100, 180, 240)
                
                pygame.draw.rect(screen, bg, button_rect)
                pygame.draw.rect(screen, (0, 0, 0), button_rect, 2)
                
                lbl_n = controls.render(name, True, (10, 20, 30))
                lbl_p = controls.render("PURCHASED" if is_bought_upgrade else f"Price: ${price}", True, (20, 90, 20))
                lbl_b = controls.render("Active" if is_bought_upgrade else "Click to buy", True, (30, 30, 40))
                screen.blit(lbl_n, (x + 10, y + 15))
                screen.blit(lbl_p, (x + 10, y + 45))
                screen.blit(lbl_b, (x + 10, y + 80))

    hud_height = 115
    pygame.draw.rect(screen, (255, 255, 255), (0, 0, WIDTH, hud_height))
    pygame.draw.line(screen, (210, 215, 225), (0, hud_height), (WIDTH, hud_height), 2)

    time_remaining = max(0, (shift_duration - (current_time - shift_start_time)) // 1000)
    
    title_surface = header_font.render(f"{current_area}  |  Day {day_number} (Target: ${daily_target})", True, (20, 30, 45))
    screen.blit(title_surface, (25, 12))

    hud_money = hud_font.render(f"Capital: ${money}   |   Shift: {time_remaining}s", True, (0, 130, 50))
    screen.blit(hud_money, (25, 48))

    outfit_text = hud_font.render(
        f"Clothes: {equipped_outfits['Shirts']}  |  "
        f"Apron: {equipped_outfits['Aprons']}  |  "
        f"Hat: {equipped_outfits['Hats']}",
        True, (120, 60, 150)
    )
    screen.blit(outfit_text, (25, 75))

    hud_stock = hud_font.render(
        f"Stock -> Burgers:{burger_stock}  Fries:{fries_stock}  Drinks:{drink_stock}   |   Tray -> B:{tray_burgers}  F:{tray_fries}  D:{tray_drinks}",
        True, (30, 60, 150)
    )
    screen.blit(hud_stock, (450, 48))

    # --- Render Clickable Bottom Navigation Area Buttons ---
    pygame.draw.rect(screen, (240, 240, 245), (0, 630, WIDTH, 70))
    pygame.draw.line(screen, (200, 205, 215), (0, 630), (WIDTH, 630), 2)

    nav_box_w, nav_box_h = 135, 38
    nav_start_x = 20
    nav_y = 645
    
    short_area_names = ["Counter", "Grills", "Drinks", "Fryers", "Wardrobe", "Tablet", "Settings"]

    for idx, area_name in enumerate(game_areas):
        b_rect = pygame.Rect(nav_start_x + idx * (nav_box_w + 6), nav_y, nav_box_w, nav_box_h)
        is_active = (current_area == area_name)
        is_hovered = b_rect.collidepoint(mouse_pos)

        if is_active:
            btn_bg = (40, 120, 220)
            txt_col = (255, 255, 255)
        elif is_hovered:
            btn_bg = (200, 215, 235)
            txt_col = (20, 30, 45)
        else:
            btn_bg = (220, 225, 235)
            txt_col = (60, 70, 85)

        pygame.draw.rect(screen, btn_bg, b_rect, border_radius=6)
        pygame.draw.rect(screen, (170, 175, 190), b_rect, 1, border_radius=6)

        btn_txt = small_font.render(f"[{idx+1}] {short_area_names[idx]}", True, txt_col)
        tx = b_rect.x + (b_rect.width - btn_txt.get_width()) // 2
        ty = b_rect.y + (b_rect.height - btn_txt.get_height()) // 2
        screen.blit(btn_txt, (tx, ty))

    pygame.display.flip()
    clock.tick(60)

save_game()
pygame.mixer.music.stop()
pygame.quit()