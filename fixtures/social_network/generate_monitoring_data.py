#!/usr/bin/env python3
"""
Social Network Monitoring Data Generator

Generates synthetic logs and metrics for a social network platform over 1 year.
Logs and metrics match exactly - each event produces both a log entry and metrics.

Usage: python generate_monitoring_data.py <total_events> <total_users>

Example: python generate_monitoring_data.py 10000000 50000
"""

import argparse
import json
import random
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional


# =============================================================================
# PERSONA DEFINITIONS
# =============================================================================

@dataclass
class Persona:
    """Defines a user behavior pattern"""
    name: str
    description: str
    # Percentage of total users with this persona
    user_percentage: float
    # Relative activity level (events per user relative to average)
    activity_multiplier: float
    # Action weights - how likely they are to perform each action category
    action_weights: Dict[str, float]
    # Time patterns - when they're active (hour weights 0-23)
    hourly_weights: List[float]
    # Day of week patterns (0=Monday, 6=Sunday)
    daily_weights: List[float]
    # Success rate (some personas might have more errors due to bad network, etc.)
    success_rate: float = 0.995
    # Response time multiplier (mobile users might be slower)
    latency_multiplier: float = 1.0


# Define 100 personas across different user archetypes
PERSONAS: List[Persona] = []

# Helper to generate hourly patterns
def peak_hours(peaks: List[int], spread: float = 2.0) -> List[float]:
    """Generate hourly weights with peaks at specified hours"""
    weights = [0.1] * 24
    for peak in peaks:
        for h in range(24):
            dist = min(abs(h - peak), 24 - abs(h - peak))
            weights[h] += max(0, 1.0 - dist / spread)
    total = sum(weights)
    return [w / total for w in weights]

def weekday_heavy() -> List[float]:
    return [0.18, 0.18, 0.17, 0.16, 0.15, 0.08, 0.08]

def weekend_heavy() -> List[float]:
    return [0.10, 0.10, 0.12, 0.13, 0.15, 0.20, 0.20]

def uniform_week() -> List[float]:
    return [1/7] * 7

def uniform_hours() -> List[float]:
    return [1/24] * 24

# -----------------------------------------------------------------------------
# POWER USERS / INFLUENCERS (5 personas, ~2% of users, ~15% of events)
# -----------------------------------------------------------------------------
for i in range(5):
    PERSONAS.append(Persona(
        name=f"influencer_{i+1}",
        description=f"High-profile content creator #{i+1}",
        user_percentage=0.4,
        activity_multiplier=7.5 + random.uniform(-0.5, 0.5),
        action_weights={
            "content_creation": 0.25,
            "engagement": 0.20,
            "feed_consumption": 0.15,
            "messaging": 0.10,
            "live_streaming": 0.12,
            "creator_tools": 0.10,
            "social_graph": 0.05,
            "discovery": 0.03,
        },
        hourly_weights=peak_hours([10, 14, 19, 21]),
        daily_weights=uniform_week(),
        success_rate=0.998,
        latency_multiplier=0.8,  # Good internet
    ))

# -----------------------------------------------------------------------------
# CONTENT CREATORS (10 personas, ~5% of users, ~12% of events)
# -----------------------------------------------------------------------------
for i in range(10):
    variant = i % 3  # photography, video, writer
    PERSONAS.append(Persona(
        name=f"creator_{['photo', 'video', 'writer'][variant]}_{i+1}",
        description=f"Regular content creator - {['photography', 'video', 'writing'][variant]}",
        user_percentage=0.5,
        activity_multiplier=2.4 + random.uniform(-0.3, 0.3),
        action_weights={
            "content_creation": 0.30 if variant != 2 else 0.35,
            "engagement": 0.18,
            "feed_consumption": 0.15,
            "messaging": 0.12,
            "live_streaming": 0.08 if variant == 1 else 0.02,
            "creator_tools": 0.08,
            "social_graph": 0.05,
            "discovery": 0.02,
        },
        hourly_weights=peak_hours([9, 12, 18, 21] if variant != 1 else [11, 15, 20]),
        daily_weights=weekend_heavy() if variant == 0 else uniform_week(),
        success_rate=0.996,
        latency_multiplier=0.9,
    ))

# -----------------------------------------------------------------------------
# ACTIVE ENGAGERS (15 personas, ~10% of users, ~18% of events)
# -----------------------------------------------------------------------------
for i in range(15):
    variant = i % 5  # commenter, reactor, messenger, group_active, all_rounder
    PERSONAS.append(Persona(
        name=f"engager_{['commenter', 'reactor', 'messenger', 'group', 'allround'][variant]}_{i+1}",
        description=f"Active engager - {['heavy commenter', 'reaction enthusiast', 'messenger', 'group participant', 'all-round'][variant]}",
        user_percentage=0.67,
        activity_multiplier=1.8 + random.uniform(-0.2, 0.2),
        action_weights={
            "content_creation": 0.12,
            "engagement": 0.35 if variant in [0, 1] else 0.20,
            "feed_consumption": 0.20,
            "messaging": 0.25 if variant in [2, 3] else 0.12,
            "live_streaming": 0.02,
            "creator_tools": 0.01,
            "social_graph": 0.08,
            "discovery": 0.05,
        },
        hourly_weights=peak_hours([12, 18, 21, 23]),
        daily_weights=uniform_week(),
        success_rate=0.994,
        latency_multiplier=1.0,
    ))

# -----------------------------------------------------------------------------
# REGULAR USERS (25 personas, ~25% of users, ~25% of events)
# -----------------------------------------------------------------------------
for i in range(25):
    age_group = i % 5  # teen, young_adult, adult, middle_age, senior
    PERSONAS.append(Persona(
        name=f"regular_{['teen', 'young', 'adult', 'middle', 'senior'][age_group]}_{i+1}",
        description=f"Regular user - {['teenager', 'young adult', 'adult', 'middle-aged', 'senior'][age_group]}",
        user_percentage=1.0,
        activity_multiplier=1.0 + random.uniform(-0.15, 0.15),
        action_weights={
            "content_creation": 0.10 if age_group < 3 else 0.05,
            "engagement": 0.22,
            "feed_consumption": 0.30,
            "messaging": 0.18,
            "live_streaming": 0.03 if age_group < 2 else 0.01,
            "creator_tools": 0.01,
            "social_graph": 0.10,
            "discovery": 0.06,
        },
        hourly_weights=peak_hours([7, 12, 19, 22] if age_group > 2 else [10, 15, 20, 23]),
        daily_weights=weekend_heavy() if age_group < 2 else weekday_heavy(),
        success_rate=0.993,
        latency_multiplier=1.1 if age_group > 3 else 1.0,
    ))

# -----------------------------------------------------------------------------
# CASUAL BROWSERS (20 personas, ~25% of users, ~15% of events)
# -----------------------------------------------------------------------------
for i in range(20):
    variant = i % 4  # morning_scroller, lunch_break, evening_wind_down, weekend_only
    PERSONAS.append(Persona(
        name=f"casual_{['morning', 'lunch', 'evening', 'weekend'][variant]}_{i+1}",
        description=f"Casual browser - {['morning scroller', 'lunch break user', 'evening wind-down', 'weekend only'][variant]}",
        user_percentage=1.25,
        activity_multiplier=0.6 + random.uniform(-0.1, 0.1),
        action_weights={
            "content_creation": 0.03,
            "engagement": 0.18,
            "feed_consumption": 0.45,
            "messaging": 0.15,
            "live_streaming": 0.01,
            "creator_tools": 0.00,
            "social_graph": 0.08,
            "discovery": 0.10,
        },
        hourly_weights=peak_hours([7, 8] if variant == 0 else [12, 13] if variant == 1 else [20, 21, 22] if variant == 2 else [11, 15, 20]),
        daily_weights=weekday_heavy() if variant < 3 else [0.02, 0.02, 0.02, 0.02, 0.02, 0.45, 0.45],
        success_rate=0.992,
        latency_multiplier=1.2,
    ))

