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
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from qairon_ids import validate_id, deployment_id_from_release_id, split_release_id


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
    # OpenTelemetry-style distributed tracing fields
    trace_id: str  # 32 hex chars (128-bit), consistent across a call chain
    span_id: str   # 16 hex chars (64-bit), unique per operation
    parent_span_id: Optional[str] = None  # 16 hex chars, links to parent (null for root spans)
    # Optional fields
    target_user_id: Optional[str] = None
    object_type: Optional[str] = None
    object_id: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    # Error source tracking for dependency analysis
    error_source: Optional[str] = None  # deployment_id of the failed upstream, or None for originating errors
    error_type: Optional[str] = None    # "client", "server", "database", "cache", "queue", "internal", "rate_limit"
    upstream_request_id: Optional[str] = None  # Request ID of the failed dependency call


def generate_trace_id(rng: random.Random) -> str:
    """Generate a 32 hex char (128-bit) trace ID (OpenTelemetry format)"""
    return ''.join(rng.choices('0123456789abcdef', k=32))


def generate_span_id(rng: random.Random) -> str:
    """Generate a 16 hex char (64-bit) span ID (OpenTelemetry format)"""
    return ''.join(rng.choices('0123456789abcdef', k=16))


def generate_child_spans_for_event(
    parent_event: dict,
    rng: random.Random,
    select_release_func,
    error_codes: dict,
    error_messages: dict,
) -> List[dict]:
    """
    Generate child span events for a parent event's service dependencies.

    For each dependency in SERVICE_DEPENDENCIES, generates a child span event
    with the same trace_id but a new span_id, linked via parent_span_id.

    Error propagation follows stack trace semantics:
    - A leaf child that fails has error_source=None (it's the originator)
    - A parent that fails because its child failed has error_source=child's deployment_id

    Args:
        parent_event: The root/parent event dict
        rng: Random number generator
        select_release_func: Function to select a release for a service
        error_codes: Dict of error codes by type
        error_messages: Dict of error messages by code

    Returns:
        List of child span event dicts
    """
    service_key = f"{parent_event['action_stack']}:{parent_event['action_service']}"
    dependencies = SERVICE_DEPENDENCIES.get(service_key, [])

    if not dependencies:
        return []

    child_spans = []
    parent_timestamp = parent_event['timestamp']

    # Calculate parent latency for timing child spans
    parent_latency = parent_event['action_base_latency_ms'] * parent_event['latency_multiplier']

    for i, dep_key in enumerate(dependencies):
        dep_stack, dep_service = dep_key.split(':')

        # Child timing: stagger starts, each takes portion of parent time
        child_start_offset_ms = (i + 1) * (parent_latency * 0.05)
        child_duration_ratio = rng.uniform(0.1, 0.3)
        child_latency = max(1.0, parent_latency * child_duration_ratio)

        max_child_end = parent_latency * 0.9
        if child_start_offset_ms + child_latency > max_child_end:
            child_latency = max(1.0, max_child_end - child_start_offset_ms)

        child_timestamp = parent_timestamp + timedelta(milliseconds=child_start_offset_ms)
        child_span_id = generate_span_id(rng)
        child_request_id = uuid.uuid4().hex

        # Select release for this dependency service
        child_release_result = select_release_func(dep_stack, dep_service, child_timestamp)
        child_release_id = child_release_result[0] if isinstance(child_release_result, tuple) else child_release_result

        # Determine if child span has an error
        child_error_info = None
        child_success = True

        # If parent failed due to this dependency (error_source is this child's deployment_id),
        # or randomly based on error rate, the child fails as the originator (error_source=None)
        parent_error_source = (parent_event.get('error_info') or {}).get('error_source', '')
        child_deployment_id = deployment_id_from_release_id(child_release_id)
        parent_blames_child = parent_error_source == child_deployment_id

        if parent_blames_child:
            # Child is the originator — no error_source (leaf of the stack trace)
            error_type = rng.choice(["server"])
            error_code = rng.choice(error_codes.get(error_type, ["500"]))
            child_error_info = {
                "error_source": None,
                "error_type": error_type,
                "error_code": error_code,
                "error_message": error_messages.get(error_code, "Unknown error"),
            }
            child_success = False

        child_event = {
            "user_id": parent_event["user_id"],
            "persona_name": parent_event["persona_name"],
            "action_service": dep_service,
            "action_stack": dep_stack,
            "action_action": f"handle_{parent_event['action_action']}",
            "action_category": "internal",
            "action_base_latency_ms": child_latency,
            "action_latency_stddev_ms": child_latency * 0.1,
            "action_base_payload_bytes": 1024,
            "action_payload_stddev_bytes": 256,
            "action_has_target_user": False,
            "action_has_object_id": parent_event.get("action_has_object_id", False),
            "action_object_type": parent_event.get("action_object_type"),
            "action_is_write": parent_event.get("action_is_write", False),
            "latency_multiplier": 1.0,
            "timestamp": child_timestamp,
            "request_id": child_request_id,
            "trace_id": parent_event["trace_id"],
            "span_id": child_span_id,
            "parent_span_id": parent_event["span_id"],
            "success": child_success,
            "error_info": child_error_info,
            "object_id": parent_event.get("object_id"),
            "target_user_id": None,
            "release_id": child_release_id,
            "is_child_span": True,
        }

        child_spans.append(child_event)

    return child_spans


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
class ServiceIncident:
    """A time window when a service is degraded, causing elevated error rates.

    Incidents target real services from SERVICE_DEPENDENCIES. During an incident,
    the service has an elevated failure rate, and any parent that calls it sees
    errors with error_source = the failed child's deployment_id.
    """
    service_key: str        # "stack:service" — the affected service
    start_time: datetime
    end_time: datetime
    failure_rate: float     # probability of failure per request during incident
    error_codes: List[str]  # e.g. ["500", "503"]
    error_type: str         # "server", "database", "cache", etc.
    error_message: str      # human-readable description


# Services that can have incidents — these are the dependency targets from
# SERVICE_DEPENDENCIES (services that other services call). When these fail,
# failures cascade to their callers via the trace/span tree.
INCIDENT_ELIGIBLE_SERVICES: Dict[str, Dict] = {}
_seen = set()
for _deps in SERVICE_DEPENDENCIES.values():
    for _dep in _deps:
        if _dep not in _seen:
            _seen.add(_dep)
            _stack, _svc = _dep.split(':')
            # Assign plausible error characteristics based on service type
            if _svc in ('posts', 'media', 'comments', 'reactions', 'shares', 'stories', 'hashtags'):
                cfg = {"failure_rate": 0.002, "error_type": "server", "error_codes": ["500", "503"], "error_message": f"{_svc} service degraded"}
            elif _svc in ('connections', 'blocks', 'suggestions', 'contacts'):
                cfg = {"failure_rate": 0.003, "error_type": "database", "error_codes": ["503", "504"], "error_message": f"{_svc} query timeout"}
            elif _svc in ('timeline', 'ranking', 'fanout', 'aggregation'):
                cfg = {"failure_rate": 0.002, "error_type": "cache", "error_codes": ["503"], "error_message": f"{_svc} cache unavailable"}
            elif _svc in ('realtime', 'presence', 'dm', 'groups'):
                cfg = {"failure_rate": 0.002, "error_type": "cache", "error_codes": ["503"], "error_message": f"{_svc} connection pool exhausted"}
            elif _svc in ('processor', 'wallet', 'bidding', 'targeting'):
                cfg = {"failure_rate": 0.001, "error_type": "server", "error_codes": ["500", "502"], "error_message": f"{_svc} upstream timeout"}
            elif _svc in ('indexer',):
                cfg = {"failure_rate": 0.002, "error_type": "search", "error_codes": ["503", "504"], "error_message": f"{_svc} cluster unavailable"}
            elif _svc in ('preferences',):
                cfg = {"failure_rate": 0.001, "error_type": "database", "error_codes": ["503"], "error_message": f"{_svc} read timeout"}
            else:
                cfg = {"failure_rate": 0.002, "error_type": "server", "error_codes": ["500", "503"], "error_message": f"{_svc} internal error"}
            INCIDENT_ELIGIBLE_SERVICES[_dep] = cfg
del _seen, _deps, _dep, _stack, _svc, cfg


@dataclass
class DeploymentWindow:
    """Represents a time window during which a service is being deployed (rolling restart)."""
    deployment_id: str
    release_id: str
    stack: str
    service: str
    env: str
    region: str
    start_time: datetime
    end_time: datetime
    throughput_factor: float    # 0.70-0.85 (15-30% req/sec reduction)
    error_rate_boost: float     # 0.02-0.05 (2-5% extra errors)
    latency_multiplier: float   # 1.2-1.5 (20-50% latency increase)


