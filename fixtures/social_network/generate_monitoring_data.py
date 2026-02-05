#!/usr/bin/env python3
"""
Social Network Monitoring Data Generator

Generates synthetic logs and metrics for a social network platform over 1 year.
Logs and metrics match exactly - each event produces both a log entry and metrics.

Usage: python generate_monitoring_data.py <total_events> <total_users>

Example: python generate_monitoring_data.py 10000000 50000
"""

import argparse
import hashlib
import json
import random
import re
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
# POWER USERS / INFLUENCERS (1 persona, ~2% of users, ~15% of events)
# -----------------------------------------------------------------------------
for i in range(1):
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
        success_rate=0.985,
        latency_multiplier=0.8,  # Good internet
    ))

# -----------------------------------------------------------------------------
# CONTENT CREATORS (2 personas, ~5% of users, ~12% of events)
# -----------------------------------------------------------------------------
for i in range(2):
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
        success_rate=0.985,
        latency_multiplier=0.9,
    ))

# -----------------------------------------------------------------------------
# ACTIVE ENGAGERS (2 personas, ~10% of users, ~18% of events)
# -----------------------------------------------------------------------------
for i in range(2):
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
        success_rate=0.982,
        latency_multiplier=1.0,
    ))

# -----------------------------------------------------------------------------
# REGULAR USERS (5 personas, ~25% of users, ~25% of events)
# -----------------------------------------------------------------------------
for i in range(5):
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
        success_rate=0.980,
        latency_multiplier=1.1 if age_group > 3 else 1.0,
    ))

# -----------------------------------------------------------------------------
# CASUAL BROWSERS (4 personas, ~25% of users, ~15% of events)
# -----------------------------------------------------------------------------
for i in range(4):
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
        success_rate=0.982,
        latency_multiplier=1.2,
    ))

# -----------------------------------------------------------------------------
# LURKERS (3 personas, ~20% of users, ~8% of events)
# -----------------------------------------------------------------------------
for i in range(3):
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
        success_rate=0.980,
        latency_multiplier=1.3,
    ))

# -----------------------------------------------------------------------------
# NEW USERS (1 persona, ~8% of users, ~4% of events)
# -----------------------------------------------------------------------------
for i in range(1):
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
        success_rate=0.975,  # More errors as they learn
        latency_multiplier=1.4,
    ))

# -----------------------------------------------------------------------------
# BUSINESS/BRAND ACCOUNTS (1 persona, ~3% of users, ~2% of events)
# -----------------------------------------------------------------------------
for i in range(1):
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
        success_rate=0.987,
        latency_multiplier=0.85,
    ))

# -----------------------------------------------------------------------------
# ADVERTISERS (1 persona, ~2% of users, ~1% of events)
# -----------------------------------------------------------------------------
for i in range(1):
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
        success_rate=0.988,
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
    # Application (part of canonical service_id)
    application: str = 'social'

    @property
    def service_id(self) -> str:
        """Canonical service_id: application:stack:service"""
        return f"{self.application}:{self.stack}:{self.service}"


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

# Documented dependencies: service_id -> list of downstream service_ids it depends on
SERVICE_DEPENDENCIES: Dict[str, List[str]] = {
    # Feed stack
    "social:feed:timeline": ["social:feed:ranking", "social:content:posts", "social:content:stories", "social:social:connections", "social:content:reactions"],
    "social:feed:ranking": ["social:discovery:interests"],
    "social:feed:fanout": ["social:social:connections"],
    "social:feed:aggregation": ["social:feed:fanout"],

    # Content stack
    "social:content:posts": ["social:content:media", "social:content:hashtags", "social:feed:fanout", "social:search:indexer"],
    "social:content:comments": ["social:content:posts"],
    "social:content:reactions": ["social:content:posts", "social:content:comments"],
    "social:content:shares": ["social:content:posts", "social:feed:fanout"],
    "social:content:stories": ["social:content:media"],

    # Messaging stack
    "social:messaging:dm": ["social:messaging:realtime", "social:messaging:presence"],
    "social:messaging:groups": ["social:messaging:realtime", "social:messaging:presence"],

    # Notifications stack
    "social:notifications:push": ["social:notifications:preferences"],
    "social:notifications:inapp": ["social:notifications:preferences"],
    "social:notifications:email": ["social:notifications:preferences"],
    "social:notifications:sms": ["social:notifications:preferences"],

    # Search stack
    "social:search:users": ["social:search:indexer"],
    "social:search:content": ["social:search:indexer"],
    "social:search:hashtags": ["social:search:indexer"],

    # Discovery stack
    "social:discovery:explore": ["social:discovery:trending", "social:discovery:recommendations", "social:feed:ranking"],
    "social:discovery:recommendations": ["social:discovery:interests"],

    # Live stack
    "social:live:streaming": ["social:live:live-chat", "social:live:gifts"],
    "social:live:live-chat": ["social:messaging:realtime"],
    "social:live:gifts": ["social:payments:wallet"],

    # Ads stack
    "social:ads:campaigns": ["social:ads:targeting", "social:ads:bidding"],
    "social:ads:delivery": ["social:ads:campaigns", "social:ads:bidding"],

    # Payments stack
    "social:payments:subscriptions": ["social:payments:processor"],
    "social:payments:payouts": ["social:payments:processor", "social:payments:wallet"],

    # Creator stack
    "social:creator:monetization": ["social:payments:wallet", "social:creator:creator-analytics"],
    "social:creator:shop": ["social:payments:processor"],

    # Social stack
    "social:social:suggestions": ["social:social:connections"],
}



# =============================================================================
# DEPLOYMENTS AND RELEASES
# =============================================================================

# Default environment config (fallback when no deployment schedule is provided)
DEFAULT_ENVIRONMENT_CONFIG = {
    "prod": {"targets": [{"provider": "aws", "account": "111111111111", "region": "us-east-1",
                           "partition": "platform", "target_type": "eks", "target": "main"},
                          {"provider": "aws", "account": "111111111111", "region": "us-west-2",
                           "partition": "platform", "target_type": "eks", "target": "main"}],
             "weight": 0.85},
    "stg": {"targets": [{"provider": "aws", "account": "222222222222", "region": "us-east-1",
                          "partition": "platform", "target_type": "eks", "target": "main"}],
            "weight": 0.10},
    "dev": {"targets": [{"provider": "aws", "account": "333333333333", "region": "us-east-1",
                          "partition": "platform", "target_type": "eks", "target": "main"}],
            "weight": 0.05},
}

