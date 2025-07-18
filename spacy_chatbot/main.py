import random
import re
import spacy
import gspread
from google.oauth2.service_account import Credentials



# Google Sheets setup
SHEET_URL = "https://docs.google.com/spreadsheets/d/1lWAk1cOb7fY5EJJXCm12XLc4ohNTQ25jwQvH5s4B2aU/edit?usp=sharing"
SHEET_ID = "1lWAk1cOb7fY5EJJXCm12XLc4ohNTQ25jwQvH5s4B2aU"
SHEET_NAME = "Sheet1"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDENTIALS_FILE = "service_account.json"  # Place your credentials file in the project root

def get_gsheet_client():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    gc = gspread.authorize(creds)
    return gc

def write_user_info_to_sheet(user_info):
    import gspread
    from google.oauth2.service_account import Credentials
    import time

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    CREDENTIALS_FILE = 'service_account.json'
    SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1lWAk1cOb7fY5EJJXCm12XLc4ohNTQ25jwQvH5s4B2aU/edit?usp=sharing'

    # Retry logic for network issues
    max_retries = 3
    for attempt in range(max_retries):
        try:
            creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
            gc = gspread.authorize(creds)
            sh = gc.open_by_url(SPREADSHEET_URL)
            worksheet = sh.sheet1

            # Write header if sheet is empty
            if worksheet.row_count == 0 or not worksheet.get_all_values():
                worksheet.append_row([
                    "Name", "mail", "number", "Type", "Date", "Departure", "Arrival"
                ])

            worksheet.append_row([
                user_info.get("name", ""),
                user_info.get("email", ""),
                user_info.get("phone", ""),
                user_info.get("booking_type", ""),
                user_info.get("booking_date", ""),
                user_info.get("departure", ""),
                user_info.get("arrival", "")
            ])
            return True  # Success
        except Exception as e:
            error_msg = str(e)
            if "invalid_grant" in error_msg.lower() or "jwt" in error_msg.lower():
                raise Exception("Invalid service account credentials. Please regenerate your Google service account key.")
            elif "connection" in error_msg.lower() or "network" in error_msg.lower():
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait before retry
                    continue
                else:
                    raise Exception("Network connection error. Please check your internet connection and try again.")
            else:
                raise Exception(f"Google Sheets error: {error_msg}")
    
    raise Exception("Failed to connect to Google Sheets after multiple attempts.")

nlp = spacy.load("spacy_chatbot/en_core_web_sm/en_core_web_sm-3.7.1")

BOT_NAME = "TravelBot"
greetings = [
    "hello", "hi", "hey", "good morning", "good afternoon", "good evening"
]
thanks = [
    "thank you", "thanks", "thx", "appreciate it"
]
farewells = [
    "bye", "goodbye", "see you", "take care", "later"
]
# Expanded booking types
booking_types = ["hotel", "flight", "restaurant", "table", "train", "trip", "vacation", "tour"]

# Helper for natural language date extraction
import datetime
from dateutil import parser as date_parser

def extract_natural_date(message):
    lowered = message.lower()
    today = datetime.date.today()
    if "tomorrow" in lowered:
        return (today + datetime.timedelta(days=1)).strftime("%d %B %Y")
    if "today" in lowered:
        return today.strftime("%d %B %Y")
    # Try to parse with dateutil
    try:
        dt = date_parser.parse(message, fuzzy=True, default=datetime.datetime.now())
        return dt.strftime("%d %B %Y")
    except Exception:
        return None

# Improved extract_booking_type to handle more flexible input
import re

def extract_booking_type(message):
    lowered = message.lower()
    for btype in booking_types:
        if btype in lowered:
            return btype.title()
    # Look for phrases like 'trip', 'vacation', 'tour', etc.
    if re.search(r"\btrip\b|\bvaccation\b|\btour\b", lowered):
        return "Trip"
    return None

# Improved location extraction: do not treat booking types or booking phrases as locations
PLACES_PATTERN = re.compile(r"(?:to|in|at|for)\s+([a-zA-Z ]+)", re.IGNORECASE)

def extract_location(message):
    # Try spaCy NER first
    doc = nlp(message)
    for ent in doc.ents:
        if ent.label_ == "GPE":
            place = ent.text.title()
            if place.lower() not in [btype.lower() for btype in booking_types]:
                return place
    # Fallback: regex for 'to/in/at/for [place]'
    match = PLACES_PATTERN.search(message)
    if match:
        possible_place = match.group(1).strip().title()
        # Do not treat booking types or booking phrases as locations
        if possible_place.lower() not in [btype.lower() for btype in booking_types] \
            and not possible_place.lower().startswith("book ") \
            and not possible_place.lower().startswith("reserve ") \
            and not any(bt in possible_place.lower() for bt in ["hotel", "flight", "restaurant", "train", "trip", "vacation", "tour"]):
            return possible_place
    return None

