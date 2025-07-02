from datetime import datetime
from graphiti_core.nodes import EpisodeType  # Adjust import based on your Graphiti setup

# List of episodes for the Fort Worth Knowledge Graph
episodes = [
    {
        "content": "Fort Worth City Services is the official Fort Worth city government departments and services for municipal operations. It includes departments such as Utilities, Permits and Licensing, Code Compliance, and more. The main contact is 817-392-1234.",
        "type": EpisodeType.text,
        "description": "City services overview",
        "reference_time": datetime(2025, 7, 2, 9, 45),
    },
    {
        "content": "Water Services, under the Utilities department of Fort Worth City Services, provides drinking water, wastewater, and reclaimed water services. It can be contacted at 817-392-4477, with service hours from 7 AM to 7 PM, Monday-Friday. Online services include bill payment, account management, and service transfers.",
        "type": EpisodeType.text,
        "description": "Water Services details",
        "reference_time": datetime(2025, 7, 2, 9, 45),
    },
    {
        "content": "Mattie Parker is the Mayor of Fort Worth, reelected in 2025. She serves alongside 10 council members. Her contact number is 817-392-6118.",
        "type": EpisodeType.text,
        "description": "Mayor's information",
        "reference_time": datetime(2025, 7, 2, 9, 45),
    },
    {
        "content": "Jesus 'Jay' Chapa became the City Manager of Fort Worth on January 28, 2025, succeeding David Cooke who retired after over 10 years of service.",
        "type": EpisodeType.text,
        "description": "City Manager transition",
        "reference_time": datetime(2025, 1, 28, 0, 0),
    },
    {
        "content": "Tarrant County Tax Assessor-Collector, led by Rick D. Barnes, handles property tax payments, motor vehicle registration, and more. The office is located at 100 W. Weatherford, Fort Worth, TX 76196, with phone 817-884-1110.",
        "type": EpisodeType.text,
        "description": "Tax Assessor-Collector details",
        "reference_time": datetime(2025, 7, 2, 9, 45),
    },
]

# Function to add episodes to Graphiti
async def add_episodes(graphiti):
    for i, episode in enumerate(episodes):
        await graphiti.add_episode(
            name=f"Fort_Worth_Episode_{i}",
            episode_body=episode["content"],
            source=episode["type"],
            source_description=episode["description"],
            reference_time=episode["reference_time"],
        )
        print(f"Added episode: Fort_Worth_Episode_{i} ({episode['type'].value})")

# Example usage (uncomment and adjust based on your Graphiti client setup)
# import asyncio
# async def main():
#     await add_episodes(graphiti)
# asyncio.run(main())