# Primary deployment targets — the main clusters where all services run
PRIMARY_DEPLOYMENT_TARGETS = [
    # PROD — 2 AWS accounts × 2 regions, 2 GCP accounts × 2 regions, 2 Azure accounts × 2 regions (12 targets)
    'prod:aws:111111111111:us-east-1:platform:eks:main',
    'prod:aws:111111111111:us-west-2:platform:eks:main',
    'prod:aws:111111111112:us-east-1:platform:eks:main',
    'prod:aws:111111111112:us-west-2:platform:eks:main',
    'prod:gcp:social-prod-001:us-central1:platform:gke:main',
    'prod:gcp:social-prod-001:southamerica-east1:platform:gke:main',
    'prod:gcp:social-prod-002:us-central1:platform:gke:main',
    'prod:gcp:social-prod-002:us-east4:platform:gke:main',
    'prod:azure:prod-sub-001:eastus:platform:aks:main',
    'prod:azure:prod-sub-001:westeurope:platform:aks:main',
    'prod:azure:prod-sub-002:eastus:platform:aks:main',
    'prod:azure:prod-sub-002:westus2:platform:aks:main',
    # STG — 1 each (3 targets)
    'stg:aws:222222222221:us-east-1:platform:eks:main',
    'stg:gcp:social-stg-001:us-central1:platform:gke:main',
    'stg:azure:stg-sub-001:eastus:platform:aks:main',
    # DEV — 1 each (3 targets)
    'dev:aws:333333333331:us-east-1:platform:eks:main',
    'dev:gcp:social-dev-001:us-central1:platform:gke:main',
    'dev:azure:dev-sub-001:eastus:platform:aks:main',
    # INT — 1 each (3 targets)
    'int:aws:444444444441:us-east-1:platform:eks:main',
    'int:gcp:social-int-001:us-central1:platform:gke:main',
    'int:azure:int-sub-001:eastus:platform:aks:main',
    # INFRA — AWS only (1 target)
    'infra:aws:555555555555:us-east-1:platform:eks:main',
]

HIGH_FREQUENCY_SERVICES = [
    'social:user:identity',
    'social:content:posts',
    'social:feed:timeline',
    'social:platform:api-gateway',
    'social:messaging:dm',
    'social:content:media',
]

BUILD_ARTIFACT_NAMES = ['docker-image', 'helm-chart', 'test-report', 'sbom', 'changelog', 'coverage-report', 'lint-report']
RELEASE_ARTIFACT_NAMES = ['manifest', 'values', 'migration', 'rollback-plan', 'changelog', 'runbook', 'smoke-test']

# Environment traffic weight by env type
ENV_WEIGHT_MAP = {
    "prod": 0.85,
    "stg": 0.10,
    "dev": 0.03,
    "int": 0.015,
    "infra": 0.005,
}

# Regional latency/error characteristics for geo-distributed simulation
REGION_PROFILES = {
    # AWS US regions (baseline)
    "us-east-1": {"latency_multiplier": 1.0, "error_multiplier": 1.0},
    "us-west-2": {"latency_multiplier": 1.1, "error_multiplier": 1.0},
    # AWS EU regions
    "eu-west-1": {"latency_multiplier": 1.3, "error_multiplier": 1.05},
    "eu-central-1": {"latency_multiplier": 1.35, "error_multiplier": 1.05},
    # AWS AP regions
    "ap-southeast-1": {"latency_multiplier": 1.5, "error_multiplier": 1.1},
    "ap-northeast-1": {"latency_multiplier": 1.45, "error_multiplier": 1.08},
    # AWS CA region
    "ca-central-1": {"latency_multiplier": 1.15, "error_multiplier": 1.02},
    # GCP US regions
    "us-central1": {"latency_multiplier": 1.05, "error_multiplier": 1.0},
    "us-east4": {"latency_multiplier": 1.0, "error_multiplier": 1.0},
    # GCP EU regions
    "europe-west1": {"latency_multiplier": 1.3, "error_multiplier": 1.05},
    "europe-west4": {"latency_multiplier": 1.32, "error_multiplier": 1.05},
    # GCP Asia regions
    "asia-southeast1": {"latency_multiplier": 1.5, "error_multiplier": 1.1},
    "asia-east1": {"latency_multiplier": 1.48, "error_multiplier": 1.09},
    # GCP South America
    "southamerica-east1": {"latency_multiplier": 1.6, "error_multiplier": 1.12},
    # Azure regions
    "eastus": {"latency_multiplier": 1.0, "error_multiplier": 1.0},
    "westus2": {"latency_multiplier": 1.1, "error_multiplier": 1.0},
    "northeurope": {"latency_multiplier": 1.3, "error_multiplier": 1.05},
    "westeurope": {"latency_multiplier": 1.3, "error_multiplier": 1.05},
    "southeastasia": {"latency_multiplier": 1.5, "error_multiplier": 1.1},
    "japaneast": {"latency_multiplier": 1.45, "error_multiplier": 1.08},
    "canadacentral": {"latency_multiplier": 1.15, "error_multiplier": 1.02},
}

# Default profile for unlisted regions
DEFAULT_REGION_PROFILE = {"latency_multiplier": 1.2, "error_multiplier": 1.05}


def get_region_profile(region: str) -> dict:
    """Get latency/error profile for a region."""
    return REGION_PROFILES.get(region, DEFAULT_REGION_PROFILE)


def build_environment_config_from_schedule(primary_targets: List[str]) -> Dict:
    """Build ENVIRONMENT_CONFIG from deployment schedule primary_deployment_targets.

    Each primary target is a target_id like:
        prod:aws:111111111111:us-east-1:platform:eks:main

    Groups by env, extracts provider/account/region/partition/target_type/target.
    Distributes traffic weight across envs and equally across regions within each env.
    """
    env_targets: Dict[str, List[Dict]] = {}

    for target_id in primary_targets:
        parts = target_id.split(':')
        if len(parts) < 7:
            continue
        env = parts[0]
        target_info = {
            "provider": parts[1],
            "account": parts[2],
            "region": parts[3],
            "partition": parts[4],
            "target_type": parts[5],
            "target": parts[6],
        }
        if env not in env_targets:
            env_targets[env] = []
        env_targets[env].append(target_info)

    config = {}
    for env, targets in env_targets.items():
        config[env] = {
            "targets": targets,
            "weight": ENV_WEIGHT_MAP.get(env, 0.01),
        }

    return config


# Active ENVIRONMENT_CONFIG — set dynamically from deployment schedule or defaults
ENVIRONMENT_CONFIG = dict(DEFAULT_ENVIRONMENT_CONFIG)