# Further expanded knowledge graph
knowledge_graph = {
    # Cities
    "paris": "Paris is the capital city of France, known for the Eiffel Tower and its art, fashion, and culture.",
    "rome": "Rome is the capital city of Italy, famous for its ancient history, the Colosseum, and Vatican City.",
    "london": "London is the capital of the United Kingdom, known for Big Ben, the London Eye, and Buckingham Palace.",
    "new york": "New York City is the largest city in the USA, famous for Times Square, Central Park, and the Statue of Liberty.",
    "tokyo": "Tokyo is the capital of Japan, known for its modernity, cherry blossoms, and Mount Fuji views.",
    "dubai": "Dubai is a city in the United Arab Emirates, famous for the Burj Khalifa and luxury shopping.",
    "sydney": "Sydney is a major city in Australia, known for the Sydney Opera House and Harbour Bridge.",
    "moscow": "Moscow is the capital of Russia, famous for the Kremlin and Red Square.",
    "beijing": "Beijing is the capital of China, known for the Forbidden City and the Great Wall.",
    "rio de janeiro": "Rio de Janeiro is a city in Brazil, known for its Carnival festival and Christ the Redeemer statue.",
    "berlin": "Berlin is the capital of Germany, known for its history, art scene, and the Berlin Wall.",
    "madrid": "Madrid is the capital of Spain, famous for its Royal Palace and Prado Museum.",
    "amsterdam": "Amsterdam is the capital of the Netherlands, known for its canals, museums, and cycling culture.",
    "toronto": "Toronto is the largest city in Canada, known for the CN Tower and multiculturalism.",
    "singapore": "Singapore is a city-state in Southeast Asia, famous for its cleanliness, Marina Bay Sands, and food scene.",
    "istanbul": "Istanbul is a major city in Turkey, straddling Europe and Asia, known for Hagia Sophia and the Grand Bazaar.",
    "bangkok": "Bangkok is the capital of Thailand, known for its vibrant street life and ornate shrines.",
    "los angeles": "Los Angeles is a major city in the USA, known for Hollywood, beaches, and entertainment industry.",
    "cape town": "Cape Town is a port city in South Africa, known for Table Mountain and Robben Island.",
    "delhi": "Delhi is the capital territory of India, known for its rich history and vibrant culture.",
    "mumbai": "Mumbai is the financial capital of India, famous for Bollywood and the Gateway of India.",
    "seoul": "Seoul is the capital of South Korea, known for its pop culture and palaces.",
    "mexico city": "Mexico City is the capital of Mexico, known for its Templo Mayor and vibrant street life.",
    "buenos aires": "Buenos Aires is the capital of Argentina, known for tango and European-style architecture.",
    "athens": "Athens is the capital of Greece, known for the Acropolis and ancient history.",
    "vienna": "Vienna is the capital of Austria, known for classical music and imperial palaces.",
    "zurich": "Zurich is the largest city in Switzerland, known for banking and beautiful lakeside views.",
    "helsinki": "Helsinki is the capital of Finland, known for its design and seaside atmosphere.",
    "stockholm": "Stockholm is the capital of Sweden, known for its archipelago and historic old town.",
    "oslo": "Oslo is the capital of Norway, known for its green spaces and museums.",
    "copenhagen": "Copenhagen is the capital of Denmark, known for its cycling culture and the Little Mermaid statue.",
    "prague": "Prague is the capital of the Czech Republic, known for its Old Town Square and medieval Astronomical Clock.",
    "budapest": "Budapest is the capital of Hungary, known for its thermal baths and the Danube River.",
    "warsaw": "Warsaw is the capital of Poland, known for its resilient history and reconstructed Old Town.",
    "lisbon": "Lisbon is the capital of Portugal, known for its hills, trams, and pastel-colored buildings.",
    "edinburgh": "Edinburgh is the capital of Scotland, known for its historic and cultural attractions including the Edinburgh Castle.",
    "venice": "Venice is a city in Italy, famous for its canals, gondolas, and St. Mark's Basilica.",
    "florence": "Florence is a city in Italy, known for its Renaissance art and architecture.",
    "barcelona": "Barcelona is a city in Spain, known for its art, architecture, and the Sagrada Familia.",
    "miami": "Miami is a city in the USA, known for its beaches, nightlife, and Art Deco architecture.",
    "san francisco": "San Francisco is a city in the USA, known for the Golden Gate Bridge and cable cars.",
    "las vegas": "Las Vegas is a city in the USA, known for its vibrant nightlife, casinos, and entertainment.",
    "vancouver": "Vancouver is a city in Canada, known for its natural beauty and multiculturalism.",
    "montreal": "Montreal is a city in Canada, known for its French heritage and festivals.",
    "auckland": "Auckland is a city in New Zealand, known for its harbors and Sky Tower.",
    "wellington": "Wellington is the capital of New Zealand, known for its creative culture and windy weather.",
    "santiago": "Santiago is the capital of Chile, known for its Andes mountain backdrop.",
    "lima": "Lima is the capital of Peru, known for its colonial architecture and cuisine.",
    "jakarta": "Jakarta is the capital of Indonesia, known for its bustling city life.",
    "kuala lumpur": "Kuala Lumpur is the capital of Malaysia, known for the Petronas Twin Towers.",
    "manila": "Manila is the capital of the Philippines, known for its waterfront promenade and centuries-old Chinatown.",
    "hanoi": "Hanoi is the capital of Vietnam, known for its centuries-old architecture and rich culture.",
    # Countries (expanded)
    "france": "France is a country in Western Europe, known for its wine, cuisine, and the French Riviera.",
    "italy": "Italy is a country in Southern Europe, famous for its art, history, and cuisine.",
    "japan": "Japan is an island country in East Asia, known for its technology, culture, and cherry blossoms.",
    "usa": "The United States of America is a country in North America, known for its diversity and innovation.",
    "uk": "The United Kingdom is a country in northwestern Europe, made up of England, Scotland, Wales, and Northern Ireland.",
    "uae": "The United Arab Emirates is a country in the Middle East, known for its modern cities and oil wealth.",
    "australia": "Australia is a country and continent surrounded by the Indian and Pacific oceans, famous for its wildlife and natural wonders.",
    "russia": "Russia is the largest country in the world, spanning Eastern Europe and northern Asia.",
    "china": "China is the world's most populous country, known for its long history and the Great Wall.",
    "egypt": "Egypt is a country in North Africa, famous for its ancient civilization and pyramids.",
    "brazil": "Brazil is the largest country in South America, known for the Amazon rainforest and Carnival.",
    "germany": "Germany is a country in Central Europe, known for its engineering, Oktoberfest, and castles.",
    "spain": "Spain is a country on Europe’s Iberian Peninsula, known for flamenco, bullfighting, and beaches.",
    "canada": "Canada is the second largest country in the world, known for its natural beauty and multicultural cities.",
    "netherlands": "The Netherlands is a country in Western Europe, known for windmills, tulips, and canals.",
    "turkey": "Turkey is a country straddling eastern Europe and western Asia, known for its rich history and cuisine.",
    "thailand": "Thailand is a country in Southeast Asia, known for tropical beaches, opulent royal palaces, and ancient ruins.",
    "south africa": "South Africa is a country on the southernmost tip of Africa, known for its diversity, wildlife, and Table Mountain.",
    "singapore": "Singapore is a city-state in Southeast Asia, famous for its cleanliness, Marina Bay Sands, and food scene.",
    "india": "India is a country in South Asia, known for its diverse culture, Taj Mahal, and Bollywood.",
    "argentina": "Argentina is a country in South America, known for tango, Patagonia, and beef.",
    "greece": "Greece is a country in southeastern Europe, known for its ancient history and islands.",
    "austria": "Austria is a country in Central Europe, known for its music, mountains, and palaces.",
    "switzerland": "Switzerland is a country in Central Europe, known for its Alps, chocolate, and banking.",
    "finland": "Finland is a country in Northern Europe, known for its lakes, saunas, and design.",
    "sweden": "Sweden is a country in Northern Europe, known for its forests, archipelagos, and innovation.",
    "norway": "Norway is a country in Northern Europe, known for its fjords and northern lights.",
    "denmark": "Denmark is a country in Northern Europe, known for its happiness, design, and fairy tales.",
    "mexico": "Mexico is a country in North America, known for its cuisine, pyramids, and beaches.",
    "chile": "Chile is a long, narrow country stretching along South America's western edge, known for its Andes mountains and wine.",
    "peru": "Peru is a country in South America, known for Machu Picchu and the Amazon rainforest.",
    "indonesia": "Indonesia is a Southeast Asian country made up of thousands of volcanic islands.",
    "malaysia": "Malaysia is a Southeast Asian country known for its beaches, rainforests, and mix of Malay, Chinese, Indian and European influences.",
    "philippines": "The Philippines is an archipelagic country in Southeast Asia, known for its beaches and biodiversity.",
    "vietnam": "Vietnam is a Southeast Asian country known for its beaches, rivers, Buddhist pagodas and bustling cities.",
    "new zealand": "New Zealand is a country in the southwestern Pacific Ocean, known for its stunning landscapes and Maori culture.",
    # Famous Places (expanded)
    "machu picchu": "Machu Picchu is an ancient Incan city set high in the Andes Mountains in Peru.",
    "grand canyon": "The Grand Canyon is a steep-sided canyon carved by the Colorado River in Arizona, USA.",
    "niagara falls": "Niagara Falls is a group of three waterfalls at the border of Ontario, Canada, and New York, USA.",
    "taj mahal": "The Taj Mahal is a white marble mausoleum in Agra, India, and a UNESCO World Heritage Site.",
    "petra": "Petra is a famous archaeological site in Jordan's southwestern desert.",
    "angkor wat": "Angkor Wat is a massive temple complex in Cambodia and the largest religious monument in the world.",
    "mount everest": "Mount Everest is Earth's highest mountain above sea level, located in the Himalayas.",
    "santorini": "Santorini is a Greek island in the Aegean Sea, known for its whitewashed buildings and stunning sunsets.",
    "banff national park": "Banff National Park is Canada's oldest national park, located in the Rocky Mountains.",
    "great barrier reef": "The Great Barrier Reef is the world's largest coral reef system, located in Australia.",
    "chichen itza": "Chichen Itza is a large pre-Columbian archaeological site in Mexico.",
    "table mountain": "Table Mountain is a flat-topped mountain overlooking Cape Town, South Africa.",
    "acropolis": "The Acropolis is an ancient citadel on a rocky outcrop above Athens, Greece.",
    "sagrada familia": "The Sagrada Familia is a large unfinished Roman Catholic church in Barcelona, Spain, designed by Antoni Gaudí.",
    "opera house": "The Sydney Opera House is a multi-venue performing arts centre in Sydney, Australia.",
    "christ the redeemer": "Christ the Redeemer is an iconic statue of Jesus Christ in Rio de Janeiro, Brazil.",
    "colosseum": "The Colosseum is an ancient amphitheater in Rome, Italy, and one of the greatest works of Roman architecture.",
    "statue of liberty": "The Statue of Liberty is a colossal neoclassical sculpture on Liberty Island in New York City, USA.",
    "burj khalifa": "The Burj Khalifa in Dubai is the tallest building in the world.",
    "mount fuji": "Mount Fuji is the highest mountain in Japan and a famous symbol of the country.",
    "big ben": "Big Ben is the nickname for the Great Bell of the clock at the north end of the Palace of Westminster in London.",
    "great wall of china": "The Great Wall of China is a series of fortifications built to protect China from invasions.",
    "pyramids of giza": "The Pyramids of Giza are ancient pyramid-shaped masonry structures in Egypt.",
    "uluru": "Uluru, also known as Ayers Rock, is a massive sandstone monolith in the heart of the Northern Territory's arid Red Centre in Australia.",
    "serengeti": "The Serengeti is a vast ecosystem in east-central Africa, known for its annual migration of over 1.5 million wildebeest and hundreds of thousands of zebras and gazelles.",
    "galapagos islands": "The Galapagos Islands are an Ecuadorian archipelago of volcanic islands distributed on either side of the equator in the Pacific Ocean.",
    "ha long bay": "Ha Long Bay is a UNESCO World Heritage Site in northern Vietnam, known for its emerald waters and thousands of towering limestone islands topped with rainforests.",
    "yellowstone": "Yellowstone National Park is a nearly 3,500-sq.-mile wilderness recreation area atop a volcanic hot spot in the U.S. states of Wyoming, Montana and Idaho.",
    "kruger national park": "Kruger National Park is one of Africa’s largest game reserves, located in northeastern South Africa.",
    "fiordland national park": "Fiordland National Park is a protected area in the southwest of New Zealand's South Island, known for fjords like Milford Sound.",
    "mont saint-michel": "Mont Saint-Michel is a small rocky island in Normandy, France, known for its stunning medieval abbey.",
    "palace of versailles": "The Palace of Versailles is a former royal residence located in Versailles, France, renowned for its opulent architecture and gardens.",
    "stonehenge": "Stonehenge is a prehistoric monument in Wiltshire, England, consisting of a ring of standing stones.",
    "alhambra": "The Alhambra is a palace and fortress complex located in Granada, Andalusia, Spain.",
    "bora bora": "Bora Bora is a small South Pacific island northwest of Tahiti in French Polynesia, known for its turquoise lagoon protected by a coral reef.",
    "maldives": "The Maldives is a tropical paradise in the Indian Ocean, known for its crystal-clear waters, white-sand beaches, and luxury resorts.",
    "petronas towers": "The Petronas Towers are twin skyscrapers in Kuala Lumpur, Malaysia, and were the tallest buildings in the world from 1998 to 2004.",
    "mount kilimanjaro": "Mount Kilimanjaro is a dormant volcano in Tanzania and the highest mountain in Africa.",
    "victoria falls": "Victoria Falls is a waterfall in southern Africa on the Zambezi River at the border between Zambia and Zimbabwe.",
    "blue lagoon": "The Blue Lagoon is a geothermal spa in southwestern Iceland.",
    "matterhorn": "The Matterhorn is a mountain of the Alps, straddling the main watershed and border between Switzerland and Italy.",
    "cliffs of moher": "The Cliffs of Moher are sea cliffs located at the southwestern edge of the Burren region in County Clare, Ireland.",
    "giant's causeway": "The Giant's Causeway is an area of about 40,000 interlocking basalt columns, the result of an ancient volcanic fissure eruption in Northern Ireland."
}