# -----------------------------------------------------------------------------
# LURKERS (15 personas, ~20% of users, ~8% of events)
# -----------------------------------------------------------------------------
for i in range(15):
    PERSONAS.append(Persona(
        name=f"lurker_{i+1}",
        description=f"Lurker - mostly consumes, rarely interacts",
        user_percentage=1.33,
        activity_multiplier=0.4 + random.uniform(-0.1, 0.1),
        action_weights={
            "content_creation": 0.01,
            "engagement": 0.08,
            "feed_consumption": 0.60,
            "messaging": 0.10,
            "live_streaming": 0.02,
            "creator_tools": 0.00,
            "social_graph": 0.05,
            "discovery": 0.14,
        },
        hourly_weights=peak_hours([22, 23, 0, 1]),  # Late night scrollers
        daily_weights=uniform_week(),
        success_rate=0.990,
        latency_multiplier=1.3,
    ))

# -----------------------------------------------------------------------------
# NEW USERS (5 personas, ~8% of users, ~4% of events)
# -----------------------------------------------------------------------------
for i in range(5):
    PERSONAS.append(Persona(
        name=f"newuser_{i+1}",
        description=f"New user - onboarding and exploring",
        user_percentage=1.6,
        activity_multiplier=0.5 + random.uniform(-0.1, 0.1),
        action_weights={
            "content_creation": 0.05,
            "engagement": 0.10,
            "feed_consumption": 0.25,
            "messaging": 0.05,
            "live_streaming": 0.01,
            "creator_tools": 0.00,
            "social_graph": 0.30,  # Adding friends
            "discovery": 0.20,
            "onboarding": 0.04,
        },
        hourly_weights=uniform_hours(),  # New users explore anytime
        daily_weights=uniform_week(),
        success_rate=0.985,  # More errors as they learn
        latency_multiplier=1.4,
    ))

# -----------------------------------------------------------------------------
# BUSINESS/BRAND ACCOUNTS (3 personas, ~3% of users, ~2% of events)
# -----------------------------------------------------------------------------
for i in range(3):
    biz_type = ["small_business", "brand", "media_company"][i]
    PERSONAS.append(Persona(
        name=f"business_{biz_type}",
        description=f"Business account - {biz_type.replace('_', ' ')}",
        user_percentage=1.0,
        activity_multiplier=0.67 + random.uniform(-0.1, 0.1),
        action_weights={
            "content_creation": 0.25,
            "engagement": 0.15,
            "feed_consumption": 0.10,
            "messaging": 0.15,
            "live_streaming": 0.05,
            "creator_tools": 0.15,
            "social_graph": 0.05,
            "discovery": 0.02,
            "advertising": 0.08,
        },
        hourly_weights=peak_hours([9, 10, 11, 14, 15]),  # Business hours
        daily_weights=weekday_heavy(),
        success_rate=0.997,
        latency_multiplier=0.85,
    ))

# -----------------------------------------------------------------------------
# ADVERTISERS (2 personas, ~2% of users, ~1% of events)
# -----------------------------------------------------------------------------
for i in range(2):
    PERSONAS.append(Persona(
        name=f"advertiser_{['agency', 'direct'][i]}",
        description=f"Advertiser - {['ad agency', 'direct advertiser'][i]}",
        user_percentage=1.0,
        activity_multiplier=0.5,
        action_weights={
            "content_creation": 0.05,
            "engagement": 0.02,
            "feed_consumption": 0.05,
            "messaging": 0.05,
            "live_streaming": 0.00,
            "creator_tools": 0.03,
            "social_graph": 0.00,
            "discovery": 0.05,
            "advertising": 0.75,
        },
        hourly_weights=peak_hours([9, 10, 14, 15, 16]),
        daily_weights=weekday_heavy(),
        success_rate=0.998,
        latency_multiplier=0.8,
    ))


# =============================================================================
# SERVICE ACTIONS DEFINITION
# =============================================================================

@dataclass
class ServiceAction:
    """Defines an action that can be performed on a service"""
    service: str
    stack: str
    action: str
    category: str  # Maps to persona action_weights
    # Base metrics
    base_latency_ms: float
    latency_stddev_ms: float
    base_payload_bytes: int
    payload_stddev_bytes: int
    # Whether this action involves another user
    has_target_user: bool = False
    # Whether this action involves a content object
    has_object_id: bool = False
    object_type: Optional[str] = None
    # Read vs write
    is_write: bool = False
    # Relative frequency within category
    weight: float = 1.0