def generate_release_id(env: str, region: str, stack: str, service: str, release_num: int,
                        target_info: Optional[Dict] = None) -> str:
    """Generate a release ID in qairon format: {deployment_id}:{release_num}

    release_num is the CI/CD pipeline's sequential build number for this release.
    Uses actual provider/account/partition/target_type/target from target_info when available.
    """
    if target_info:
        provider = target_info["provider"]
        account = target_info["account"]
        partition = target_info["partition"]
        target_type = target_info["target_type"]
        target = target_info["target"]
    else:
        # Fallback for when no target context is available
        env_config = ENVIRONMENT_CONFIG.get(env, {})
        targets = env_config.get("targets", [])
        # Find a target matching this region
        matching = [t for t in targets if t["region"] == region]
        if matching:
            t = matching[0]
            provider, account, partition, target_type, target = (
                t["provider"], t["account"], t["partition"], t["target_type"], t["target"])
        else:
            provider, account, partition, target_type, target = "aws", "111111111111", "platform", "eks", "main"

    deployment_id = f"{env}:{provider}:{account}:{region}:{partition}:{target_type}:{target}:social:{stack}:{service}:default"
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
    error_source: Optional[str] = None  # deployment_id of the failed downstream dependency, or None for originating errors
    error_type: Optional[str] = None    # "client", "server", "database", "cache", "queue", "internal", "rate_limit"
    downstream_request_id: Optional[str] = None  # Request ID of the failed downstream dependency call


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
    max_depth: int = 5,
    current_depth: int = 0,
    visited: Optional[set] = None,
) -> List[dict]:
    """
    Recursively generate child span events for a parent event's service dependencies.

    Walks SERVICE_DEPENDENCIES to produce a full multi-level trace tree.
    For example, a feed:timeline request generates:
      timeline → content:posts → content:media, content:hashtags, feed:fanout, search:indexer
      timeline → feed:ranking → discovery:interests

    Error propagation follows stack trace semantics:
    - A leaf child that fails has error_source=None (it's the originator)
    - A parent that fails because its child failed has error_source=child's deployment_id

    Args:
        parent_event: The root/parent event dict
        rng: Random number generator
        select_release_func: Function to select a release for a service
        error_codes: Dict of error codes by type
        error_messages: Dict of error messages by code
        max_depth: Maximum recursion depth (default 5, prevents runaway recursion)
        current_depth: Current recursion depth (internal use)
        visited: Set of visited service_ids in this trace path (cycle detection)

    Returns:
        List of child span event dicts (includes all descendants)
    """
    if current_depth >= max_depth:
        return []

    if visited is None:
        visited = set()

    # Use canonical field names (application/service/stack, not action_* prefixed)
    service_key = f"{parent_event['application']}:{parent_event['stack']}:{parent_event['service']}"

    # Cycle detection: skip if we've already visited this service in this path
    if service_key in visited:
        return []
    visited = visited | {service_key}  # Create new set to avoid mutation across branches

    dependencies = SERVICE_DEPENDENCIES.get(service_key, [])

    if not dependencies:
        return []

    all_spans = []
    parent_timestamp = parent_event['timestamp']

    # Calculate parent latency for timing child spans
    parent_latency = parent_event['action_base_latency_ms'] * parent_event['latency_multiplier']

    for i, dep_service_id in enumerate(dependencies):
        dep_application, dep_stack, dep_service = dep_service_id.split(':')

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

        # Use canonical field names (application/service/stack) for consistency
        # with root events and downstream log/metric conversion
        child_event = {
            "user_id": parent_event["user_id"],
            "persona_name": parent_event["persona_name"],
            "application": dep_application,
            "service": dep_service,
            "stack": dep_stack,
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

        all_spans.append(child_event)

        # Recursively generate grandchild spans for this child's dependencies
        grandchild_spans = generate_child_spans_for_event(
            parent_event=child_event,
            rng=rng,
            select_release_func=select_release_func,
            error_codes=error_codes,
            error_messages=error_messages,
            max_depth=max_depth,
            current_depth=current_depth + 1,
            visited=visited,
        )
        all_spans.extend(grandchild_spans)

    return all_spans


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
    service_key: str        # canonical service_id — the affected service
    start_time: datetime
    end_time: datetime
    failure_rate: float     # probability of failure per request during incident
    error_codes: List[str]  # e.g. ["500", "503"]
    error_type: str         # "server", "database", "cache", etc.
    error_message: str      # human-readable description
    region_scope: Optional[str] = None  # None = all regions, or specific region


# Services that can have incidents — these are the dependency targets from
# SERVICE_DEPENDENCIES (services that other services call). When these fail,
# failures cascade to their callers via the trace/span tree.
INCIDENT_ELIGIBLE_SERVICES: Dict[str, Dict] = {}
_seen = set()
for _deps in SERVICE_DEPENDENCIES.values():
    for _dep in _deps:
        if _dep not in _seen:
            _seen.add(_dep)
            _app, _stack, _svc = _dep.split(':')
            # Assign plausible error characteristics based on service type
            if _svc in ('posts', 'media', 'comments', 'reactions', 'shares', 'stories', 'hashtags'):
                cfg = {"failure_rate_range": (0.02, 0.15), "error_type": "server", "error_codes": ["500", "503"], "error_message": "Service degraded"}
            elif _svc in ('connections', 'blocks', 'suggestions', 'contacts'):
                cfg = {"failure_rate_range": (0.03, 0.20), "error_type": "database", "error_codes": ["503", "504"], "error_message": "Query timeout"}
            elif _svc in ('timeline', 'ranking', 'fanout', 'aggregation'):
                cfg = {"failure_rate_range": (0.02, 0.15), "error_type": "cache", "error_codes": ["503"], "error_message": "Cache unavailable"}
            elif _svc in ('realtime', 'presence', 'dm', 'groups'):
                cfg = {"failure_rate_range": (0.02, 0.12), "error_type": "cache", "error_codes": ["503"], "error_message": "Connection pool exhausted"}
            elif _svc in ('processor', 'wallet', 'bidding', 'targeting'):
                cfg = {"failure_rate_range": (0.03, 0.10), "error_type": "server", "error_codes": ["500", "502"], "error_message": "Downstream timeout"}
            elif _svc in ('indexer',):
                cfg = {"failure_rate_range": (0.03, 0.15), "error_type": "search", "error_codes": ["503", "504"], "error_message": "Cluster unavailable"}
            elif _svc in ('preferences',):
                cfg = {"failure_rate_range": (0.02, 0.08), "error_type": "database", "error_codes": ["503"], "error_message": "Read timeout"}
            else:
                cfg = {"failure_rate_range": (0.02, 0.12), "error_type": "server", "error_codes": ["500", "503"], "error_message": "Internal error"}
            INCIDENT_ELIGIBLE_SERVICES[_dep] = cfg
del _seen, _deps, _dep, _app, _stack, _svc, cfg


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
    """Manages deployment windows and release timelines.

    Provides:
    - Active release lookup by (env, region, stack, service, timestamp)
    - Active deployment window lookup for dip effects
    - Deployment log events (start/complete)
    - Serialization for parallel worker transport
    """

    def __init__(self):
        self.primary_targets = []
        self.stack_region_groups = {}
        # Build per-(env, region, stack, service) sorted release timelines
        # Each entry: (created_at_datetime, release_id, build_num)
        self._release_timelines: Dict[Tuple[str, str, str, str], List[Tuple[datetime, str, int]]] = {}
        # Deployment windows keyed by (stack, service, env, region)
        self._deployment_windows: Dict[Tuple[str, str, str, str], List[DeploymentWindow]] = {}

    @classmethod
    def from_generated_data(cls, release_timelines, deployment_windows, primary_targets):
        """Construct from internally generated release data.

        Args:
            release_timelines: Dict[(env, region, stack, service)] -> [(created_at, release_id, build_num)]
            deployment_windows: Dict[(stack, service, env, region)] -> [DeploymentWindow]
            primary_targets: List of target_id strings
        """
        obj = cls()
        obj.primary_targets = primary_targets
        obj._release_timelines = release_timelines
        obj._deployment_windows = deployment_windows
        return obj

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
        timelines = {}
        for str_key, timeline in data.get("timelines", {}).items():
            key = tuple(str_key.split('|'))
            timelines[key] = [
                (datetime.fromisoformat(created_at), release_id, build_num)
                for created_at, release_id, build_num in timeline
            ]

        windows = {}
        for str_key, win_list in data.get("windows", {}).items():
            key = tuple(str_key.split('|'))
            windows[key] = [
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

        return cls.from_generated_data(
            timelines, windows,
            data.get("primary_deployment_targets", [])
        )


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
        "downstream_request_id": None,
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
    - incidents_data: list of serialized ServiceIncident dicts
    - env_config_data: dict (serialized ENVIRONMENT_CONFIG)

    Returns:
    - (event_count, logs_file_path, metrics_file_path)
    """
    (worker_id, user_chunk, start_time, end_time,
     base_seed, error_codes, error_messages, output_dir, deployment_schedule_data,
     incidents_data, env_config_data) = args

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
            region_scope=inc.get("region_scope"),
        )
        for inc in incidents_data
    ]

    # Reconstruct environment config from serializable form
    env_config = env_config_data if env_config_data else dict(DEFAULT_ENVIRONMENT_CONFIG)

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
    def get_active_incident(service_key: str, timestamp: datetime, region: str = None) -> Optional[ServiceIncident]:
        for incident in incidents:
            if incident.start_time <= timestamp <= incident.end_time:
                if incident.service_key == service_key:
                    # Check region scope
                    if incident.region_scope is None or incident.region_scope == region:
                        return incident
        return None

    def determine_error(action, user_data, timestamp, env=None, region=None) -> Optional[Dict]:
        service_key = action.service_id

        # Apply regional error multiplier
        region_profile = get_region_profile(region) if region else DEFAULT_REGION_PROFILE
        regional_error_mult = region_profile["error_multiplier"]

        # 1. Service incident: check if any dependency has an active incident
        deps = SERVICE_DEPENDENCIES.get(service_key, [])
        for dep_key in deps:
            incident = get_active_incident(dep_key, timestamp, region)
            if incident and rng.random() < incident.failure_rate * regional_error_mult:
                dep_application, dep_stack, dep_service = dep_key.split(':')
                dep_release_result = select_release_by_key(dep_stack, dep_service, timestamp)
                dep_release_id = dep_release_result[0] if isinstance(dep_release_result, tuple) else dep_release_result
                dep_deployment_id = deployment_id_from_release_id(dep_release_id)
                return {
                    "error_source": dep_deployment_id,
                    "error_type": incident.error_type,
                    "error_code": rng.choice(incident.error_codes),
                    "error_message": f"Downstream dependency failed: {incident.error_message}",
                    "downstream_request_id": uuid.uuid4().hex,
                }

        # Also check if this service itself has an incident (originating error)
        incident = get_active_incident(service_key, timestamp, region)
        if incident and rng.random() < incident.failure_rate * regional_error_mult:
            return {
                "error_source": None,
                "error_type": incident.error_type,
                "error_code": rng.choice(incident.error_codes),
                "error_message": incident.error_message,
                "downstream_request_id": None,
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
                    "error_message": "Service restarting during deployment",
                    "downstream_request_id": None,
                }

        # 3. Stochastic errors — base rate 1-2% (scaled by persona success_rate and regional multiplier)
        stochastic_error_rate = (1.0 - user_data["success_rate"]) * regional_error_mult
        if rng.random() < stochastic_error_rate:
            # Dependency failure: blame a downstream service's deployment_id
            deps = SERVICE_DEPENDENCIES.get(service_key, [])
            if deps and rng.random() < 0.4:
                dep_key = rng.choice(deps)
                dep_application, dep_stack, dep_service = dep_key.split(':')
                dep_release_result = select_release_by_key(dep_stack, dep_service, timestamp)
                dep_release_id = dep_release_result[0] if isinstance(dep_release_result, tuple) else dep_release_result
                dep_deployment_id = deployment_id_from_release_id(dep_release_id)
                return {
                    "error_source": dep_deployment_id,
                    "error_type": "server",
                    "error_code": rng.choice(error_codes["server"]),
                    "error_message": "Downstream dependency failed",
                    "downstream_request_id": uuid.uuid4().hex,
                }

            # Originating error (no downstream to blame)
            if rng.random() < 0.6:
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
                "downstream_request_id": None,
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
        total_days = (end_time - start_time).days
        days_ago = rng.randint(0, max(0, total_days - 1))
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
        """Returns (release_id, env, region, target_info) tuple."""
        envs = list(env_config.keys())
        weights = [env_config[e]["weight"] for e in envs]
        env = rng.choices(envs, weights=weights)[0]
        targets = env_config[env]["targets"]
        # Select a target (and thus region) uniformly from available targets
        target_info = rng.choice(targets)
        region = target_info["region"]

        # Try deployment schedule first
        if deploy_schedule:
            scheduled = deploy_schedule.get_active_release_id(
                env, region, action.stack, action.service, timestamp
            )
            if scheduled:
                return (scheduled, env, region, target_info)

        total_days = (end_time - start_time).days
        days_into_range = (timestamp - start_time).days
        range_progress = max(0, days_into_range) / max(1, total_days)
        base_release = 50 + int(range_progress * 200)
        service_hash = hash(f"{action.stack}:{action.service}") % 50
        release_num = base_release + service_hash
        return (generate_release_id(env, region, action.stack, action.service, release_num, target_info), env, region, target_info)

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
        """Returns (release_id, env, region, target_info) tuple."""
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
        downstream_request_id = None

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
                downstream_request_id = error_info.get("downstream_request_id")
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
            "service": event["service"],
            "stack": event["stack"],
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
            "downstream_request_id": downstream_request_id,
        }
        return json.dumps(log_entry)

    def event_to_metrics_json(event: dict) -> List[str]:
        """Convert event to metric JSON lines"""
        lines = []
        epoch_ts = event["timestamp"].timestamp()
        success = event["success"]

        base_tags = {
            "service": event["service"],
            "stack": event["stack"],
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
                release_id, env, region, target_info = select_release(action, timestamp)

                # Throughput dip: skip events during deployment windows
                if deploy_schedule:
                    window = deploy_schedule.get_active_deployment_window(
                        action.stack, action.service, env, region, timestamp
                    )
                    if window and rng.random() > window.throughput_factor:
                        continue

                error_info = determine_error(action, user_data, timestamp, env, region)
                success = error_info is None

                # Regional latency multiplier
                region_profile = get_region_profile(region)
                regional_latency_mult = region_profile["latency_multiplier"]

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
                    "application": action.application,
                    "service": action.service,
                    "stack": action.stack,
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
                    "latency_multiplier": user_data["latency_multiplier"] * deployment_latency_mult * regional_latency_mult,
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


class MonitoringDataGenerator:
    """Generates synthetic monitoring data"""

    def __init__(self, total_events: int, total_users: int, seed: int = 42, num_workers: int = 1):
        self.total_events = total_events
        self.total_users = total_users
        self.seed = seed
        self.num_workers = num_workers
        self.rng = random.Random(seed)

        # Time range: now - 1 year to now + 6 months (18 months total)
        self.end_time = datetime.now() + timedelta(days=183)
        self.start_time = self.end_time - timedelta(days=548)

        # Deployment schedule — populated by generate_releases()
        self.deployment_schedule: Optional[DeploymentSchedule] = None

        # Derive ENVIRONMENT_CONFIG from PRIMARY_DEPLOYMENT_TARGETS
        global ENVIRONMENT_CONFIG
        ENVIRONMENT_CONFIG = build_environment_config_from_schedule(PRIMARY_DEPLOYMENT_TARGETS)
        env_summary = {e: len(c["targets"]) for e, c in ENVIRONMENT_CONFIG.items()}
        print(f"  Derived ENVIRONMENT_CONFIG from primary targets: {env_summary}")

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

    def generate_releases(self):
        """Generate builds and releases for all services across all primary deployment targets.

        Creates release timelines and deployment windows internally, replacing the
        external deployment_schedule.json dependency.
        """
        print("  Generating releases...")

        # Collect unique (application, stack, service) tuples from SERVICE_ACTIONS
        service_pairs = set()
        for action in SERVICE_ACTIONS:
            service_pairs.add((action.application, action.stack, action.service))

        # Parse primary targets into structured form, grouped by env
        targets_by_env: Dict[str, List[Dict]] = {}
        for target_id in PRIMARY_DEPLOYMENT_TARGETS:
            parts = target_id.split(':')
            env = parts[0]
            target_info = {
                "target_id": target_id,
                "provider": parts[1],
                "account": parts[2],
                "region": parts[3],
                "partition": parts[4],
                "target_type": parts[5],
                "target": parts[6],
            }
            if env not in targets_by_env:
                targets_by_env[env] = []
            targets_by_env[env].append(target_info)

        # Environment promotion delays (days)
        env_delays = {
            "dev": (0, 1),
            "int": (1, 3),
            "stg": (3, 7),
            "prod": (7, 14),
            "infra": (2, 5),
        }

        # Build release timelines and deployment windows
        release_timelines: Dict[Tuple[str, str, str, str], List[Tuple[datetime, str, int]]] = {}
        deployment_windows: Dict[Tuple[str, str, str, str], List[DeploymentWindow]] = {}

        # Fixture record collectors
        self.build_records = []
        self.build_artifact_records = []
        self.release_records = []
        self.release_artifact_records = []
        # Track latest release per deployment_id for deployment_current_release
        latest_release_by_deployment: Dict[str, Tuple[datetime, str]] = {}  # deployment_id -> (created_at, release_id)

        total_days = (self.end_time - self.start_time).days

        for application, stack, service in sorted(service_pairs):
            service_id = f"{application}:{stack}:{service}"
            app_stack_slug = f"{application}-{stack}"

            # Determine release cadence
            if service_id in HIGH_FREQUENCY_SERVICES:
                num_builds = 40
            elif self.rng.random() < 0.3:
                num_builds = 20
            else:
                num_builds = self.rng.randint(10, 15)

            build_num_start = self.rng.randint(50, 200)

            # Generate builds spread across the time range
            builds = []
            for i in range(num_builds):
                build_num = build_num_start + i
                # Spread evenly with jitter
                base_day = int(i * total_days / num_builds)
                jitter = self.rng.randint(-3, 3)
                day_offset = max(0, min(total_days - 1, base_day + jitter))
                build_created_at = self.start_time + timedelta(days=day_offset,
                                                                hours=self.rng.randint(8, 18),
                                                                minutes=self.rng.randint(0, 59))
                builds.append((build_num, build_created_at))

                # Collect build fixture record
                build_id = f"{service_id}:{build_num}"
                vcs_ref = hashlib.md5(f"{service_id}:{build_num}".encode()).hexdigest()[:7]
                ver = re.sub(r"[^0-9a-zA-Z.-]", '-', vcs_ref)
                self.build_records.append({
                    "id": build_id,
                    "service_id": service_id,
                    "build_num": build_num,
                    "vcs_ref": vcs_ref,
                    "ver": ver,
                    "created_at": build_created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "defaults": "{}",
                })

                # Collect build artifact records (5-7 per build)
                num_artifacts = self.rng.randint(5, 7)
                selected_artifacts = self.rng.sample(BUILD_ARTIFACT_NAMES, num_artifacts)
                for artifact_name in selected_artifacts:
                    artifact_created_at = build_created_at + timedelta(seconds=self.rng.uniform(0, 59))
                    if artifact_name == 'docker-image':
                        input_repo_id = f"git:{app_stack_slug}"
                        output_repo_id = f"ecr:{app_stack_slug}"
                        upload_path = f"{app_stack_slug}/{service}:{vcs_ref}"
                    elif artifact_name == 'helm-chart':
                        input_repo_id = f"git:{app_stack_slug}"
                        output_repo_id = f"helm:{app_stack_slug}"
                        upload_path = f"charts/{app_stack_slug}-{service}-{build_num}.tgz"
                    else:
                        input_repo_id = f"git:{app_stack_slug}"
                        output_repo_id = f"s3:{app_stack_slug}"
                        upload_path = f"artifacts/{service}/{build_num}/{artifact_name}"
                    self.build_artifact_records.append({
                        "id": f"{build_id}:{artifact_name}",
                        "build_id": build_id,
                        "input_repo_id": input_repo_id,
                        "output_repo_id": output_repo_id,
                        "name": artifact_name,
                        "upload_path": upload_path,
                        "data": "{}",
                        "created_at": artifact_created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    })

            # For each env, promote ~70% of builds to each target
            for env, targets in targets_by_env.items():
                delay_min, delay_max = env_delays.get(env, (0, 2))

                # Sort targets deterministically for stagger order
                sorted_targets = sorted(targets, key=lambda t: t["target_id"])

                for build_num, build_created_at in builds:
                    # ~70% of builds get promoted to each environment
                    if self.rng.random() > 0.7:
                        continue

                    # Promotion delay
                    delay_days = self.rng.uniform(delay_min, delay_max)
                    base_release_time = build_created_at + timedelta(days=delay_days)

                    # CI/CD pipeline delay: 3-10 minutes
                    cicd_delay = timedelta(minutes=self.rng.uniform(3, 10))

                    # Determine if this is a "bad" deployment (~3-5%)
                    is_bad_deploy = self.rng.random() < 0.04

                    for target_idx, target_info in enumerate(sorted_targets):
                        region = target_info["region"]
                        target_id = target_info["target_id"]

                        # Build release_id
                        deployment_id = f"{target_id}:social:{stack}:{service}:default"
                        release_id = f"{deployment_id}:{build_num}"
                        build_id = f"{service_id}:{build_num}"

                        # Release created_at: 1 min to 2 days after build
                        release_created_at = build_created_at + timedelta(
                            seconds=self.rng.uniform(60, 2 * 24 * 3600)
                        )

                        # Collect release fixture record
                        self.release_records.append({
                            "id": release_id,
                            "deployment_id": deployment_id,
                            "build_id": build_id,
                            "build_num": build_num,
                            "created_at": release_created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "defaults": "{}",
                        })

                        # Collect release artifact records (5-7 per release)
                        num_rel_artifacts = self.rng.randint(5, 7)
                        selected_rel_artifacts = self.rng.sample(RELEASE_ARTIFACT_NAMES, num_rel_artifacts)
                        for artifact_name in selected_rel_artifacts:
                            artifact_created_at = release_created_at + timedelta(seconds=self.rng.uniform(0, 59))
                            if artifact_name == 'manifest':
                                input_repo_id = f"ecr:{app_stack_slug}"
                                output_repo_id = f"s3:{app_stack_slug}"
                                upload_path = f"releases/{deployment_id}/{build_num}/manifest.yaml"
                            elif artifact_name == 'values':
                                input_repo_id = f"helm:{app_stack_slug}"
                                output_repo_id = f"s3:{app_stack_slug}"
                                upload_path = f"releases/{deployment_id}/{build_num}/values.yaml"
                            else:
                                input_repo_id = f"helm:{app_stack_slug}"
                                output_repo_id = f"s3:{app_stack_slug}"
                                upload_path = f"releases/{deployment_id}/{build_num}/{artifact_name}"
                            self.release_artifact_records.append({
                                "id": f"{release_id}:{artifact_name}",
                                "release_id": release_id,
                                "input_repo_id": input_repo_id,
                                "output_repo_id": output_repo_id,
                                "name": artifact_name,
                                "upload_path": upload_path,
                                "data": "{}",
                                "created_at": artifact_created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                            })

                        # Track latest release per deployment
                        prev = latest_release_by_deployment.get(deployment_id)
                        if prev is None or release_created_at > prev[0]:
                            latest_release_by_deployment[deployment_id] = (release_created_at, release_id)

                        # Add to release timeline
                        timeline_key = (env, region, stack, service)
                        if timeline_key not in release_timelines:
                            release_timelines[timeline_key] = []
                        release_timelines[timeline_key].append(
                            (base_release_time, release_id, build_num)
                        )

                        # Multi-region stagger for deployment windows
                        if target_idx == 0:
                            deploy_start = base_release_time + cicd_delay
                        else:
                            stagger = timedelta(minutes=self.rng.uniform(30, 60))
                            deploy_start = base_release_time + cicd_delay + (stagger * target_idx)

                        # Rolling restart duration
                        if is_bad_deploy:
                            deploy_duration = timedelta(minutes=self.rng.uniform(15, 45))
                            throughput_factor = self.rng.uniform(0.60, 0.75)
                            error_rate_boost = self.rng.uniform(0.08, 0.15)
                            latency_multiplier = self.rng.uniform(1.5, 2.5)
                        else:
                            deploy_duration = timedelta(minutes=self.rng.uniform(5, 15))
                            throughput_factor = self.rng.uniform(0.70, 0.85)
                            error_rate_boost = self.rng.uniform(0.02, 0.05)
                            latency_multiplier = self.rng.uniform(1.2, 1.5)

                        deploy_end = deploy_start + deploy_duration

                        window = DeploymentWindow(
                            deployment_id=deployment_id,
                            release_id=release_id,
                            stack=stack,
                            service=service,
                            env=env,
                            region=region,
                            start_time=deploy_start,
                            end_time=deploy_end,
                            throughput_factor=throughput_factor,
                            error_rate_boost=error_rate_boost,
                            latency_multiplier=latency_multiplier,
                        )

                        win_key = (stack, service, env, region)
                        if win_key not in deployment_windows:
                            deployment_windows[win_key] = []
                        deployment_windows[win_key].append(window)

        # Build deployment_current_release from tracked latest releases
        self.deployment_current_release = [
            {"deployment_id": dep_id, "release_id": rel_id}
            for dep_id, (_, rel_id) in sorted(latest_release_by_deployment.items())
        ]

        # Sort all timelines and windows
        for key in release_timelines:
            release_timelines[key].sort(key=lambda x: x[0])
        for key in deployment_windows:
            deployment_windows[key].sort(key=lambda w: w.start_time)

        # Create DeploymentSchedule
        self.deployment_schedule = DeploymentSchedule.from_generated_data(
            release_timelines, deployment_windows, PRIMARY_DEPLOYMENT_TARGETS
        )

        window_count = sum(len(w) for w in deployment_windows.values())
        timeline_count = sum(len(t) for t in release_timelines.values())
        bad_deploy_count = sum(
            1 for wins in deployment_windows.values()
            for w in wins if w.error_rate_boost >= 0.08
        )
        print(f"    Generated {timeline_count} release timeline entries, {window_count} deployment windows")
        print(f"    Bad deployments: {bad_deploy_count}")
        print(f"    Fixture records: {len(self.build_records)} builds, {len(self.build_artifact_records)} build artifacts, "
              f"{len(self.release_records)} releases, {len(self.release_artifact_records)} release artifacts, "
              f"{len(self.deployment_current_release)} deployment current releases")

    def write_fixture_tsvs(self, output_dir: Path):
        """Write build/release/artifact fixture TSV files to the output directory.

        Uses numbered filenames matching the generate_fixtures.py scheme (continuing
        from 32) so they can be loaded by the same bulk_insert pipeline.
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        def write_tsv(filename, table_name, columns, records):
            filepath = output_dir / filename
            with open(filepath, 'w') as f:
                f.write(f"# {table_name}\n")
                f.write(f"# Format: {chr(9).join(columns)}\n")
                f.write("# Generated by generate_monitoring_data.py\n\n")
                for rec in records:
                    f.write('\t'.join(str(rec[col]) for col in columns) + '\n')
            print(f"    Wrote {len(records)} records to {filepath}")

        write_tsv("33_builds.txt", "Builds",
                  ["id", "service_id", "build_num", "vcs_ref", "ver", "created_at", "defaults"],
                  self.build_records)

        write_tsv("34_build_artifacts.txt", "Build Artifacts",
                  ["id", "build_id", "input_repo_id", "output_repo_id", "name", "upload_path", "data", "created_at"],
                  self.build_artifact_records)

        write_tsv("35_releases.txt", "Releases",
                  ["id", "deployment_id", "build_id", "build_num", "created_at", "defaults"],
                  self.release_records)

        write_tsv("36_release_artifacts.txt", "Release Artifacts",
                  ["id", "release_id", "input_repo_id", "output_repo_id", "name", "upload_path", "data", "created_at"],
                  self.release_artifact_records)

        write_tsv("37_deployment_current_release.txt", "Deployment Current Release",
                  ["deployment_id", "release_id"],
                  self.deployment_current_release)

    def generate_incidents(self):
        """Generate service incidents throughout the time range.

        Each eligible service gets 8-20 incidents per year with severity tiers:
        - Minor (60%): 2-5% failure rate, 5-30 minutes
        - Moderate (30%): 5-15% failure rate, 30min-2hr
        - Major (10%): 15-30% failure rate, 1-4hr

        ~80% of incidents are region-specific, ~20% are multi-region.
        Incidents cluster in bursts (bad deploy → rollback → redeploy).
        """
        print("  Generating service incidents...")
        total_days = (self.end_time - self.start_time).days

        for service_key, cfg in INCIDENT_ELIGIBLE_SERVICES.items():
            num_incidents = self.rng.randint(8, 20)
            min_rate, max_rate = cfg["failure_rate_range"]

            i = 0
            while i < num_incidents:
                # Pick a random time in the range
                day_offset = self.rng.randint(1, max(1, total_days - 1))
                hour = self.rng.randint(0, 23)
                start = self.start_time + timedelta(days=day_offset, hours=hour)

                # Severity tier
                severity_roll = self.rng.random()
                if severity_roll < 0.60:
                    # Minor
                    failure_rate = self.rng.uniform(min_rate, min_rate + (max_rate - min_rate) * 0.3)
                    duration_minutes = self.rng.randint(5, 30)
                elif severity_roll < 0.90:
                    # Moderate
                    failure_rate = self.rng.uniform(min_rate + (max_rate - min_rate) * 0.3,
                                                   min_rate + (max_rate - min_rate) * 0.7)
                    duration_minutes = self.rng.randint(30, 120)
                else:
                    # Major
                    failure_rate = self.rng.uniform(min_rate + (max_rate - min_rate) * 0.7, max_rate)
                    duration_minutes = self.rng.randint(60, 240)

                end = start + timedelta(minutes=duration_minutes)

                # Region scoping: ~80% region-specific, ~20% multi-region
                region_scope = None  # None = all regions
                if self.rng.random() < 0.80:
                    # Pick a random region from the environment config
                    all_regions = []
                    for env_cfg in ENVIRONMENT_CONFIG.values():
                        for t in env_cfg.get("targets", []):
                            all_regions.append(t["region"])
                    if all_regions:
                        region_scope = self.rng.choice(all_regions)

                self.incidents.append(ServiceIncident(
                    service_key=service_key,
                    start_time=start,
                    end_time=end,
                    failure_rate=failure_rate,
                    error_codes=cfg["error_codes"],
                    error_type=cfg["error_type"],
                    error_message=cfg["error_message"],
                    region_scope=region_scope,
                ))
                i += 1

                # Incident clustering: 30% chance of a follow-up incident (burst)
                if i < num_incidents and self.rng.random() < 0.30:
                    # Follow-up 1-4 hours after the first incident ends
                    followup_gap = timedelta(minutes=self.rng.randint(60, 240))
                    followup_start = end + followup_gap
                    followup_duration = self.rng.randint(5, 60)
                    followup_end = followup_start + timedelta(minutes=followup_duration)
                    followup_rate = failure_rate * self.rng.uniform(0.3, 0.7)  # Usually less severe

                    self.incidents.append(ServiceIncident(
                        service_key=service_key,
                        start_time=followup_start,
                        end_time=followup_end,
                        failure_rate=followup_rate,
                        error_codes=cfg["error_codes"],
                        error_type=cfg["error_type"],
                        error_message=cfg["error_message"],
                        region_scope=region_scope,
                    ))
                    i += 1

        self.incidents.sort(key=lambda x: x.start_time)
        print(f"    Generated {len(self.incidents)} service incidents across {len(INCIDENT_ELIGIBLE_SERVICES)} services")

    def get_active_incident(self, service_key: str, timestamp: datetime, region: str = None) -> Optional[ServiceIncident]:
        """Check if there's an active incident affecting this service at this time."""
        for incident in self.incidents:
            if incident.start_time <= timestamp <= incident.end_time:
                if incident.service_key == service_key:
                    if incident.region_scope is None or incident.region_scope == region:
                        return incident
        return None

    def determine_error(self, action: ServiceAction, user: User, timestamp: datetime,
                        env: str = None, region: str = None) -> Optional[Dict]:
        """Determine if this request should fail and why.

        Error priority:
        1. Service incident (elevated error rate during incident window)
        2. Deployment dip (rolling restart errors)
        3. Stochastic errors (1-2% base rate, scaled by persona and region)
        """
        service_key = action.service_id

        # Apply regional error multiplier
        region_profile = get_region_profile(region) if region else DEFAULT_REGION_PROFILE
        regional_error_mult = region_profile["error_multiplier"]

        # 1. Service incident: check if any dependency has an active incident
        deps = SERVICE_DEPENDENCIES.get(service_key, [])
        for dep_key in deps:
            incident = self.get_active_incident(dep_key, timestamp, region)
            if incident and self.rng.random() < incident.failure_rate * regional_error_mult:
                dep_application, dep_stack, dep_service = dep_key.split(':')
                dep_action = ServiceAction(
                    category="internal", service=dep_service, stack=dep_stack,
                    action="internal", weight=1.0, base_latency_ms=10,
                    latency_stddev_ms=1, base_payload_bytes=1024,
                    payload_stddev_bytes=256, has_target_user=False,
                    has_object_id=False, object_type=None, is_write=False,
                )
                dep_release_id, _, _, _ = self.select_release(dep_action, timestamp)
                dep_deployment_id = deployment_id_from_release_id(dep_release_id)
                return {
                    "error_source": dep_deployment_id,
                    "error_type": incident.error_type,
                    "error_code": self.rng.choice(incident.error_codes),
                    "error_message": f"Downstream dependency failed: {incident.error_message}",
                    "downstream_request_id": uuid.uuid4().hex,
                }

        # Also check if this service itself has an incident (originating error)
        incident = self.get_active_incident(service_key, timestamp, region)
        if incident and self.rng.random() < incident.failure_rate * regional_error_mult:
            return {
                "error_source": None,
                "error_type": incident.error_type,
                "error_code": self.rng.choice(incident.error_codes),
                "error_message": incident.error_message,
                "downstream_request_id": None,
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
                    "error_message": "Service restarting during deployment",
                    "downstream_request_id": None,
                }

        # 3. Stochastic errors — base rate 1-2% (scaled by persona success_rate and regional multiplier)
        stochastic_error_rate = (1.0 - user.persona.success_rate) * regional_error_mult
        if self.rng.random() < stochastic_error_rate:
            # Dependency failure: blame a downstream service's deployment_id
            if deps and self.rng.random() < 0.4:
                dep_key = self.rng.choice(deps)
                dep_application, dep_stack, dep_service = dep_key.split(':')
                dep_action = ServiceAction(
                    category="internal", service=dep_service, stack=dep_stack,
                    action="internal", weight=1.0, base_latency_ms=10,
                    latency_stddev_ms=1, base_payload_bytes=1024,
                    payload_stddev_bytes=256, has_target_user=False,
                    has_object_id=False, object_type=None, is_write=False,
                )
                dep_release_id, _, _, _ = self.select_release(dep_action, timestamp)
                dep_deployment_id = deployment_id_from_release_id(dep_release_id)
                return {
                    "error_source": dep_deployment_id,
                    "error_type": "server",
                    "error_code": self.rng.choice(self.error_codes["server"]),
                    "error_message": "Downstream dependency failed",
                    "downstream_request_id": uuid.uuid4().hex,
                }

            # Originating error (no downstream to blame)
            if self.rng.random() < 0.6:
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
                "downstream_request_id": None,
            }

        return None

    def select_release(self, action: ServiceAction, timestamp: datetime) -> Tuple[str, str, str, Dict]:
        """Select a release_id for this request based on environment weights and time.

        Returns (release_id, env, region, target_info) tuple.
        """
        # Select environment based on weights
        envs = list(ENVIRONMENT_CONFIG.keys())
        weights = [ENVIRONMENT_CONFIG[e]["weight"] for e in envs]
        env = self.rng.choices(envs, weights=weights)[0]

        # Select target (and thus region) from available targets
        targets = ENVIRONMENT_CONFIG[env]["targets"]
        target_info = self.rng.choice(targets)
        region = target_info["region"]

        # Try deployment schedule first
        if self.deployment_schedule:
            scheduled_release = self.deployment_schedule.get_active_release_id(
                env, region, action.stack, action.service, timestamp
            )
            if scheduled_release:
                return (scheduled_release, env, region, target_info)

        # Fallback to synthetic release_id
        total_days = (self.end_time - self.start_time).days
        days_into_range = (timestamp - self.start_time).days
        range_progress = max(0, days_into_range) / max(1, total_days)
        base_release = 50 + int(range_progress * 200)
        service_hash = hash(f"{action.stack}:{action.service}") % 50
        release_num = base_release + service_hash

        return (generate_release_id(env, region, action.stack, action.service, release_num, target_info), env, region, target_info)

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

        # Pick a random day in the time range
        total_days = (self.end_time - self.start_time).days
        days_ago = self.rng.randint(0, max(0, total_days - 1))
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
        downstream_request_id = None

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
                downstream_request_id = error_info.get("downstream_request_id")
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
            downstream_request_id=downstream_request_id,
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
                release_id, env, region, target_info = self.select_release(action, timestamp)

                # Throughput dip: skip events during deployment windows
                if self.deployment_schedule:
                    window = self.deployment_schedule.get_active_deployment_window(
                        action.stack, action.service, env, region, timestamp
                    )
                    if window and self.rng.random() > window.throughput_factor:
                        continue

                error_info = self.determine_error(action, user, timestamp, env, region)
                success = error_info is None

                # Regional latency multiplier
                region_profile = get_region_profile(region)
                regional_latency_mult = region_profile["latency_multiplier"]

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
                    "deployment_latency_multiplier": deployment_latency_mult * regional_latency_mult,
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
        self, parent_event: dict, action: 'ServiceAction', user: 'User', timestamp: datetime,
        max_depth: int = 5, current_depth: int = 0, visited: Optional[set] = None
    ) -> List[dict]:
        """
        Recursively generate child span events for service dependencies (sequential format).

        Walks SERVICE_DEPENDENCIES to produce a full multi-level trace tree.
        """
        if current_depth >= max_depth:
            return []

        if visited is None:
            visited = set()

        service_key = action.service_id

        # Cycle detection
        if service_key in visited:
            return []
        visited = visited | {service_key}

        dependencies = SERVICE_DEPENDENCIES.get(service_key, [])

        if not dependencies:
            return []

        all_spans = []
        parent_latency = action.base_latency_ms * user.persona.latency_multiplier

        for i, dep_key in enumerate(dependencies):
            dep_application, dep_stack, dep_service = dep_key.split(':')

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
                application=dep_application,
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

            child_release_id, _, _, _ = self.select_release(child_action, child_timestamp)

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
            all_spans.append(child_event)

            # Recursively generate grandchild spans
            grandchild_spans = self._generate_child_spans_sequential(
                parent_event=child_event,
                action=child_action,
                user=user,
                timestamp=child_timestamp,
                max_depth=max_depth,
                current_depth=current_depth + 1,
                visited=visited,
            )
            all_spans.extend(grandchild_spans)

        return all_spans

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
                "region_scope": inc.region_scope,
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
                dict(ENVIRONMENT_CONFIG),
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
        is_parallel_format = "service" in events[0] if events else False

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
            service = event["service"] if is_parallel_format else event["action"].service
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

        is_parallel_format = "service" in events[0] if events else False

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
        downstream_request_id = None

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
                downstream_request_id = error_info.get("downstream_request_id")
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
            service=event["service"],
            stack=event["stack"],
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
            downstream_request_id=downstream_request_id,
        )

    def _generate_metrics_from_flat(self, event: dict) -> List[MetricEntry]:
        """Generate metrics from flat parallel event format"""
        metrics = []
        epoch_ts = event["timestamp"].timestamp()
        success = event["success"]

        base_tags = {
            "service": event["service"],
            "stack": event["stack"],
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
    parser.add_argument("--txt-output", metavar='DIR',
                        help="Directory for numbered fixture TSV files (default: same as --output)")

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
    print("=" * 70)

    generator = MonitoringDataGenerator(
        total_events=args.total_events,
        total_users=args.total_users,
        seed=args.seed,
        num_workers=args.workers,
    )

    # Set output path for streaming (parallel workers write directly to disk)
    generator._output_path = Path(args.output)

    generator.generate_users()
    generator.generate_releases()
    txt_output = Path(args.txt_output) if args.txt_output else Path(args.output)
    generator.write_fixture_tsvs(txt_output)
    generator.generate_incidents()
    events = generator.generate_events()

    # Write deployment schedule to output directory
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)
    schedule_file = output_path / "deployment_schedule.json"
    schedule_data = generator.deployment_schedule.to_serializable()
    schedule_data["primary_deployment_targets"] = PRIMARY_DEPLOYMENT_TARGETS
    with open(schedule_file, 'w') as f:
        json.dump(schedule_data, f, indent=2)
    print(f"  Wrote deployment schedule to {schedule_file}")

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