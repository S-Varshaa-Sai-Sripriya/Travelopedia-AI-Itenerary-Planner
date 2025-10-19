"""
Itinerary display component for showing travel plans in an elegant card layout.
"""

import streamlit as st
from typing import Dict, Any, List


def display_itinerary_card(itinerary: Dict[str, Any]):
    """Display complete itinerary in card format."""
    
    st.markdown("""
        <div class="itinerary-header">
            <h1>✈️ Your Travel Itinerary</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Trip Summary Card
    with st.container():
        st.markdown("### 📍 Trip Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        summary = itinerary['trip_summary']
        
        with col1:
            st.metric("Destination", summary['destination'])
        with col2:
            st.metric("Duration", f"{summary['duration_days']} days")
        with col3:
            st.metric("Travelers", summary['group_size'])
        with col4:
            st.metric("Value Score", f"{itinerary.get('value_score', 0)}/100")
    
    st.markdown("---")
    
    # Budget Summary Card
    st.markdown("### 💰 Budget Breakdown")
    budget = itinerary['budget_summary']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Budget", f"${budget['total_budget']:,.2f}")
    with col2:
        st.metric("Total Cost", f"${budget['total_cost']:,.2f}")
    with col3:
        balance_delta = budget['balance']
        st.metric(
            "Balance",
            f"${abs(balance_delta):,.2f}",
            delta=f"${balance_delta:,.2f}",
            delta_color="normal"
        )
    
    # Detailed breakdown
    with st.expander("📊 View Detailed Breakdown"):
        breakdown = budget['breakdown']
        for category, amount in breakdown.items():
            st.write(f"**{category.replace('_', ' ').title()}:** ${amount:,.2f}")
    
    st.markdown("---")
    
    # Flight Information
    if itinerary['transportation']['outbound_flight']:
        st.markdown("### ✈️ Flights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🛫 Outbound**")
            outbound = itinerary['transportation']['outbound_flight']
            display_flight_card(outbound, "outbound")
        
        with col2:
            if itinerary['transportation']['return_flight']:
                st.markdown("**🛬 Return**")
                return_flight = itinerary['transportation']['return_flight']
                display_flight_card(return_flight, "return")
    
    st.markdown("---")
    
    # Accommodation
    if itinerary['accommodation']:
        st.markdown("### 🏨 Accommodation")
        display_hotel_card(itinerary['accommodation'])
    
    st.markdown("---")
    
    # Activities
    if itinerary['activities']:
        st.markdown("### 🎯 Recommended Activities")
        display_activities_grid(itinerary['activities'])
    
    st.markdown("---")
    
    # Daily Schedule
    st.markdown("### 📅 Daily Schedule")
    display_daily_schedule(itinerary['daily_schedule'])


def display_flight_card(flight: Dict[str, Any], flight_type: str):
    """Display flight information card."""
    
    st.markdown(f"""
    <div class="flight-card">
        <p><strong>Airline:</strong> {flight.get('airline', 'N/A')}</p>
        <p><strong>Flight:</strong> {flight.get('flight_number', 'N/A')}</p>
        <p><strong>Class:</strong> {flight.get('cabin_class', 'Economy')}</p>
        <hr>
        <p>🛫 <strong>Departure:</strong> {flight['departure'].get('airport', 'N/A')}</p>
        <p>🕐 {flight['departure'].get('time', 'N/A')}</p>
        <p>📍 Terminal {flight['departure'].get('terminal', 'N/A')}</p>
        <hr>
        <p>🛬 <strong>Arrival:</strong> {flight['arrival'].get('airport', 'N/A')}</p>
        <p>🕐 {flight['arrival'].get('time', 'N/A')}</p>
        <p>📍 Terminal {flight['arrival'].get('terminal', 'N/A')}</p>
        <hr>
        <p>⏱️ <strong>Duration:</strong> {flight.get('duration_hours', 'N/A')} hours</p>
        <p>🔄 <strong>Stops:</strong> {flight.get('stops', 0)}</p>
    </div>
    """, unsafe_allow_html=True)


def display_hotel_card(hotel: Dict[str, Any]):
    """Display hotel information card."""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"### {hotel['name']}")
        st.markdown(f"**⭐ Rating:** {hotel['rating']}/5.0")
        st.markdown(f"**📍 Location:** {hotel['location']['address']}")
        st.markdown(f"**🛏️ Room Type:** {hotel['room_type']}")
        
        if hotel.get('amenities'):
            st.markdown("**🎁 Amenities:**")
            # Display amenities in columns
            amenity_cols = st.columns(3)
            for i, amenity in enumerate(hotel['amenities'][:9]):
                with amenity_cols[i % 3]:
                    st.write(f"• {amenity}")
    
    with col2:
        st.markdown("### 💵 Pricing")
        st.metric("Per Night", f"${hotel['price']['per_night']:,.2f}")
        st.metric("Total", f"${hotel['price']['total']:,.2f}")
        st.caption(f"For {hotel['price']['nights']} nights")
        
        st.markdown("### 📋 Policies")
        policies = hotel.get('policies', {})
        st.write(f"**Check-in:** {policies.get('check_in', 'N/A')}")
        st.write(f"**Check-out:** {policies.get('check_out', 'N/A')}")


def display_activities_grid(activities: List[Dict[str, Any]]):
    """Display activities in a grid layout."""
    
    # Show activities in rows of 2
    for i in range(0, len(activities), 2):
        col1, col2 = st.columns(2)
        
        with col1:
            if i < len(activities):
                display_activity_card(activities[i], i + 1)
        
        with col2:
            if i + 1 < len(activities):
                display_activity_card(activities[i + 1], i + 2)


def display_activity_card(activity: Dict[str, Any], index: int):
    """Display single activity card."""
    
    with st.container():
        st.markdown(f"""
        <div class="activity-card">
            <h4>{index}. {activity['name']}</h4>
            <p><strong>Category:</strong> {activity['category'].title()}</p>
            <p><strong>Description:</strong> {activity['description']}</p>
            <p><strong>⏱️ Duration:</strong> {activity['duration_hours']} hours</p>
            <p><strong>💵 Price:</strong> ${activity['price']:.2f}</p>
            <p><strong>⭐ Rating:</strong> {activity.get('rating', 'N/A')}/5.0</p>
            <p><strong>🕐 Best Time:</strong> {activity.get('best_time', 'Anytime')}</p>
        </div>
        """, unsafe_allow_html=True)


def display_daily_schedule(schedule: List[Dict[str, Any]]):
    """Display day-by-day schedule."""
    
    # Use tabs for each day
    if schedule:
        tabs = st.tabs([f"Day {day['day']} - {day['date']}" for day in schedule])
        
        for i, day in enumerate(schedule):
            with tabs[i]:
                # Weather info
                st.markdown(f"**🌤️ Weather:** {day['weather']['condition']}")
                st.markdown(f"**🌡️ Temperature:** High {day['weather']['temperature']['high']}°C")
                
                st.markdown("---")
                
                # Events
                st.markdown("**📅 Schedule:**")
                for event in day['events']:
                    st.markdown(f"- **{event['time']}:** {event['activity']}")


def display_alternative_plans(alternatives: List[Dict[str, Any]]):
    """Display alternative budget plans."""
    
    st.markdown("### 💡 Alternative Plans")
    st.caption("Compare different budget allocations based on comfort level")
    
    tabs = st.tabs([alt['label'] for alt in alternatives])
    
    for i, alt in enumerate(alternatives):
        with tabs[i]:
            st.markdown(f"**{alt['description']}**")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Cost", f"${alt['total_cost']:,.2f}")
            with col2:
                st.metric("Balance", f"${alt['balance']:,.2f}")
            with col3:
                st.metric("Value Score", f"{alt['value_score']}/100")
            with col4:
                st.metric("Comfort", alt['comfort_level'].title())
            
            # Show what's included
            with st.expander("View Details"):
                selected = alt['selected_options']
                
                if selected['flight']:
                    st.markdown(f"**✈️ Flight:** {selected['flight'].get('airline', 'N/A')} - ${selected['flight']['price']:,.2f}")
                
                if selected['hotel']:
                    st.markdown(f"**🏨 Hotel:** {selected['hotel']['name']} - ${selected['hotel']['price']['total']:,.2f}")
                
                st.markdown(f"**🎯 Activities:** {len(selected['activities'])} activities")
