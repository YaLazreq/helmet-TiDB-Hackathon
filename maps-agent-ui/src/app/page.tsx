'use client';

import { useState } from 'react';
import axios from 'axios';
import GoogleMap from '@/components/GoogleMap';
import LocationsList from '@/components/LocationsList';

interface LocationData {
  name: string;
  address: string;
  lat: number;
  lng: number;
  place_id?: string;
  rating?: number;
  types?: string[];
}

interface AgentResponse {
  topic: string;
  description: string;
  answer: string[];
  source: string[];
  tools_used: string[];
  locations: LocationData[];
}

export default function Home() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<AgentResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a query');
      return;
    }

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const result = await axios.post('/api/agent', { query });
      console.log('Received response:', result.data);
      
      // Ensure the response has the expected structure
      const responseData = result.data;
      
      // Convert tools_used to strings if they're objects
      let tools_used = [];
      if (Array.isArray(responseData.tools_used)) {
        tools_used = responseData.tools_used.map((tool: any) => 
          typeof tool === 'string' ? tool : JSON.stringify(tool)
        );
      }
      
      // Convert source to strings if they're objects
      let source = [];
      if (Array.isArray(responseData.source)) {
        source = responseData.source.map((src: any) => 
          typeof src === 'string' ? src : JSON.stringify(src)
        );
      }

      // Handle answer field
      let answer = [];
      if (Array.isArray(responseData.answer)) {
        answer = responseData.answer.map((ans: any) => 
          typeof ans === 'string' ? ans : JSON.stringify(ans)
        );
      }

      // Handle locations
      let locations = [];
      if (Array.isArray(responseData.locations)) {
        locations = responseData.locations.filter((loc: any) => 
          loc && typeof loc.lat === 'number' && typeof loc.lng === 'number'
        );
      }
      
      const formattedResponse = {
        topic: responseData.topic || 'Maps Query Response',
        description: responseData.description || JSON.stringify(responseData, null, 2),
        answer: answer,
        source: source,
        tools_used: tools_used,
        locations: locations
      };
      
      setResponse(formattedResponse);
    } catch (err) {
      setError('Failed to get response from agent');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Maps Agent Interface
          </h1>
          <p className="text-lg text-gray-600">
            Ask questions about maps, locations, places, and get intelligent responses
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
                Your Question
              </label>
              <textarea
                id="query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g., Find coffee shops near Times Square, New York"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                rows={4}
                disabled={loading}
              />
            </div>
            
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Processing...
                </div>
              ) : (
                'Ask Agent'
              )}
            </button>
          </form>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            </div>
          </div>
        )}

        {response && (
          <div className="space-y-6">
            {/* Map and Locations Section */}
            {response.locations && response.locations.length > 0 && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <GoogleMap 
                    locations={response.locations} 
                    className="h-96 w-full rounded-lg shadow-lg"
                  />
                </div>
                <div>
                  <LocationsList 
                    locations={response.locations}
                    className="h-96"
                  />
                </div>
              </div>
            )}

            {/* Response Details */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-6">Détails de la réponse</h2>
              
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-700 mb-2">Sujet</h3>
                  <p className="text-gray-900 bg-gray-50 p-3 rounded-lg">{response.topic}</p>
                </div>
                
                <div>
                  <h3 className="text-lg font-medium text-gray-700 mb-2">Description</h3>
                  <p className="text-gray-900 bg-gray-50 p-3 rounded-lg whitespace-pre-wrap">{response.description}</p>
                </div>

                {response.answer && response.answer.length > 0 && (
                  <div>
                    <h3 className="text-lg font-medium text-gray-700 mb-2">Réponses</h3>
                    <div className="space-y-2">
                      {response.answer.map((ans, index) => (
                        <div key={index} className="text-gray-900 bg-blue-50 p-3 rounded-lg border-l-4 border-blue-500">
                          {ans}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {response.tools_used && response.tools_used.length > 0 && (
                  <div>
                    <h3 className="text-lg font-medium text-gray-700 mb-2">Outils utilisés</h3>
                    <div className="flex flex-wrap gap-2">
                      {response.tools_used.map((tool, index) => (
                        <span key={index} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                          {tool}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {response.source && response.source.length > 0 && (
                  <div>
                    <h3 className="text-lg font-medium text-gray-700 mb-2">Sources</h3>
                    <ul className="space-y-1">
                      {response.source.map((src, index) => (
                        <li key={index} className="text-gray-600 bg-gray-50 p-2 rounded text-sm">
                          {src}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
