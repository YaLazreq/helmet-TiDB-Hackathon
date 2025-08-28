'use client';

interface LocationData {
  name: string;
  address: string;
  lat: number;
  lng: number;
  place_id?: string;
  rating?: number;
  types?: string[];
}

interface LocationsListProps {
  locations: LocationData[];
  className?: string;
}

export default function LocationsList({ locations, className = '' }: LocationsListProps) {
  if (locations.length === 0) {
    return (
      <div className={`bg-white rounded-lg shadow p-6 ${className}`}>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Adresses trouvées</h3>
        <p className="text-gray-500 italic">Aucune adresse trouvée pour cette requête.</p>
      </div>
    );
  }

  const formatTypes = (types: string[] = []) => {
    return types
      .filter(type => !type.includes('_'))
      .map(type => type.replace(/_/g, ' '))
      .slice(0, 3)
      .join(', ');
  };

  const openInGoogleMaps = (location: LocationData) => {
    const url = `https://www.google.com/maps/search/?api=1&query=${location.lat},${location.lng}&query_place_id=${location.place_id}`;
    window.open(url, '_blank');
  };

  return (
    <div className={`bg-white rounded-lg shadow ${className}`}>
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">
          Adresses trouvées ({locations.length})
        </h3>
      </div>
      
      <div className="max-h-96 overflow-y-auto">
        {locations.map((location, index) => (
          <div
            key={`${location.lat}-${location.lng}-${index}`}
            className="p-4 border-b border-gray-100 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center mb-2">
                  <span className="bg-blue-600 text-white text-xs font-bold rounded-full h-6 w-6 flex items-center justify-center mr-3">
                    {index + 1}
                  </span>
                  <h4 className="font-semibold text-gray-900 text-sm">{location.name}</h4>
                </div>
                
                <p className="text-gray-600 text-sm mb-2 ml-9">{location.address}</p>
                
                <div className="ml-9 space-y-1">
                  {location.rating && location.rating > 0 && (
                    <div className="flex items-center text-sm">
                      <span className="text-yellow-500 mr-1">★</span>
                      <span className="text-gray-700">{location.rating.toFixed(1)}</span>
                    </div>
                  )}
                  
                  {location.types && location.types.length > 0 && (
                    <div className="text-xs text-gray-500">
                      {formatTypes(location.types)}
                    </div>
                  )}
                  
                  <div className="text-xs text-gray-400">
                    {location.lat.toFixed(6)}, {location.lng.toFixed(6)}
                  </div>
                </div>
              </div>
              
              <button
                onClick={() => openInGoogleMaps(location)}
                className="ml-3 text-blue-600 hover:text-blue-800 text-sm font-medium transition-colors"
                title="Ouvrir dans Google Maps"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}