class DeploymentSchedule:
    """Manages deployment windows and release timelines from generate_fixtures.py output.

    Provides:
    - Active release lookup by (env, region, stack, service, timestamp)
    - Active deployment window lookup for dip effects
    - Deployment log events (start/complete)
    - Serialization for parallel worker transport
    """

    def __init__(self, schedule_path: str, start_time: datetime, end_time: datetime, rng=None):
        with open(schedule_path) as f:
            data = json.load(f)

        self.primary_targets = data.get("primary_deployment_targets", [])
        self.stack_region_groups = data.get("stack_region_groups", {})

        # Build per-(env, region, stack, service) sorted release timelines
        # Each entry: (created_at_datetime, release_id, build_num)
        self._release_timelines: Dict[Tuple[str, str, str, str], List[Tuple[datetime, str, int]]] = {}
        # Deployment windows keyed by (stack, service, env, region)
        self._deployment_windows: Dict[Tuple[str, str, str, str], List[DeploymentWindow]] = {}

        if rng is None:
            rng = random.Random(42)

        self._build_timelines(data)
        self._build_deployment_windows(data, rng, start_time, end_time)

    def _parse_deployment_id(self, deployment_id: str) -> Optional[Dict]:
        """Parse a deployment_id into its components.

        Format: env:provider:account:region:partition:target_type:target:app:stack:service:tag
        """
        parts = deployment_id.split(':')
        if len(parts) < 11:
            return None
        return {
            "env": parts[0],
            "provider": parts[1],
            "account": parts[2],
            "region": parts[3],
            "partition": parts[4],
            "target_type": parts[5],
            "target": parts[6],
            "app": parts[7],
            "stack": parts[8],
            "service": parts[9],
            "tag": parts[10],
            "target_id": ':'.join(parts[:7]),
        }

    def _build_timelines(self, data: Dict):
        """Build sorted release timelines per (env, region, stack, service)."""
        for deployment_id, dep_data in data.get("deployments", {}).items():
            parsed = self._parse_deployment_id(deployment_id)
            if not parsed:
                continue

            key = (parsed["env"], parsed["region"], parsed["stack"], parsed["service"])
            if key not in self._release_timelines:
                self._release_timelines[key] = []

            for rel in dep_data.get("releases", []):
                created_at = datetime.fromisoformat(rel["created_at"])
                self._release_timelines[key].append(
                    (created_at, rel["release_id"], rel["build_num"])
                )

        # Sort each timeline by created_at
        for key in self._release_timelines:
            self._release_timelines[key].sort(key=lambda x: x[0])

    def _build_deployment_windows(self, data: Dict, rng, start_time: datetime, end_time: datetime):
        """Build deployment windows with multi-region stagger per stack."""
        stack_region_groups = data.get("stack_region_groups", {})

        # Collect all releases grouped by (stack, service, env) with their target_ids
        # Key: (stack, service, env) -> {target_id -> [(release_id, created_at, build_num)]}
        releases_by_stack_service_env: Dict[Tuple[str, str, str], Dict[str, List]] = {}

        for deployment_id, dep_data in data.get("deployments", {}).items():
            parsed = self._parse_deployment_id(deployment_id)
            if not parsed or parsed["target_id"] not in self.primary_targets:
                continue

            group_key = (parsed["stack"], parsed["service"], parsed["env"])
            if group_key not in releases_by_stack_service_env:
                releases_by_stack_service_env[group_key] = {}

            target_id = parsed["target_id"]
            if target_id not in releases_by_stack_service_env[group_key]:
                releases_by_stack_service_env[group_key][target_id] = []

            for rel in dep_data.get("releases", []):
                created_at = datetime.fromisoformat(rel["created_at"])
                if start_time <= created_at <= end_time:
                    releases_by_stack_service_env[group_key][target_id].append(
                        (rel["release_id"], created_at, rel["build_num"])
                    )

        # Determine region order per stack+env from stack_region_groups
        stack_env_region_order: Dict[Tuple[str, str], List[str]] = {}
        for stack_id, envs in stack_region_groups.items():
            for env, targets in envs.items():
                stack_env_region_order[(stack_id, env)] = sorted(targets)

        # Build windows for each (stack, service, env)
        for (stack, service, env), targets_releases in releases_by_stack_service_env.items():
            stack_id = f"{data.get('deployments', {})}"  # We need the app prefix
            # Find the app from one of the deployment IDs
            app = None
            for deployment_id in data.get("deployments", {}):
                parsed = self._parse_deployment_id(deployment_id)
                if parsed and parsed["stack"] == stack:
                    app = parsed["app"]
                    break
            if not app:
                continue
            full_stack_id = f"{app}:{stack}"

            # Get region deployment order for this stack+env
            region_order = stack_env_region_order.get((full_stack_id, env), sorted(targets_releases.keys()))

            # Collect unique build_nums across all targets for this service
            # Use earliest created_at per build_num as the "release time"
            build_num_times: Dict[int, datetime] = {}
            build_num_release_ids: Dict[int, Dict[str, str]] = {}  # build_num -> {target_id -> release_id}

            for target_id, releases in targets_releases.items():
                for release_id, created_at, build_num in releases:
                    if build_num not in build_num_times or created_at < build_num_times[build_num]:
                        build_num_times[build_num] = created_at
                    if build_num not in build_num_release_ids:
                        build_num_release_ids[build_num] = {}
                    build_num_release_ids[build_num][target_id] = release_id

            # For each build_num, create staggered deployment windows across regions
            for build_num in sorted(build_num_times.keys()):
                base_created_at = build_num_times[build_num]
                # CI/CD pipeline delay: 3-10 minutes
                cicd_delay = timedelta(minutes=rng.uniform(3, 10))

                for region_idx, target_id in enumerate(region_order):
                    release_id = build_num_release_ids.get(build_num, {}).get(target_id)
                    if not release_id:
                        continue

                    # Extract region from target_id
                    target_parts = target_id.split(':')
                    region = target_parts[3] if len(target_parts) > 3 else ""

                    # Multi-region stagger: first region deploys after CI/CD delay,
                    # subsequent regions wait 30-60min after previous
                    if region_idx == 0:
                        deploy_start = base_created_at + cicd_delay
                    else:
                        stagger = timedelta(minutes=rng.uniform(30, 60))
                        deploy_start = base_created_at + cicd_delay + (stagger * region_idx)

                    # Rolling restart duration: 5-15 minutes
                    deploy_duration = timedelta(minutes=rng.uniform(5, 15))
                    deploy_end = deploy_start + deploy_duration

                    window = DeploymentWindow(
                        deployment_id=':'.join(release_id.rsplit(':', 1)[0:1]),  # strip build_num
                        release_id=release_id,
                        stack=stack,
                        service=service,
                        env=env,
                        region=region,
                        start_time=deploy_start,
                        end_time=deploy_end,
                        throughput_factor=rng.uniform(0.70, 0.85),
                        error_rate_boost=rng.uniform(0.02, 0.05),
                        latency_multiplier=rng.uniform(1.2, 1.5),
                    )

                    win_key = (stack, service, env, region)
                    if win_key not in self._deployment_windows:
                        self._deployment_windows[win_key] = []
                    self._deployment_windows[win_key].append(window)

        # Sort windows by start_time for each key
        for key in self._deployment_windows:
            self._deployment_windows[key].sort(key=lambda w: w.start_time)

    def get_active_release_id(self, env: str, region: str, stack: str, service: str,
                               timestamp: datetime) -> Optional[str]:
        """Binary search to find which release was active at a given timestamp.

        Returns the release_id of the most recent release created before timestamp,
        or None if no releases exist for this combination.
        """
        key = (env, region, stack, service)
        timeline = self._release_timelines.get(key)
        if not timeline:
            return None

        # Binary search for the latest release before timestamp
        lo, hi = 0, len(timeline) - 1
        result = None
        while lo <= hi:
            mid = (lo + hi) // 2
            if timeline[mid][0] <= timestamp:
                result = timeline[mid]
                lo = mid + 1
            else:
                hi = mid - 1

        return result[1] if result else None

    def get_active_deployment_window(self, stack: str, service: str, env: str, region: str,
                                      timestamp: datetime) -> Optional[DeploymentWindow]:
        """Check if timestamp falls within a deployment window for this service."""
        key = (stack, service, env, region)
        windows = self._deployment_windows.get(key)
        if not windows:
            return None

        # Binary search for candidate window
        lo, hi = 0, len(windows) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if windows[mid].end_time < timestamp:
                lo = mid + 1
            elif windows[mid].start_time > timestamp:
                hi = mid - 1
            else:
                return windows[mid]
        return None

    def get_deployment_log_events(self) -> List[Dict]:
        """Returns list of deployment_start/deployment_complete log entries."""
        events = []
        for windows in self._deployment_windows.values():
            for window in windows:
                deploy_request_id = f"deploy_{uuid.uuid4().hex[:16]}"
                base = {
                    "service": window.service,
                    "stack": window.stack,
                    "user_id": "system",
                    "success": True,
                    "release_id": window.release_id,
                    "object_type": "deployment",
                    "object_id": window.deployment_id,
                    "persona_name": "system",
                }
                events.append({
                    **base,
                    "timestamp": window.start_time,
                    "action": "deployment_start",
                    "request_id": deploy_request_id,
                    "message": f"Deployment started: rolling restart for release {window.release_id}",
                    "trace_id": ''.join(random.choices('0123456789abcdef', k=32)),
                    "span_id": ''.join(random.choices('0123456789abcdef', k=16)),
                })
                events.append({
                    **base,
                    "timestamp": window.end_time,
                    "action": "deployment_complete",
                    "request_id": deploy_request_id,
                    "message": f"Deployment complete: release {window.release_id} fully rolled out",
                    "trace_id": ''.join(random.choices('0123456789abcdef', k=32)),
                    "span_id": ''.join(random.choices('0123456789abcdef', k=16)),
                })
        events.sort(key=lambda e: e["timestamp"])
        return events

    def to_serializable(self) -> Dict:
        """Serialize for passing to parallel workers via ProcessPoolExecutor."""
        timelines = {}
        for key, timeline in self._release_timelines.items():
            str_key = '|'.join(key)
            timelines[str_key] = [
                (created_at.isoformat(), release_id, build_num)
                for created_at, release_id, build_num in timeline
            ]

        windows = {}
        for key, win_list in self._deployment_windows.items():
            str_key = '|'.join(key)
            windows[str_key] = [
                {
                    "deployment_id": w.deployment_id,
                    "release_id": w.release_id,
                    "stack": w.stack,
                    "service": w.service,
                    "env": w.env,
                    "region": w.region,
                    "start_time": w.start_time.isoformat(),
                    "end_time": w.end_time.isoformat(),
                    "throughput_factor": w.throughput_factor,
                    "error_rate_boost": w.error_rate_boost,
                    "latency_multiplier": w.latency_multiplier,
                }
                for w in win_list
            ]

        return {"timelines": timelines, "windows": windows}

    @classmethod
    def from_serializable(cls, data: Dict) -> 'DeploymentSchedule':
        """Reconstruct from serialized form in worker process."""
        obj = cls.__new__(cls)
        obj.primary_targets = []
        obj.stack_region_groups = {}

        obj._release_timelines = {}
        for str_key, timeline in data.get("timelines", {}).items():
            key = tuple(str_key.split('|'))
            obj._release_timelines[key] = [
                (datetime.fromisoformat(created_at), release_id, build_num)
                for created_at, release_id, build_num in timeline
            ]

        obj._deployment_windows = {}
        for str_key, win_list in data.get("windows", {}).items():
            key = tuple(str_key.split('|'))
            obj._deployment_windows[key] = [
                DeploymentWindow(
                    deployment_id=w["deployment_id"],
                    release_id=w["release_id"],
                    stack=w["stack"],
                    service=w["service"],
                    env=w["env"],
                    region=w["region"],
                    start_time=datetime.fromisoformat(w["start_time"]),
                    end_time=datetime.fromisoformat(w["end_time"]),
                    throughput_factor=w["throughput_factor"],
                    error_rate_boost=w["error_rate_boost"],
                    latency_multiplier=w["latency_multiplier"],
                )
                for w in win_list
            ]

        return obj


# =============================================================================
# PARALLEL EVENT GENERATION WORKER
# =============================================================================

