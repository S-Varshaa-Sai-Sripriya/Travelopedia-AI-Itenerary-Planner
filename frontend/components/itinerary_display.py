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
        
        # The complete flight object is in outbound_flight (includes both legs)
        flight_data = itinerary['transportation']['outbound_flight']
        display_flight_card(flight_data, "round-trip")
    else:
        # No flights available - show helpful message
        st.markdown("### ✈️ Flights")
        st.warning("""
        **⚠️ No flights available from SERP API for this route.**
        
        **Possible reasons:**
        - Route may not be available on the selected dates
        - Try increasing your budget  
        - Try different dates
        - SERP API may not have data for this route
        
        **Tip:** International routes like JFK to DEL typically require higher budgets ($1500-$3000+).
        """)
    
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
    """Display flight information card - shows ONLY actual SERP API data."""
    
    # Debug: Show what data we have
    import json
    with st.expander("🔍 Debug: Flight Data Structure"):
        st.code(json.dumps(flight, indent=2, default=str), language='json')
    
    # Display overall flight info at top (from SERP API)
    total_price = flight.get('total_price', 0)
    travel_class = flight.get('travel_class', 'N/A')
    carbon = flight.get('carbon_emissions', 0)
    
    if total_price > 0:
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <h3 style="margin: 0;">💰 Total: ${total_price:,.2f} | ✈️ {travel_class} | 🌍 {carbon:,} kg CO₂</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # Get outbound and return data from SERP API
    outbound = flight.get('outbound', {})
    return_flight = flight.get('return', {})
    
    # Debug info
    st.info(f"📊 Flight data check: Outbound={bool(outbound)}, Return={bool(return_flight)}")
    
    if outbound and return_flight:
        # NEW FORMAT: Separate outbound and return flights
        
        # OUTBOUND FLIGHT
        st.markdown("### 🛫 Outbound Flight")
        outbound_date = outbound.get('date', 'N/A')
        st.markdown(f"**📅 Date:** {outbound_date}")
        
        # Display outbound airline logo
        outbound_logo = outbound.get('airline_logo', '')
        outbound_airline = outbound.get('airline', 'N/A')
        
        if outbound_logo:
            st.image(outbound_logo, width=100, caption=outbound_airline)
        else:
            st.markdown(f"**Airline:** {outbound_airline}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="flight-card">
                <p><strong>Flight:</strong> {outbound.get('flight_number', 'N/A')}</p>
                <p><strong>Duration:</strong> {outbound.get('duration_hours', 'N/A')} hours</p>
                <p><strong>Stops:</strong> {outbound.get('stops', 0)}</p>
                <hr>
                <h4>🛫 Departure</h4>
                <p><strong>Airport:</strong> {outbound.get('departure', {}).get('airport', 'N/A')}</p>
                <p><strong>Time:</strong> {outbound.get('departure', {}).get('time', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="flight-card">
                <h4>🛬 Arrival</h4>
                <p><strong>Airport:</strong> {outbound.get('arrival', {}).get('airport', 'N/A')}</p>
                <p><strong>Time:</strong> {outbound.get('arrival', {}).get('time', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Show outbound layovers if any
        if outbound.get('layovers'):
            with st.expander("🔄 Outbound Layover Details"):
                for i, layover in enumerate(outbound['layovers'], 1):
                    st.write(f"**Stop {i}:** {layover}")
        
        st.markdown("---")
        
        # RETURN FLIGHT
        st.markdown("### �� Return Flight")
        return_date = return_flight.get('date', 'N/A')
        st.markdown(f"**📅 Date:** {return_date}")
        
        # Display return airline logo
        return_logo = return_flight.get('airline_logo', '')
        return_airline = return_flight.get('airline', 'N/A')
        
        if return_logo:
            st.image(return_logo, width=100, caption=return_airline)
        else:
            st.markdown(f"**Airline:** {return_airline}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="flight-card">
                <p><strong>Flight:</strong> {return_flight.get('flight_number', 'N/A')}</p>
                <p><strong>Duration:</strong> {return_flight.get('duration_hours', 'N/A')} hours</p>
                <p><strong>Stops:</strong> {return_flight.get('stops', 0)}</p>
                <hr>
                <h4>🛫 Departure</h4>
                <p><strong>Airport:</strong> {return_flight.get('departure', {}).get('airport', 'N/A')}</p>
                <p><strong>Time:</strong> {return_flight.get('departure', {}).get('time', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="flight-card">
                <h4>🛬 Arrival</h4>
                <p><strong>Airport:</strong> {return_flight.get('arrival', {}).get('airport', 'N/A')}</p>
                <p><strong>Time:</strong> {return_flight.get('arrival', {}).get('time', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Show return layovers if any
        if return_flight.get('layovers') and len(return_flight['layovers']) > 0:
            with st.expander("🔄 Return Layover Details"):
                for i, layover in enumerate(return_flight['layovers'], 1):
                    st.write(f"**Stop {i}:** {layover}")
    
    elif outbound and not return_flight:
        # Only outbound data available
        st.error("❌ **MISSING RETURN FLIGHT DATA!**")
        st.warning("""
        The flight object has outbound data but is missing return flight information.
        This is a backend data issue - the return flight should be populated by the API.
        """)
        
        # Still show outbound
        st.markdown("### 🛫 Outbound Flight (Available)")
        st.markdown(f"**📅 Date:** {outbound.get('date', 'N/A')}")
        
        outbound_logo = outbound.get('airline_logo', '')
        outbound_airline = outbound.get('airline', 'N/A')
        
        if outbound_logo:
            st.image(outbound_logo, width=100, caption=outbound_airline)
        else:
            st.markdown(f"**✈️ Airline:** {outbound_airline}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="flight-card">
                <p><strong>Flight:</strong> {outbound.get('flight_number', 'N/A')}</p>
                <p><strong>Duration:</strong> {outbound.get('duration_hours', 'N/A')} hours</p>
                <p><strong>Stops:</strong> {outbound.get('stops', 0)}</p>
                <hr>
                <h4>🛫 Departure</h4>
                <p><strong>Airport:</strong> {outbound.get('departure', {}).get('airport', 'N/A')}</p>
                <p><strong>Time:</strong> {outbound.get('departure', {}).get('time', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="flight-card">
                <h4>🛬 Arrival</h4>
                <p><strong>Airport:</strong> {outbound.get('arrival', {}).get('airport', 'N/A')}</p>
                <p><strong>Time:</strong> {outbound.get('arrival', {}).get('time', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        # No valid SERP API flight data
        st.warning("⚠️ No flight information available from SERP API. Please check your API configuration.")


def display_hotel_card(hotel: Dict[str, Any]):
    """Display hotel information card with images."""
    
    # Display hotel images if available
    images = hotel.get('images', [])
    thumbnail = hotel.get('thumbnail', '')
    
    if images or thumbnail:
        # Show first image or thumbnail
        image_to_show = images[0] if images else thumbnail
        if image_to_show:
            st.image(image_to_show, caption=hotel['name'], use_container_width=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"### {hotel['name']}")
        st.markdown(f"**⭐ Rating:** {hotel['rating']}/5.0 ({hotel.get('review_count', 0)} reviews)")
        st.markdown(f"**🏨 Type:** {hotel.get('type', 'Hotel')}")
        st.markdown(f"**📍 Location:** {hotel['location']['address']}")
        st.markdown(f"**🛏️ Room Type:** {hotel['room_type']}")
        
        # Show hotel class if available
        if hotel.get('hotel_class'):
            st.markdown(f"**⭐ Class:** {hotel['hotel_class']}")
        
        # Show eco certification
        if hotel.get('eco_certified'):
            st.markdown("**🌿 Eco-Certified**")
        
        if hotel.get('amenities'):
            st.markdown("**🎁 Amenities:**")
            # Display amenities in columns
            amenity_cols = st.columns(3)
            for i, amenity in enumerate(hotel['amenities'][:12]):
                with amenity_cols[i % 3]:
                    st.write(f"• {amenity}")
    
    with col2:
        st.markdown("### 💵 Pricing")
        st.metric("Per Night", f"${hotel['price']['per_night']:,.2f}")
        st.metric("Total", f"${hotel['price']['total']:,.2f}")
        st.caption(f"For {hotel['price'].get('nights', 'N/A')} nights")
        
        st.markdown("### 📋 Policies")
        policies = hotel.get('policies', {})
        st.write(f"**Check-in:** {policies.get('check_in', 'N/A')}")
        st.write(f"**Check-out:** {policies.get('check_out', 'N/A')}")
        
        # Booking link
        if hotel.get('booking_url'):
            st.link_button("📖 View on Google", hotel['booking_url'])
    
    # Show more images if available
    if len(images) > 1:
        with st.expander("📸 View More Photos"):
            img_cols = st.columns(3)
            for i, img in enumerate(images[1:6]):  # Show up to 5 more images
                with img_cols[i % 3]:
                    st.image(img, use_container_width=True)


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
