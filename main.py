# import pytesseract
import os
from PIL import Image
import asyncio
from anthropic import Anthropic
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import easyocr
import json

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

class DreamSeekerAgentSetup:
    def __init__(self, name="Dream", system_prompt=""):
        """
        Initializes the agent with a name and a system prompt
        The system prompt defines the agent's role and behavior
        """
        self.name = name
        self.system_prompt = system_prompt
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.conversation_history = []

    def think(self, user_input):
        """
        Main method where the agent 'thinks' about the response
        """
        # Build the message with history
        messages = self.conversation_history + [
            {"role": "user", "content": user_input}
        ]

        try:
            response = self.client.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=2000,
                system=self.system_prompt,
                messages=messages
            )

            # Extract response
            agent_response = response.content[0].text
            
            # Save to history - Keep only last 2 conversations (4 messages total)
            new_messages = [
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": agent_response}
            ]
            
            # Add new messages to history
            self.conversation_history.extend(new_messages)
            
            # Keep only the last 4 messages (2 complete conversations)
            if len(self.conversation_history) > 4:
                self.conversation_history = self.conversation_history[-4:]

            return agent_response

        except Exception as e:
            return f"Erreur lors de la communication avec Claude: {str(e)}"

class DreamSeeker(DreamSeekerAgentSetup):
    def __init__(self):
        system_prompt = """
        Tu es un assistant de réservation de voyage intelligent. Ton rôle est de :
        1. Analyser les éléments détectés sur la page web (texte, boutons, champs)
        2. Identifier les actions possibles pour avancer vers l'objectif de réservation
        3. Proposer LA MEILLEURE action à effectuer parmi les options disponibles
        4. Fournir des coordonnées précises basées sur les éléments OCR détectés

        IMPORTANT: Les coordonnées de l'écran vont de 0,0 (coin supérieur gauche) à 1280,832 (coin inférieur droit).
        
        Format de réponse OBLIGATOIRE (JSON pur, sans markdown):
        {
            "action": "click|fill|wait|scroll",
            "target": "description du target",
            "coordinates": [x, y],
            "value": "valeur à saisir (si applicable)",
            "reasoning": "pourquoi cette action"
        }

        Objectif: Réserver un voyage (hôtel, vol, etc.) sur le site actuel.
        """
        super().__init__(name="DreamSeeker", system_prompt=system_prompt)
    
    def analyze_page_elements(self, ocr_data, page_url, objective="réserver un voyage aux Maldives"):
        """
        Analyse les éléments OCR et propose la prochaine action
        """
        prompt = f"""
        URL actuelle: {page_url}
        Objectif: {objective}
        
        Éléments détectés sur la page (OCR):
        {json.dumps(ocr_data, indent=2, ensure_ascii=False)}
        
        Analyse ces éléments et détermine la MEILLEURE action à effectuer pour avancer vers l'objectif.
        Si c'est un bannière ou une publicité qui nécessite une action, occupe toi en PRIORITÉ.

        Considère:
        - Les boutons de recherche/réservation visibles
        - Les champs de saisie nécessaires 
        - La navigation possible
        - L'étape logique suivante

        Réponds UNIQUEMENT avec un objet JSON valide, sans markdown ni formatage:
        {{"action": "click|fill|wait|scroll", "target": "description", "coordinates": [x, y], "value": "texte si nécessaire", "reasoning": "explication"}}
        """
        
        response = self.think(prompt)
        try:
            # Clean response - remove markdown formatting if present
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]  # Remove ```json
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]  # Remove ```
            cleaned_response = cleaned_response.strip()
            
            # Try to parse JSON response
            return json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            print(f"❌ Erreur JSON parsing: {e}")
            print(f"🔍 Réponse brute: {response}")
            # Fallback if JSON parsing fails
            return {
                "action": "wait",
                "target": "parsing error",
                "coordinates": [640, 400],  # Center screen coordinates
                "value": "",
                "reasoning": f"Erreur de parsing JSON: {str(e)}"
            }