def _deployment_event_to_log_json(event: dict) -> str:
    """Convert a deployment event dict to a log JSON line."""
    ts_str = event["timestamp"].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    log_entry = {
        "timestamp": ts_str,
        "level": "INFO",
        "service": event["service"],
        "stack": event["stack"],
        "action": event["action"],
        "user_id": event["user_id"],
        "request_id": event["request_id"],
        "success": event["success"],
        "message": event["message"],
        "release_id": event["release_id"],
        "trace_id": event.get("trace_id", ""),
        "span_id": event.get("span_id", ""),
        "parent_span_id": None,
        "target_user_id": None,
        "object_type": event.get("object_type"),
        "object_id": event.get("object_id"),
        "error_code": None,
        "error_message": None,
        "error_source": None,
        "error_type": None,
        "upstream_request_id": None,
    }
    return json.dumps(log_entry)


def _generate_events_for_chunk_streaming(args: Tuple) -> Tuple[int, str, str]:
    """
    Worker function for parallel event generation - STREAMING VERSION.
    Writes events directly to temp files to avoid memory issues.

    Args is a tuple containing:
    - worker_id: int
    - user_chunk: List of (user_dict, event_count) pairs
    - start_time: datetime
    - end_time: datetime
    - base_seed: int
    - error_codes: dict
    - error_messages: dict
    - output_dir: str (temp directory for worker output)
    - deployment_schedule_data: dict or None (serialized DeploymentSchedule)

    Returns:
    - (event_count, logs_file_path, metrics_file_path)
    """
    (worker_id, user_chunk, start_time, end_time,
     base_seed, error_codes, error_messages, output_dir, deployment_schedule_data,
     incidents_data) = args

    # Create worker-local RNG with deterministic seed
    rng = random.Random(base_seed + worker_id * 1000000)

    # Reconstruct incidents from serializable form
    incidents = [
        ServiceIncident(
            service_key=inc["service_key"],
            start_time=datetime.fromisoformat(inc["start_time"]),
            end_time=datetime.fromisoformat(inc["end_time"]),
            failure_rate=inc["failure_rate"],
            error_codes=inc["error_codes"],
            error_type=inc["error_type"],
            error_message=inc["error_message"],
        )
        for inc in incidents_data
    ]

    # Reconstruct deployment schedule if provided
    deploy_schedule = None
    if deployment_schedule_data:
        deploy_schedule = DeploymentSchedule.from_serializable(deployment_schedule_data)

    # Worker-local content pools
    all_posts = []
    all_stories = []
    all_streams = []
    all_hashtags = [f"#{word}" for word in [
        "trending", "viral", "fyp", "lifestyle", "travel", "food", "fitness",
        "tech", "gaming", "music", "art", "fashion", "beauty", "sports",
        "news", "memes", "photography", "nature", "pets", "diy", "cooking"
    ]]

    # Helper functions
    def get_active_incident(service_key: str, timestamp: datetime) -> Optional[ServiceIncident]:
        for incident in incidents:
            if incident.start_time <= timestamp <= incident.end_time:
                if incident.service_key == service_key:
                    return incident
        return None

    def determine_error(action, user_data, timestamp, env=None, region=None) -> Optional[Dict]:
        service_key = f"{action.stack}:{action.service}"

        # 1. Service incident: check if any dependency has an active incident
        deps = SERVICE_DEPENDENCIES.get(service_key, [])
        for dep_key in deps:
            incident = get_active_incident(dep_key, timestamp)
            if incident and rng.random() < incident.failure_rate:
                dep_stack, dep_service = dep_key.split(':')
                dep_release_result = select_release_by_key(dep_stack, dep_service, timestamp)
                dep_release_id = dep_release_result[0] if isinstance(dep_release_result, tuple) else dep_release_result
                dep_deployment_id = deployment_id_from_release_id(dep_release_id)
                return {
                    "error_source": dep_deployment_id,
                    "error_type": incident.error_type,
                    "error_code": rng.choice(incident.error_codes),
                    "error_message": f"Upstream {dep_key} failed: {incident.error_message}",
                    "upstream_request_id": uuid.uuid4().hex,
                }

        # Also check if this service itself has an incident (originating error)
        incident = get_active_incident(service_key, timestamp)
        if incident and rng.random() < incident.failure_rate:
            return {
                "error_source": None,
                "error_type": incident.error_type,
                "error_code": rng.choice(incident.error_codes),
                "error_message": incident.error_message,
                "upstream_request_id": None,
            }

        # 2. Deployment dip errors
        if deploy_schedule and env and region:
            window = deploy_schedule.get_active_deployment_window(
                action.stack, action.service, env, region, timestamp
            )
            if window and rng.random() < window.error_rate_boost:
                return {
                    "error_source": deployment_id_from_release_id(window.release_id),
                    "error_type": "server",
                    "error_code": rng.choice(["500", "502", "503"]),
                    "error_message": f"Service restarting during deployment of {window.release_id}",
                    "upstream_request_id": None,
                }

        if rng.random() > user_data["success_rate"]:
            # 2. Dependency failure: blame a child's deployment_id
            service_key = f"{action.stack}:{action.service}"
            deps = SERVICE_DEPENDENCIES.get(service_key, [])
            if deps and rng.random() < 0.4:
                dep_key = rng.choice(deps)
                dep_stack, dep_service = dep_key.split(':')
                dep_release_result = select_release_by_key(dep_stack, dep_service, timestamp)
                dep_release_id = dep_release_result[0] if isinstance(dep_release_result, tuple) else dep_release_result
                dep_deployment_id = deployment_id_from_release_id(dep_release_id)
                return {
                    "error_source": dep_deployment_id,
                    "error_type": "server",
                    "error_code": rng.choice(error_codes["server"]),
                    "error_message": f"Upstream {dep_key} failed",
                    "upstream_request_id": uuid.uuid4().hex,
                }

            # 3. Originating error (no upstream to blame)
            if rng.random() < 0.7:
                error_code = rng.choice(error_codes["client"])
                error_type = "client"
            else:
                error_code = rng.choice(error_codes["server"])
                error_type = "server"
            return {
                "error_source": None,
                "error_type": error_type,
                "error_code": error_code,
                "error_message": error_messages[error_code],
                "upstream_request_id": None,
            }
        return None

    def select_action_for_user(user_data) -> 'ServiceAction':
        action_weights = user_data["action_weights"]
        categories = list(action_weights.keys())
        weights = [action_weights.get(c, 0) for c in categories]
        valid = [(c, w) for c, w in zip(categories, weights) if c in ACTIONS_BY_CATEGORY and w > 0]
        if not valid:
            valid = [(c, 1.0) for c in ACTIONS_BY_CATEGORY.keys()]
        categories, weights = zip(*valid)
        category = rng.choices(categories, weights=weights)[0]
        actions = ACTIONS_BY_CATEGORY[category]
        action_weights_list = [a.weight for a in actions]
        return rng.choices(actions, weights=action_weights_list)[0]

    def generate_timestamp(user_data) -> datetime:
        hourly_weights = user_data["hourly_weights"]
        daily_weights = user_data["daily_weights"]
        days_ago = rng.randint(0, 364)
        date = end_time - timedelta(days=days_ago)
        dow = date.weekday()
        if rng.random() > daily_weights[dow] * 7:
            preferred_dow = rng.choices(range(7), weights=daily_weights)[0]
            days_diff = preferred_dow - dow
            date = date + timedelta(days=days_diff)
        hour = rng.choices(range(24), weights=hourly_weights)[0]
        minute = rng.randint(0, 59)
        second = rng.randint(0, 59)
        microsecond = rng.randint(0, 999999)
        return date.replace(hour=hour, minute=minute, second=second, microsecond=microsecond)

    def select_release(action, timestamp):
        """Returns (release_id, env, region) tuple."""
        envs = list(ENVIRONMENT_CONFIG.keys())
        weights = [ENVIRONMENT_CONFIG[e]["weight"] for e in envs]
        env = rng.choices(envs, weights=weights)[0]
        regions = ENVIRONMENT_CONFIG[env]["regions"]
        if len(regions) > 1:
            region_weights = [0.6, 0.4] if len(regions) == 2 else [1.0]
            region = rng.choices(regions, weights=region_weights)[0]
        else:
            region = regions[0]

        # Try deployment schedule first
        if deploy_schedule:
            scheduled = deploy_schedule.get_active_release_id(
                env, region, action.stack, action.service, timestamp
            )
            if scheduled:
                return (scheduled, env, region)

        days_into_year = (timestamp - start_time).days
        year_progress = max(0, days_into_year) / 365.0
        base_release = 50 + int(year_progress * 200)
        service_hash = hash(f"{action.stack}:{action.service}") % 50
        release_num = base_release + service_hash
        return (generate_release_id(env, region, action.stack, action.service, release_num), env, region)

    def generate_object_id(action, user_data) -> Optional[str]:
        if not action.has_object_id:
            return None
        obj_type = action.object_type
        if obj_type == "post":
            if action.is_write and action.action == "create_post":
                post_id = f"post_{uuid.uuid4().hex[:16]}"
                all_posts.append((post_id, user_data["user_id"]))
                return post_id
            elif all_posts:
                return rng.choice(all_posts)[0]
            return f"post_{uuid.uuid4().hex[:16]}"
        elif obj_type == "story":
            if action.is_write and action.action == "create_story":
                story_id = f"story_{uuid.uuid4().hex[:16]}"
                all_stories.append((story_id, user_data["user_id"]))
                return story_id
            elif all_stories:
                return rng.choice(all_stories)[0]
            return f"story_{uuid.uuid4().hex[:16]}"
        elif obj_type == "stream":
            if action.action == "start_stream":
                stream_id = f"stream_{uuid.uuid4().hex[:12]}"
                all_streams.append((stream_id, user_data["user_id"]))
                return stream_id
            elif all_streams:
                return rng.choice(all_streams)[0]
            return f"stream_{uuid.uuid4().hex[:12]}"
        elif obj_type == "hashtag":
            return rng.choice(all_hashtags)
        else:
            return f"{obj_type}_{uuid.uuid4().hex[:12]}"

    def generate_target_user(action, user_data) -> Optional[str]:
        if not action.has_target_user:
            return None
        following = user_data.get("following", [])
        followers = user_data.get("followers", [])
        if following and rng.random() < 0.6:
            return rng.choice(following)
        elif followers and rng.random() < 0.3:
            return rng.choice(followers)
        return f"user_{uuid.uuid4().hex[:12]}"

    def select_release_by_key(stack: str, service: str, timestamp: datetime):
        """Returns (release_id, env, region) tuple."""
        class MinimalAction:
            pass
        action = MinimalAction()
        action.stack = stack
        action.service = service
        return select_release(action, timestamp)

    def event_to_log_json(event: dict) -> str:
        """Convert event to log JSON line"""
        timestamp = event["timestamp"]
        ts_str = timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        success = event["success"]
        action_name = event["action_action"]

        error_code = None
        error_message = None
        error_source = None
        error_type = None
        upstream_request_id = None

        if success:
            message = f"{action_name} completed successfully" if event.get("action_is_write") else f"{action_name} returned data"
            level = "INFO"
        else:
            error_info = event.get("error_info", {})
            if error_info:
                error_code = error_info.get("error_code")
                error_message = error_info.get("error_message")
                error_source = error_info.get("error_source")
                error_type = error_info.get("error_type")
                upstream_request_id = error_info.get("upstream_request_id")
            else:
                error_code = "500"
                error_message = "Unknown error"
                error_type = "server"
                error_source = None
            message = f"{action_name} failed: {error_message}"
            level = "ERROR" if error_type in ("server", "database", "cache", "queue", "internal") else "WARN"

        log_entry = {
            "timestamp": ts_str,
            "level": level,
            "service": event["action_service"],
            "stack": event["action_stack"],
            "action": event["action_action"],
            "user_id": event["user_id"],
            "request_id": event["request_id"],
            "success": success,
            "message": message,
            "release_id": event["release_id"],
            "trace_id": event["trace_id"],
            "span_id": event["span_id"],
            "parent_span_id": event.get("parent_span_id"),
            "target_user_id": event.get("target_user_id"),
            "object_type": event.get("action_object_type"),
            "object_id": event.get("object_id"),
            "error_code": error_code,
            "error_message": error_message,
            "error_source": error_source,
            "error_type": error_type,
            "upstream_request_id": upstream_request_id,
        }
        return json.dumps(log_entry)

    def event_to_metrics_json(event: dict) -> List[str]:
        """Convert event to metric JSON lines"""
        lines = []
        epoch_ts = event["timestamp"].timestamp()
        success = event["success"]

        base_tags = {
            "service": event["action_service"],
            "stack": event["action_stack"],
            "action": event["action_action"],
            "success": "true" if success else "false",
            "is_write": "true" if event.get("action_is_write") else "false",
            "persona": event["persona_name"],
            "release_id": event["release_id"],
        }

        if event.get("action_object_type"):
            base_tags["object_type"] = event["action_object_type"]

        # Latency
        latency = max(1.0, rng.gauss(
            event["action_base_latency_ms"] * event.get("latency_multiplier", 1.0),
            event.get("action_latency_stddev_ms", 10)
        ))
        if not success:
            latency *= 0.3 if rng.random() < 0.5 else 3

        # Error-biased exemplar sampling
        trace_id = event["trace_id"]
        attach_exemplar = (not success or latency > 500 or rng.random() < 0.01)
        tags = dict(base_tags)
        if attach_exemplar:
            tags["trace_id"] = trace_id

        lines.append(json.dumps({"metric": "request_duration_ms", "ts": epoch_ts, "value": round(latency, 2), "tags": tags}))

        # Request size
        request_size = max(64, int(rng.gauss(event.get("action_base_payload_bytes", 1024) * 0.1, event.get("action_payload_stddev_bytes", 100) * 0.1)))
        lines.append(json.dumps({"metric": "request_size_bytes", "ts": epoch_ts, "value": float(request_size), "tags": dict(base_tags)}))

        # Response size
        response_size = max(64, int(rng.gauss(event.get("action_base_payload_bytes", 1024), event.get("action_payload_stddev_bytes", 100)))) if success else rng.randint(128, 512)
        lines.append(json.dumps({"metric": "response_size_bytes", "ts": epoch_ts, "value": float(response_size), "tags": dict(base_tags)}))

        # DB queries
        db_queries = rng.randint(1, 5) if success else rng.randint(0, 2)
        lines.append(json.dumps({"metric": "db_query_count", "ts": epoch_ts, "value": float(db_queries), "tags": dict(base_tags)}))

        # Cache hit (reads only)
        if not event.get("action_is_write") and success:
            cache_hit = 1.0 if rng.random() < 0.7 else 0.0
            lines.append(json.dumps({"metric": "cache_hit", "ts": epoch_ts, "value": cache_hit, "tags": dict(base_tags)}))

        return lines

    # Open output files for this worker
    logs_file = f"{output_dir}/logs_{worker_id}.jsonl"
    metrics_file = f"{output_dir}/metrics_{worker_id}.jsonl"
    event_count = 0

    with open(logs_file, 'w', encoding='utf-8') as log_f, \
         open(metrics_file, 'w', encoding='utf-8') as metric_f:

        # Write deployment log events (worker 0 only)
        if worker_id == 0 and deploy_schedule:
            for dep_event in deploy_schedule.get_deployment_log_events():
                dep_log = _deployment_event_to_log_json(dep_event)
                log_f.write(dep_log + "\n")
                event_count += 1

        for user_data, count in user_chunk:
            for _ in range(count):
                action = select_action_for_user(user_data)
                timestamp = generate_timestamp(user_data)
                request_id = uuid.uuid4().hex
                trace_id = ''.join(rng.choices('0123456789abcdef', k=32))
                span_id = ''.join(rng.choices('0123456789abcdef', k=16))
                object_id = generate_object_id(action, user_data)
                target_user_id = generate_target_user(action, user_data)
                release_id, env, region = select_release(action, timestamp)

                # Throughput dip: skip events during deployment windows
                if deploy_schedule:
                    window = deploy_schedule.get_active_deployment_window(
                        action.stack, action.service, env, region, timestamp
                    )
                    if window and rng.random() > window.throughput_factor:
                        continue

                error_info = determine_error(action, user_data, timestamp, env, region)
                success = error_info is None

                # Deployment latency multiplier
                deployment_latency_mult = 1.0
                if deploy_schedule:
                    window = deploy_schedule.get_active_deployment_window(
                        action.stack, action.service, env, region, timestamp
                    )
                    if window:
                        deployment_latency_mult = window.latency_multiplier

                root_event = {
                    "user_id": user_data["user_id"],
                    "persona_name": user_data["persona_name"],
                    "action_service": action.service,
                    "action_stack": action.stack,
                    "action_action": action.action,
                    "action_category": action.category,
                    "action_base_latency_ms": action.base_latency_ms,
                    "action_latency_stddev_ms": action.latency_stddev_ms,
                    "action_base_payload_bytes": action.base_payload_bytes,
                    "action_payload_stddev_bytes": action.payload_stddev_bytes,
                    "action_has_target_user": action.has_target_user,
                    "action_has_object_id": action.has_object_id,
                    "action_object_type": action.object_type,
                    "action_is_write": action.is_write,
                    "latency_multiplier": user_data["latency_multiplier"] * deployment_latency_mult,
                    "timestamp": timestamp,
                    "request_id": request_id,
                    "trace_id": trace_id,
                    "span_id": span_id,
                    "parent_span_id": None,
                    "success": success,
                    "error_info": error_info,
                    "object_id": object_id,
                    "target_user_id": target_user_id,
                    "release_id": release_id,
                }

                # Write root event
                log_f.write(event_to_log_json(root_event) + "\n")
                for metric_line in event_to_metrics_json(root_event):
                    metric_f.write(metric_line + "\n")
                event_count += 1

                # Generate and write child spans
                child_spans = generate_child_spans_for_event(
                    parent_event=root_event,
                    rng=rng,
                    select_release_func=select_release_by_key,
                    error_codes=error_codes,
                    error_messages=error_messages,
                )
                for child_event in child_spans:
                    log_f.write(event_to_log_json(child_event) + "\n")
                    for metric_line in event_to_metrics_json(child_event):
                        metric_f.write(metric_line + "\n")
                    event_count += 1

    return (event_count, logs_file, metrics_file)


