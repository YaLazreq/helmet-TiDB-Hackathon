# Interface Web Maps Agent - Version avec Carte

## Nouvelles Fonctionnalités

### 🗺️ Carte Interactive Google Maps
- Affichage des points d'intérêt trouvés directement sur une carte
- Marqueurs numérotés correspondant à la liste des adresses
- Info-bulles avec détails (nom, adresse, note)
- Zoom automatique pour inclure tous les points

### 📍 Liste des Adresses
- Liste détaillée des lieux trouvés avec:
  - Nom et adresse complète
  - Coordonnées GPS
  - Note (si disponible)
  - Types de lieux (restaurant, café, etc.)
  - Bouton pour ouvrir dans Google Maps

### 🎯 Réponses Structurées
- Nouvelles sections "answer" pour les réponses spécifiques
- Interface en français
- Meilleure organisation visuelle

## Configuration

### 1. Clé API Google Maps

Vous devez obtenir une clé API Google Maps :

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Activez l'API "Maps JavaScript API"
3. Créez une clé API
4. Copiez le fichier d'exemple :

```bash
cd maps-agent-ui
cp .env.local.example .env.local
```

5. Modifiez `.env.local` et ajoutez votre clé :

```env
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=votre_cle_api_ici
```

### 2. Installation des Dépendances

```bash
cd maps-agent-ui
npm install
```

### 3. Démarrage

Utilisez le script de démarrage complet :

```bash
./start_stack.sh
```

Ou démarrez manuellement :

```bash
# MCP Server
python server/server_api.py

# Agent Server  
python agent_server.py

# Frontend
cd maps-agent-ui && npm run dev
```

## Structure des Données

### Backend Response Format

```typescript
interface LocationData {
  name: string;          // Nom du lieu
  address: string;       // Adresse complète
  lat: number;          // Latitude
  lng: number;          // Longitude
  place_id?: string;    // ID Google Maps
  rating?: number;      // Note (0-5)
  types?: string[];     // Types de lieu
}

interface MapsResponse {
  topic: string;
  description: string;
  answer: string[];        // Réponses spécifiques
  source: string[];
  tools_used: string[];
  locations: LocationData[]; // Données pour la carte
}
```

## Exemples de Requêtes

### Recherche de Lieux
- "Trouve des cafés près de la Tour Eiffel"
- "Restaurants italiens à Paris 7ème"
- "Pharmacies ouvertes près de Châtelet"

### Géocodage
- "Quelle est l'adresse de l'Opéra de Paris ?"
- "Coordonnées GPS de la Gare du Nord"

### Recherche de Proximité  
- "Hôtels dans un rayon de 2km du Louvre"
- "Stations de métro près de République"

## Interface Utilisateur

### Layout Responsive
- **Desktop** : Carte et liste côte à côte
- **Mobile** : Carte et liste empilées verticalement

### Composants
- **GoogleMap** : Carte interactive avec marqueurs
- **LocationsList** : Liste scrollable des adresses
- **Response Details** : Informations détaillées de l'agent

### Actions Utilisateur
- Clic sur marqueur → Info-bulle
- Clic sur bouton "Ouvrir" → Google Maps externe
- Scroll dans la liste des adresses

## Débogage

### Carte ne s'affiche pas
1. Vérifiez votre clé API Google Maps
2. Vérifiez que l'API JavaScript est activée
3. Consultez la console du navigateur

### Pas de données de localisation
1. Vérifiez que les outils MCP retournent des données GPS
2. Consultez les logs du serveur agent
3. Testez avec une requête simple comme "cafés Paris"

### Erreurs de parsing
1. Vérifiez les logs du backend
2. Les données GPS doivent être des nombres valides
3. Format JSON doit être correct

## Développement

### Ajouter de Nouveaux Types de Lieux
Modifiez `agent_server.py` dans la section d'extraction des locations pour supporter d'autres formats d'API.

### Personnaliser l'Apparence de la Carte
Modifiez `GoogleMap.tsx` pour changer styles, icônes, ou comportements.

### Ajouter des Filtres
Étendez `LocationsList.tsx` pour ajouter des options de tri/filtrage.