# Define all user-facing service actions
SERVICE_ACTIONS: List[ServiceAction] = [
    # -------------------------------------------------------------------------
    # USER STACK
    # -------------------------------------------------------------------------
    # identity
    ServiceAction("identity", "user", "login", "onboarding", 150, 50, 512, 128, weight=3.0),
    ServiceAction("identity", "user", "logout", "onboarding", 50, 20, 128, 32, weight=1.0),
    ServiceAction("identity", "user", "token_refresh", "feed_consumption", 30, 10, 256, 64, weight=5.0),
    ServiceAction("identity", "user", "oauth_authorize", "onboarding", 200, 80, 1024, 256, weight=0.5),

    # profile
    ServiceAction("profile", "user", "get_profile", "feed_consumption", 45, 15, 2048, 512, has_target_user=True, weight=8.0),
    ServiceAction("profile", "user", "get_own_profile", "feed_consumption", 40, 12, 2048, 512, weight=3.0),
    ServiceAction("profile", "user", "update_profile", "content_creation", 120, 40, 1024, 256, is_write=True, weight=0.3),
    ServiceAction("profile", "user", "update_avatar", "content_creation", 800, 300, 524288, 262144, is_write=True, weight=0.1),
    ServiceAction("profile", "user", "update_bio", "content_creation", 80, 25, 512, 128, is_write=True, weight=0.2),

    # privacy
    ServiceAction("privacy", "user", "get_privacy_settings", "social_graph", 35, 12, 512, 128, weight=0.5),
    ServiceAction("privacy", "user", "update_privacy_settings", "social_graph", 90, 30, 256, 64, is_write=True, weight=0.1),

    # account
    ServiceAction("account", "user", "get_account_status", "onboarding", 30, 10, 256, 64, weight=0.2),
    ServiceAction("account", "user", "deactivate_account", "onboarding", 200, 50, 128, 32, is_write=True, weight=0.01),
    ServiceAction("account", "user", "reactivate_account", "onboarding", 180, 45, 128, 32, is_write=True, weight=0.005),

    # -------------------------------------------------------------------------
    # SOCIAL GRAPH STACK
    # -------------------------------------------------------------------------
    # connections
    ServiceAction("connections", "social", "follow_user", "social_graph", 80, 25, 256, 64, has_target_user=True, is_write=True, weight=3.0),
    ServiceAction("connections", "social", "unfollow_user", "social_graph", 70, 20, 128, 32, has_target_user=True, is_write=True, weight=1.0),
    ServiceAction("connections", "social", "accept_follow_request", "social_graph", 60, 20, 128, 32, has_target_user=True, is_write=True, weight=0.8),
    ServiceAction("connections", "social", "reject_follow_request", "social_graph", 55, 18, 128, 32, has_target_user=True, is_write=True, weight=0.2),
    ServiceAction("connections", "social", "get_followers", "social_graph", 60, 25, 8192, 4096, weight=2.0),
    ServiceAction("connections", "social", "get_following", "social_graph", 55, 22, 8192, 4096, weight=2.0),
    ServiceAction("connections", "social", "get_mutual_friends", "social_graph", 90, 35, 4096, 2048, has_target_user=True, weight=1.0),

    # blocks
    ServiceAction("blocks", "social", "block_user", "social_graph", 70, 22, 128, 32, has_target_user=True, is_write=True, weight=0.1),
    ServiceAction("blocks", "social", "unblock_user", "social_graph", 65, 20, 128, 32, has_target_user=True, is_write=True, weight=0.05),
    ServiceAction("blocks", "social", "mute_user", "social_graph", 60, 18, 128, 32, has_target_user=True, is_write=True, weight=0.15),
    ServiceAction("blocks", "social", "unmute_user", "social_graph", 55, 16, 128, 32, has_target_user=True, is_write=True, weight=0.08),

    # suggestions
    ServiceAction("suggestions", "social", "get_friend_suggestions", "discovery", 120, 45, 4096, 2048, weight=2.0),
    ServiceAction("suggestions", "social", "dismiss_suggestion", "discovery", 40, 12, 128, 32, has_target_user=True, is_write=True, weight=0.5),

    # contacts
    ServiceAction("contacts", "social", "sync_contacts", "onboarding", 500, 200, 65536, 32768, is_write=True, weight=0.1),
    ServiceAction("contacts", "social", "find_contacts", "social_graph", 150, 60, 8192, 4096, weight=0.3),

    # -------------------------------------------------------------------------
    # CONTENT STACK
    # -------------------------------------------------------------------------
    # posts
    ServiceAction("posts", "content", "create_post", "content_creation", 180, 60, 4096, 2048, is_write=True, has_object_id=True, object_type="post", weight=5.0),
    ServiceAction("posts", "content", "edit_post", "content_creation", 150, 50, 4096, 2048, is_write=True, has_object_id=True, object_type="post", weight=0.5),
    ServiceAction("posts", "content", "delete_post", "content_creation", 100, 30, 128, 32, is_write=True, has_object_id=True, object_type="post", weight=0.3),
    ServiceAction("posts", "content", "get_post", "feed_consumption", 50, 18, 8192, 4096, has_object_id=True, object_type="post", weight=15.0),
    ServiceAction("posts", "content", "get_user_posts", "feed_consumption", 80, 30, 32768, 16384, has_target_user=True, weight=5.0),

    # media
    ServiceAction("media", "content", "upload_image", "content_creation", 1200, 500, 2097152, 1048576, is_write=True, has_object_id=True, object_type="media", weight=3.0),
    ServiceAction("media", "content", "upload_video", "content_creation", 5000, 2000, 52428800, 26214400, is_write=True, has_object_id=True, object_type="media", weight=1.0),
    ServiceAction("media", "content", "get_media", "feed_consumption", 80, 30, 1048576, 524288, has_object_id=True, object_type="media", weight=20.0),
    ServiceAction("media", "content", "delete_media", "content_creation", 120, 40, 128, 32, is_write=True, has_object_id=True, object_type="media", weight=0.2),

    # stories
    ServiceAction("stories", "content", "create_story", "content_creation", 600, 200, 1048576, 524288, is_write=True, has_object_id=True, object_type="story", weight=2.0),
    ServiceAction("stories", "content", "view_story", "feed_consumption", 60, 20, 524288, 262144, has_object_id=True, object_type="story", has_target_user=True, weight=10.0),
    ServiceAction("stories", "content", "react_to_story", "engagement", 50, 15, 256, 64, is_write=True, has_object_id=True, object_type="story", weight=2.0),
    ServiceAction("stories", "content", "get_stories_feed", "feed_consumption", 100, 40, 16384, 8192, weight=8.0),

    # comments
    ServiceAction("comments", "content", "add_comment", "engagement", 100, 35, 1024, 512, is_write=True, has_object_id=True, object_type="post", weight=5.0),
    ServiceAction("comments", "content", "edit_comment", "engagement", 90, 30, 1024, 512, is_write=True, has_object_id=True, object_type="comment", weight=0.3),
    ServiceAction("comments", "content", "delete_comment", "engagement", 70, 22, 128, 32, is_write=True, has_object_id=True, object_type="comment", weight=0.2),
    ServiceAction("comments", "content", "get_comments", "feed_consumption", 70, 25, 16384, 8192, has_object_id=True, object_type="post", weight=12.0),

    # reactions
    ServiceAction("reactions", "content", "add_reaction", "engagement", 40, 12, 256, 64, is_write=True, has_object_id=True, object_type="post", weight=15.0),
    ServiceAction("reactions", "content", "remove_reaction", "engagement", 35, 10, 128, 32, is_write=True, has_object_id=True, object_type="post", weight=1.0),
    ServiceAction("reactions", "content", "get_reactions", "feed_consumption", 50, 18, 4096, 2048, has_object_id=True, object_type="post", weight=3.0),

    # shares
    ServiceAction("shares", "content", "share_post", "engagement", 90, 30, 512, 128, is_write=True, has_object_id=True, object_type="post", weight=2.0),
    ServiceAction("shares", "content", "get_shares", "feed_consumption", 55, 20, 4096, 2048, has_object_id=True, object_type="post", weight=1.0),

    # hashtags
    ServiceAction("hashtags", "content", "get_hashtag_posts", "discovery", 90, 35, 32768, 16384, has_object_id=True, object_type="hashtag", weight=3.0),
    ServiceAction("hashtags", "content", "get_trending_hashtags", "discovery", 70, 25, 4096, 2048, weight=2.0),

    # -------------------------------------------------------------------------
    # FEED STACK
    # -------------------------------------------------------------------------
    ServiceAction("timeline", "feed", "get_timeline", "feed_consumption", 120, 45, 65536, 32768, weight=25.0),
    ServiceAction("timeline", "feed", "refresh_timeline", "feed_consumption", 100, 38, 32768, 16384, weight=15.0),
    ServiceAction("timeline", "feed", "get_timeline_page", "feed_consumption", 90, 32, 32768, 16384, weight=20.0),

    # -------------------------------------------------------------------------
    # MESSAGING STACK
    # -------------------------------------------------------------------------
    # dm
    ServiceAction("dm", "messaging", "send_message", "messaging", 80, 28, 2048, 1024, is_write=True, has_target_user=True, has_object_id=True, object_type="conversation", weight=8.0),
    ServiceAction("dm", "messaging", "get_messages", "messaging", 70, 25, 16384, 8192, has_object_id=True, object_type="conversation", weight=10.0),
    ServiceAction("dm", "messaging", "get_conversations", "messaging", 65, 22, 8192, 4096, weight=6.0),
    ServiceAction("dm", "messaging", "mark_read", "messaging", 30, 10, 128, 32, is_write=True, has_object_id=True, object_type="conversation", weight=5.0),
    ServiceAction("dm", "messaging", "delete_message", "messaging", 60, 20, 128, 32, is_write=True, has_object_id=True, object_type="message", weight=0.3),

    # groups
    ServiceAction("groups", "messaging", "create_group", "messaging", 120, 40, 1024, 256, is_write=True, has_object_id=True, object_type="group", weight=0.3),
    ServiceAction("groups", "messaging", "send_group_message", "messaging", 85, 30, 2048, 1024, is_write=True, has_object_id=True, object_type="group", weight=4.0),
    ServiceAction("groups", "messaging", "get_group_messages", "messaging", 75, 28, 16384, 8192, has_object_id=True, object_type="group", weight=5.0),
    ServiceAction("groups", "messaging", "add_group_member", "messaging", 90, 32, 256, 64, is_write=True, has_object_id=True, object_type="group", has_target_user=True, weight=0.2),
    ServiceAction("groups", "messaging", "leave_group", "messaging", 70, 24, 128, 32, is_write=True, has_object_id=True, object_type="group", weight=0.1),

    # realtime
    ServiceAction("realtime", "messaging", "ws_connect", "messaging", 150, 50, 512, 128, is_write=True, weight=2.0),
    ServiceAction("realtime", "messaging", "ws_disconnect", "messaging", 30, 10, 64, 16, is_write=True, weight=2.0),
    ServiceAction("realtime", "messaging", "ws_ping", "messaging", 10, 5, 32, 8, weight=10.0),

    # presence
    ServiceAction("presence", "messaging", "set_online", "messaging", 40, 15, 128, 32, is_write=True, weight=2.0),
    ServiceAction("presence", "messaging", "set_offline", "messaging", 35, 12, 128, 32, is_write=True, weight=2.0),
    ServiceAction("presence", "messaging", "get_presence", "messaging", 30, 10, 256, 64, has_target_user=True, weight=3.0),

    # -------------------------------------------------------------------------
    # NOTIFICATIONS STACK
    # -------------------------------------------------------------------------
    ServiceAction("inapp", "notifications", "get_notifications", "feed_consumption", 60, 22, 8192, 4096, weight=8.0),
    ServiceAction("inapp", "notifications", "mark_notification_read", "feed_consumption", 35, 12, 128, 32, is_write=True, has_object_id=True, object_type="notification", weight=4.0),
    ServiceAction("inapp", "notifications", "clear_notifications", "feed_consumption", 50, 18, 128, 32, is_write=True, weight=0.5),
    ServiceAction("preferences", "notifications", "get_notification_prefs", "social_graph", 40, 14, 512, 128, weight=0.3),
    ServiceAction("preferences", "notifications", "update_notification_prefs", "social_graph", 70, 25, 256, 64, is_write=True, weight=0.1),

    # -------------------------------------------------------------------------
    # SEARCH STACK
    # -------------------------------------------------------------------------
    ServiceAction("users", "search", "search_users", "discovery", 100, 40, 8192, 4096, weight=3.0),
    ServiceAction("content", "search", "search_posts", "discovery", 120, 50, 32768, 16384, weight=4.0),
    ServiceAction("hashtags", "search", "search_hashtags", "discovery", 80, 30, 4096, 2048, weight=2.0),

    # -------------------------------------------------------------------------
    # DISCOVERY STACK
    # -------------------------------------------------------------------------
    ServiceAction("trending", "discovery", "get_trending", "discovery", 80, 30, 16384, 8192, weight=5.0),
    ServiceAction("explore", "discovery", "get_explore", "discovery", 100, 40, 32768, 16384, weight=6.0),
    ServiceAction("recommendations", "discovery", "get_recommendations", "discovery", 110, 45, 16384, 8192, weight=4.0),
    ServiceAction("interests", "discovery", "get_interests", "discovery", 60, 22, 2048, 512, weight=1.0),
    ServiceAction("interests", "discovery", "update_interests", "social_graph", 80, 28, 512, 128, is_write=True, weight=0.2),

    # -------------------------------------------------------------------------
    # MODERATION STACK (user-initiated)
    # -------------------------------------------------------------------------
    ServiceAction("reports", "moderation", "report_content", "engagement", 100, 35, 1024, 256, is_write=True, has_object_id=True, object_type="post", weight=0.1),
    ServiceAction("reports", "moderation", "report_user", "engagement", 95, 32, 1024, 256, is_write=True, has_target_user=True, weight=0.05),
    ServiceAction("reports", "moderation", "get_report_status", "engagement", 50, 18, 512, 128, has_object_id=True, object_type="report", weight=0.02),

    # -------------------------------------------------------------------------
    # ADS STACK (advertiser actions)
    # -------------------------------------------------------------------------
    ServiceAction("campaigns", "ads", "create_campaign", "advertising", 200, 70, 4096, 1024, is_write=True, has_object_id=True, object_type="campaign", weight=0.5),
    ServiceAction("campaigns", "ads", "get_campaigns", "advertising", 90, 35, 16384, 8192, weight=2.0),
    ServiceAction("campaigns", "ads", "update_campaign", "advertising", 150, 55, 2048, 512, is_write=True, has_object_id=True, object_type="campaign", weight=1.0),
    ServiceAction("campaigns", "ads", "pause_campaign", "advertising", 80, 28, 256, 64, is_write=True, has_object_id=True, object_type="campaign", weight=0.3),
    ServiceAction("targeting", "ads", "get_audiences", "advertising", 100, 40, 8192, 4096, weight=1.5),
    ServiceAction("targeting", "ads", "create_audience", "advertising", 180, 65, 4096, 1024, is_write=True, has_object_id=True, object_type="audience", weight=0.3),
    ServiceAction("ad-analytics", "ads", "get_campaign_metrics", "advertising", 150, 55, 32768, 16384, has_object_id=True, object_type="campaign", weight=3.0),

    # -------------------------------------------------------------------------
    # PAYMENTS STACK
    # -------------------------------------------------------------------------
    ServiceAction("subscriptions", "payments", "subscribe", "creator_tools", 250, 80, 1024, 256, is_write=True, has_target_user=True, weight=0.2),
    ServiceAction("subscriptions", "payments", "unsubscribe", "creator_tools", 150, 50, 256, 64, is_write=True, has_target_user=True, weight=0.1),
    ServiceAction("subscriptions", "payments", "get_subscriptions", "creator_tools", 70, 25, 4096, 1024, weight=0.5),
    ServiceAction("wallet", "payments", "get_balance", "creator_tools", 50, 18, 256, 64, weight=0.3),
    ServiceAction("wallet", "payments", "add_funds", "creator_tools", 300, 100, 512, 128, is_write=True, weight=0.05),

    # -------------------------------------------------------------------------
    # CREATOR STACK
    # -------------------------------------------------------------------------
    ServiceAction("studio", "creator", "upload_content", "creator_tools", 2000, 800, 10485760, 5242880, is_write=True, has_object_id=True, object_type="content", weight=1.0),
    ServiceAction("studio", "creator", "edit_content", "creator_tools", 500, 200, 2097152, 1048576, is_write=True, has_object_id=True, object_type="content", weight=0.5),
    ServiceAction("creator-analytics", "creator", "get_analytics", "creator_tools", 120, 45, 32768, 16384, weight=2.0),
    ServiceAction("creator-analytics", "creator", "get_post_insights", "creator_tools", 80, 30, 8192, 4096, has_object_id=True, object_type="post", weight=1.5),
    ServiceAction("monetization", "creator", "get_earnings", "creator_tools", 70, 25, 4096, 1024, weight=0.5),
    ServiceAction("shop", "creator", "create_product", "creator_tools", 200, 70, 4096, 1024, is_write=True, has_object_id=True, object_type="product", weight=0.2),
    ServiceAction("shop", "creator", "get_products", "creator_tools", 80, 30, 16384, 8192, weight=0.3),

    # -------------------------------------------------------------------------
    # LIVE STACK
    # -------------------------------------------------------------------------
    ServiceAction("streaming", "live", "start_stream", "live_streaming", 500, 200, 2048, 512, is_write=True, has_object_id=True, object_type="stream", weight=0.5),
    ServiceAction("streaming", "live", "end_stream", "live_streaming", 200, 80, 512, 128, is_write=True, has_object_id=True, object_type="stream", weight=0.5),
    ServiceAction("streaming", "live", "get_stream", "live_streaming", 80, 30, 4096, 1024, has_object_id=True, object_type="stream", weight=5.0),
    ServiceAction("streaming", "live", "get_live_streams", "live_streaming", 100, 40, 16384, 8192, weight=3.0),
    ServiceAction("live-chat", "live", "send_chat_message", "live_streaming", 40, 15, 512, 128, is_write=True, has_object_id=True, object_type="stream", weight=8.0),
    ServiceAction("live-chat", "live", "get_chat_messages", "live_streaming", 50, 18, 8192, 4096, has_object_id=True, object_type="stream", weight=6.0),
    ServiceAction("gifts", "live", "send_gift", "live_streaming", 150, 55, 512, 128, is_write=True, has_object_id=True, object_type="stream", has_target_user=True, weight=1.0),
    ServiceAction("gifts", "live", "get_gifts", "live_streaming", 60, 22, 4096, 1024, has_object_id=True, object_type="stream", weight=0.5),
    ServiceAction("vod", "live", "get_vod", "live_streaming", 90, 35, 8192, 4096, has_object_id=True, object_type="vod", weight=2.0),
]

