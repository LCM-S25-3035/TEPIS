"""
Context Analyzer for intelligent routing of user requirements to appropriate agents
"""

import re
import json
from typing import Dict, List, Tuple, Any

class ContextAnalyzer:
    def __init__(self):
        # Keywords and patterns for different categories
        self.agent_keywords = {
            'hotel': {
                'keywords': ['hotel', 'accommodation', 'stay', 'lodge', 'resort', 'inn', 'motel', 'hostel', 
                           'room', 'suite', 'apartment', 'airbnb', 'booking', 'check-in', 'check-out'],
                'patterns': [r'where to stay', r'place to sleep', r'somewhere to rest', r'need accommodation'],
                'preferences': ['location', 'amenities', 'price range', 'rating', 'pool', 'gym', 'wifi', 
                              'breakfast', 'parking', 'pet-friendly', 'family-friendly']
            },
            'restaurant': {
                'keywords': ['restaurant', 'food', 'eat', 'dining', 'meal', 'cuisine', 'cafe', 'bar', 
                           'breakfast', 'lunch', 'dinner', 'snack', 'drink', 'coffee', 'menu', 'takeout'],
                'patterns': [r'where to eat', r'good food', r'restaurant recommendation', r'dining options'],
                'preferences': ['cuisine type', 'price range', 'dietary restrictions', 'atmosphere', 
                              'location', 'rating', 'reservations', 'outdoor seating']
            },
            'transportation': {
                'keywords': ['transport', 'travel', 'car', 'taxi', 'uber', 'lyft', 'bus', 'train', 
                           'flight', 'plane', 'airport', 'parking', 'rental', 'drive', 'walk', 'metro'],
                'patterns': [r'how to get', r'transportation to', r'getting around', r'travel between'],
                'preferences': ['mode of transport', 'budget', 'time preference', 'comfort level', 
                              'luggage requirements', 'accessibility needs']
            },
            'itinerary': {
                'keywords': ['activity', 'attraction', 'tour', 'visit', 'see', 'do', 'explore', 'museum', 
                           'park', 'shopping', 'entertainment', 'show', 'concert', 'sightseeing', 'landmark'],
                'patterns': [r'things to do', r'places to visit', r'what to see', r'activities near'],
                'preferences': ['interests', 'activity level', 'indoor/outdoor', 'duration', 'group size', 
                              'age appropriateness', 'accessibility']
            },
            'weather': {
                'keywords': ['weather', 'temperature', 'rain', 'sunny', 'cloudy', 'snow', 'forecast', 
                           'climate', 'what to wear', 'umbrella', 'jacket'],
                'patterns': [r'weather forecast', r'what will the weather be like', r'should I bring'],
                'preferences': ['dates', 'activities planned', 'clothing recommendations']
            }
        }
        
        # Preference extractors
        self.preference_patterns = {
            'budget': {
                'low': ['cheap', 'budget', 'affordable', 'inexpensive', 'low cost', 'economical'],
                'medium': ['moderate', 'mid-range', 'reasonable', 'average price'],
                'high': ['luxury', 'expensive', 'high-end', 'premium', 'upscale', 'fancy']
            },
            'dietary': ['vegetarian', 'vegan', 'gluten-free', 'kosher', 'halal', 'dairy-free', 'keto', 'paleo'],
            'cuisine': ['italian', 'chinese', 'japanese', 'mexican', 'indian', 'thai', 'french', 'american', 
                       'mediterranean', 'korean', 'vietnamese', 'greek', 'spanish'],
            'accommodation_type': ['hotel', 'hostel', 'apartment', 'resort', 'inn', 'b&b', 'airbnb'],
            'transport_mode': ['car', 'taxi', 'uber', 'bus', 'train', 'walk', 'bike', 'metro', 'flight']
        }

    def analyze_user_input(self, user_input: str, event_data: Dict = None) -> Dict[str, Any]:
        """
        Analyze user input and determine which agents should handle the request
        Returns routing information and extracted preferences
        """
        user_input_lower = user_input.lower()
        
        # Initialize result structure
        result = {
            'primary_agents': [],
            'secondary_agents': [],
            'extracted_preferences': {},
            'context': {
                'original_input': user_input,
                'event_info': event_data,
                'confidence_scores': {}
            },
            'agent_instructions': {}
        }
        
        # Analyze for each agent type
        for agent_type, config in self.agent_keywords.items():
            confidence_score = self._calculate_confidence(user_input_lower, config)
            result['context']['confidence_scores'][agent_type] = confidence_score
            
            if confidence_score > 0.7:  # High confidence
                result['primary_agents'].append(agent_type)
            elif confidence_score > 0.3:  # Medium confidence
                result['secondary_agents'].append(agent_type)
        
        # If no specific agent detected, default to itinerary
        if not result['primary_agents'] and not result['secondary_agents']:
            result['primary_agents'].append('itinerary')
            result['context']['confidence_scores']['itinerary'] = 0.5
        
        # Extract specific preferences
        result['extracted_preferences'] = self._extract_preferences(user_input_lower)
        
        # Generate agent-specific instructions
        result['agent_instructions'] = self._generate_agent_instructions(
            user_input, result['primary_agents'], result['extracted_preferences'], event_data
        )
        
        return result

    def _calculate_confidence(self, text: str, config: Dict) -> float:
        """Calculate confidence score for an agent type"""
        score = 0.0
        total_weight = 0.0
        
        # Check keywords
        keyword_matches = sum(1 for keyword in config['keywords'] if keyword in text)
        if keyword_matches > 0:
            score += (keyword_matches / len(config['keywords'])) * 0.6
            total_weight += 0.6
        
        # Check patterns
        pattern_matches = sum(1 for pattern in config['patterns'] if re.search(pattern, text))
        if pattern_matches > 0:
            score += (pattern_matches / len(config['patterns'])) * 0.4
            total_weight += 0.4
        
        return score / total_weight if total_weight > 0 else 0.0

    def _extract_preferences(self, text: str) -> Dict[str, Any]:
        """Extract specific preferences from user input"""
        preferences = {}
        
        # Budget preferences
        for budget_level, keywords in self.preference_patterns['budget'].items():
            if any(keyword in text for keyword in keywords):
                preferences['budget'] = budget_level
                break
        
        # Dietary restrictions
        dietary_prefs = [diet for diet in self.preference_patterns['dietary'] if diet in text]
        if dietary_prefs:
            preferences['dietary_restrictions'] = dietary_prefs
        
        # Cuisine preferences
        cuisine_prefs = [cuisine for cuisine in self.preference_patterns['cuisine'] if cuisine in text]
        if cuisine_prefs:
            preferences['preferred_cuisines'] = cuisine_prefs
        
        # Accommodation type
        for acc_type in self.preference_patterns['accommodation_type']:
            if acc_type in text:
                preferences['accommodation_type'] = acc_type
                break
        
        # Transportation mode
        transport_prefs = [mode for mode in self.preference_patterns['transport_mode'] if mode in text]
        if transport_prefs:
            preferences['preferred_transport'] = transport_prefs
        
        # Extract numbers (group size, days, budget amounts)
        numbers = re.findall(r'\b(\d+)\b', text)
        if numbers:
            preferences['numbers_mentioned'] = [int(n) for n in numbers]
        
        # Extract time-related preferences
        time_keywords = ['morning', 'afternoon', 'evening', 'night', 'early', 'late']
        time_prefs = [time for time in time_keywords if time in text]
        if time_prefs:
            preferences['time_preferences'] = time_prefs
        
        return preferences

    def _generate_agent_instructions(self, user_input: str, primary_agents: List[str], 
                                   preferences: Dict, event_data: Dict = None) -> Dict[str, str]:
        """Generate specific instructions for each agent based on context"""
        instructions = {}
        
        base_context = f"User request: '{user_input}'"
        if event_data:
            base_context += f"\nEvent: {event_data.get('event_title', 'N/A')} in {event_data.get('city_name', 'N/A')}"
        
        for agent in primary_agents:
            if agent == 'hotel':
                instruction = f"{base_context}\n\nFocus on accommodation recommendations"
                if preferences.get('budget'):
                    instruction += f" with {preferences['budget']} budget"
                if preferences.get('accommodation_type'):
                    instruction += f", specifically {preferences['accommodation_type']} options"
                instruction += ". Consider location relative to the event venue."
                
            elif agent == 'restaurant':
                instruction = f"{base_context}\n\nFocus on dining recommendations"
                if preferences.get('budget'):
                    instruction += f" with {preferences['budget']} pricing"
                if preferences.get('preferred_cuisines'):
                    instruction += f", especially {', '.join(preferences['preferred_cuisines'])} cuisine"
                if preferences.get('dietary_restrictions'):
                    instruction += f". Must accommodate: {', '.join(preferences['dietary_restrictions'])}"
                instruction += ". Consider proximity to event and accommodation."
                
            elif agent == 'transportation':
                instruction = f"{base_context}\n\nFocus on transportation options"
                if preferences.get('preferred_transport'):
                    instruction += f", prioritizing {', '.join(preferences['preferred_transport'])}"
                if preferences.get('budget'):
                    instruction += f" with {preferences['budget']} budget considerations"
                instruction += ". Include options to/from event venue."
                
            elif agent == 'itinerary':
                instruction = f"{base_context}\n\nFocus on activities and attractions"
                if preferences.get('time_preferences'):
                    instruction += f", emphasizing {', '.join(preferences['time_preferences'])} activities"
                if preferences.get('numbers_mentioned'):
                    instruction += f". Consider group size or duration: {preferences['numbers_mentioned']}"
                instruction += ". Integrate with the main event schedule."
                
            elif agent == 'weather':
                instruction = f"{base_context}\n\nProvide weather information"
                instruction += " and clothing/preparation recommendations based on forecast."
            
            instructions[agent] = instruction
        
        return instructions

    def format_for_display(self, analysis_result: Dict) -> Dict[str, str]:
        """Format analysis result for user display"""
        return {
            'detected_needs': ', '.join(analysis_result['primary_agents']).title(),
            'confidence': f"{max(analysis_result['context']['confidence_scores'].values()) * 100:.0f}%",
            'preferences_found': len(analysis_result['extracted_preferences']),
            'will_consult': ', '.join(analysis_result['primary_agents']).replace('_', ' ').title()
        }


# Usage example and testing
if __name__ == "__main__":
    analyzer = ContextAnalyzer()
    
    test_inputs = [
        "I need a good Italian restaurant near the venue that's not too expensive",
        "Where should I stay? Looking for a luxury hotel with a pool",
        "How do I get from the airport to downtown? Prefer not to drive",
        "What activities are there for kids in the morning before the event?",
        "I'm vegetarian and need gluten-free options for dinner"
    ]
    
    for test_input in test_inputs:
        print(f"\nInput: {test_input}")
        result = analyzer.analyze_user_input(test_input)
        display = analyzer.format_for_display(result)
        print(f"Detected: {display['detected_needs']}")
        print(f"Confidence: {display['confidence']}")
        print(f"Preferences: {result['extracted_preferences']}")