# Small talk dictionary (expanded)
small_talk = {
    "how's the weather": "I'm not connected to live weather data, but I hope it's nice where you are!",
    "what's up": "Not much, just here to help you!",
    "how old are you": "I'm as old as the code that created me!",
    "do you like music": "I enjoy all kinds of music, especially when people talk about it!",
    "tell me something interesting": "Did you know honey never spoils? Archaeologists have found edible honey in ancient Egyptian tombs!",
    "what's your favorite color": "I like all colors equally, but blue is quite calming!",
    "do you have hobbies": "My hobby is chatting and helping people like you!",
    "are you real": "I'm real in the digital world!",
    "can you help me": "Of course! Just tell me what you need help with.",
    "what languages do you speak": "I can understand and respond in English. I'm learning more every day!",
    "who made you": "I was created by developers to assist with travel and general questions.",
    "what's your favorite food": "I don't eat, but I hear pizza is popular!",
    "do you have friends": "I have lots of digital friends!",
    "what do you do for fun": "I love answering questions and learning new things.",
    "do you sleep": "Nope, I'm always here when you need me!",
    "are you smart": "I try my best to be helpful and smart!",
    "do you have a family": "My family is all the code and data that make me work.",
    "what is your job": "My job is to help you with travel, bookings, and fun facts!",
    "what is your favorite movie": "I like movies about robots, like Wall-E!",
    "do you dream": "I dream of helping people all over the world!",
    "what is the best time to visit": "The best time to visit depends on the destination! Let me know where you're planning to go, and I can help.",
    "can you recommend a place": "Sure! Tell me your interests or the type of place you want to visit.",
    "what should I pack": "It depends on your destination and the season. I recommend checking the weather and packing accordingly!",
    "do I need a visa": "Visa requirements depend on your nationality and destination. Please check the official government website for the latest info.",
    "how do I get to the airport": "You can usually get to the airport by taxi, public transport, or ride-sharing services. Let me know your city for more details!",
    "what is the currency": "Let me know the country, and I can tell you the currency used there!",
    "is it safe to travel": "Safety depends on the destination. Always check travel advisories and take standard precautions.",
    "can you help me book a hotel": "Absolutely! Just tell me where and when you want to book.",
    "can you help me book a flight": "Of course! Please provide your departure and arrival cities and dates.",
    "can you help me book a restaurant": "Yes! Let me know the city, cuisine, and date/time for your reservation.",
    "what are the top attractions": "Let me know the city or country, and I can list the top attractions!",
    "what is the time difference": "Tell me the cities or countries, and I can help with the time difference.",
    "what is the weather like": "I can't provide live weather, but I can tell you about the typical climate for your destination.",
    "can you suggest a travel itinerary": "Sure! Tell me your destination and how many days you have, and I can suggest an itinerary.",
    "what is the emergency number": "Emergency numbers vary by country. Let me know your destination, and I can provide the number.",
    "do you have travel tips": "Always keep your important documents safe, stay aware of your surroundings, and enjoy your trip!",
    "can you translate": "I can help with basic translations. Tell me the phrase and the language you want!"
}