# Build lookup by category
ACTIONS_BY_CATEGORY: Dict[str, List[ServiceAction]] = {}
for action in SERVICE_ACTIONS:
    if action.category not in ACTIONS_BY_CATEGORY:
        ACTIONS_BY_CATEGORY[action.category] = []
    ACTIONS_BY_CATEGORY[action.category].append(action)

# Build lookup by service
ACTIONS_BY_SERVICE: Dict[str, List[ServiceAction]] = {}
for action in SERVICE_ACTIONS:
    key = f"{action.stack}:{action.service}"
    if key not in ACTIONS_BY_SERVICE:
        ACTIONS_BY_SERVICE[key] = []
    ACTIONS_BY_SERVICE[key].append(action)


# =============================================================================
# SERVICE DEPENDENCIES
# =============================================================================

# Documented dependencies: service -> list of services it depends on
SERVICE_DEPENDENCIES: Dict[str, List[str]] = {
    # Feed stack
    "feed:timeline": ["feed:ranking", "content:posts", "content:stories", "social:connections", "content:reactions"],
    "feed:ranking": ["discovery:interests"],
    "feed:fanout": ["social:connections"],
    "feed:aggregation": ["feed:fanout"],

    # Content stack
    "content:posts": ["content:media", "content:hashtags", "feed:fanout", "search:indexer"],
    "content:comments": ["content:posts"],
    "content:reactions": ["content:posts", "content:comments"],
    "content:shares": ["content:posts", "feed:fanout"],
    "content:stories": ["content:media"],

    # Messaging stack
    "messaging:dm": ["messaging:realtime", "messaging:presence"],
    "messaging:groups": ["messaging:realtime", "messaging:presence"],

    # Notifications stack
    "notifications:push": ["notifications:preferences"],
    "notifications:inapp": ["notifications:preferences"],
    "notifications:email": ["notifications:preferences"],
    "notifications:sms": ["notifications:preferences"],

    # Search stack
    "search:users": ["search:indexer"],
    "search:content": ["search:indexer"],
    "search:hashtags": ["search:indexer"],

    # Discovery stack
    "discovery:explore": ["discovery:trending", "discovery:recommendations", "feed:ranking"],
    "discovery:recommendations": ["discovery:interests"],

    # Live stack
    "live:streaming": ["live:live-chat", "live:gifts"],
    "live:live-chat": ["messaging:realtime"],
    "live:gifts": ["payments:wallet"],

    # Ads stack
    "ads:campaigns": ["ads:targeting", "ads:bidding"],
    "ads:delivery": ["ads:campaigns", "ads:bidding"],

    # Payments stack
    "payments:subscriptions": ["payments:processor"],
    "payments:payouts": ["payments:processor", "payments:wallet"],

    # Creator stack
    "creator:monetization": ["payments:wallet", "creator:creator-analytics"],
    "creator:shop": ["payments:processor"],

    # Social stack
    "social:suggestions": ["social:connections"],
}