def _generate_events_for_chunk(args: Tuple) -> List[dict]:
    """
    Worker function for parallel event generation.
    Generates events for a chunk of (user_data, event_count) pairs.

    Args is a tuple containing:
    - worker_id: int
    - user_chunk: List of (user_dict, event_count) pairs
    - start_time: datetime
    - end_time: datetime
    - base_seed: int
    - error_codes: dict
    - error_messages: dict
    - deployment_schedule_data: dict or None
    """
    (worker_id, user_chunk, start_time, end_time,
     base_seed, error_codes, error_messages, deployment_schedule_data,
     incidents_data) = args

    # Create worker-local RNG with deterministic seed
    rng = random.Random(base_seed + worker_id * 1000000)

    # Reconstruct incidents from serializable form
    incidents = [
        ServiceIncident(
            service_key=inc["service_key"],
            start_time=datetime.fromisoformat(inc["start_time"]),
            end_time=datetime.fromisoformat(inc["end_time"]),
            failure_rate=inc["failure_rate"],
            error_codes=inc["error_codes"],
            error_type=inc["error_type"],
            error_message=inc["error_message"],
        )
        for inc in incidents_data
    ]

    # Reconstruct deployment schedule if provided
    deploy_schedule = None
    if deployment_schedule_data:
        deploy_schedule = DeploymentSchedule.from_serializable(deployment_schedule_data)

    # Worker-local content pools
    all_posts = []
    all_stories = []
    all_streams = []
    all_hashtags = [f"#{word}" for word in [
        "trending", "viral", "fyp", "lifestyle", "travel", "food", "fitness",
        "tech", "gaming", "music", "art", "fashion", "beauty", "sports",
        "news", "memes", "photography", "nature", "pets", "diy", "cooking"
    ]]

    def get_active_incident(service_key: str, timestamp: datetime) -> Optional[ServiceIncident]:
        for incident in incidents:
            if incident.start_time <= timestamp <= incident.end_time:
                if incident.service_key == service_key:
                    return incident
        return None

    def determine_error(action, user_data, timestamp, env=None, region=None) -> Optional[Dict]:
        service_key = f"{action.stack}:{action.service}"

        # 1. Service incident: check if any dependency has an active incident
        deps = SERVICE_DEPENDENCIES.get(service_key, [])
        for dep_key in deps:
            incident = get_active_incident(dep_key, timestamp)
            if incident and rng.random() < incident.failure_rate:
                dep_stack, dep_service = dep_key.split(':')
                dep_release_result = select_release_by_key(dep_stack, dep_service, timestamp)
                dep_release_id = dep_release_result[0] if isinstance(dep_release_result, tuple) else dep_release_result
                dep_deployment_id = deployment_id_from_release_id(dep_release_id)
                return {
                    "error_source": dep_deployment_id,
                    "error_type": incident.error_type,
                    "error_code": rng.choice(incident.error_codes),
                    "error_message": f"Upstream {dep_key} failed: {incident.error_message}",
                    "upstream_request_id": uuid.uuid4().hex,
                }

        # Also check if this service itself has an incident (originating error)
        incident = get_active_incident(service_key, timestamp)
        if incident and rng.random() < incident.failure_rate:
            return {
                "error_source": None,
                "error_type": incident.error_type,
                "error_code": rng.choice(incident.error_codes),
                "error_message": incident.error_message,
                "upstream_request_id": None,
            }

        # 2. Deployment dip errors
        if deploy_schedule and env and region:
            window = deploy_schedule.get_active_deployment_window(
                action.stack, action.service, env, region, timestamp
            )
            if window and rng.random() < window.error_rate_boost:
                return {
                    "error_source": deployment_id_from_release_id(window.release_id),
                    "error_type": "server",
                    "error_code": rng.choice(["500", "502", "503"]),
                    "error_message": f"Service restarting during deployment of {window.release_id}",
                    "upstream_request_id": None,
                }

        if rng.random() > user_data["success_rate"]:
            # 2. Dependency failure: blame a child's deployment_id
            service_key = f"{action.stack}:{action.service}"
            deps = SERVICE_DEPENDENCIES.get(service_key, [])
            if deps and rng.random() < 0.4:
                dep_key = rng.choice(deps)
                dep_stack, dep_service = dep_key.split(':')
                dep_release_result = select_release_by_key(dep_stack, dep_service, timestamp)
                dep_release_id = dep_release_result[0] if isinstance(dep_release_result, tuple) else dep_release_result
                dep_deployment_id = deployment_id_from_release_id(dep_release_id)
                return {
                    "error_source": dep_deployment_id,
                    "error_type": "server",
                    "error_code": rng.choice(error_codes["server"]),
                    "error_message": f"Upstream {dep_key} failed",
                    "upstream_request_id": uuid.uuid4().hex,
                }

            # 3. Originating error (no upstream to blame)
            if rng.random() < 0.7:
                error_code = rng.choice(error_codes["client"])
                error_type = "client"
            else:
                error_code = rng.choice(error_codes["server"])
                error_type = "server"
            return {
                "error_source": None,
                "error_type": error_type,
                "error_code": error_code,
                "error_message": error_messages[error_code],
                "upstream_request_id": None,
            }
        return None

    def select_action_for_user(user_data) -> 'ServiceAction':
        action_weights = user_data["action_weights"]
        categories = list(action_weights.keys())
        weights = [action_weights.get(c, 0) for c in categories]
        valid = [(c, w) for c, w in zip(categories, weights) if c in ACTIONS_BY_CATEGORY and w > 0]
        if not valid:
            valid = [(c, 1.0) for c in ACTIONS_BY_CATEGORY.keys()]
        categories, weights = zip(*valid)
        category = rng.choices(categories, weights=weights)[0]
        actions = ACTIONS_BY_CATEGORY[category]
        action_weights_list = [a.weight for a in actions]
        return rng.choices(actions, weights=action_weights_list)[0]

    def generate_timestamp(user_data) -> datetime:
        hourly_weights = user_data["hourly_weights"]
        daily_weights = user_data["daily_weights"]
        days_ago = rng.randint(0, 364)
        date = end_time - timedelta(days=days_ago)
        dow = date.weekday()
        if rng.random() > daily_weights[dow] * 7:
            preferred_dow = rng.choices(range(7), weights=daily_weights)[0]
            days_diff = preferred_dow - dow
            date = date + timedelta(days=days_diff)
        hour = rng.choices(range(24), weights=hourly_weights)[0]
        minute = rng.randint(0, 59)
        second = rng.randint(0, 59)
        microsecond = rng.randint(0, 999999)
        return date.replace(hour=hour, minute=minute, second=second, microsecond=microsecond)

    def select_release(action, timestamp):
        """Returns (release_id, env, region) tuple."""
        envs = list(ENVIRONMENT_CONFIG.keys())
        weights = [ENVIRONMENT_CONFIG[e]["weight"] for e in envs]
        env = rng.choices(envs, weights=weights)[0]
        regions = ENVIRONMENT_CONFIG[env]["regions"]
        if len(regions) > 1:
            region_weights = [0.6, 0.4] if len(regions) == 2 else [1.0]
            region = rng.choices(regions, weights=region_weights)[0]
        else:
            region = regions[0]

        if deploy_schedule:
            scheduled = deploy_schedule.get_active_release_id(
                env, region, action.stack, action.service, timestamp
            )
            if scheduled:
                return (scheduled, env, region)

        days_into_year = (timestamp - start_time).days
        year_progress = max(0, days_into_year) / 365.0
        base_release = 50 + int(year_progress * 200)
        service_hash = hash(f"{action.stack}:{action.service}") % 50
        release_num = base_release + service_hash
        return (generate_release_id(env, region, action.stack, action.service, release_num), env, region)

    def generate_object_id(action, user_data) -> Optional[str]:
        if not action.has_object_id:
            return None
        obj_type = action.object_type
        if obj_type == "post":
            if action.is_write and action.action == "create_post":
                post_id = f"post_{uuid.uuid4().hex[:16]}"
                all_posts.append((post_id, user_data["user_id"]))
                return post_id
            elif all_posts:
                return rng.choice(all_posts)[0]
            return f"post_{uuid.uuid4().hex[:16]}"
        elif obj_type == "story":
            if action.is_write and action.action == "create_story":
                story_id = f"story_{uuid.uuid4().hex[:16]}"
                all_stories.append((story_id, user_data["user_id"]))
                return story_id
            elif all_stories:
                return rng.choice(all_stories)[0]
            return f"story_{uuid.uuid4().hex[:16]}"
        elif obj_type == "stream":
            if action.action == "start_stream":
                stream_id = f"stream_{uuid.uuid4().hex[:12]}"
                all_streams.append((stream_id, user_data["user_id"]))
                return stream_id
            elif all_streams:
                return rng.choice(all_streams)[0]
            return f"stream_{uuid.uuid4().hex[:12]}"
        elif obj_type == "hashtag":
            return rng.choice(all_hashtags)
        else:
            return f"{obj_type}_{uuid.uuid4().hex[:12]}"

    def generate_target_user(action, user_data) -> Optional[str]:
        if not action.has_target_user:
            return None
        following = user_data.get("following", [])
        followers = user_data.get("followers", [])
        if following and rng.random() < 0.6:
            return rng.choice(following)
        elif followers and rng.random() < 0.3:
            return rng.choice(followers)
        return f"user_{uuid.uuid4().hex[:12]}"

    def select_release_by_key(stack: str, service: str, timestamp: datetime):
        """Returns (release_id, env, region) tuple."""
        class MinimalAction:
            pass
        action = MinimalAction()
        action.stack = stack
        action.service = service
        return select_release(action, timestamp)

    # Generate events for this chunk
    events = []
    for user_data, count in user_chunk:
        for _ in range(count):
            action = select_action_for_user(user_data)
            timestamp = generate_timestamp(user_data)
            request_id = uuid.uuid4().hex
            # OpenTelemetry tracing - root span
            trace_id = ''.join(rng.choices('0123456789abcdef', k=32))
            span_id = ''.join(rng.choices('0123456789abcdef', k=16))
            object_id = generate_object_id(action, user_data)
            target_user_id = generate_target_user(action, user_data)
            release_id, env, region = select_release(action, timestamp)

            # Throughput dip
            if deploy_schedule:
                window = deploy_schedule.get_active_deployment_window(
                    action.stack, action.service, env, region, timestamp
                )
                if window and rng.random() > window.throughput_factor:
                    continue

            error_info = determine_error(action, user_data, timestamp, env, region)
            success = error_info is None

            # Deployment latency multiplier
            deployment_latency_mult = 1.0
            if deploy_schedule:
                window = deploy_schedule.get_active_deployment_window(
                    action.stack, action.service, env, region, timestamp
                )
                if window:
                    deployment_latency_mult = window.latency_multiplier

            root_event = {
                "user_id": user_data["user_id"],
                "persona_name": user_data["persona_name"],
                "action_service": action.service,
                "action_stack": action.stack,
                "action_action": action.action,
                "action_category": action.category,
                "action_base_latency_ms": action.base_latency_ms,
                "action_latency_stddev_ms": action.latency_stddev_ms,
                "action_base_payload_bytes": action.base_payload_bytes,
                "action_payload_stddev_bytes": action.payload_stddev_bytes,
                "action_has_target_user": action.has_target_user,
                "action_has_object_id": action.has_object_id,
                "action_object_type": action.object_type,
                "action_is_write": action.is_write,
                "latency_multiplier": user_data["latency_multiplier"] * deployment_latency_mult,
                "timestamp": timestamp,
                "request_id": request_id,
                "trace_id": trace_id,
                "span_id": span_id,
                "parent_span_id": None,  # Root span
                "success": success,
                "error_info": error_info,
                "object_id": object_id,
                "target_user_id": target_user_id,
                "release_id": release_id,
            }
            events.append(root_event)

            # Generate child spans for service dependencies
            child_spans = generate_child_spans_for_event(
                parent_event=root_event,
                rng=rng,
                select_release_func=select_release_by_key,
                error_codes=error_codes,
                error_messages=error_messages,
            )
            events.extend(child_spans)

    return events


