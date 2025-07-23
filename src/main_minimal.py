"""
Minimal FastAPI app for testing without database issues
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from src.core.config import get_settings
import random
import re
import json
from datetime import datetime
from typing import Dict, List, Optional
import requests
import asyncio

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="VoiceBot API (Minimal)",
    description="Two-Wheeler Sales VoiceBot - Minimal Version",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/manifest.json")
async def serve_manifest():
    """Serve PWA manifest"""
    return FileResponse("frontend/manifest.json")

@app.get("/sw.js")
async def serve_service_worker():
    """Serve service worker"""
    return FileResponse("frontend/sw.js")

@app.get("/script.js")
async def serve_script():
    """Serve script file"""
    return FileResponse("frontend/script.js")

@app.get("/styles.css")
async def serve_styles():
    """Serve styles file"""
    return FileResponse("frontend/styles.css")

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    language: str = "en-IN"
    user_id: Optional[str] = None
    context: Optional[Dict] = None

class ChatResponse(BaseModel):
    response: str
    language: str
    audio_url: str | None = None
    intent: Optional[str] = None
    confidence: Optional[float] = None
    suggestions: Optional[List[str]] = None

# Dynamic Conversation Manager with Advanced AI
class AdvancedAIChatBot:
    def __init__(self):
        self.conversation_memory = {}
        
        # Comprehensive vehicle database
        self.vehicle_database = {
            "two_wheelers": {
                "petrol": {
                    "honda_cb_shine": {"name": "Honda CB Shine", "price": 72000, "mileage": "65 kmpl", "engine": "125cc", "type": "Commuter"},
                    "bajaj_pulsar_125": {"name": "Bajaj Pulsar 125", "price": 94000, "mileage": "52 kmpl", "engine": "125cc", "type": "Sports"},
                    "tvs_raider_125": {"name": "TVS Raider 125", "price": 85000, "mileage": "67 kmpl", "engine": "125cc", "type": "Sporty Commuter"},
                    "hero_hf_deluxe": {"name": "Hero HF Deluxe", "price": 65000, "mileage": "70 kmpl", "engine": "100cc", "type": "Economy"},
                    "yamaha_fzs": {"name": "Yamaha FZS V3", "price": 110000, "mileage": "49 kmpl", "engine": "149cc", "type": "Sports"},
                    "royal_enfield_classic": {"name": "Royal Enfield Classic 350", "price": 195000, "mileage": "41 kmpl", "engine": "349cc", "type": "Cruiser"}
                },
                "electric": {
                    "ather_450x": {"name": "Ather 450X", "price": 145000, "range": "85 km", "battery": "2.9 kWh", "type": "Performance Scooter"},
                    "tvs_iqube": {"name": "TVS iQube Electric", "price": 112000, "range": "75 km", "battery": "2.25 kWh", "type": "Smart Scooter"},
                    "bajaj_chetak": {"name": "Bajaj Chetak Electric", "price": 125000, "range": "95 km", "battery": "2.9 kWh", "type": "Classic Scooter"},
                    "hero_vida_v1": {"name": "Hero Vida V1", "price": 115000, "range": "110 km", "battery": "3.44 kWh", "type": "Modern Scooter"},
                    "ola_s1_pro": {"name": "Ola S1 Pro", "price": 135000, "range": "181 km", "battery": "3.97 kWh", "type": "High-tech Scooter"},
                    "simple_one": {"name": "Simple One", "price": 110000, "range": "203 km", "battery": "4.8 kWh", "type": "Long Range Scooter"}
                }
            },
            "four_wheelers": {
                "petrol": {
                    "maruti_alto": {"name": "Maruti Alto", "price": 350000, "mileage": "22 kmpl", "engine": "800cc", "type": "Hatchback"},
                    "hyundai_i10": {"name": "Hyundai Grand i10", "price": 550000, "mileage": "20 kmpl", "engine": "1200cc", "type": "Hatchback"}
                },
                "electric": {
                    "tata_nexon_ev": {"name": "Tata Nexon EV", "price": 1400000, "range": "312 km", "battery": "30.2 kWh", "type": "Compact SUV"},
                    "mg_zs_ev": {"name": "MG ZS EV", "price": 2100000, "range": "419 km", "battery": "44.5 kWh", "type": "SUV"},
                    "mahindra_xe40": {"name": "Mahindra eXUV300", "price": 1500000, "range": "315 km", "battery": "34.5 kWh", "type": "Compact SUV"}
                }
            }
        }
        
        # Language translations
        self.language_translations = {
            "en": {
                "welcome": "Hello! I'm your intelligent AI assistant for vehicles. I can help with any vehicle-related questions.",
                "price_info": "Here's the pricing information you requested:",
                "not_found": "I couldn't find specific information about that vehicle. Let me provide alternatives.",
                "average_cost": "The average cost varies by category and type. Let me break it down for you:",
                "electric_info": "Electric vehicles are becoming increasingly popular. Here's what you need to know:"
            },
            "hi": {
                "welcome": "नमस्ते! मैं आपका बुद्धिमान AI सहायक हूं। मैं किसी भी वाहन संबंधी प्रश्न में आपकी सहायता कर सकता हूं।",
                "price_info": "यहाँ आपके द्वारा मांगी गई मूल्य जानकारी है:",
                "not_found": "मुझे उस वाहन के बारे में विशिष्ट जानकारी नहीं मिली। मैं विकल्प प्रदान करता हूं।",
                "average_cost": "औसत लागत श्रेणी और प्रकार के अनुसार अलग होती है। मैं इसे विस्तार से बताता हूं:",
                "electric_info": "इलेक्ट्रिक वाहन तेजी से लोकप्रिय हो रहे हैं। यहाँ जानने योग्य बातें हैं:"
            },
            "ta": {
                "welcome": "வணக்கம்! நான் உங்கள் புத்திசாலி AI உதவியாளர். வாகன தொடர்பான எந்த கேள்விக்கும் உதவ முடியும்.",
                "price_info": "நீங்கள் கேட்ட விலை தகவல் இதோ:",
                "not_found": "அந்த வாகனத்தைப் பற்றிய குறிப்பிட்ட தகவல் கிடைக்கவில்லை. மாற்று வழிகளை தருகிறேன்.",
                "average_cost": "சராசரி விலை வகை மற்றும் வகையைப் பொறுத்து மாறுபடும். விரிவாக விளக்குகிறேன்:",
                "electric_info": "மின்சார வாகனங்கள் வேகமாக பிரபலமாகி வருகின்றன. தெரிந்து கொள்ள வேண்டியவை:"
            }
        }
        
    def detect_language(self, text: str) -> str:
        """Detect language of input text"""
        # Simple language detection based on script
        if re.search(r'[\u0900-\u097F]', text):  # Devanagari (Hindi)
            return "hi"
        elif re.search(r'[\u0B80-\u0BFF]', text):  # Tamil
            return "ta"
        else:
            return "en"
    
    def translate_text(self, text: str, target_lang: str) -> str:
        """Basic translation support"""
        if target_lang == "en":
            return text
        
        # Simple keyword-based translation for common terms
        translations = {
            "hi": {
                "bike": "बाइक", "price": "कीमत", "electric": "इलेक्ट्रिक", 
                "vehicle": "वाहन", "cost": "लागत", "average": "औसत"
            },
            "ta": {
                "bike": "பைக்", "price": "விலை", "electric": "மின்சார", 
                "vehicle": "வாகனம்", "cost": "செலவு", "average": "சராசரி"
            }
        }
        
        if target_lang in translations:
            for eng, local in translations[target_lang].items():
                text = text.replace(eng, local)
        
        return text
    
    def analyze_query_intelligently(self, message: str, language: str) -> Dict:
        """Advanced query analysis with AI-like understanding"""
        message_lower = message.lower()
        analysis = {
            "intent": "general",
            "entities": {},
            "query_type": "informational",
            "confidence": 0.5
        }
        
        # Electric vehicle queries
        if any(term in message_lower for term in ['electric', 'ev', 'e-vehicle', 'battery', 'charging', 'इलेक्ट्रिक', 'மின்சார']):
            analysis["intent"] = "electric_vehicle_inquiry"
            analysis["confidence"] = 0.9
            
            # Extract specific queries about electric vehicles
            if any(term in message_lower for term in ['average cost', 'average price', 'औसत कीमत', 'சராசரி விலை']):
                analysis["query_type"] = "average_pricing"
            elif any(term in message_lower for term in ['range', 'battery life', 'charging time']):
                analysis["query_type"] = "technical_specs"
                
        # Price and cost queries
        elif any(term in message_lower for term in ['cost', 'price', 'average', 'कीमत', 'लागत', 'औसत', 'விலை', 'செலவு']):
            analysis["intent"] = "pricing_inquiry"
            analysis["confidence"] = 0.85
            
            if any(term in message_lower for term in ['average', 'typical', 'normal', 'औसत', 'सामान्य', 'சராசரி']):
                analysis["query_type"] = "average_pricing"
                
        # Specific vehicle queries
        elif any(term in message_lower for term in ['honda', 'bajaj', 'tvs', 'ather', 'ola', 'tata']):
            analysis["intent"] = "specific_vehicle_inquiry"
            analysis["confidence"] = 0.8
            
        # Comparison queries
        elif any(term in message_lower for term in ['compare', 'vs', 'versus', 'difference', 'बेहतर', 'तुलना']):
            analysis["intent"] = "comparison"
            analysis["confidence"] = 0.75
            
        return analysis
    
    def generate_intelligent_response(self, message: str, user_id: str = None, language: str = "en") -> Dict:
        """Generate truly intelligent, context-aware responses"""
        
        # Detect language if not provided
        detected_lang = self.detect_language(message)
        if detected_lang != "en":
            language = detected_lang
            
        analysis = self.analyze_query_intelligently(message, language)
        
        response_data = {
            "response": "",
            "intent": analysis["intent"],
            "confidence": analysis["confidence"],
            "suggestions": [],
            "language": language
        }
        
        # Generate response based on intent and query type
        if analysis["intent"] == "electric_vehicle_inquiry":
            if analysis["query_type"] == "average_pricing":
                response_data.update(self._generate_ev_average_cost_response(language))
            else:
                response_data.update(self._generate_ev_general_response(language))
                
        elif analysis["intent"] == "pricing_inquiry":
            if analysis["query_type"] == "average_pricing":
                response_data.update(self._generate_average_pricing_response(language))
            else:
                response_data.update(self._generate_general_pricing_response(language))
                
        elif analysis["intent"] == "specific_vehicle_inquiry":
            response_data.update(self._generate_specific_vehicle_response(message, language))
            
        elif analysis["intent"] == "comparison":
            response_data.update(self._generate_comparison_response(language))
            
        else:
            response_data.update(self._generate_intelligent_general_response(message, language))
        
        # Update conversation memory
        if user_id:
            if user_id not in self.conversation_memory:
                self.conversation_memory[user_id] = {"history": [], "preferences": {}}
            self.conversation_memory[user_id]["history"].append({
                "message": message,
                "response": response_data["response"],
                "intent": analysis["intent"],
                "language": language,
                "timestamp": datetime.now().isoformat()
            })
            
        return response_data
    
    def _generate_ev_average_cost_response(self, language: str) -> Dict:
        """Generate detailed response about electric vehicle average costs"""
        
        # Calculate averages from our database
        ev_two_wheelers = self.vehicle_database["two_wheelers"]["electric"]
        ev_four_wheelers = self.vehicle_database["four_wheelers"]["electric"]
        
        avg_two_wheeler = sum(v["price"] for v in ev_two_wheelers.values()) // len(ev_two_wheelers)
        avg_four_wheeler = sum(v["price"] for v in ev_four_wheelers.values()) // len(ev_four_wheelers)
        
        if language == "hi":
            response = f"""🔋 इलेक्ट्रिक वाहनों की औसत लागत:

📱 दो पहिया इलेक्ट्रिक वाहन:
• औसत कीमत: ₹{avg_two_wheeler:,} 
• रेंज: ₹1,10,000 - ₹1,45,000
• बैटरी रेंज: 75-203 km

🚗 चार पहिया इलेक्ट्रिक वाहन:
• औसत कीमत: ₹{avg_four_wheeler:,}
• रेंज: ₹14,00,000 - ₹21,00,000  
• बैटरी रेंज: 312-419 km

💡 सबसे किफायती: TVS iQube (₹1,12,000)
🏆 सबसे अच्छी रेंज: Simple One (203 km)
⚡ तेज़ चार्जिंग: Ather 450X"""
            
        elif language == "ta":
            response = f"""🔋 மின்சார வாகனங்களின் சராசரி விலை:

📱 இரு சக்கர மின்சார வாகனங்கள்:
• சராசரி விலை: ₹{avg_two_wheeler:,}
• வரம்பு: ₹1,10,000 - ₹1,45,000
• பேட்டரி வரம்பு: 75-203 km

🚗 நான்கு சக்கர மின்சார வாகனங்கள்:
• சராசரி விலை: ₹{avg_four_wheeler:,}
• வரம்பு: ₹14,00,000 - ₹21,00,000
• பேட்டரி வரம்பு: 312-419 km