# Hidden/undocumented dependencies - these represent shared infrastructure
# that can cause correlated failures. Used for "discoverable" errors.
HIDDEN_DEPENDENCIES: Dict[str, Dict] = {
    # Shared database clusters
    "aurora_primary": {
        "services": ["user:profile", "user:privacy", "user:account", "content:posts",
                     "content:comments", "content:shares", "ads:campaigns",
                     "payments:subscriptions", "payments:wallet", "payments:payouts",
                     "moderation:content-review", "moderation:reports", "moderation:trust-safety"],
        "failure_rate": 0.001,  # 0.1% of requests during incident
        "error_type": "database",
        "error_codes": ["503", "504"],
        "error_message": "Database connection pool exhausted",
    },
    "dynamodb_throttle": {
        "services": ["user:identity", "social:blocks", "social:contacts", "content:stories",
                     "content:reactions", "content:hashtags", "feed:timeline",
                     "messaging:dm", "messaging:groups", "messaging:presence",
                     "notifications:inapp", "notifications:preferences",
                     "discovery:trending", "discovery:interests",
                     "platform:feature-flags", "platform:ab-testing"],
        "failure_rate": 0.002,
        "error_type": "database",
        "error_codes": ["429", "503"],
        "error_message": "DynamoDB throughput exceeded",
    },
    "neptune_timeout": {
        "services": ["social:connections", "social:blocks", "social:suggestions"],
        "failure_rate": 0.003,
        "error_type": "database",
        "error_codes": ["504"],
        "error_message": "Graph query timeout",
    },
    "opensearch_cluster": {
        "services": ["content:hashtags", "search:indexer", "search:users",
                     "search:content", "search:hashtags", "moderation:trust-safety"],
        "failure_rate": 0.002,
        "error_type": "search",
        "error_codes": ["503", "504"],
        "error_message": "OpenSearch cluster unavailable",
    },
    # Shared cache clusters
    "redis_session": {
        "services": ["user:identity", "platform:rate-limiter"],
        "failure_rate": 0.001,
        "error_type": "cache",
        "error_codes": ["503"],
        "error_message": "Redis session cluster connection failed",
    },
    "redis_feed": {
        "services": ["feed:timeline", "feed:ranking", "feed:fanout"],
        "failure_rate": 0.002,
        "error_type": "cache",
        "error_codes": ["503"],
        "error_message": "Redis feed cache unavailable",
    },
    "redis_content": {
        "services": ["content:posts", "content:comments", "content:reactions", "content:stories"],
        "failure_rate": 0.001,
        "error_type": "cache",
        "error_codes": ["503"],
        "error_message": "Redis content cache connection timeout",
    },
    "redis_messaging": {
        "services": ["messaging:dm", "messaging:groups", "messaging:realtime", "messaging:presence"],
        "failure_rate": 0.001,
        "error_type": "cache",
        "error_codes": ["503"],
        "error_message": "Redis messaging cluster failover in progress",
    },
    # Shared processing queues
    "media_processing": {
        "services": ["content:media", "content:stories", "creator:studio", "live:vod"],
        "failure_rate": 0.003,
        "error_type": "queue",
        "error_codes": ["503", "504"],
        "error_message": "Media processing queue backlogged",
    },
    "kinesis_feed": {
        "services": ["feed:timeline", "feed:fanout", "feed:aggregation", "discovery:trending"],
        "failure_rate": 0.001,
        "error_type": "queue",
        "error_codes": ["503"],
        "error_message": "Kinesis shard iterator expired",
    },
    # Shared libraries/common code
    "auth_library": {
        "services": ["user:identity", "user:profile", "user:privacy", "user:account",
                     "content:posts", "messaging:dm", "payments:processor"],
        "failure_rate": 0.0005,
        "error_type": "internal",
        "error_codes": ["500"],
        "error_message": "JWT validation failed - library version mismatch",
    },
    "serialization_bug": {
        "services": ["content:posts", "content:comments", "messaging:dm", "messaging:groups"],
        "failure_rate": 0.0003,
        "error_type": "internal",
        "error_codes": ["500"],
        "error_message": "Unexpected null in response serialization",
    },
    # Rate limiting
    "rate_limiter_shared": {
        "services": ["platform:api-gateway", "platform:rate-limiter"],
        "failure_rate": 0.004,
        "error_type": "rate_limit",
        "error_codes": ["429"],
        "error_message": "Global rate limit exceeded",
    },
}

# Build reverse lookup: service -> hidden dependencies it's part of
SERVICE_HIDDEN_DEPS: Dict[str, List[str]] = {}
for dep_name, dep_info in HIDDEN_DEPENDENCIES.items():
    for service in dep_info["services"]:
        if service not in SERVICE_HIDDEN_DEPS:
            SERVICE_HIDDEN_DEPS[service] = []
        SERVICE_HIDDEN_DEPS[service].append(dep_name)


# =============================================================================
# DEPLOYMENTS AND RELEASES
# =============================================================================

# Environment configurations with AWS account IDs
ENVIRONMENT_CONFIG = {
    "prod": {"account": "111111111111", "regions": ["us-east-1", "us-west-2"], "weight": 0.85},
    "stg": {"account": "222222222222", "regions": ["us-east-1"], "weight": 0.10},
    "dev": {"account": "333333333333", "regions": ["us-east-1"], "weight": 0.05},
}

def generate_release_id(env: str, region: str, stack: str, service: str, release_num: int) -> str:
    """Generate a release ID in qairon format: {deployment_id}:{release_num}

    release_num is the CI/CD pipeline's sequential build number for this release.
    """
    account = ENVIRONMENT_CONFIG[env]["account"]
    deployment_id = f"{env}:aws:{account}:{region}:platform:eks:main:social:{stack}:{service}:default"
    return f"{deployment_id}:{release_num}"


# =============================================================================
# DATA GENERATION
# =============================================================================

@dataclass
class User:
    """A synthetic user"""
    user_id: str
    persona: Persona
    created_at: datetime
    # Content this user has created (for realistic object references)
    posts: List[str] = field(default_factory=list)
    stories: List[str] = field(default_factory=list)
    # Users this user follows/is followed by
    following: List[str] = field(default_factory=list)
    followers: List[str] = field(default_factory=list)
    # Conversations
    conversations: List[str] = field(default_factory=list)
    groups: List[str] = field(default_factory=list)


@dataclass
class LogEntry:
    """A log entry"""
    timestamp: str
    level: str
    service: str
    stack: str
    action: str
    user_id: str
    request_id: str
    success: bool
    message: str
    release_id: str  # Full qairon release ID: {deployment_id}:{release_num}
    # Optional fields
    target_user_id: Optional[str] = None
    object_type: Optional[str] = None
    object_id: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    # Error source tracking for dependency analysis
    error_source: Optional[str] = None  # "self", "dependency:<service>", "infrastructure:<component>"
    error_type: Optional[str] = None    # "client", "server", "database", "cache", "queue", "internal", "rate_limit"
    upstream_request_id: Optional[str] = None  # Request ID of the failed dependency call