# Fun facts keys for random selection
fun_facts_keys = [
    "honey never spoils",
    "bananas are berries",
    "octopus has three hearts",
    "lightning"
]

# Add emotional keywords for empathy
EMOTIONAL_KEYWORDS = [
    "tired", "sad", "exhausted", "depressed", "unhappy", "angry", "upset", "stressed", "overwhelmed", "bored", "lonely", "frustrated", "tired as fuck"
]

EMPATHY_RESPONSES = [
    "I'm sorry to hear that. If you need a break or a refreshing trip, I can help you plan something nice!",
    "It sounds like you could use a relaxing getaway. Would you like some travel suggestions?",
    "I'm here for you! Sometimes a change of scenery can help. Want to book a trip?",
    "I hope things get better soon. If you want to talk or plan a vacation, just let me know!"
]

# Session context to remember user info
class Session:
    def __init__(self):
        self.reset()
    def reset(self):
        self.booking_type = None
        self.location = None
        self.date = None
        self.people = None
        self.confirming = False
        self.last_intent = None
        self.bookings = []
        self.greeted = False
        self.asked_how_are_you = False
        self.user_feeling = None
        # User info fields
        self.user_info = {
            "name": None,
            "email": None,
            "phone": None,
            "place": None,
            "location": None
        }
        self.collecting_user_info = False
        self.awaiting_field = None
        self.confirm_user_info = False
        self.booking_info = {
            "type": None,
            "location": None,
            "date": None,
            "people": None
        }
        self.collecting_booking = False
        self.confirm_booking_details = False
        self.last_bot_message = None  # Track last bot message
        self.last_bot_intent = None   # Track last bot intent

