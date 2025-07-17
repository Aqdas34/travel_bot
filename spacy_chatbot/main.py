import random
import re
import spacy

nlp = spacy.load("en_core_web_sm")

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
booking_types = ["hotel", "flight", "restaurant", "table"]

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
    "cairo": "Cairo is the capital of Egypt, famous for the Pyramids of Giza.",
    "rio de janeiro": "Rio de Janeiro is a city in Brazil, known for its Carnival festival and Christ the Redeemer statue.",
    # Countries
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
    # Famous People
    "sundar pichai": "Sundar Pichai is the CEO of Google.",
    "elon musk": "Elon Musk is the CEO of Tesla and SpaceX, and founder of several innovative companies.",
    "bill gates": "Bill Gates is the co-founder of Microsoft and a philanthropist.",
    "jeff bezos": "Jeff Bezos is the founder of Amazon and Blue Origin.",
    "tim cook": "Tim Cook is the CEO of Apple Inc.",
    "mark zuckerberg": "Mark Zuckerberg is the co-founder and CEO of Facebook (Meta Platforms).",
    "malala yousafzai": "Malala Yousafzai is a Pakistani activist for female education and the youngest Nobel Prize laureate.",
    "albert einstein": "Albert Einstein was a theoretical physicist who developed the theory of relativity.",
    "marie curie": "Marie Curie was a physicist and chemist who conducted pioneering research on radioactivity.",
    "nelson mandela": "Nelson Mandela was a South African anti-apartheid revolutionary and former President of South Africa.",
    # Companies
    "google": "Google is a multinational technology company specializing in Internet-related services and products.",
    "tesla": "Tesla is an American electric vehicle and clean energy company.",
    "microsoft": "Microsoft is a multinational technology company known for Windows, Office, and Azure.",
    "apple": "Apple Inc. is a technology company known for the iPhone, Mac computers, and innovative design.",
    "amazon": "Amazon is a global e-commerce and cloud computing company.",
    "facebook": "Facebook (now Meta Platforms) is a social media and technology company.",
    "samsung": "Samsung is a South Korean multinational electronics company.",
    "toyota": "Toyota is a Japanese multinational automotive manufacturer.",
    "coca-cola": "Coca-Cola is a world-famous beverage company known for its soft drinks.",
    "disney": "Disney is an American multinational entertainment and media company.",
    # Landmarks & General Facts
    "eiffel tower": "The Eiffel Tower is a wrought-iron lattice tower in Paris, France, and a global cultural icon.",
    "colosseum": "The Colosseum is an ancient amphitheater in Rome, Italy, and one of the greatest works of Roman architecture.",
    "statue of liberty": "The Statue of Liberty is a colossal neoclassical sculpture on Liberty Island in New York City, USA.",
    "burj khalifa": "The Burj Khalifa in Dubai is the tallest building in the world.",
    "mount fuji": "Mount Fuji is the highest mountain in Japan and a famous symbol of the country.",
    "big ben": "Big Ben is the nickname for the Great Bell of the clock at the north end of the Palace of Westminster in London.",
    "great wall of china": "The Great Wall of China is a series of fortifications built to protect China from invasions.",
    "pyramids of giza": "The Pyramids of Giza are ancient pyramid-shaped masonry structures in Egypt.",
    "sydney opera house": "The Sydney Opera House is a multi-venue performing arts centre in Sydney, Australia.",
    "christ the redeemer": "Christ the Redeemer is an iconic statue of Jesus Christ in Rio de Janeiro, Brazil.",
    # Fun Facts
    "honey never spoils": "Honey never spoils. Archaeologists have found edible honey in ancient Egyptian tombs.",
    "bananas are berries": "Botanically, bananas are berries, but strawberries are not.",
    "octopus has three hearts": "An octopus has three hearts and blue blood.",
    "lightning": "Lightning is hotter than the surface of the sun."
}

# Fun facts keys for random selection
fun_facts_keys = [
    "honey never spoils",
    "bananas are berries",
    "octopus has three hearts",
    "lightning"
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

session = Session()

def extract_booking_type(message):
    for btype in booking_types:
        if btype in message.lower():
            return btype
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
        r"i\s*(')?m\s*(not fine|not good|not great|bad|not okay|not ok|sad|upset|unwell)",
        r"i am\s*(not fine|not good|not great|bad|not okay|not ok|sad|upset|unwell)"
    ]
    for pat in negative_patterns:
        if re.search(pat, msg):
            return "negative"
    return None

def parse_message(message):
    doc = nlp(message)
    entities = {ent.label_: ent.text for ent in doc.ents}
    lowered = message.lower()
    # Small talk and knowledge graph
    if any(greet in lowered for greet in greetings):
        intent = "greeting"
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
    elif any(word in lowered for word in ["book", "reserve", "schedule"]):
        intent = "booking"
    elif "cancel" in lowered:
        intent = "cancel"
    elif any(thank in lowered for thank in thanks):
        intent = "thanks"
    elif any(farewell in lowered for farewell in farewells):
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

def update_context(intent, entities, message):
    # Extract booking type
    btype = extract_booking_type(message)
    if btype:
        session.booking_type = btype
    # Extract location
    if "GPE" in entities:
        session.location = entities["GPE"]
    # Extract date
    if "DATE" in entities:
        session.date = entities["DATE"]
    # Extract number of people
    if "CARDINAL" in entities:
        try:
            num = int(entities["CARDINAL"])
            session.people = num
        except:
            pass
    # If user is confirming
    if intent == "booking" and session.booking_type and session.location and session.date:
        session.confirming = True
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