💡 மிகவும் மலிவான: TVS iQube (₹1,12,000)
🏆 சிறந்த வரம்பு: Simple One (203 km)
⚡ வேகமான சார்ஜிங்: Ather 450X"""
            
        else:  # English
            response = f"""🔋 Average Cost of Electric Vehicles:

📱 Two-Wheeler Electric Vehicles:
• Average Price: ₹{avg_two_wheeler:,}
• Price Range: ₹1,10,000 - ₹1,45,000
• Battery Range: 75-203 km per charge

🚗 Four-Wheeler Electric Vehicles:
• Average Price: ₹{avg_four_wheeler:,}
• Price Range: ₹14,00,000 - ₹21,00,000
• Battery Range: 312-419 km per charge

💡 Most Affordable: TVS iQube Electric (₹1,12,000)
🏆 Best Range: Simple One (203 km)
⚡ Fast Charging: Ather 450X (0-80% in 3.3 hrs)

🎯 Key Benefits of EVs:
• Zero emissions & eco-friendly
• Lower running costs (₹0.80/km vs ₹3.5/km)
• Government subsidies up to ₹1,50,000
• Minimal maintenance required"""

        suggestions = [
            "Show specific EV models", 
            "Compare EV vs petrol costs", 
            "EV charging infrastructure", 
            "Government EV subsidies"
        ]
        
        return {"response": response, "suggestions": suggestions}
    
    def _generate_ev_general_response(self, language: str) -> Dict:
        """Generate general electric vehicle information"""
        
        if language == "hi":
            response = """🔋 इलेक्ट्रिक वाहन - भविष्य यहाँ है!