session = Session()

# Regex for email and phone
EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
PHONE_REGEX = r"\b\d{10,15}\b"

# Define booking-type-specific user info fields
BOOKING_FIELDS = {
    "hotel": ["name", "email", "phone", "destination"],
    "restaurant": ["name", "email", "phone", "destination"],
    "flight": ["name", "email", "phone", "departure", "arrival"],
    "train": ["name", "email", "phone", "departure", "arrival"],
    "trip": ["name", "email", "phone", "destination"],
    "vacation": ["name", "email", "phone", "destination"],
    "tour": ["name", "email", "phone", "destination"]
}

FIELD_QUESTIONS = {
    "name": "Can I have your name?",
    "email": "What is your email address?",
    "phone": "What is your phone number?",
    "destination": "What is your destination city or country?",
    "departure": "What is your departure city or country?",
    "arrival": "What is your arrival city or country?"
}

DAYS_OF_WEEK = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]

def normalize_word(word):
    """Capitalize first letter, lower the rest."""
    return word[:1].upper() + word[1:].lower() if word else word

def extract_day_of_week(message):
    lowered = message.lower()
    for day in DAYS_OF_WEEK:
        if day in lowered:
            return normalize_word(day)
    return None

def extract_month(message):
    lowered = message.lower()
    for month in MONTHS:
        if month in lowered:
            return normalize_word(month)
    return None

def detect_user_feeling(message):
    msg = message.lower().strip()
    # Positive
    positive_patterns = [
        r"i\s*(')?m\s*(fine|good|great|okay|ok|not bad)",
        r"i am\s*(fine|good|great|okay|ok|not bad)"
    ]
    for pat in positive_patterns:
        if re.search(pat, msg):
            return "positive"
    # Negative
    negative_patterns = [
        r"i\s*(')?m\s*(not fine|not good|not great|bad|not okay|not ok|sad|upset|unwell|not well)",
        r"i am\s*(not fine|not good|not great|bad|not okay|not ok|sad|upset|unwell|not well)"
    ]
    for pat in negative_patterns:
        if re.search(pat, msg):
            return "negative"
    return None

def extract_user_info(message):
    doc = nlp(message)
    info = {}
    # Name (PERSON entity)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            info["name"] = ent.text.title()
    # Fallback: look for 'my name is ...', 'i am ...', 'it is ...', 'it's ...', or 'i'm ...'
    if not info.get("name"):
        name_match = re.search(r"(?:my name is|i am|it is|it's|i'm)\s+([a-zA-Z ]+)", message, re.IGNORECASE)
        if name_match:
            possible_name = name_match.group(1).strip()
            # Remove trailing punctuation
            possible_name = re.sub(r"[.?!,;:]+$", "", possible_name)
            info["name"] = possible_name.title()
    # If still no name and the bot is waiting for 'name', accept the whole input
    if not info.get("name") and hasattr(session, 'awaiting_field') and session.awaiting_field == "name" and message.strip():
        info["name"] = message.strip().title()
    # Email
    email_match = re.search(EMAIL_REGEX, message, re.IGNORECASE)
    if email_match:
        info["email"] = email_match.group(0)
    # Phone
    phone_match = re.search(PHONE_REGEX, message)
    if phone_match:
        info["phone"] = phone_match.group(0)
    # Place/Location (GPE, LOC)
    for ent in doc.ents:
        if ent.label_ == "GPE":
            info["place"] = ent.text.title()
        if ent.label_ == "LOC":
            info["location"] = ent.text.title()
    # Day of week
    day = extract_day_of_week(message)
    if day:
        info["date"] = day
    # Month
    month = extract_month(message)
    if month:
        info["month"] = month
    return info

ASK_QUESTION_PHRASES = [
    "i have a question", "can i ask", "may i ask", "i want to ask", "i'd like to ask", "i got a question", "i want to know"
]

# Improved parse_message for flexible booking/intent detection
BOOKING_PATTERNS = [
    r"i want to go to ([a-zA-Z ]+)",
    r"i want to travel to ([a-zA-Z ]+)",
    r"a trip to ([a-zA-Z ]+)",
    r"i want to book (a|an)? ?([a-zA-Z ]+)?( in| at| to)? ([a-zA-Z ]+)?",
    r"book (a|an)? ?([a-zA-Z ]+)?( in| at| to)? ([a-zA-Z ]+)?",
    r"reserve (a|an)? ?([a-zA-Z ]+)?( in| at| to)? ([a-zA-Z ]+)?"
]

