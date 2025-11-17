"""
Survival Service for uDOS v1.0.18 - Apocalypse Adventures
Manages survival variables, health tracking, and environmental conditions.
"""

import sqlite3
import os
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple


class SurvivalStat(Enum):
    """Core survival statistics"""
    HEALTH = "health"           # 0-100, critical below 20
    HUNGER = "hunger"           # 0-100, critical above 80
    THIRST = "thirst"           # 0-100, critical above 90
    FATIGUE = "fatigue"         # 0-100, critical above 80
    RADIATION = "radiation"     # 0-100, dangerous above 50
    TEMPERATURE = "temperature" # -20 to 50°C, danger outside 0-40


class StatusEffect(Enum):
    """Status effects that can be active"""
    HEALTHY = "healthy"
    HUNGRY = "hungry"
    STARVING = "starving"
    THIRSTY = "thirsty"
    DEHYDRATED = "dehydrated"
    TIRED = "tired"
    EXHAUSTED = "exhausted"
    IRRADIATED = "irradiated"
    POISONED = "poisoned"
    INJURED = "injured"
    SICK = "sick"
    FREEZING = "freezing"
    OVERHEATING = "overheating"
    BLEEDING = "bleeding"
    INFECTED = "infected"


class SurvivalService:
    """Service for managing survival state and variables"""

    def __init__(self, data_dir: str = "data"):
        """Initialize survival service with SQLite database"""
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.db_path = os.path.join(data_dir, "survival.db")
        self._init_database()

    def _init_database(self):
        """Create survival database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Survival stats table - current values
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS survival_stats (
                stat_name TEXT PRIMARY KEY,
                current_value REAL DEFAULT 0,
                max_value REAL DEFAULT 100,
                min_value REAL DEFAULT 0,
                critical_threshold REAL DEFAULT 20,
                warning_threshold REAL DEFAULT 40,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Status effects table - active conditions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS status_effects (
                effect_name TEXT PRIMARY KEY,
                severity INTEGER DEFAULT 1,     -- 1-5 scale
                started_at TEXT DEFAULT CURRENT_TIMESTAMP,
                duration_minutes INTEGER,        -- NULL = indefinite
                description TEXT
            )
        """)

        # Survival events log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS survival_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                stat_affected TEXT,
                value_change REAL,
                description TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Initialize default stats
        default_stats = [
            ("health", 100, 100, 0, 20, 40),
            ("hunger", 0, 100, 0, 80, 60),
            ("thirst", 0, 100, 0, 90, 70),
            ("fatigue", 0, 100, 0, 80, 60),
            ("radiation", 0, 100, 0, 50, 30),
            ("temperature", 20, 50, -20, 5, 10),  # Celsius
        ]

        for stat_name, current, max_val, min_val, critical, warning in default_stats:
            cursor.execute("""
                INSERT OR IGNORE INTO survival_stats
                (stat_name, current_value, max_value, min_value, critical_threshold, warning_threshold)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (stat_name, current, max_val, min_val, critical, warning))

        conn.commit()
        conn.close()

    def get_stat(self, stat: SurvivalStat) -> Dict:
        """Get current value and info for a survival stat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT current_value, max_value, min_value,
                   critical_threshold, warning_threshold
            FROM survival_stats
            WHERE stat_name = ?
        """, (stat.value,))

        result = cursor.fetchone()
        conn.close()

        if not result:
            return {"error": f"Stat {stat.value} not found"}

        current, max_val, min_val, critical, warning = result

        # Determine status
        if stat.value in ['hunger', 'thirst', 'fatigue', 'radiation']:
            # Higher is worse
            if current >= critical:
                status = "critical"
            elif current >= warning:
                status = "warning"
            else:
                status = "normal"
        elif stat.value == 'health':
            # Lower is worse
            if current <= critical:
                status = "critical"
            elif current <= warning:
                status = "warning"
            else:
                status = "normal"
        elif stat.value == 'temperature':
            # Range-based
            if current <= 0 or current >= 40:
                status = "critical"
            elif current <= 10 or current >= 35:
                status = "warning"
            else:
                status = "normal"
        else:
            status = "normal"

        return {
            "stat": stat.value,
            "current": current,
            "max": max_val,
            "min": min_val,
            "status": status,
            "percent": int((current / max_val) * 100) if max_val > 0 else 0
        }

    def update_stat(self, stat: SurvivalStat, change: float,
                    reason: str = "") -> Dict:
        """
        Update a survival stat by a delta amount.

        Args:
            stat: Stat to update
            change: Amount to change (positive or negative)
            reason: Description of why stat changed

        Returns:
            Dict with old/new values and effects triggered
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get current value and limits
        cursor.execute("""
            SELECT current_value, max_value, min_value
            FROM survival_stats
            WHERE stat_name = ?
        """, (stat.value,))

        result = cursor.fetchone()
        if not result:
            conn.close()
            return {"error": f"Stat {stat.value} not found"}

        current, max_val, min_val = result
        new_value = max(min_val, min(max_val, current + change))

        # Update stat
        cursor.execute("""
            UPDATE survival_stats
            SET current_value = ?, last_updated = ?
            WHERE stat_name = ?
        """, (new_value, datetime.now().isoformat(), stat.value))

        # Log event
        cursor.execute("""
            INSERT INTO survival_events
            (event_type, stat_affected, value_change, description)
            VALUES (?, ?, ?, ?)
        """, ("stat_change", stat.value, change, reason))

        conn.commit()
        conn.close()

        # Check for status effects
        effects = self._check_status_effects(stat, new_value)

        return {
            "stat": stat.value,
            "old_value": current,
            "new_value": new_value,
            "change": change,
            "reason": reason,
            "effects_triggered": effects
        }

    def set_stat(self, stat: SurvivalStat, value: float,
                 reason: str = "") -> Dict:
        """
        Set a survival stat to an absolute value.

        Args:
            stat: Stat to set
            value: New value
            reason: Description of change

        Returns:
            Dict with old/new values
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get current value and limits
        cursor.execute("""
            SELECT current_value, max_value, min_value
            FROM survival_stats
            WHERE stat_name = ?
        """, (stat.value,))

        result = cursor.fetchone()
        if not result:
            conn.close()
            return {"error": f"Stat {stat.value} not found"}

        current, max_val, min_val = result
        new_value = max(min_val, min(max_val, value))

        # Update stat
        cursor.execute("""
            UPDATE survival_stats
            SET current_value = ?, last_updated = ?
            WHERE stat_name = ?
        """, (new_value, datetime.now().isoformat(), stat.value))

        # Log event
        cursor.execute("""
            INSERT INTO survival_events
            (event_type, stat_affected, value_change, description)
            VALUES (?, ?, ?, ?)
        """, ("stat_set", stat.value, new_value - current, reason))

        conn.commit()
        conn.close()

        return {
            "stat": stat.value,
            "old_value": current,
            "new_value": new_value,
            "reason": reason
        }

    def get_all_stats(self) -> Dict[str, Dict]:
        """Get all survival stats"""
        stats = {}
        for stat in SurvivalStat:
            stats[stat.value] = self.get_stat(stat)
        return stats

    def add_status_effect(self, effect: StatusEffect, severity: int = 1,
                          duration_minutes: Optional[int] = None,
                          description: str = "") -> Dict:
        """
        Add a status effect.

        Args:
            effect: Effect to add
            severity: 1-5 scale
            duration_minutes: How long effect lasts (None = indefinite)
            description: Effect description

        Returns:
            Dict with effect details
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if effect already exists
        cursor.execute("SELECT started_at FROM status_effects WHERE effect_name = ?", (effect.value,))
        existing = cursor.fetchone()

        if existing:
            # Update existing effect, preserve started_at
            cursor.execute("""
                UPDATE status_effects
                SET severity = ?, duration_minutes = ?, description = ?
                WHERE effect_name = ?
            """, (severity, duration_minutes, description, effect.value))
        else:
            # Insert new effect with explicit UTC timestamp
            cursor.execute("""
                INSERT INTO status_effects
                (effect_name, severity, started_at, duration_minutes, description)
                VALUES (?, ?, ?, ?, ?)
            """, (effect.value, severity, datetime.utcnow().isoformat(), duration_minutes, description))

        # Log event
        cursor.execute("""
            INSERT INTO survival_events
            (event_type, description)
            VALUES (?, ?)
        """, ("effect_added", f"Status effect: {effect.value} (severity {severity})"))

        conn.commit()
        conn.close()

        return {
            "effect": effect.value,
            "severity": severity,
            "duration": duration_minutes,
            "description": description
        }

    def remove_status_effect(self, effect: StatusEffect) -> Dict:
        """Remove a status effect"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM status_effects
            WHERE effect_name = ?
        """, (effect.value,))

        removed = cursor.rowcount > 0

        if removed:
            cursor.execute("""
                INSERT INTO survival_events
                (event_type, description)
                VALUES (?, ?)
            """, ("effect_removed", f"Status effect cleared: {effect.value}"))

        conn.commit()
        conn.close()

        return {
            "effect": effect.value,
            "removed": removed
        }

    def get_active_effects(self) -> List[Dict]:
        """Get all active status effects"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT effect_name, severity, started_at, duration_minutes, description
            FROM status_effects
            ORDER BY severity DESC, started_at DESC
        """)

        results = cursor.fetchall()
        conn.close()

        effects = []
        for row in results:
            effect_name, severity, started_at, duration, description = row

            # Calculate time remaining
            if duration:
                # Parse timestamp (handle both ISO format and SQLite format)
                if ' ' in started_at:
                    started = datetime.fromisoformat(started_at.replace(' ', 'T'))
                else:
                    started = datetime.fromisoformat(started_at)

                expires = started + timedelta(minutes=duration)
                now = datetime.utcnow()  # Use UTC to match stored timestamps
                remaining = (expires - now).total_seconds() / 60
                expired = remaining <= 0
            else:
                remaining = None
                expired = False

            effects.append({
                "effect": effect_name,
                "severity": severity,
                "started_at": started_at,
                "duration": duration,
                "remaining_minutes": remaining,
                "expired": expired,
                "description": description
            })

        return effects

    def clear_expired_effects(self) -> List[str]:
        """Remove expired status effects"""
        active = self.get_active_effects()
        cleared = []

        for effect in active:
            if effect['expired']:
                self.remove_status_effect(StatusEffect(effect['effect']))
                cleared.append(effect['effect'])

        return cleared

    def get_survival_events(self, limit: int = 20) -> List[Dict]:
        """Get recent survival events"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT event_type, stat_affected, value_change, description, timestamp
            FROM survival_events
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

        results = cursor.fetchall()
        conn.close()

        events = []
        for row in results:
            events.append({
                "type": row[0],
                "stat": row[1],
                "change": row[2],
                "description": row[3],
                "timestamp": row[4]
            })

        return events

    def _check_status_effects(self, stat: SurvivalStat, value: float) -> List[str]:
        """Check if stat value triggers status effects"""
        effects = []

        if stat == SurvivalStat.HEALTH:
            if value <= 20:
                self.add_status_effect(StatusEffect.INJURED, severity=3,
                                      description="Critically low health")
                effects.append("injured")
            elif value <= 40:
                self.add_status_effect(StatusEffect.INJURED, severity=1,
                                      description="Low health")
                effects.append("injured")

        elif stat == SurvivalStat.HUNGER:
            if value >= 90:
                self.add_status_effect(StatusEffect.STARVING, severity=3,
                                      description="Critically hungry")
                effects.append("starving")
            elif value >= 70:
                self.add_status_effect(StatusEffect.HUNGRY, severity=2,
                                      description="Very hungry")
                effects.append("hungry")

        elif stat == SurvivalStat.THIRST:
            if value >= 90:
                self.add_status_effect(StatusEffect.DEHYDRATED, severity=3,
                                      description="Severely dehydrated")
                effects.append("dehydrated")
            elif value >= 70:
                self.add_status_effect(StatusEffect.THIRSTY, severity=2,
                                      description="Very thirsty")
                effects.append("thirsty")

        elif stat == SurvivalStat.FATIGUE:
            if value >= 90:
                self.add_status_effect(StatusEffect.EXHAUSTED, severity=3,
                                      description="Completely exhausted")
                effects.append("exhausted")
            elif value >= 70:
                self.add_status_effect(StatusEffect.TIRED, severity=2,
                                      description="Very tired")
                effects.append("tired")

        elif stat == SurvivalStat.RADIATION:
            if value >= 70:
                self.add_status_effect(StatusEffect.IRRADIATED, severity=3,
                                      description="Severe radiation sickness")
                effects.append("irradiated")
            elif value >= 40:
                self.add_status_effect(StatusEffect.IRRADIATED, severity=1,
                                      description="Radiation exposure")
                effects.append("irradiated")

        elif stat == SurvivalStat.TEMPERATURE:
            if value <= 0:
                self.add_status_effect(StatusEffect.FREEZING, severity=3,
                                      description="Hypothermia danger")
                effects.append("freezing")
            elif value <= 10:
                self.add_status_effect(StatusEffect.FREEZING, severity=1,
                                      description="Very cold")
                effects.append("freezing")
            elif value >= 40:
                self.add_status_effect(StatusEffect.OVERHEATING, severity=3,
                                      description="Heat stroke danger")
                effects.append("overheating")
            elif value >= 35:
                self.add_status_effect(StatusEffect.OVERHEATING, severity=1,
                                      description="Very hot")
                effects.append("overheating")

        return effects

    def apply_time_decay(self, hours: float = 1.0) -> Dict:
        """
        Apply natural stat decay over time.

        Args:
            hours: Number of hours passed

        Returns:
            Dict with all stat changes
        """
        changes = {}

        # Hunger increases ~10 per hour
        hunger_change = 10 * hours
        changes['hunger'] = self.update_stat(SurvivalStat.HUNGER, hunger_change,
                                             f"Time passed: {hours}h")

        # Thirst increases ~15 per hour (faster than hunger)
        thirst_change = 15 * hours
        changes['thirst'] = self.update_stat(SurvivalStat.THIRST, thirst_change,
                                             f"Time passed: {hours}h")

        # Fatigue increases ~8 per hour
        fatigue_change = 8 * hours
        changes['fatigue'] = self.update_stat(SurvivalStat.FATIGUE, fatigue_change,
                                              f"Time passed: {hours}h")

        # Health decreases if hungry/thirsty/exhausted
        stats = self.get_all_stats()
        health_change = 0
        if stats['hunger']['current'] > 80:
            health_change -= 5 * hours
        if stats['thirst']['current'] > 90:
            health_change -= 10 * hours
        if stats['fatigue']['current'] > 80:
            health_change -= 3 * hours

        if health_change < 0:
            changes['health'] = self.update_stat(SurvivalStat.HEALTH, health_change,
                                                 "Deteriorating conditions")

        return changes