🌟 लोकप्रिय दो पहिया EV मॉडल:
• Ather 450X - ₹1,45,000 (85 km रेंज)
• TVS iQube - ₹1,12,000 (75 km रेंज) 
• Bajaj Chetak - ₹1,25,000 (95 km रेंज)
• Ola S1 Pro - ₹1,35,000 (181 km रेंज)

💰 फायदे:
• कम चलाने की लागत
• पर्यावरण-अनुकूल
• सरकारी सब्सिडी
• कम रखरखाव"""
            
        else:
            response = """🔋 Electric Vehicles - The Future is Here!

🌟 Popular Two-Wheeler EV Models:
• Ather 450X - ₹1,45,000 (85 km range)
• TVS iQube Electric - ₹1,12,000 (75 km range)
• Bajaj Chetak Electric - ₹1,25,000 (95 km range)
• Ola S1 Pro - ₹1,35,000 (181 km range)

💰 Benefits:
• Lower running costs (₹0.80/km)
• Zero emissions
• Government subsidies
• Minimal maintenance
• Smart connectivity features"""

        suggestions = ["EV average costs", "Best EV models", "EV vs petrol comparison", "Charging stations near me"]
        return {"response": response, "suggestions": suggestions}
    
    def _generate_average_pricing_response(self, language: str) -> Dict:
        """Generate comprehensive average pricing information"""
        
        if language == "hi":
            response = """💰 वाहनों की औसत कीमत (2025):