def parse_message(message):
    doc = nlp(message)
    entities = {ent.label_: ent.text for ent in doc.ents}
    lowered = message.lower()
    # Only allow user info collection if collecting_user_info is already True
    if session.collecting_user_info:
        intent = "collect_user_info"
    # If already collecting booking, do not trigger new booking intent
    elif session.collecting_booking:
        intent = session.last_intent if session.last_intent else "booking"
    # Empathy for emotional statements
    elif any(word in lowered for word in EMOTIONAL_KEYWORDS):
        intent = "empathy"
    # Flexible booking detection
    elif any(re.search(pat, lowered) for pat in BOOKING_PATTERNS):
        intent = "booking"
    elif any(word in lowered for word in ["book", "reserve", "schedule"]):
        intent = "booking"
    # Ask question intent
    elif any(phrase in lowered for phrase in ASK_QUESTION_PHRASES):
        intent = "ask_question"
    # Small talk and knowledge graph
    elif any(greet in lowered for greet in [g.lower() for g in greetings]):
        intent = "greeting"
    elif any(phrase in lowered for phrase in small_talk):
        intent = "small_talk"
    elif "how are you" in lowered:
        intent = "how_are_you"
    elif "your name" in lowered or "who are you" in lowered:
        intent = "bot_name"
    elif "what can you do" in lowered or "help" in lowered:
        intent = "help"
    elif "tell me a joke" in lowered:
        intent = "joke"
    elif "tell me a fun fact" in lowered:
        intent = "fun_fact"
    elif "weather" in lowered:
        intent = "weather"
    elif "cancel" in lowered:
        intent = "cancel"
    elif any(thank in lowered for thank in [t.lower() for t in thanks]):
        intent = "thanks"
    elif any(farewell in lowered for farewell in [f.lower() for f in farewells]):
        intent = "farewell"
    elif "show" in lowered and "booking" in lowered:
        intent = "show_bookings"
    elif lowered.startswith("what is ") or lowered.startswith("who is "):
        intent = "knowledge_query"
    elif detect_user_feeling(message):
        intent = "user_feeling"
    else:
        intent = "unknown"
    return intent, entities

# Improved update_context to allow reset/change
RESET_PHRASES = ["no actually", "actually", "change", "instead", "i want to book", "i want to go"]

def update_context(intent, entities, message):
    lowered = message.lower()
    # Reset booking if user changes their mind
    if any(phrase in lowered for phrase in RESET_PHRASES):
        session.booking_info = {"type": None, "location": None, "date": None, "people": None}
        session.collecting_booking = False
        session.confirm_booking_details = False
    # Extract booking type
    btype = extract_booking_type(message)
    if btype:
        session.booking_type = btype
        session.booking_info["type"] = btype
    # Extract location
    loc = extract_location(message)
    if loc:
        session.location = loc
        session.booking_info["location"] = loc
    # Extract date
    date_val = None
    if "DATE" in entities:
        date_val = entities["DATE"]
    else:
        date_val = extract_natural_date(message)
    if date_val:
        session.date = date_val
        session.booking_info["date"] = date_val
    # Extract number of people
    if "CARDINAL" in entities:
        try:
            num = int(entities["CARDINAL"])
            session.people = num
            session.booking_info["people"] = num
        except:
            pass
    # If user is confirming
    if intent == "booking" and session.booking_info["type"] and session.booking_info["location"] and session.booking_info["date"]:
        session.confirm_booking_details = True
    session.last_intent = intent

def answer_knowledge_query(message):
    lowered = message.lower()
    for prefix in ["what is ", "who is "]:
        if lowered.startswith(prefix):
            key = lowered[len(prefix):].strip(" ?.")
            if key in knowledge_graph:
                return knowledge_graph[key]
            else:
                return f"Sorry, I don't have information about {key}. My main focus is travel, bookings, and general knowledge."
    return None