class MonitoringDataGenerator:
    """Generates synthetic monitoring data"""

    def __init__(self, total_events: int, total_users: int, seed: int = 42, num_workers: int = 1,
                 deployment_schedule_path: str = None):
        self.total_events = total_events
        self.total_users = total_users
        self.seed = seed
        self.num_workers = num_workers
        self.rng = random.Random(seed)

        # Time range: 1 year ending now
        self.end_time = datetime.now()
        self.start_time = self.end_time - timedelta(days=365)

        # Deployment schedule (optional, for real release_id mapping and deployment dips)
        self.deployment_schedule: Optional[DeploymentSchedule] = None
        if deployment_schedule_path:
            print(f"Loading deployment schedule from {deployment_schedule_path}...")
            self.deployment_schedule = DeploymentSchedule(
                deployment_schedule_path, self.start_time, self.end_time, self.rng
            )
            window_count = sum(len(w) for w in self.deployment_schedule._deployment_windows.values())
            timeline_count = sum(len(t) for t in self.deployment_schedule._release_timelines.values())
            print(f"  Loaded {timeline_count} release timeline entries, {window_count} deployment windows")

        # Users
        self.users: List[User] = []
        self.user_by_id: Dict[str, User] = {}

        # Service incidents (time windows of degraded services)
        self.incidents: List[ServiceIncident] = []

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
        """Generate service incidents throughout the year.

        Each eligible service (dependency targets from SERVICE_DEPENDENCIES) gets
        2-8 incidents per year, each lasting 5 minutes to 4 hours.
        """
        print("  Generating service incidents...")

        for service_key, cfg in INCIDENT_ELIGIBLE_SERVICES.items():
            num_incidents = self.rng.randint(2, 8)

            for _ in range(num_incidents):
                days_ago = self.rng.randint(1, 364)
                hour = self.rng.randint(0, 23)
                start = self.start_time + timedelta(days=365 - days_ago, hours=hour)
                duration_minutes = self.rng.randint(5, 240)
                end = start + timedelta(minutes=duration_minutes)

                self.incidents.append(ServiceIncident(
                    service_key=service_key,
                    start_time=start,
                    end_time=end,
                    failure_rate=cfg["failure_rate"],
                    error_codes=cfg["error_codes"],
                    error_type=cfg["error_type"],
                    error_message=cfg["error_message"],
                ))

        self.incidents.sort(key=lambda x: x.start_time)
        print(f"    Generated {len(self.incidents)} service incidents across {len(INCIDENT_ELIGIBLE_SERVICES)} services")

    def get_active_incident(self, service_key: str, timestamp: datetime) -> Optional[ServiceIncident]:
        """Check if there's an active incident affecting this service at this time."""
        for incident in self.incidents:
            if incident.start_time <= timestamp <= incident.end_time:
                if incident.service_key == service_key:
                    return incident
        return None

    def determine_error(self, action: ServiceAction, user: User, timestamp: datetime,
                        env: str = None, region: str = None) -> Optional[Dict]:
        """Determine if this request should fail and why.

        Error priority:
        1. Service incident (elevated error rate during incident window)
        2. Deployment dip (rolling restart errors)
        3. Dependency failure (upstream service, error_source = child's deployment_id)
        4. Random service error (originating error, error_source = None)
        """
        service_key = f"{action.stack}:{action.service}"

        # 1. Service incident: check if any dependency has an active incident
        deps = SERVICE_DEPENDENCIES.get(service_key, [])
        for dep_key in deps:
            incident = self.get_active_incident(dep_key, timestamp)
            if incident and self.rng.random() < incident.failure_rate:
                dep_stack, dep_service = dep_key.split(':')
                dep_action = ServiceAction(
                    category="internal", service=dep_service, stack=dep_stack,
                    action="internal", weight=1.0, base_latency_ms=10,
                    latency_stddev_ms=1, base_payload_bytes=1024,
                    payload_stddev_bytes=256, has_target_user=False,
                    has_object_id=False, object_type=None, is_write=False,
                )
                dep_release_id, _, _ = self.select_release(dep_action, timestamp)
                dep_deployment_id = deployment_id_from_release_id(dep_release_id)
                return {
                    "error_source": dep_deployment_id,
                    "error_type": incident.error_type,
                    "error_code": self.rng.choice(incident.error_codes),
                    "error_message": f"Upstream {dep_key} failed: {incident.error_message}",
                    "upstream_request_id": uuid.uuid4().hex,
                }

        # Also check if this service itself has an incident (originating error)
        incident = self.get_active_incident(service_key, timestamp)
        if incident and self.rng.random() < incident.failure_rate:
            return {
                "error_source": None,
                "error_type": incident.error_type,
                "error_code": self.rng.choice(incident.error_codes),
                "error_message": incident.error_message,
                "upstream_request_id": None,
            }

        # 2. Deployment dip errors
        if self.deployment_schedule and env and region:
            window = self.deployment_schedule.get_active_deployment_window(
                action.stack, action.service, env, region, timestamp
            )
            if window and self.rng.random() < window.error_rate_boost:
                return {
                    "error_source": deployment_id_from_release_id(window.release_id),
                    "error_type": "server",
                    "error_code": self.rng.choice(["500", "502", "503"]),
                    "error_message": f"Service restarting during deployment of {window.release_id}",
                    "upstream_request_id": None,
                }

        # 3. Random errors based on persona success rate
        if self.rng.random() > user.persona.success_rate:
            # Dependency failure: blame a child's deployment_id
            if deps and self.rng.random() < 0.4:
                dep_key = self.rng.choice(deps)
                dep_stack, dep_service = dep_key.split(':')
                dep_action = ServiceAction(
                    category="internal", service=dep_service, stack=dep_stack,
                    action="internal", weight=1.0, base_latency_ms=10,
                    latency_stddev_ms=1, base_payload_bytes=1024,
                    payload_stddev_bytes=256, has_target_user=False,
                    has_object_id=False, object_type=None, is_write=False,
                )
                dep_release_id, _, _ = self.select_release(dep_action, timestamp)
                dep_deployment_id = deployment_id_from_release_id(dep_release_id)
                return {
                    "error_source": dep_deployment_id,
                    "error_type": "server",
                    "error_code": self.rng.choice(self.error_codes["server"]),
                    "error_message": f"Upstream {dep_key} failed",
                    "upstream_request_id": uuid.uuid4().hex,
                }

            # Originating error (no upstream to blame)
            if self.rng.random() < 0.7:
                error_code = self.rng.choice(self.error_codes["client"])
                error_type = "client"
            else:
                error_code = self.rng.choice(self.error_codes["server"])
                error_type = "server"

            return {
                "error_source": None,
                "error_type": error_type,
                "error_code": error_code,
                "error_message": self.error_messages[error_code],
                "upstream_request_id": None,
            }

        return None

    def select_release(self, action: ServiceAction, timestamp: datetime) -> Tuple[str, str, str]:
        """Select a release_id for this request based on environment weights and time.

        Returns (release_id, env, region) tuple.
        """
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

        # Try deployment schedule first
        if self.deployment_schedule:
            scheduled_release = self.deployment_schedule.get_active_release_id(
                env, region, action.stack, action.service, timestamp
            )
            if scheduled_release:
                return (scheduled_release, env, region)

        # Fallback to synthetic release_id
        days_into_year = (timestamp - self.start_time).days
        year_progress = max(0, days_into_year) / 365.0
        base_release = 50 + int(year_progress * 200)
        service_hash = hash(f"{action.stack}:{action.service}") % 50
        release_num = base_release + service_hash

        return (generate_release_id(env, region, action.stack, action.service, release_num), env, region)

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
                         timestamp: datetime, success: bool, release_id: str,
                         trace_id: str, latency_ms: float = None,
                         deployment_latency_multiplier: float = 1.0) -> List[MetricEntry]:
        """Generate performance metrics for an event

        Args:
            trace_id: Used for error-biased exemplar sampling
            latency_ms: Pre-computed latency (for determining if slow request)
            deployment_latency_multiplier: Extra latency during deployments (1.0 = no effect)
        """
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

        # Error-biased exemplar sampling:
        # - 100% of errors get trace_id
        # - 100% of slow requests (> 500ms) get trace_id
        # - 1% random sample of normal requests get trace_id
        attach_exemplar = (
            not success  # All errors
            or (latency_ms and latency_ms > 500)  # Slow requests
            or self.rng.random() < 0.01  # 1% sample
        )
        if attach_exemplar:
            base_tags["trace_id"] = trace_id

        # Add optional tags only if they have values
        if action.object_type:
            base_tags["object_type"] = action.object_type

        # Response time
        latency = max(1.0, self.rng.gauss(
            action.base_latency_ms * user.persona.latency_multiplier * deployment_latency_multiplier,
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
                     release_id: str, trace_id: str, span_id: str,
                     parent_span_id: Optional[str] = None,
                     error_info: Optional[Dict] = None) -> LogEntry:
        """Generate a log entry for an event"""
        ts_str = timestamp.isoformat() + "Z"

        error_code = None
        error_message = None
        error_source = None
        error_type = None
        upstream_request_id = None

        if success:
            level = "INFO"
            if action.is_write:
                message = f"{action.action} completed successfully"
            else:
                message = f"{action.action} returned data"
        else:
            # Use error_info if provided (from determine_error)
            if error_info:
                error_code = error_info["error_code"]
                error_message = error_info["error_message"]
                error_source = error_info["error_source"]
                error_type = error_info["error_type"]
                upstream_request_id = error_info.get("upstream_request_id")
            else:
                # Fallback to random error (shouldn't happen with new flow)
                if self.rng.random() < 0.7:
                    error_code = self.rng.choice(self.error_codes["client"])
                    error_type = "client"
                else:
                    error_code = self.rng.choice(self.error_codes["server"])
                    error_type = "server"
                error_message = self.error_messages[error_code]
                error_source = None

            message = f"{action.action} failed: {error_message}"
            # Set log level based on error type
            level = "ERROR" if error_type in ("server", "database", "cache", "queue", "internal") else "WARN"

        return LogEntry(
            timestamp=ts_str,
            level=level,
            service=action.service,
            stack=action.stack,
            action=action.action,
            user_id=user.user_id,
            request_id=request_id,
            success=success,
            message=message,
            release_id=release_id,
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            target_user_id=target_user_id,
            object_type=action.object_type,
            object_id=object_id,
            error_code=error_code,
            error_message=error_message,
            error_source=error_source,
            error_type=error_type,
            upstream_request_id=upstream_request_id,
        )

    def generate_events(self):
        """Generate all events (parallel if num_workers > 1)"""
        print(f"Generating {self.total_events} events with {self.num_workers} workers...")

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

        if self.num_workers > 1:
            return self._generate_events_parallel(user_event_counts)
        else:
            return self._generate_events_sequential(user_event_counts)

    def _generate_events_sequential(self, user_event_counts: List[Tuple]) -> List[dict]:
        """Generate events sequentially (original implementation)"""
        all_events = []

        for user, count in user_event_counts:
            for _ in range(count):
                action = self.select_action_for_user(user)
                timestamp = self.generate_timestamp(user)
                request_id = uuid.uuid4().hex
                # OpenTelemetry tracing - root span
                trace_id = generate_trace_id(self.rng)
                span_id = generate_span_id(self.rng)

                object_id = self.generate_object_id(action, user)
                target_user_id = self.generate_target_user(action, user)
                release_id, env, region = self.select_release(action, timestamp)

                # Throughput dip: skip events during deployment windows
                if self.deployment_schedule:
                    window = self.deployment_schedule.get_active_deployment_window(
                        action.stack, action.service, env, region, timestamp
                    )
                    if window and self.rng.random() > window.throughput_factor:
                        continue

                error_info = self.determine_error(action, user, timestamp, env, region)
                success = error_info is None

                # Deployment latency multiplier
                deployment_latency_mult = 1.0
                if self.deployment_schedule:
                    window = self.deployment_schedule.get_active_deployment_window(
                        action.stack, action.service, env, region, timestamp
                    )
                    if window:
                        deployment_latency_mult = window.latency_multiplier

                root_event = {
                    "user": user,
                    "action": action,
                    "timestamp": timestamp,
                    "request_id": request_id,
                    "trace_id": trace_id,
                    "span_id": span_id,
                    "parent_span_id": None,  # Root span
                    "success": success,
                    "error_info": error_info,
                    "object_id": object_id,
                    "target_user_id": target_user_id,
                    "release_id": release_id,
                    "deployment_latency_multiplier": deployment_latency_mult,
                }
                all_events.append(root_event)

                # Generate child spans for service dependencies
                child_spans = self._generate_child_spans_sequential(
                    root_event, action, user, timestamp
                )
                all_events.extend(child_spans)

        print("  Sorting events by timestamp...")
        all_events.sort(key=lambda e: e["timestamp"])
        return all_events

    def _generate_child_spans_sequential(
        self, parent_event: dict, action: 'ServiceAction', user: 'User', timestamp: datetime
    ) -> List[dict]:
        """Generate child span events for service dependencies (sequential format)."""
        service_key = f"{action.stack}:{action.service}"
        dependencies = SERVICE_DEPENDENCIES.get(service_key, [])

        if not dependencies:
            return []

        child_spans = []
        parent_latency = action.base_latency_ms * user.persona.latency_multiplier

        for i, dep_key in enumerate(dependencies):
            dep_stack, dep_service = dep_key.split(':')

            # Child timing
            child_start_offset_ms = (i + 1) * (parent_latency * 0.05)
            child_duration_ratio = self.rng.uniform(0.1, 0.3)
            child_latency = max(1.0, parent_latency * child_duration_ratio)

            max_child_end = parent_latency * 0.9
            if child_start_offset_ms + child_latency > max_child_end:
                child_latency = max(1.0, max_child_end - child_start_offset_ms)

            child_timestamp = timestamp + timedelta(milliseconds=child_start_offset_ms)
            child_span_id = generate_span_id(self.rng)
            child_request_id = uuid.uuid4().hex

            # Create a child ServiceAction for the dependency
            child_action = ServiceAction(
                category="internal",
                service=dep_service,
                stack=dep_stack,
                action=f"handle_{action.action}",
                weight=1.0,
                base_latency_ms=child_latency,
                latency_stddev_ms=child_latency * 0.1,
                base_payload_bytes=1024,
                payload_stddev_bytes=256,
                has_target_user=False,
                has_object_id=action.has_object_id,
                object_type=action.object_type,
                is_write=action.is_write,
            )

            child_release_id, _, _ = self.select_release(child_action, child_timestamp)

            # Check if parent blames this child
            child_error_info = None
            child_success = True
            parent_error_source = (parent_event.get("error_info") or {}).get("error_source", "")
            child_deployment_id = deployment_id_from_release_id(child_release_id)
            if parent_error_source == child_deployment_id:
                error_code = self.rng.choice(self.error_codes["server"])
                child_error_info = {
                    "error_source": None,
                    "error_type": "server",
                    "error_code": error_code,
                    "error_message": self.error_messages[error_code],
                }
                child_success = False

            child_event = {
                "user": user,
                "action": child_action,
                "timestamp": child_timestamp,
                "request_id": child_request_id,
                "trace_id": parent_event["trace_id"],
                "span_id": child_span_id,
                "parent_span_id": parent_event["span_id"],
                "success": child_success,
                "error_info": child_error_info,
                "object_id": parent_event.get("object_id"),
                "target_user_id": None,
                "release_id": child_release_id,
            }
            child_spans.append(child_event)

        return child_spans

    def _generate_events_parallel(self, user_event_counts: List[Tuple]) -> List[dict]:
        """Generate events in parallel using multiprocessing"""
        # Serialize user data for workers (can't pickle User objects directly)
        user_data_counts = []
        for user, count in user_event_counts:
            user_data = {
                "user_id": user.user_id,
                "persona_name": user.persona.name,
                "activity_multiplier": user.persona.activity_multiplier,
                "action_weights": user.persona.action_weights,
                "hourly_weights": user.persona.hourly_weights,
                "daily_weights": user.persona.daily_weights,
                "success_rate": user.persona.success_rate,
                "latency_multiplier": user.persona.latency_multiplier,
                "following": user.following[:100] if user.following else [],  # Limit for serialization
                "followers": user.followers[:100] if user.followers else [],
            }
            user_data_counts.append((user_data, count))

        # Serialize deployment schedule
        deployment_schedule_data = None
        if self.deployment_schedule:
            deployment_schedule_data = self.deployment_schedule.to_serializable()

        # Serialize incidents for workers
        incidents_data = [
            {
                "service_key": inc.service_key,
                "start_time": inc.start_time.isoformat(),
                "end_time": inc.end_time.isoformat(),
                "failure_rate": inc.failure_rate,
                "error_codes": inc.error_codes,
                "error_type": inc.error_type,
                "error_message": inc.error_message,
            }
            for inc in self.incidents
        ]

        # Split into chunks for workers
        chunks = [[] for _ in range(self.num_workers)]
        for i, item in enumerate(user_data_counts):
            chunks[i % self.num_workers].append(item)

        # Write directly to output directory (no temp files, no concatenation)
        import shutil
        if not hasattr(self, '_output_path'):
            self._output_path = Path("fixtures/test_data")
        self._output_path.mkdir(parents=True, exist_ok=True)
        output_dir = str(self._output_path)
        print(f"  Writing directly to: {output_dir}")

        # Prepare worker arguments - workers write directly to output dir
        worker_args = [
            (
                worker_id,
                chunks[worker_id],
                self.start_time,
                self.end_time,
                self.seed,
                self.error_codes,
                self.error_messages,
                output_dir,
                deployment_schedule_data,
                incidents_data,
            )
            for worker_id in range(self.num_workers)
        ]

        # Run workers in parallel - each streams to its own file
        print(f"  Starting {self.num_workers} parallel workers (streaming to disk)...")
        total_events = 0

        with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
            futures = {executor.submit(_generate_events_for_chunk_streaming, args): i for i, args in enumerate(worker_args)}
            completed = 0
            for future in as_completed(futures):
                worker_id = futures[future]
                try:
                    event_count, logs_path, metrics_path = future.result()
                    total_events += event_count
                    completed += 1
                    print(f"  Worker {worker_id} completed ({completed}/{self.num_workers}), generated {event_count:,} events, total: {total_events:,}")
                except Exception as e:
                    print(f"  Worker {worker_id} failed: {e}")
                    raise

        print(f"  Total events written: {total_events:,}")
        print(f"  Output files: {output_dir}/logs_*.jsonl, {output_dir}/metrics_*.jsonl")
        self._streaming_complete = True
        self._total_events_written = total_events
        return []

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

        # Check if events are from parallel (flat dict) or sequential (objects) generation
        is_parallel_format = "action_service" in events[0] if events else False

        with open(logs_file, 'w', encoding='utf-8') as log_f, \
             open(metrics_file, 'w', encoding='utf-8') as metric_f:

            # Write deployment log events first
            if self.deployment_schedule:
                for dep_event in self.deployment_schedule.get_deployment_log_events():
                    log_f.write(_deployment_event_to_log_json(dep_event) + "\n")
                    log_count += 1

            for i, event in enumerate(events):
                if i % 100000 == 0:
                    print(f"  Processing event {i}/{len(events)}...")

                if is_parallel_format:
                    # Parallel format - flat dict with action_* fields
                    log_entry = self._generate_log_from_flat(event)
                    metrics = self._generate_metrics_from_flat(event)
                else:
                    # Sequential format - User/ServiceAction objects
                    log_entry = self.generate_log(
                        event["action"], event["user"], event["timestamp"],
                        event["request_id"], event["success"],
                        event["target_user_id"], event["object_id"],
                        event["release_id"], event["trace_id"], event["span_id"],
                        event.get("parent_span_id"), event.get("error_info")
                    )
                    metrics = self.generate_metrics(
                        event["action"], event["user"], event["timestamp"],
                        event["success"], event["release_id"], event["trace_id"],
                        deployment_latency_multiplier=event.get("deployment_latency_multiplier", 1.0),
                    )

                log_f.write(json.dumps(asdict(log_entry)) + "\n")
                log_count += 1

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
            service = event["action_service"] if is_parallel_format else event["action"].service
            if service not in summary["actions_by_service"]:
                summary["actions_by_service"][service] = 0
            summary["actions_by_service"][service] += 1

        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"  Wrote summary to {summary_file}")

    def write_otlp_output(self, events: List[dict], base_dir: Path):
        """Write logs and metrics in OpenTelemetry OTLP JSON format"""
        base_dir.mkdir(parents=True, exist_ok=True)

        logs_file = base_dir / "logs.otlp.json"
        metrics_file = base_dir / "metrics.otlp.json"

        print(f"Writing OTLP output to {base_dir}...")
        print(f"  Logs: {logs_file}")
        print(f"  Metrics: {metrics_file}")

        is_parallel_format = "action_service" in events[0] if events else False

        # Collect all log records and metric data points
        log_records = []
        metric_data = {}  # metric_name -> list of data points

        for i, event in enumerate(events):
            if i % 100000 == 0:
                print(f"  Processing event {i}/{len(events)}...")

            if is_parallel_format:
                log_entry = self._generate_log_from_flat(event)
                metrics = self._generate_metrics_from_flat(event)
            else:
                log_entry = self.generate_log(
                    event["action"], event["user"], event["timestamp"],
                    event["request_id"], event["success"],
                    event["target_user_id"], event["object_id"],
                    event["release_id"], event["trace_id"], event["span_id"],
                    event.get("parent_span_id"), event.get("error_info")
                )
                metrics = self.generate_metrics(
                    event["action"], event["user"], event["timestamp"],
                    event["success"], event["release_id"], event["trace_id"],
                    deployment_latency_multiplier=event.get("deployment_latency_multiplier", 1.0),
                )

            # Convert log to OTLP format
            log_records.append(self._log_to_otlp(log_entry))

            # Convert metrics to OTLP format
            for metric in metrics:
                if metric.metric not in metric_data:
                    metric_data[metric.metric] = []
                metric_data[metric.metric].append(self._metric_to_otlp_datapoint(metric))

        # Build OTLP logs structure
        otlp_logs = {
            "resourceLogs": [{
                "resource": {
                    "attributes": [
                        {"key": "service.name", "value": {"stringValue": "social-network"}},
                        {"key": "service.version", "value": {"stringValue": "1.0.0"}}
                    ]
                },
                "scopeLogs": [{
                    "scope": {
                        "name": "qairon-generator",
                        "version": "1.0.0"
                    },
                    "logRecords": log_records
                }]
            }]
        }

        # Build OTLP metrics structure
        otlp_metrics = {
            "resourceMetrics": [{
                "resource": {
                    "attributes": [
                        {"key": "service.name", "value": {"stringValue": "social-network"}},
                        {"key": "service.version", "value": {"stringValue": "1.0.0"}}
                    ]
                },
                "scopeMetrics": [{
                    "scope": {
                        "name": "qairon-generator",
                        "version": "1.0.0"
                    },
                    "metrics": [
                        {
                            "name": metric_name,
                            "unit": "ms" if "duration" in metric_name or "latency" in metric_name else "1",
                            "gauge": {
                                "dataPoints": data_points
                            }
                        }
                        for metric_name, data_points in metric_data.items()
                    ]
                }]
            }]
        }

        # Write files
        with open(logs_file, 'w', encoding='utf-8') as f:
            json.dump(otlp_logs, f)
        print(f"  Wrote {len(log_records)} log records")

        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(otlp_metrics, f)
        print(f"  Wrote {sum(len(dp) for dp in metric_data.values())} metric data points")

        # Write summary
        summary_file = base_dir / "summary.json"
        summary = {
            "format": "otlp",
            "total_events": len(events),
            "total_logs": len(log_records),
            "total_metrics": sum(len(dp) for dp in metric_data.values()),
            "time_range": {
                "start": self.start_time.isoformat(),
                "end": self.end_time.isoformat(),
            },
        }
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"  Wrote summary to {summary_file}")

    def _log_to_otlp(self, log_entry: LogEntry) -> dict:
        """Convert LogEntry to OTLP log record format"""
        # Parse timestamp to nanoseconds
        ts = datetime.fromisoformat(log_entry.timestamp.replace("Z", "+00:00"))
        time_unix_nano = str(int(ts.timestamp() * 1_000_000_000))

        # Severity mapping
        severity_map = {"DEBUG": 5, "INFO": 9, "WARN": 13, "ERROR": 17, "FATAL": 21}
        severity_number = severity_map.get(log_entry.level, 9)

        # Build attributes from all log fields
        attributes = [
            {"key": "service", "value": {"stringValue": log_entry.service}},
            {"key": "stack", "value": {"stringValue": log_entry.stack}},
            {"key": "action", "value": {"stringValue": log_entry.action}},
            {"key": "user_id", "value": {"stringValue": log_entry.user_id}},
            {"key": "request_id", "value": {"stringValue": log_entry.request_id}},
            {"key": "success", "value": {"boolValue": log_entry.success}},
            {"key": "release_id", "value": {"stringValue": log_entry.release_id}},
        ]

        # Add optional fields if present
        if log_entry.target_user_id:
            attributes.append({"key": "target_user_id", "value": {"stringValue": log_entry.target_user_id}})
        if log_entry.object_type:
            attributes.append({"key": "object_type", "value": {"stringValue": log_entry.object_type}})
        if log_entry.object_id:
            attributes.append({"key": "object_id", "value": {"stringValue": log_entry.object_id}})
        if log_entry.error_code:
            attributes.append({"key": "error_code", "value": {"stringValue": log_entry.error_code}})
        if log_entry.error_message:
            attributes.append({"key": "error_message", "value": {"stringValue": log_entry.error_message}})
        if log_entry.error_source:
            attributes.append({"key": "error_source", "value": {"stringValue": log_entry.error_source}})
        if log_entry.error_type:
            attributes.append({"key": "error_type", "value": {"stringValue": log_entry.error_type}})

        return {
            "timeUnixNano": time_unix_nano,
            "observedTimeUnixNano": time_unix_nano,
            "severityNumber": severity_number,
            "severityText": log_entry.level,
            "body": {"stringValue": log_entry.message},
            "attributes": attributes,
            "traceId": log_entry.trace_id,
            "spanId": log_entry.span_id,
        }

    def _metric_to_otlp_datapoint(self, metric: MetricEntry) -> dict:
        """Convert MetricEntry to OTLP metric data point format"""
        time_unix_nano = str(int(metric.ts * 1_000_000_000))

        attributes = []
        for key, value in metric.tags.items():
            if isinstance(value, bool):
                attributes.append({"key": key, "value": {"boolValue": value}})
            elif isinstance(value, (int, float)):
                attributes.append({"key": key, "value": {"doubleValue": value}})
            else:
                attributes.append({"key": key, "value": {"stringValue": str(value)}})

        return {
            "timeUnixNano": time_unix_nano,
            "asDouble": metric.value,
            "attributes": attributes,
        }

    def _generate_log_from_flat(self, event: dict) -> LogEntry:
        """Generate log entry from flat parallel event format"""
        ts_str = event["timestamp"].isoformat() + "Z"
        success = event["success"]
        error_info = event.get("error_info")

        error_code = None
        error_message = None
        error_source = None
        error_type = None
        upstream_request_id = None

        if success:
            level = "INFO"
            action_name = event["action_action"]
            if event["action_is_write"]:
                message = f"{action_name} completed successfully"
            else:
                message = f"{action_name} returned data"
        else:
            action_name = event["action_action"]
            if error_info:
                error_code = error_info["error_code"]
                error_message = error_info["error_message"]
                error_source = error_info["error_source"]
                error_type = error_info["error_type"]
                upstream_request_id = error_info.get("upstream_request_id")
            else:
                error_code = "500"
                error_message = "Unknown error"
                error_type = "server"
                error_source = None
            message = f"{action_name} failed: {error_message}"
            level = "ERROR" if error_type in ("server", "database", "cache", "queue", "internal") else "WARN"

        return LogEntry(
            timestamp=ts_str,
            level=level,
            service=event["action_service"],
            stack=event["action_stack"],
            action=event["action_action"],
            user_id=event["user_id"],
            request_id=event["request_id"],
            success=success,
            message=message,
            release_id=event["release_id"],
            trace_id=event["trace_id"],
            span_id=event["span_id"],
            parent_span_id=event.get("parent_span_id"),
            target_user_id=event["target_user_id"],
            object_type=event["action_object_type"],
            object_id=event["object_id"],
            error_code=error_code,
            error_message=error_message,
            error_source=error_source,
            error_type=error_type,
            upstream_request_id=upstream_request_id,
        )

    def _generate_metrics_from_flat(self, event: dict) -> List[MetricEntry]:
        """Generate metrics from flat parallel event format"""
        metrics = []
        epoch_ts = event["timestamp"].timestamp()
        success = event["success"]

        base_tags = {
            "service": event["action_service"],
            "stack": event["action_stack"],
            "action": event["action_action"],
            "success": "true" if success else "false",
            "is_write": "true" if event["action_is_write"] else "false",
            "persona": event["persona_name"],
            "release_id": event["release_id"],
        }

        if event["action_object_type"]:
            base_tags["object_type"] = event["action_object_type"]

        # Response time
        latency = max(1.0, self.rng.gauss(
            event["action_base_latency_ms"] * event["latency_multiplier"],
            event["action_latency_stddev_ms"]
        ))
        if not success:
            if self.rng.random() < 0.5:
                latency *= 0.3
            else:
                latency *= 3

        # Error-biased exemplar sampling:
        # - 100% of errors get trace_id
        # - 100% of slow requests (> 500ms) get trace_id
        # - 1% random sample of normal requests get trace_id
        attach_exemplar = (
            not success  # All errors
            or latency > 500  # Slow requests
            or self.rng.random() < 0.01  # 1% sample
        )
        if attach_exemplar:
            base_tags["trace_id"] = event["trace_id"]

        metrics.append(MetricEntry(
            metric="request_duration_ms",
            ts=epoch_ts,
            value=round(latency, 2),
            tags=dict(base_tags),
        ))

        # Request payload size
        request_size = max(64, int(self.rng.gauss(
            event["action_base_payload_bytes"] * 0.1,
            event["action_payload_stddev_bytes"] * 0.1
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
                event["action_base_payload_bytes"],
                event["action_payload_stddev_bytes"]
            )))
        else:
            response_size = self.rng.randint(128, 512)

        metrics.append(MetricEntry(
            metric="response_size_bytes",
            ts=epoch_ts,
            value=float(response_size),
            tags=dict(base_tags),
        ))

        # Database query count
        if success:
            db_queries = self.rng.randint(1, 5) if not event["action_is_write"] else self.rng.randint(1, 3)
        else:
            db_queries = self.rng.randint(0, 2)

        metrics.append(MetricEntry(
            metric="db_query_count",
            ts=epoch_ts,
            value=float(db_queries),
            tags=dict(base_tags),
        ))

        # Cache hit/miss (for reads)
        if not event["action_is_write"] and success:
            cache_hit = 1.0 if self.rng.random() < 0.7 else 0.0
            metrics.append(MetricEntry(
                metric="cache_hit",
                ts=epoch_ts,
                value=cache_hit,
                tags=dict(base_tags),
            ))

        return metrics


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
    parser.add_argument("--workers", "-w", type=int, default=1,
                        help="Number of parallel workers for event generation (default: 1)")
    parser.add_argument("--format", "-f", type=str, default="jsonl",
                        choices=["jsonl", "otlp"],
                        help="Output format: jsonl (default) or otlp (OpenTelemetry)")
    parser.add_argument("--deployment-schedule", type=str, default=None,
                        help="Path to deployment_schedule.json from generate_fixtures.py (optional)")

    args = parser.parse_args()

    print("=" * 70)
    print("Social Network Monitoring Data Generator")
    print("=" * 70)
    print(f"Total events: {args.total_events:,}")
    print(f"Total users: {args.total_users:,}")
    print(f"Output directory: {args.output}")
    print(f"Random seed: {args.seed}")
    print(f"Workers: {args.workers}")
    print(f"Format: {args.format}")
    print(f"Deployment schedule: {args.deployment_schedule or 'None (synthetic releases)'}")
    print("=" * 70)

    generator = MonitoringDataGenerator(
        total_events=args.total_events,
        total_users=args.total_users,
        seed=args.seed,
        num_workers=args.workers,
        deployment_schedule_path=args.deployment_schedule,
    )

    # Set output path for streaming (parallel workers write directly to disk)
    generator._output_path = Path(args.output)

    generator.generate_users()
    generator.generate_incidents()
    events = generator.generate_events()

    # Check if streaming was used (parallel with > 1 worker)
    if getattr(generator, '_streaming_complete', False):
        # Already written to disk during generation
        print(f"  Logs and metrics streamed to {args.output}")
        # Write summary
        summary_file = Path(args.output) / "summary.json"
        summary = {
            "total_events": generator._total_events_written,
            "total_users": len(generator.users),
            "time_range": {
                "start": generator.start_time.isoformat(),
                "end": generator.end_time.isoformat(),
            },
        }
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"  Wrote summary to {summary_file}")
    elif args.format == "otlp":
        generator.write_otlp_output(events, Path(args.output))
    else:
        generator.write_output(events, Path(args.output))

    print("=" * 70)
    print("Done!")


if __name__ == "__main__":
    main()