🏍️ दो पहिया वाहन:
• बेसिक कम्यूटर: ₹65,000 - ₹85,000
• स्पोर्ट्स बाइक: ₹90,000 - ₹1,50,000  
• प्रीमियम बाइक: ₹1,50,000 - ₹3,00,000
• इलेक्ट्रिक स्कूटर: ₹1,10,000 - ₹1,45,000

🚗 चार पहिया वाहन:
• हैचबैक: ₹3,50,000 - ₹8,00,000
• सेडान: ₹8,00,000 - ₹15,00,000
• SUV: ₹12,00,000 - ₹30,00,000
• इलेक्ट्रिक कार: ₹14,00,000 - ₹50,00,000"""
            
        else:
            response = """💰 Average Vehicle Pricing (2025):

🏍️ Two-Wheeler Vehicles:
• Basic Commuter: ₹65,000 - ₹85,000
• Sports Bikes: ₹90,000 - ₹1,50,000
• Premium Bikes: ₹1,50,000 - ₹3,00,000
• Electric Scooters: ₹1,10,000 - ₹1,45,000

🚗 Four-Wheeler Vehicles:
• Hatchbacks: ₹3,50,000 - ₹8,00,000
• Sedans: ₹8,00,000 - ₹15,00,000
• SUVs: ₹12,00,000 - ₹30,00,000
• Electric Cars: ₹14,00,000 - ₹50,00,000

📊 Market Trends:
• Electric vehicle prices dropping 15% annually
• Petrol prices affecting conventional vehicle demand
• Government incentives making EVs more attractive"""

        suggestions = ["Show specific models", "EV vs petrol costs", "Finance options", "Best value vehicles"]
        return {"response": response, "suggestions": suggestions}
    
    def _generate_specific_vehicle_response(self, message: str, language: str) -> Dict:
        """Generate response for specific vehicle queries"""
        message_lower = message.lower()
        
        # Find mentioned vehicles
        mentioned_vehicles = []
        for category in self.vehicle_database.values():
            for fuel_type in category.values():
                for vehicle_id, vehicle in fuel_type.items():
                    if any(word in message_lower for word in vehicle["name"].lower().split()):
                        mentioned_vehicles.append(vehicle)
        
        if mentioned_vehicles:
            vehicle = mentioned_vehicles[0]  # Take first match
            
            if language == "hi":
                if "price" in vehicle:
                    response = f"""🏍️ {vehicle['name']} की जानकारी:

💰 कीमत: ₹{vehicle['price']:,}
⛽ माइलेज: {vehicle['mileage']}
🔧 इंजन: {vehicle['engine']}
📋 टाइप: {vehicle['type']}

✅ मुख्य विशेषताएं:
• विश्वसनीयता और गुणवत्ता
• बेहतरीन ईंधन दक्षता
• आकर्षक डिज़ाइन
• व्यापक सर्विस नेटवर्क"""
                else:
                    response = f"""🔋 {vehicle['name']} की जानकारी:

💰 कीमत: ₹{vehicle['price']:,}
🔋 रेंज: {vehicle['range']}
⚡ बैटरी: {vehicle['battery']}
📋 टाइप: {vehicle['type']}"""
            else:
                if "price" in vehicle:
                    response = f"""🏍️ {vehicle['name']} Details:

💰 Price: ₹{vehicle['price']:,}
⛽ Mileage: {vehicle['mileage']}
🔧 Engine: {vehicle['engine']}
📋 Type: {vehicle['type']}

✅ Key Features:
• Reliable performance
• Excellent fuel efficiency
• Attractive design
• Wide service network"""
                else:
                    response = f"""🔋 {vehicle['name']} Details:

💰 Price: ₹{vehicle['price']:,}
🔋 Range: {vehicle['range']}
⚡ Battery: {vehicle['battery']}
📋 Type: {vehicle['type']}

✅ Key Features:
• Zero emissions
• Smart connectivity
• Fast charging capability
• Government subsidies available"""
        else:
            response = "I'd be happy to help you with specific vehicle information! Could you please mention the exact model name you're interested in?"
            
        suggestions = ["Compare with similar models", "Check financing options", "Book test ride", "View all specifications"]
        return {"response": response, "suggestions": suggestions}
    
    def _generate_comparison_response(self, language: str) -> Dict:
        """Generate comparison assistance response"""
        
        if language == "hi":
            response = """⚖️ तुलना सहायता:

🔍 मैं निम्नलिखित तुलना कर सकता हूं:
• विभिन्न मॉडलों की कीमत तुलना
• ईंधन दक्षता और प्रदर्शन
• इलेक्ट्रिक vs पेट्रोल वाहन
• ब्रांड्स की तुलना
• विशेषताओं की तुलना

कृपया बताएं कि आप किन वाहनों की तुलना करना चाहते हैं?"""
        else:
            response = """⚖️ Comparison Assistant:

🔍 I can help you compare:
• Price comparison between models
• Fuel efficiency and performance
• Electric vs Petrol vehicles
• Brand comparisons
• Feature comparisons
• Running costs analysis

Please tell me which specific vehicles you'd like to compare!"""

        suggestions = ["Electric vs Petrol", "Honda vs Bajaj", "Budget bikes under 1L", "Premium bikes comparison"]
        return {"response": response, "suggestions": suggestions}
    
    def _generate_intelligent_general_response(self, message: str, language: str) -> Dict:
        """Generate intelligent general response for any query"""
        
        message_lower = message.lower()
        
        # Analyze what user might be looking for
        if any(term in message_lower for term in ['help', 'assist', 'support', 'मदद', 'सहायता']):
            if language == "hi":
                response = """🤖 मैं आपका बुद्धिमान AI वाहन सहायक हूं!

मैं इन सब में आपकी मदद कर सकता हूं:
• किसी भी वाहन की कीमत और जानकारी
• इलेक्ट्रिक और पेट्रोल वाहनों की तुलना
• औसत कीमतों की जानकारी
• बेस्ट मॉडल सुझाव
• EMI और फाइनेंस विकल्प
• टेस्ट राइड बुकिंग

कोई भी सवाल पूछें - मैं तुरंत जवाब दूंगा!"""
            else:
                response = """🤖 I'm your intelligent AI vehicle assistant!

I can help you with:
• Any vehicle pricing and information
• Electric vs petrol vehicle comparisons  
• Average cost analysis
• Best model recommendations
• EMI and financing options
• Test ride bookings
• Technical specifications
• Market trends and insights

Ask me anything about vehicles - I'll provide instant, accurate answers!"""
        else:
            # Try to understand and respond to the specific query
            if language == "hi":
                response = f"""🤔 मैं समझ गया कि आप '{message}' के बारे में पूछ रहे हैं।

मैं आपका व्यक्तिगत वाहन सलाहकार हूं और किसी भी वाहन संबंधी प्रश्न का सटीक उत्तर दे सकता हूं। कृपया अधिक विशिष्ट जानकारी दें ताकि मैं बेहतर सहायता कर सकूं।

उदाहरण:
• "इलेक्ट्रिक स्कूटर की औसत कीमत क्या है?"
• "Honda CB Shine की कीमत बताओ"
• "बेस्ट बाइक 1 लाख के अंदर सुझाओ" """
            else:
                response = f"""🤔 I understand you're asking about '{message}'.

I'm your personal vehicle advisor and can provide accurate answers to any vehicle-related question. Please provide more specific details so I can assist you better.

Examples:
• "What's the average cost of electric scooters?"
• "Tell me about Honda CB Shine pricing"
• "Suggest best bikes under 1 lakh"
• "Compare electric vs petrol vehicles" """

        suggestions = ["Vehicle pricing info", "Electric vehicle costs", "Best bike recommendations", "Compare vehicles"]
        return {"response": response, "suggestions": suggestions}