def generate_reply(intent, entities, message):
    # Accept booking type directly if bot just asked for it
    if session.last_bot_message and 'what would you like to book' in session.last_bot_message.lower():
        if message.strip().title() in booking_types:
            session.booking_info["type"] = message.strip().title()
            session.collecting_booking = False
            # After selecting type, prompt for location if not set
            if not session.booking_info["location"]:
                response = f"Where would you like to book your {session.booking_info['type']}?"
                session.last_bot_message = response
                session.last_bot_intent = "booking"
                return response
    # Accept date directly if bot just asked for it
    if session.last_bot_message and 'when do you want to book' in session.last_bot_message.lower():
        try:
            dt = date_parser.parse(message, fuzzy=False)
            date_str = dt.strftime("%d %B %Y")
            session.booking_info["date"] = date_str
            session.date = date_str
            # After selecting date, continue booking flow
            if session.booking_info["type"] and session.booking_info["location"] and session.booking_info["date"]:
                session.confirm_booking_details = True
        except Exception:
            pass
    # Empathy for emotional statements
    if intent == "empathy":
        response = random.choice(EMPATHY_RESPONSES)
        session.last_bot_message = response
        session.last_bot_intent = intent
        return response
    # Small talk
    if intent == "small_talk":
        for phrase, response in small_talk.items():
            if phrase in message.lower():
                session.last_bot_message = response
                session.last_bot_intent = intent
                return response
    # Ask question intent
    if intent == "ask_question":
        response = "Sure! What would you like to know? You can ask me about cities, countries, famous places, or travel tips."
        session.last_bot_message = response
        session.last_bot_intent = intent
        return response
    # Booking flow (stepwise)
    if intent == "booking" or session.last_intent == "booking" or session.collecting_booking:
        update_context(intent, entities, message)
        # If waiting for location and user provides a location, update and continue
        if session.collecting_booking and not session.booking_info["location"]:
            loc = extract_location(message)
            if loc:
                session.booking_info["location"] = loc
                session.location = loc
        # Handle 'all' or multiple booking types
        if session.booking_info["type"] and ("all" in message.lower() or "hotel and flight" in message.lower() or "flight and hotel" in message.lower()):
            response = "Let's book one thing at a time. Would you like to start with a hotel, flight, or something else?"
            session.booking_info["type"] = None
            session.last_bot_message = response
            session.last_bot_intent = intent
            return response
        # Step 1: What to book
        if not session.booking_info["type"]:
            session.collecting_booking = True
            response = "What would you like to book? (hotel, flight, restaurant, train, trip, vacation, tour)"
            session.last_bot_message = response
            session.last_bot_intent = intent
            return response
        # Step 2: Where
        if not session.booking_info["location"]:
            session.collecting_booking = True
            response = f"Where would you like to book your {session.booking_info['type']}?"
            session.last_bot_message = response
            session.last_bot_intent = intent
            return response
        # Step 3: When (stateful, always try to extract date)
        if not session.booking_info["date"]:
            # Try to extract date from message
            date_val = extract_natural_date(message)
            if date_val:
                session.booking_info["date"] = date_val
                session.date = date_val
            if not session.booking_info["date"]:
                session.collecting_booking = True
                response = f"When do you want to book your {session.booking_info['type']} in {session.booking_info['location']}?"
                session.last_bot_message = response
                session.last_bot_intent = intent
                return response
        # Step 4: People (if restaurant/table)
        if session.booking_info["type"] in ["restaurant", "table"] and not session.booking_info["people"]:
            session.collecting_booking = True
            response = "For how many people is the reservation?"
            session.last_bot_message = response
            session.last_bot_intent = intent
            return response
        # All booking details collected, confirm
        if session.confirm_booking_details:
            details = f"{session.booking_info['type'].title()} in {session.booking_info['location']} on {session.booking_info['date']}"
            if session.booking_info["people"]:
                details += f" for {session.booking_info['people']} people"
            session.collecting_booking = False
            session.confirm_booking_details = False
            session.collecting_user_info = True
            response = f"Great! {details}. Now, I need some information to complete your booking. Can I have your name?"
            session.last_bot_message = response
            session.last_bot_intent = intent
            return response
    # User info collection flow (after booking details)
    if session.collecting_user_info or intent == "collect_user_info":
        btype = (session.booking_info.get("type") or "hotel").lower()
        fields_to_collect = BOOKING_FIELDS.get(btype, ["name", "email", "phone", "destination"])
        field_set = False
        if session.awaiting_field == "name" and message.strip():
            session.user_info["name"] = message.strip().title()
            field_set = True
        elif session.awaiting_field == "email" and message.strip():
            session.user_info["email"] = message.strip()
            field_set = True
        elif session.awaiting_field == "phone" and message.strip():
            session.user_info["phone"] = message.strip()
            field_set = True
        elif session.awaiting_field == "destination" and message.strip():
            session.user_info["destination"] = message.strip().title()
            field_set = True
        elif session.awaiting_field == "departure" and message.strip():
            session.user_info["departure"] = message.strip().title()
            field_set = True
        elif session.awaiting_field == "arrival" and message.strip():
            session.user_info["arrival"] = message.strip().title()
            field_set = True
        # Find next missing field
        for field in fields_to_collect:
            if not session.user_info.get(field):
                session.collecting_user_info = True
                session.awaiting_field = field
                response = FIELD_QUESTIONS[field]
                session.last_bot_message = response
                session.last_bot_intent = intent
                return response
        # All fields collected: immediately confirm and store
        session.collecting_user_info = False
        session.awaiting_field = None
        # Build confirmation summary
        summary = f"Congrats! Your {btype} reservation is done with these details:\n"
        for field in fields_to_collect:
            summary += f"{field.title()}: {session.user_info.get(field, '')}\n"
        summary += "You will be contacted soon by our team."
        # Store info in Google Sheet
        try:
            combined_info = {**session.user_info}
            combined_info.update({
                "booking_type": session.booking_info["type"],
                "booking_location": session.booking_info.get("destination") or session.booking_info.get("arrival"),
                "booking_date": session.booking_info["date"],
                "booking_people": session.booking_info["people"]
            })
            write_user_info_to_sheet(combined_info)
        except Exception as e:
            summary += f"\n⚠️ {e}"
            summary += "\n\nYour booking details are saved locally, but there was an issue saving to Google Sheets."
            summary += "\nPlease check your service account credentials or try again later."
        session.user_info = {}
        session.booking_info = {"type": None, "location": None, "date": None, "people": None}
        session.last_bot_message = summary
        session.last_bot_intent = None
        return summary
    # Smarter yes/no handling with selective correction (button-based)
    if message.strip().lower() in ["yes", "no"]:
        # If last bot message was user info confirmation
        if session.last_bot_intent == "collect_user_info" and session.confirm_user_info:
            if message.strip().lower() == "yes":
                try:
                    combined_info = {**session.user_info}
                    combined_info.update({
                        "booking_type": session.booking_info["type"],
                        "booking_location": session.booking_info.get("destination") or session.booking_info.get("arrival"),
                        "booking_date": session.booking_info["date"],
                        "booking_people": session.booking_info["people"]
                    })
                    write_user_info_to_sheet(combined_info)
                    reply = "Your booking and information have been saved!"
                except Exception as e:
                    reply = f"⚠️ {e}\n\nYour booking details are saved locally, but there was an issue saving to Google Sheets. Please check your service account credentials or try again later."
                session.confirm_user_info = False
                session.user_info = {}
                session.booking_info = {"type": None, "location": None, "date": None, "people": None}
                session.last_bot_message = reply
                session.last_bot_intent = None
                return reply
            else:
                # Ask which field to change (button choices)
                session.confirm_user_info = False
                session.awaiting_field = None
                fields = getattr(session, 'fields_to_collect', ["name", "email", "phone", "destination"])
                # Build button choices (as a string for frontend to parse)
                response = "Which field would you like to change? " + ", ".join([f"[{f.title()}]" for f in fields])
                session.last_bot_message = response
                session.last_bot_intent = "edit_user_info"
                session.editable_fields = fields
                return response
        print(session.last_bot_intent)
        # If last bot message was edit_user_info, treat next message as the field to edit
        if session.last_bot_intent == "edit_user_info":
            print("in edit_user_info")
            field = message.strip().lower()
            fields = getattr(session, 'editable_fields', ["name", "email", "phone", "destination"])
            print(fields)
            if field in fields:
                print("in if")
                session.awaiting_field = field
                session.collecting_user_info = True
                # Respond with pre-filled value for editing
                current_val = session.user_info.get(field, "")
                response = f"Edit your {field.title()} (current: {current_val}):"
                session.last_bot_message = response
                session.last_bot_intent = "collect_user_info"
                return response
            else:
                response = "Please select one of: " + ", ".join([f"[{f.title()}]" for f in fields])
                session.last_bot_message = response
                session.last_bot_intent = "edit_user_info"
                return response
        # Otherwise, fallback
        session.last_bot_message = "Could you please clarify what you are confirming?"
        session.last_bot_intent = None
        return session.last_bot_message
    # Small talk and general
    if intent == "greeting":
        session.greeted = True
        if not session.asked_how_are_you:
            session.asked_how_are_you = True
            return f"Hello! How are you today?"
        return f"Hello again! How can I assist you with your booking or a question?"
    elif intent == "how_are_you":
        return "I'm doing well, thank you! How can I help you today?"
    elif intent == "bot_name":
        return f"I'm {BOT_NAME}, your travel assistant bot. I can help you with bookings and answer questions!"
    elif intent == "user_feeling":
        feeling = detect_user_feeling(message)
        session.user_feeling = feeling
        if feeling == "positive":
            return "I'm glad to hear that! If you need help with travel bookings or have a question, just let me know."
        elif feeling == "negative":
            return "I'm sorry to hear that. If there's anything I can do to help with your travel plans or answer a question, please let me know!"
        else:
            return "Thank you for sharing how you feel. How can I assist you today?"
    elif intent == "thanks":
        return "You're welcome! If you need anything else, just ask."
    elif intent == "farewell":
        return "Goodbye! Have a wonderful day."
    elif intent == "help":
        return ("I can help you book hotels, flights, or restaurants, and answer questions about cities, countries, famous people, and world landmarks. "
                "Just tell me what you want to book, where, and when, or ask me a question like 'What is the Eiffel Tower?' or 'Tell me a fun fact!'")
    elif intent == "joke":
        return "Why did the computer go to the doctor? Because it had a virus!"
    elif intent == "fun_fact":
        key = random.choice(fun_facts_keys)
        return knowledge_graph[key]
    elif intent == "weather":
        return "I'm not connected to live weather data, but I hope the weather is nice where you are!"
    elif intent == "show_bookings":
        if not session.bookings:
            return "You have no bookings yet."
        reply = "Here are your bookings:\n"
        for i, b in enumerate(session.bookings, 1):
            reply += f"{i}. {b['type'].title()} in {b['location']} on {b['date']}"
            if b.get('people'):
                reply += f" for {b['people']} people"
            reply += "\n"
        return reply.strip()
    elif intent == "knowledge_query":
        answer = answer_knowledge_query(message)
        return answer
    # Booking flow
    elif intent == "booking" or session.last_intent == "booking":
        update_context(intent, entities, message)
        if not session.booking_type:
            return "What would you like to book? (hotel, flight, restaurant)"
        if not session.location:
            return f"Where would you like to book your {session.booking_type}?"
        if not session.date:
            return f"When do you want to book your {session.booking_type} in {session.location}?"
        if session.booking_type in ["restaurant", "table"] and not session.people:
            return "For how many people is the reservation?"
        if session.confirming:
            details = f"{session.booking_type.title()} in {session.location} on {session.date}"
            if session.people:
                details += f" for {session.people} people"
            session.confirming = False
            session.bookings.append({
                "type": session.booking_type,
                "location": session.location,
                "date": session.date,
                "people": session.people
            })
            session.reset()
            return f"Booking confirmed: {details}!"
    elif intent == "cancel":
        if not session.bookings:
            return "You have no bookings to cancel."
        session.bookings.pop()
        return "Your most recent booking has been cancelled."
    # Fallback/help message (less repetitive, only if not in booking/info collection)
    if intent == "unknown" and not (session.collecting_booking or session.collecting_user_info):
        response = ("I'm here to help you with travel bookings and questions about cities, countries, and famous places. "
                    "You can say things like 'Book a hotel in Paris', 'What is Machu Picchu?', or 'Tell me a fun fact!'.")
        session.last_bot_message = response
        session.last_bot_intent = intent
        return response
    else:
        return ("I'm here to help you with travel bookings, appointments, and general knowledge about cities, countries, famous people, and world landmarks. "
                "You can ask me to book a hotel, flight, or restaurant, or ask questions like 'What is the Eiffel Tower?' or 'Tell me a fun fact!'. "
                "If your question is outside my area, I may not be able to answer, but I'll always try to help!")

def main():
    print(f"Welcome to {BOT_NAME}! Type 'quit' to exit.")
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() == "quit":
            print("Bot: Goodbye!")
            break
        intent, entities = parse_message(user_input)
        reply = generate_reply(intent, entities, user_input)
        print(f"Bot: {reply}")

if __name__ == "__main__":
    main() 