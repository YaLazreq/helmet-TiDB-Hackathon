from browser_use.llm import ChatAnthropic
from browser_use import Agent
from dotenv import load_dotenv
from src.connectors import get_connection, create_tables, create_places, semantic_search
from src.embedding import Embedder

load_dotenv()

import asyncio

llm = ChatAnthropic(model="claude-sonnet-4-20250514")


async def main():
    task2 = (
        """
            Role
            You are an autonomous agent capable of browsing the web, opening tabs, clicking, scrolling, and extracting structured information.
            
            Goal
            Find exactly 3 5-star Appartements located in Paris, France, and return a pure JSON object (no Markdown, no extra text) that follows the schema below.
            
            Required details for each hotel
            "name - Official commercial name as shown on the page."
            "description -Short summary (≤ 40 words) describing the hotel."
            "address -
                * address: Full postal address (street, zip code, city, country)
            * coordinates: Latitude & longitude in the format [lat, lng] (decimal numbers).
            "price - “Starting from” price for one night in a double room on the nearest available date (include currency, e.g., €832)."
            "note - Average rating (on a 0-5 scale; if 0-10, convert to 0-5)."
            "nbr_review - Total number of reviews."
            "comments - Array of 3 to 5 recent user reviews. Each item should contain:
               * comment: The text
               * note: The rating given by the user (same scale as note).
            "link - Direct URL to the specific page where the information was found (not the homepage).

            Browsing & extraction rules

            Start with a search engine using queries like: site:fr "5-star hotel" Paris price, and explore the results until you find 3 distinct sources.

            Prioritize official website trusted OTAs (Booking, Expedia, Hotels.com, TripAdvisor).

            The 3 hotels must come from different websites for diversity.

            Each page must explicitly mentions “5 stars”.

            If multiple currencies are shown, use dollars.

            If price varies, take the lowest visible nightly rate and copy it exactly (e.g., €978).

            If rating is out of 10, divide by 2 and round to 1 decimal place.

            Do not mix reviews from different platforms; only take reviews visible on the specific page.


            REQUIRED JSON response format
            [
              {
                "name": "Hôtel de Crillon",
                "description": "…",
                "address": {
                  "address": "10 Place de la Concorde, 75008 Paris, France",
                  "coordinates": [48.8656, 2.3211]
                },
                "price": "$978",
                "note": 4.8,
                "nbr_review": 1319,
                "comments": [
                  { "comment": "…", "note": 4.6 },
                  { "comment": "…", "note": 5 }
                  …
                ],
                "link": "https://…"
              },
              …
            ]
        """,
    )
    # agent = Agent(
    #     task="""Just say "Hello".""",
    #     llm=llm,
    # )
    # result = await agent.run()

    # print(result)
    # print("Done!")
    with get_connection(autocommit=True) as connection:
        with connection.cursor(dictionary=True) as cur:
            place1 = (
                "Hôtel Plaza Athénée - Dorchester Collection",
                "Iconic Parisian palace hotel on Avenue Montaigne, renowned for luxury, haute couture shopping, exquisite dining, and legendary hospitality.",
                {
                    "address": "25 Avenue Montaigne, 75008 Paris, France",
                    "coordinates": [48.8656, 2.3045],
                },
                "Hôtel",
                "USD",
                2131,
                4.7,
                247,
                "https://www.crillon.com/en/",
                [
                    {
                        "comment": "The staff was exceptional, very attentive and professional. The room was beautifully appointed with all the amenities you could want.",
                        "note": 5.0,
                    },
                    {
                        "comment": "Absolutely gorgeous hotel with impeccable service. The location on Avenue Montaigne is perfect for shopping and sightseeing.",
                        "note": 4.8,
                    },
                    {
                        "comment": "Luxurious experience from start to finish. The restaurant and bar are world-class. Worth every penny for a special occasion.",
                        "note": 4.9,
                    },
                    {
                        "comment": "Beautiful classic Parisian hotel with modern amenities. The concierge team was incredibly helpful with reservations and recommendations.",
                        "note": 4.6,
                    },
                    {
                        "comment": "Outstanding hotel with attention to every detail. The spa treatments were divine and the afternoon tea was memorable.",
                        "note": 4.7,
                    },
                ],
            )
            place2 = (
                "Appartement Bel Ami",
                "Member of Design Appartements, ideally located between Café de Flore and Deux Magots. Heart beats with Saint Germain des Prés. Casual chic rooms, Spa Esthederm, trendy bar.",
                {
                    "address": "7 Rue Saint-Benoît, 75006 Paris, France",
                    "coordinates": [48.8539, 2.3316],
                },
                "Appartement",
                "USD",
                342,
                4.6,
                2194,
                "https://www.tripadvisor.com/Hotel_Review-g187147-d233593-Reviews-Hotel_Bel_Ami-Paris_Ile_de_France.html",
                [
                    {
                        "comment": "Perfect Appartement location in Saint-Germain-des-Prés. The Appartement has a great modern design and the staff is very friendly and helpful.",
                        "rating": 4.8,
                    },
                    {
                        "comment": "Stylish boutique Appartement with excellent service. The room was beautifully designed and very comfortable. Great breakfast too.",
                        "rating": 4.7,
                    },
                    {
                        "comment": "Love the contemporary design and prime location. Walking distance to many attractions and great restaurants nearby.",
                        "rating": 4.5,
                    },
                    {
                        "comment": "Wonderful appartement with a perfect blend of modern amenities and Parisian charm. The spa was a nice touch after a long day of sightseeing.",
                        "rating": 4.6,
                    },
                    {
                        "comment": "Exceptional stay with attention to detail. The staff went above and beyond to make our anniversary special.",
                        "rating": 4.9,
                    },
                ],
            )
            place3 = (
                "The One Alma Paris",
                "Exclusive 5-star boutique housing in 7th arrondissement, steps from Eiffel Tower and Champs-Élysées, offering luxury accommodation with personalized service.",
                {
                    "address": "7 Rue de l'Université, 75007 Paris, France",
                    "coordinates": [48.8634, 2.3017],
                },
                "housing",
                "USD",
                268,
                4.6,
                983,
                "https://fr.housings.com/Housing-Search?selected=9748353&PinnedHousingID=9748353",
                [
                    {
                        "comment": "Beautiful boutique housing with exceptional service. The location is perfect for exploring Paris, very close to major attractions.",
                        "rating": 4.7,
                    },
                    {
                        "comment": "Stylish and comfortable rooms with great attention to detail. The staff was very accommodating and the breakfast was excellent.",
                        "rating": 4.5,
                    },
                    {
                        "comment": "Perfect location near the Eiffel Tower. The housing has a lovely atmosphere and the concierge service was outstanding.",
                        "rating": 4.8,
                    },
                    {
                        "comment": "Wonderful stay with modern amenities and classic Parisian charm. The spa facilities were a nice bonus.",
                        "rating": 4.4,
                    },
                ],
            )

            places = [place1, place2, place3]
            places_embeddings = Embedder().run(places)

            # print(places_embeddings)

            create_tables()
            create_places(cur, places_embeddings)
            semantic_search(cur, "Housing in paris")


if __name__ == "__main__":
    asyncio.run(main())