# Initialize advanced AI chatbot
advanced_ai_chatbot = AdvancedAIChatBot()

@app.get("/")
async def serve_frontend():
    """Serve the frontend"""
    return FileResponse("frontend/index.html")

@app.get("/api/root")
async def root():
    """Root endpoint"""
    return {
        "message": "VoiceBot API is running!",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "sqlite_ready",
        "speech_service": "available",
        "timestamp": "2025-07-22T00:00:00Z"
    }

@app.get("/api/health")
async def api_health_check():
    """API Health check endpoint"""
    return {
        "status": "healthy",
        "database": "sqlite_ready",
        "speech_service": "available",
        "timestamp": "2025-07-22T00:00:00Z",
        "api_version": "1.0.0"
    }

@app.get("/api/speech/languages")
async def get_supported_languages():
    """Get supported languages"""
    return {
        "languages": [
            {"code": "en-IN", "name": "English (India)"},
            {"code": "hi-IN", "name": "हिंदी (Hindi)"},
            {"code": "ta-IN", "name": "தமிழ் (Tamil)"},
            {"code": "te-IN", "name": "తెలుగు (Telugu)"},
            {"code": "mr-IN", "name": "मराठी (Marathi)"},
            {"code": "gu-IN", "name": "ગુજરાતી (Gujarati)"},
            {"code": "bn-IN", "name": "বাংলা (Bengali)"}
        ]
    }

@app.post("/api/chat")
async def chat_endpoint(chat_message: ChatMessage) -> ChatResponse:
    """Advanced AI chat endpoint with multilingual intelligence"""
    try:
        # Use the advanced AI chatbot for truly intelligent responses
        response_data = advanced_ai_chatbot.generate_intelligent_response(
            message=chat_message.message,
            user_id=chat_message.user_id,
            language=chat_message.language or "en"
        )
        
        return ChatResponse(
            response=response_data["response"],
            language=response_data["language"],
            intent=response_data["intent"],
            confidence=response_data["confidence"],
            suggestions=response_data["suggestions"]
        )
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        # Fallback response
        return ChatResponse(
            response="I apologize for the technical issue. However, I'm here to help with any vehicle-related questions! Please feel free to ask about pricing, models, electric vehicles, or any other vehicle information.",
            language=chat_message.language or "en",
            intent="error",
            confidence=0.0,
            suggestions=["Vehicle pricing", "Electric vehicles", "Best models", "Technical support"]
        )

@app.post("/chat")
async def simple_chat_endpoint(chat_message: ChatMessage) -> ChatResponse:
    """Simple chat endpoint without /api prefix"""
    return await chat_endpoint(chat_message)