@dataclass
class MetricEntry:
    """A metric entry - individual measurement in standard format"""
    metric: str
    ts: float  # epoch time (seconds since 1970)
    value: float
    tags: Dict[str, str]  # Tags as key-value pairs

    def to_dict(self) -> Dict:
        """Convert to output format"""
        return {
            "metric": self.metric,
            "ts": self.ts,
            "value": self.value,
            "tags": self.tags,
        }


@dataclass
class InfrastructureIncident:
    """Represents a time window when a hidden dependency is failing"""
    dependency_name: str
    start_time: datetime
    end_time: datetime
    affected_services: List[str]
    error_info: Dict


class MonitoringDataGenerator:
    """Generates synthetic monitoring data"""

    def __init__(self, total_events: int, total_users: int, seed: int = 42):
        self.total_events = total_events
        self.total_users = total_users
        self.rng = random.Random(seed)

        # Time range: 1 year ending now
        self.end_time = datetime.now()
        self.start_time = self.end_time - timedelta(days=365)

        # Users
        self.users: List[User] = []
        self.user_by_id: Dict[str, User] = {}

        # Infrastructure incidents (time windows of hidden dependency failures)
        self.incidents: List[InfrastructureIncident] = []

        # Content pools for realistic references
        self.all_posts: List[Tuple[str, str]] = []  # (post_id, author_id)
        self.all_stories: List[Tuple[str, str]] = []
        self.all_streams: List[Tuple[str, str]] = []
        self.all_hashtags: List[str] = [f"#{word}" for word in [
            "trending", "viral", "fyp", "lifestyle", "travel", "food", "fitness",
            "tech", "gaming", "music", "art", "fashion", "beauty", "sports",
            "news", "memes", "photography", "nature", "pets", "diy", "cooking"
        ]]

        # Error codes
        self.error_codes = {
            "client": ["400", "401", "403", "404", "422", "429"],
            "server": ["500", "502", "503", "504"],
        }
        self.error_messages = {
            "400": "Bad request",
            "401": "Unauthorized",
            "403": "Forbidden",
            "404": "Not found",
            "422": "Validation error",
            "429": "Rate limited",
            "500": "Internal server error",
            "502": "Bad gateway",
            "503": "Service unavailable",
            "504": "Gateway timeout",
        }

    def generate_users(self):
        """Generate synthetic users distributed across personas"""
        print(f"Generating {self.total_users} users across {len(PERSONAS)} personas...")

        # Calculate users per persona based on percentages
        total_percentage = sum(p.user_percentage for p in PERSONAS)

        for persona in PERSONAS:
            num_users = int(self.total_users * (persona.user_percentage / total_percentage))
            for _ in range(num_users):
                user_id = f"user_{uuid.uuid4().hex[:12]}"
                # Users join throughout the year, weighted toward earlier
                days_ago = int(self.rng.betavariate(2, 5) * 365)
                created_at = self.end_time - timedelta(days=days_ago)

                user = User(
                    user_id=user_id,
                    persona=persona,
                    created_at=created_at,
                )
                self.users.append(user)
                self.user_by_id[user_id] = user

        # Fill remaining users with random personas
        while len(self.users) < self.total_users:
            persona = self.rng.choice(PERSONAS)
            user_id = f"user_{uuid.uuid4().hex[:12]}"
            days_ago = int(self.rng.betavariate(2, 5) * 365)
            created_at = self.end_time - timedelta(days=days_ago)

            user = User(
                user_id=user_id,
                persona=persona,
                created_at=created_at,
            )
            self.users.append(user)
            self.user_by_id[user_id] = user

        print(f"  Created {len(self.users)} users")

        # Build some initial social connections
        print("  Building social graph...")
        for user in self.users:
            # Each user follows some others based on persona
            num_following = int(self.rng.gauss(50, 30) * user.persona.activity_multiplier)
            num_following = max(5, min(num_following, 500))

            potential_follows = [u for u in self.users if u.user_id != user.user_id]
            follows = self.rng.sample(potential_follows, min(num_following, len(potential_follows)))

            for followed in follows:
                user.following.append(followed.user_id)
                followed.followers.append(user.user_id)

    def generate_incidents(self):
        """Generate infrastructure incidents throughout the year"""
        print("  Generating infrastructure incidents...")

        for dep_name, dep_info in HIDDEN_DEPENDENCIES.items():
            # Each hidden dependency has 2-8 incidents per year
            num_incidents = self.rng.randint(2, 8)

            for _ in range(num_incidents):
                # Random start time during the year
                days_ago = self.rng.randint(1, 364)
                hour = self.rng.randint(0, 23)
                start = self.start_time + timedelta(days=365 - days_ago, hours=hour)

                # Incidents last 5 minutes to 4 hours
                duration_minutes = self.rng.randint(5, 240)
                end = start + timedelta(minutes=duration_minutes)

                incident = InfrastructureIncident(
                    dependency_name=dep_name,
                    start_time=start,
                    end_time=end,
                    affected_services=dep_info["services"],
                    error_info={
                        "error_type": dep_info["error_type"],
                        "error_codes": dep_info["error_codes"],
                        "error_message": dep_info["error_message"],
                        "failure_rate": dep_info["failure_rate"],
                    }
                )
                self.incidents.append(incident)

        # Sort by start time
        self.incidents.sort(key=lambda x: x.start_time)
        print(f"    Generated {len(self.incidents)} infrastructure incidents")

    def get_active_incident(self, service_key: str, timestamp: datetime) -> Optional[InfrastructureIncident]:
        """Check if there's an active incident affecting this service at this time"""
        for incident in self.incidents:
            if incident.start_time <= timestamp <= incident.end_time:
                if service_key in incident.affected_services:
                    return incident
        return None

    def check_dependency_failure(self, action: ServiceAction, timestamp: datetime) -> Optional[Tuple[str, str, str, str]]:
        """
        Check if a dependency of this service is failing.
        Returns (failed_service, error_type, error_code, error_message) or None
        """
        service_key = f"{action.stack}:{action.service}"

        # Check documented dependencies
        if service_key in SERVICE_DEPENDENCIES:
            for dep_service in SERVICE_DEPENDENCIES[service_key]:
                # Check if the dependency has an active incident
                incident = self.get_active_incident(dep_service, timestamp)
                if incident:
                    # During an incident, use the incident's failure rate
                    if self.rng.random() < incident.error_info["failure_rate"] * 10:  # Amplified during cascade
                        error_code = self.rng.choice(incident.error_info["error_codes"])
                        return (
                            dep_service,
                            incident.error_info["error_type"],
                            error_code,
                            f"Upstream service {dep_service} failed: {incident.error_info['error_message']}"
                        )
        return None

    def check_hidden_dependency_failure(self, action: ServiceAction, timestamp: datetime) -> Optional[Tuple[str, str, str, str]]:
        """
        Check if a hidden/infrastructure dependency is failing.
        Returns (dependency_name, error_type, error_code, error_message) or None
        """
        service_key = f"{action.stack}:{action.service}"

        # Check if this service is affected by any active incident
        incident = self.get_active_incident(service_key, timestamp)
        if incident:
            # Use the incident's failure rate
            if self.rng.random() < incident.error_info["failure_rate"]:
                error_code = self.rng.choice(incident.error_info["error_codes"])
                return (
                    incident.dependency_name,
                    incident.error_info["error_type"],
                    error_code,
                    incident.error_info["error_message"]
                )
        return None

    def determine_error(self, action: ServiceAction, user: User, timestamp: datetime) -> Optional[Dict]:
        """
        Determine if this request should fail and why.
        Returns error details dict or None for success.

        Error priority:
        1. Hidden dependency failure (infrastructure incident)
        2. Documented dependency cascade
        3. Random service error (based on persona success rate)
        """
        service_key = f"{action.stack}:{action.service}"

        # 1. Check hidden dependency failures first
        hidden_failure = self.check_hidden_dependency_failure(action, timestamp)
        if hidden_failure:
            dep_name, error_type, error_code, error_message = hidden_failure
            return {
                "error_source": f"infrastructure:{dep_name}",
                "error_type": error_type,
                "error_code": error_code,
                "error_message": error_message,
                "upstream_request_id": None,
            }

        # 2. Check documented dependency failures
        dep_failure = self.check_dependency_failure(action, timestamp)
        if dep_failure:
            dep_service, error_type, error_code, error_message = dep_failure
            return {
                "error_source": f"dependency:{dep_service}",
                "error_type": error_type,
                "error_code": error_code,
                "error_message": error_message,
                "upstream_request_id": uuid.uuid4().hex,  # The failed upstream call
            }

        # 3. Random service errors based on persona success rate
        if self.rng.random() > user.persona.success_rate:
            # Determine error type
            if self.rng.random() < 0.7:
                error_code = self.rng.choice(self.error_codes["client"])
                error_type = "client"
            else:
                error_code = self.rng.choice(self.error_codes["server"])
                error_type = "server"

            return {
                "error_source": "self",
                "error_type": error_type,
                "error_code": error_code,
                "error_message": self.error_messages[error_code],
                "upstream_request_id": None,
            }

        return None  # Success

    def select_release(self, action: ServiceAction, timestamp: datetime) -> str:
        """Select a release_id for this request based on environment weights and time"""
        # Select environment based on weights
        envs = list(ENVIRONMENT_CONFIG.keys())
        weights = [ENVIRONMENT_CONFIG[e]["weight"] for e in envs]
        env = self.rng.choices(envs, weights=weights)[0]

        # Select region from available regions for this environment
        regions = ENVIRONMENT_CONFIG[env]["regions"]
        if len(regions) > 1:
            # us-east-1 gets more traffic than us-west-2
            region_weights = [0.6, 0.4] if len(regions) == 2 else [1.0]
            region = self.rng.choices(regions, weights=region_weights)[0]
        else:
            region = regions[0]

        # Calculate release number based on time progression through the year
        # Services get deployed at different cadences
        days_into_year = (timestamp - self.start_time).days
        year_progress = days_into_year / 365.0

        # Base release number that grows over the year (simulating CI/CD pipeline)
        # Different services have different deployment frequencies
        base_release = 50 + int(year_progress * 200)  # 50-250 releases over the year
        # Add some variance per service
        service_hash = hash(f"{action.stack}:{action.service}") % 50
        release_num = base_release + service_hash

        return generate_release_id(env, region, action.stack, action.service, release_num)

    def select_action_for_user(self, user: User) -> ServiceAction:
        """Select an action for a user based on their persona"""
        persona = user.persona

        # First select a category based on persona weights
        categories = list(persona.action_weights.keys())
        weights = [persona.action_weights.get(c, 0) for c in categories]

        # Filter to categories that have actions
        valid = [(c, w) for c, w in zip(categories, weights) if c in ACTIONS_BY_CATEGORY and w > 0]
        if not valid:
            valid = [(c, 1.0) for c in ACTIONS_BY_CATEGORY.keys()]

        categories, weights = zip(*valid)
        category = self.rng.choices(categories, weights=weights)[0]

        # Then select an action within that category
        actions = ACTIONS_BY_CATEGORY[category]
        action_weights = [a.weight for a in actions]

        return self.rng.choices(actions, weights=action_weights)[0]

    def generate_timestamp(self, user: User) -> datetime:
        """Generate a timestamp based on user's persona patterns"""
        persona = user.persona

        # Pick a random day in the year - uniform distribution across the full year
        # This represents aggregate activity across the entire social network
        days_ago = self.rng.randint(0, 364)
        date = self.end_time - timedelta(days=days_ago)

        # Apply day-of-week weights
        dow = date.weekday()
        if self.rng.random() > persona.daily_weights[dow] * 7:
            # Resample to preferred days
            preferred_dow = self.rng.choices(range(7), weights=persona.daily_weights)[0]
            days_diff = preferred_dow - dow
            date = date + timedelta(days=days_diff)

        # Apply hourly weights
        hour = self.rng.choices(range(24), weights=persona.hourly_weights)[0]
        minute = self.rng.randint(0, 59)
        second = self.rng.randint(0, 59)
        microsecond = self.rng.randint(0, 999999)

        return date.replace(hour=hour, minute=minute, second=second, microsecond=microsecond)

    def generate_object_id(self, action: ServiceAction, user: User) -> Optional[str]:
        """Generate a realistic object ID for the action"""
        if not action.has_object_id:
            return None

        obj_type = action.object_type

        if obj_type == "post":
            if action.is_write and action.action == "create_post":
                # New post
                post_id = f"post_{uuid.uuid4().hex[:16]}"
                user.posts.append(post_id)
                self.all_posts.append((post_id, user.user_id))
                return post_id
            elif user.posts and self.rng.random() < 0.3:
                # Own post
                return self.rng.choice(user.posts)
            elif self.all_posts:
                # Someone else's post
                return self.rng.choice(self.all_posts)[0]
            else:
                return f"post_{uuid.uuid4().hex[:16]}"

        elif obj_type == "story":
            if action.is_write and action.action == "create_story":
                story_id = f"story_{uuid.uuid4().hex[:16]}"
                user.stories.append(story_id)
                self.all_stories.append((story_id, user.user_id))
                return story_id
            elif self.all_stories:
                return self.rng.choice(self.all_stories)[0]
            else:
                return f"story_{uuid.uuid4().hex[:16]}"

        elif obj_type == "media":
            return f"media_{uuid.uuid4().hex[:16]}"

        elif obj_type == "comment":
            return f"comment_{uuid.uuid4().hex[:16]}"

        elif obj_type == "conversation":
            if not user.conversations:
                conv_id = f"conv_{uuid.uuid4().hex[:12]}"
                user.conversations.append(conv_id)
                return conv_id
            return self.rng.choice(user.conversations)

        elif obj_type == "group":
            if action.action == "create_group" or not user.groups:
                group_id = f"group_{uuid.uuid4().hex[:12]}"
                user.groups.append(group_id)
                return group_id
            return self.rng.choice(user.groups)

        elif obj_type == "message":
            return f"msg_{uuid.uuid4().hex[:16]}"

        elif obj_type == "notification":
            return f"notif_{uuid.uuid4().hex[:16]}"

        elif obj_type == "stream":
            if action.action == "start_stream":
                stream_id = f"stream_{uuid.uuid4().hex[:12]}"
                self.all_streams.append((stream_id, user.user_id))
                return stream_id
            elif self.all_streams:
                return self.rng.choice(self.all_streams)[0]
            else:
                return f"stream_{uuid.uuid4().hex[:12]}"

        elif obj_type == "hashtag":
            return self.rng.choice(self.all_hashtags)

        elif obj_type == "campaign":
            return f"campaign_{uuid.uuid4().hex[:12]}"

        elif obj_type == "audience":
            return f"audience_{uuid.uuid4().hex[:12]}"

        elif obj_type == "content":
            return f"content_{uuid.uuid4().hex[:16]}"

        elif obj_type == "product":
            return f"product_{uuid.uuid4().hex[:12]}"

        elif obj_type == "vod":
            return f"vod_{uuid.uuid4().hex[:12]}"

        elif obj_type == "report":
            return f"report_{uuid.uuid4().hex[:12]}"

        return f"{obj_type}_{uuid.uuid4().hex[:12]}"

    def generate_target_user(self, action: ServiceAction, user: User) -> Optional[str]:
        """Generate a target user ID if the action involves another user"""
        if not action.has_target_user:
            return None

        # Prefer users in social graph
        if user.following and self.rng.random() < 0.6:
            return self.rng.choice(user.following)
        elif user.followers and self.rng.random() < 0.3:
            return self.rng.choice(user.followers)
        else:
            # Random user
            other = self.rng.choice(self.users)
            while other.user_id == user.user_id:
                other = self.rng.choice(self.users)
            return other.user_id

    def generate_metrics(self, action: ServiceAction, user: User,
                         timestamp: datetime, success: bool, release_id: str) -> List[MetricEntry]:
        """Generate performance metrics for an event"""
        metrics = []
        epoch_ts = timestamp.timestamp()

        # Build base tags dict - all metadata goes here
        # Note: request_id, user_id, object_id excluded due to high cardinality
        base_tags = {
            "service": action.service,
            "stack": action.stack,
            "action": action.action,
            "success": "true" if success else "false",
            "is_write": "true" if action.is_write else "false",
            "persona": user.persona.name,
            "release_id": release_id,
        }

        # Add optional tags only if they have values
        if action.object_type:
            base_tags["object_type"] = action.object_type

        # Response time
        latency = max(1.0, self.rng.gauss(
            action.base_latency_ms * user.persona.latency_multiplier,
            action.latency_stddev_ms
        ))
        if not success:
            # Errors often have different latency patterns
            if self.rng.random() < 0.5:
                latency *= 0.3  # Fast fail
            else:
                latency *= 3  # Timeout

        metrics.append(MetricEntry(
            metric="request_duration_ms",
            ts=epoch_ts,
            value=round(latency, 2),
            tags=dict(base_tags),
        ))

        # Request payload size
        request_size = max(64, int(self.rng.gauss(
            action.base_payload_bytes * 0.1,  # Request is typically smaller
            action.payload_stddev_bytes * 0.1
        )))
        metrics.append(MetricEntry(
            metric="request_size_bytes",
            ts=epoch_ts,
            value=float(request_size),
            tags=dict(base_tags),
        ))

        # Response payload size
        if success:
            response_size = max(64, int(self.rng.gauss(
                action.base_payload_bytes,
                action.payload_stddev_bytes
            )))
        else:
            response_size = self.rng.randint(128, 512)  # Error responses are small

        metrics.append(MetricEntry(
            metric="response_size_bytes",
            ts=epoch_ts,
            value=float(response_size),
            tags=dict(base_tags),
        ))

        # Database query count (for reads/writes)
        if success:
            db_queries = self.rng.randint(1, 5) if not action.is_write else self.rng.randint(1, 3)
        else:
            db_queries = self.rng.randint(0, 2)

        metrics.append(MetricEntry(
            metric="db_query_count",
            ts=epoch_ts,
            value=float(db_queries),
            tags=dict(base_tags),
        ))

        # Cache hit/miss (for reads)
        if not action.is_write and success:
            cache_hit = 1.0 if self.rng.random() < 0.7 else 0.0
            metrics.append(MetricEntry(
                metric="cache_hit",
                ts=epoch_ts,
                value=cache_hit,
                tags=dict(base_tags),
            ))

        return metrics

    def generate_log(self, action: ServiceAction, user: User,
                     timestamp: datetime, request_id: str, success: bool,
                     target_user_id: Optional[str], object_id: Optional[str],
                     release_id: str) -> LogEntry:
        """Generate a log entry for an event"""
        ts_str = timestamp.isoformat() + "Z"

        error_code = None
        error_message = None

        if success:
            if action.is_write:
                message = f"{action.action} completed successfully"
            else:
                message = f"{action.action} returned data"
        else:
            # Determine error type
            if self.rng.random() < 0.7:
                error_code = self.rng.choice(self.error_codes["client"])
            else:
                error_code = self.rng.choice(self.error_codes["server"])
            error_message = self.error_messages[error_code]
            message = f"{action.action} failed: {error_message}"

        return LogEntry(
            timestamp=ts_str,
            level="INFO",
            service=action.service,
            stack=action.stack,
            action=action.action,
            user_id=user.user_id,
            request_id=request_id,
            success=success,
            message=message,
            release_id=release_id,
            target_user_id=target_user_id,
            object_type=action.object_type,
            object_id=object_id,
            error_code=error_code,
            error_message=error_message,
        )

    def generate_events(self):
        """Generate all events"""
        print(f"Generating {self.total_events} events...")

        # Calculate events per user based on persona activity
        total_activity = sum(u.persona.activity_multiplier for u in self.users)
        events_per_activity_unit = self.total_events / total_activity

        # Assign event counts to users
        user_event_counts = []
        for user in self.users:
            count = int(events_per_activity_unit * user.persona.activity_multiplier)
            count = max(1, count + self.rng.randint(-count // 10, count // 10))
            user_event_counts.append((user, count))

        # Adjust to match total
        total_assigned = sum(c for _, c in user_event_counts)
        if total_assigned < self.total_events:
            diff = self.total_events - total_assigned
            for i in range(diff):
                idx = i % len(user_event_counts)
                user, count = user_event_counts[idx]
                user_event_counts[idx] = (user, count + 1)

        # Generate events
        all_events = []

        for user, count in user_event_counts:
            for _ in range(count):
                action = self.select_action_for_user(user)
                timestamp = self.generate_timestamp(user)
                request_id = uuid.uuid4().hex

                # Determine success/failure
                success = self.rng.random() < user.persona.success_rate

                # Generate contextual IDs
                object_id = self.generate_object_id(action, user)
                target_user_id = self.generate_target_user(action, user)

                # Select release for this request
                release_id = self.select_release(action, timestamp)

                all_events.append({
                    "user": user,
                    "action": action,
                    "timestamp": timestamp,
                    "request_id": request_id,
                    "success": success,
                    "object_id": object_id,
                    "target_user_id": target_user_id,
                    "release_id": release_id,
                })

        # Sort by timestamp
        print("  Sorting events by timestamp...")
        all_events.sort(key=lambda e: e["timestamp"])

        return all_events

    def write_output(self, events: List[dict], base_dir: Path):
        """Write logs and metrics to files"""
        base_dir.mkdir(parents=True, exist_ok=True)

        logs_file = base_dir / "logs.jsonl"
        metrics_file = base_dir / "metrics.jsonl"

        print(f"Writing output to {base_dir}...")
        print(f"  Logs: {logs_file}")
        print(f"  Metrics: {metrics_file}")

        log_count = 0
        metric_count = 0

        with open(logs_file, 'w', encoding='utf-8') as log_f, \
             open(metrics_file, 'w', encoding='utf-8') as metric_f:

            for i, event in enumerate(events):
                if i % 100000 == 0:
                    print(f"  Processing event {i}/{len(events)}...")

                # Generate log entry
                log_entry = self.generate_log(
                    event["action"], event["user"], event["timestamp"],
                    event["request_id"], event["success"],
                    event["target_user_id"], event["object_id"],
                    event["release_id"]
                )
                log_f.write(json.dumps(asdict(log_entry)) + "\n")
                log_count += 1

                # Generate metrics
                metrics = self.generate_metrics(
                    event["action"], event["user"], event["timestamp"],
                    event["success"], event["release_id"]
                )
                for metric in metrics:
                    metric_f.write(json.dumps(metric.to_dict()) + "\n")
                    metric_count += 1

        print(f"  Wrote {log_count} log entries")
        print(f"  Wrote {metric_count} metric entries")

        # Write summary
        summary_file = base_dir / "summary.json"
        summary = {
            "total_events": len(events),
            "total_users": len(self.users),
            "total_logs": log_count,
            "total_metrics": metric_count,
            "time_range": {
                "start": self.start_time.isoformat(),
                "end": self.end_time.isoformat(),
            },
            "personas": {p.name: sum(1 for u in self.users if u.persona.name == p.name) for p in PERSONAS},
            "actions_by_service": {},
        }

        # Count actions by service
        for event in events:
            service = event["action"].service
            if service not in summary["actions_by_service"]:
                summary["actions_by_service"][service] = 0
            summary["actions_by_service"][service] += 1

        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"  Wrote summary to {summary_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic monitoring data for social network"
    )
    parser.add_argument("total_events", type=int, help="Total number of events to generate")
    parser.add_argument("total_users", type=int, help="Total number of users")
    parser.add_argument("--output", "-o", type=str, default="fixtures/test_data",
                        help="Output directory (default: fixtures/test_data)")
    parser.add_argument("--seed", "-s", type=int, default=42,
                        help="Random seed for reproducibility (default: 42)")

    args = parser.parse_args()

    print("=" * 70)
    print("Social Network Monitoring Data Generator")
    print("=" * 70)
    print(f"Total events: {args.total_events:,}")
    print(f"Total users: {args.total_users:,}")
    print(f"Output directory: {args.output}")
    print(f"Random seed: {args.seed}")
    print("=" * 70)

    generator = MonitoringDataGenerator(
        total_events=args.total_events,
        total_users=args.total_users,
        seed=args.seed
    )

    generator.generate_users()
    events = generator.generate_events()
    generator.write_output(events, Path(args.output))

    print("=" * 70)
    print("Done!")


if __name__ == "__main__":
    main()