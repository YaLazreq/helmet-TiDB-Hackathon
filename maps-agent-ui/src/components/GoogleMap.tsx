'use client';

import { useEffect, useRef, useState } from 'react';
import { Loader } from '@googlemaps/js-api-loader';

interface LocationData {
  name: string;
  address: string;
  lat: number;
  lng: number;
  place_id?: string;
  rating?: number;
  types?: string[];
}

interface GoogleMapProps {
  locations: LocationData[];
  className?: string;
}

export default function GoogleMap({ locations, className = '' }: GoogleMapProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const [map, setMap] = useState<google.maps.Map | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    const initMap = async () => {
      const loader = new Loader({
        apiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || '',
        version: 'weekly',
        libraries: ['places'],
      });

      try {
        await loader.load();
        setIsLoaded(true);
      } catch (error) {
        console.error('Error loading Google Maps:', error);
      }
    };

    if (!isLoaded) {
      initMap();
    }
  }, [isLoaded]);

  useEffect(() => {
    if (!isLoaded || !mapRef.current) return;

    // Default center (Paris if no locations)
    let center = { lat: 48.8566, lng: 2.3522 };
    let zoom = 12;

    if (locations.length > 0) {
      // Calculate bounds to fit all locations
      const bounds = new google.maps.LatLngBounds();
      locations.forEach((location) => {
        bounds.extend(new google.maps.LatLng(location.lat, location.lng));
      });

      // Create the map
      const mapInstance = new google.maps.Map(mapRef.current, {
        center: bounds.getCenter(),
        zoom: 12,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
      });

      // Fit map to bounds
      mapInstance.fitBounds(bounds);

      // Add markers for each location
      locations.forEach((location, index) => {
        const marker = new google.maps.Marker({
          position: { lat: location.lat, lng: location.lng },
          map: mapInstance,
          title: location.name,
          label: (index + 1).toString(),
        });

        // Create info window
        const infoWindow = new google.maps.InfoWindow({
          content: `
            <div class="p-3 max-w-xs">
              <h3 class="font-semibold text-gray-900 mb-1">${location.name}</h3>
              <p class="text-gray-600 text-sm mb-2">${location.address}</p>
              ${location.rating && location.rating > 0 ? 
                `<div class="flex items-center text-sm">
                  <span class="text-yellow-500">★</span>
                  <span class="ml-1 text-gray-700">${location.rating.toFixed(1)}</span>
                </div>` : 
                ''
              }
            </div>
          `,
        });

        marker.addListener('click', () => {
          infoWindow.open(mapInstance, marker);
        });
      });

      setMap(mapInstance);
    } else {
      // Create empty map
      const mapInstance = new google.maps.Map(mapRef.current, {
        center,
        zoom,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
      });
      setMap(mapInstance);
    }
  }, [isLoaded, locations]);

  if (!isLoaded) {
    return (
      <div className={`flex items-center justify-center bg-gray-100 ${className}`}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
          <p className="text-gray-600">Chargement de la carte...</p>
        </div>
      </div>
    );
  }

  return <div ref={mapRef} className={className} />;
}