@app.get("/api/conversation/{user_id}")
async def get_conversation_history(user_id: str):
    """Get conversation history for a user"""
    if user_id in advanced_ai_chatbot.conversation_memory:
        return {
            "user_id": user_id,
            "history": advanced_ai_chatbot.conversation_memory[user_id]["history"][-10:],  # Last 10 messages
            "preferences": advanced_ai_chatbot.conversation_memory[user_id]["preferences"]
        }
    return {"user_id": user_id, "history": [], "preferences": {}}

@app.delete("/api/conversation/{user_id}")
async def clear_conversation_history(user_id: str):
    """Clear conversation history for a user"""
    if user_id in advanced_ai_chatbot.conversation_memory:
        del advanced_ai_chatbot.conversation_memory[user_id]
    return {"message": f"Conversation history cleared for user {user_id}"}

@app.get("/api/chatbot/stats")
async def get_chatbot_statistics():
    """Get advanced chatbot usage statistics"""
    total_users = len(advanced_ai_chatbot.conversation_memory)
    total_conversations = sum(len(user_data["history"]) for user_data in advanced_ai_chatbot.conversation_memory.values())
    
    # Language distribution
    language_counts = {}
    intent_counts = {}
    
    for user_data in advanced_ai_chatbot.conversation_memory.values():
        for msg in user_data["history"]:
            # Count languages
            lang = msg.get("language", "en")
            language_counts[lang] = language_counts.get(lang, 0) + 1
            
            # Count intents  
            intent = msg.get("intent", "unknown")
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
    
    return {
        "total_users": total_users,
        "total_conversations": total_conversations,
        "language_distribution": language_counts,
        "intent_distribution": intent_counts,
        "supported_languages": ["en", "hi", "ta", "te", "mr"],
        "available_vehicles": {
            "two_wheeler_petrol": len(advanced_ai_chatbot.vehicle_database["two_wheelers"]["petrol"]),
            "two_wheeler_electric": len(advanced_ai_chatbot.vehicle_database["two_wheelers"]["electric"]),
            "four_wheeler_petrol": len(advanced_ai_chatbot.vehicle_database["four_wheelers"]["petrol"]),
            "four_wheeler_electric": len(advanced_ai_chatbot.vehicle_database["four_wheelers"]["electric"])
        },
        "ai_capabilities": [
            "Multilingual support (English, Hindi, Tamil)",
            "Intelligent intent detection",
            "Context-aware responses", 
            "Electric vehicle expertise",
            "Average pricing calculations",
            "Dynamic query understanding"
        ]
    }

@app.get("/api/models")
async def get_bike_models():
    """Get available bike models"""
    return {
        "models": [
            {
                "name": "Honda CB Shine",
                "price": 72000,
                "mileage": "65 kmpl",
                "engine": "125cc",
                "type": "Commuter"
            },
            {
                "name": "Bajaj Pulsar 125",
                "price": 94000,
                "mileage": "50 kmpl", 
                "engine": "125cc",
                "type": "Sports"
            },
            {
                "name": "TVS Raider 125",
                "price": 85000,
                "mileage": "67 kmpl",
                "engine": "125cc", 
                "type": "Sporty Commuter"
            },
            {
                "name": "Hero HF Deluxe",
                "price": 65000,
                "mileage": "70 kmpl",
                "engine": "100cc",
                "type": "Economy"
            }
        ]
    }

@app.get("/api/offers")
async def get_current_offers():
    """Get current offers and promotions"""
    return {
        "offers": [
            {
                "title": "Festive Bonanza",
                "description": "Up to ₹15,000 off on select models",
                "validity": "Till Jan 31, 2025",
                "models": ["CB Shine", "Pulsar 125"]
            },
            {
                "title": "Zero Down Payment",
                "description": "Take your dream bike home with 0% down payment",
                "validity": "Limited time offer",
                "models": ["All models"]
            },
            {
                "title": "Exchange Bonus",
                "description": "Extra ₹5,000 on old bike exchange",
                "validity": "Ongoing",
                "models": ["All models"]
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