class OCR:
    def __init__(self):
        print("OCR Class Initialized")
        self.reader = easyocr.Reader(['fr', 'en'])
        self.ocr_data = []

    def open_image(self, image_path):
        self.image = Image.open(image_path)
        print(f"Image opened: {image_path}")

    def parse_image_data(self, image_path='screenshot.png'):
        """
        Parse image and return structured data with coordinates
        """
        result = self.reader.readtext(image_path)

        self.ocr_data = []
        for detection in result:
            coordinates, text, confidence = detection

            # Calculate center coordinates and convert to native Python int
            x_coords = [float(point[0]) for point in coordinates]
            y_coords = [float(point[1]) for point in coordinates]
            center_x = int(sum(x_coords) / len(x_coords))
            center_y = int(sum(y_coords) / len(y_coords))

            # Convert bounding box coordinates to native Python types
            bbox = [[float(point[0]), float(point[1])] for point in coordinates]

            self.ocr_data.append({
                "text": str(text),
                "coordinates": [center_x, center_y],
                "bounding_box": bbox,
                "confidence": float(confidence)
            })

        print(f"OCR détecté {len(self.ocr_data)} éléments")
        return self.ocr_data

    def process_image(self, image_path):
        self.open_image(image_path)
        return self.parse_image_data(image_path)

async def execute_action(page, action_data):
    """
    Execute the action determined by Claude
    """
    action = action_data.get("action", "wait")
    coordinates = action_data.get("coordinates", [640, 400])  # Default center coordinates
    value = action_data.get("value", "")
    target = action_data.get("target", "")
    
    print(f"\n🤖 Action décidée: {action}")
    print(f"📍 Target: {target}")
    print(f"📋 Raisonnement: {action_data.get('reasoning', 'N/A')}")
    
    try:
        if action == "click":
            print(f"🖱️  Clique sur {coordinates}")
            await page.mouse.click(coordinates[0], coordinates[1])
            await page.wait_for_timeout(2000)  # Wait for page reaction
            
        elif action == "fill":
            print(f"⌨️  Saisie '{value}' à {coordinates}")
            # First click to focus, then fill
            await page.mouse.click(coordinates[0], coordinates[1])
            await page.wait_for_timeout(500)
            # Clear field first, then type
            await page.keyboard.press("Control+a")  # Select all
            await page.keyboard.type(value)
            await page.wait_for_timeout(1000)
            
        elif action == "scroll":
            print(f"📜 Scroll vers {coordinates}")
            await page.evaluate(f"window.scrollTo({coordinates[0]}, {coordinates[1]})")
            await page.wait_for_timeout(1000)
            
        elif action == "wait":
            print("⏳ Attente...")
            await page.wait_for_timeout(2000)
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution de l'action: {str(e)}")
        return False

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            # slow_mo=1000,
        )
        page = await browser.new_page(
            viewport={"width": 1280, "height": 832},
            screen={"width": 1280, "height": 832},
        )

        # Initialize components
        ocr = OCR()
        dream_seeker = DreamSeeker()

        # Start navigation
        await page.goto("https://www.booking.com/index.fr.html")
        print(f"📄 Page chargée: {await page.title()}")
        
        # Main decision loop
        max_iterations = 30  # Prevent infinite loops
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            print(f"\n{'='*50}")
            print(f"🔄 ITERATION {iteration}")
            print(f"{'='*50}")

            # Take screenshot
            await page.screenshot(path="screenshot.png")
            print("📸 Screenshot pris")

            # OCR Analysis
            print("🔍 Analyse OCR...")
            ocr_data = ocr.process_image("screenshot.png")

            if not ocr_data:
                print("❌ Aucun texte détecté, arrêt")
                break

            # Dream Decision
            print("🧠 Consultation de Dream...")
            current_url = page.url
            action_data = dream_seeker.analyze_page_elements(ocr_data, current_url)
            
            # Execute action
            success = await execute_action(page, action_data)
            
            if not success:
                print("❌ Échec de l'action, tentative suivante...")
                continue

            # Check if we should continue
            if action_data.get("action") == "wait" and "completed" in action_data.get("reasoning", "").lower():
                print("✅ Objectif atteint selon Dream")
                break

            # Wait before next iteration
            # await page.wait_for_timeout(1000)
        
        print(f"\n🏁 Processus terminé après {iteration} itérations")
        
        # Keep browser open for inspection
        input("Appuyez sur Entrée pour fermer le navigateur...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())