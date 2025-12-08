"""
Scenario Service for uDOS v1.0.18 - Apocalypse Adventures
Manages adventure scenarios, quests, and game state.
"""

import sqlite3
import os
import json
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any


class ScenarioType(Enum):
    """Types of scenarios"""
    STORY = "story"           # Narrative-driven adventure
    ROGUELIKE = "roguelike"   # Procedural dungeon crawler
    SURVIVAL = "survival"     # Survival challenge
    TUTORIAL = "tutorial"     # Teaching scenario
    CAMPAIGN = "campaign"     # Multi-part story


class QuestStatus(Enum):
    """Quest completion states"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"


class ScenarioService:
    """Service for managing scenarios and quests"""

    def __init__(self, data_dir: str = "data"):
        """Initialize scenario service with SQLite database"""
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.db_path = os.path.join(data_dir, "scenarios.db")
        self._init_database()

    def _init_database(self):
        """Create scenario database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Scenarios table - available scenarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scenarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                scenario_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                difficulty INTEGER DEFAULT 1,
                estimated_minutes INTEGER DEFAULT 30,
                xp_reward INTEGER DEFAULT 100,
                template_path TEXT,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Active sessions table - current playthrough state
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scenario_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario_id INTEGER,
                started_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_played TEXT DEFAULT CURRENT_TIMESTAMP,
                current_state TEXT,              -- JSON game state
                checkpoints TEXT,                -- JSON checkpoints
                completed BOOLEAN DEFAULT 0,
                play_time_minutes INTEGER DEFAULT 0,
                FOREIGN KEY (scenario_id) REFERENCES scenarios(id)
            )
        """)

        # Quests table - quest definitions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario_id INTEGER,
                quest_name TEXT NOT NULL,
                quest_type TEXT DEFAULT 'main',  -- main, side, optional
                title TEXT NOT NULL,
                description TEXT,
                objectives TEXT,                  -- JSON list of objectives
                rewards TEXT,                     -- JSON rewards
                prerequisites TEXT,               -- JSON quest dependencies
                FOREIGN KEY (scenario_id) REFERENCES scenarios(id)
            )
        """)

        # Quest progress table - player progress on quests
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quest_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                quest_id INTEGER,
                status TEXT DEFAULT 'not_started',
                objectives_completed TEXT,        -- JSON boolean array
                started_at TEXT,
                completed_at TEXT,
                FOREIGN KEY (session_id) REFERENCES scenario_sessions(id),
                FOREIGN KEY (quest_id) REFERENCES quests(id)
            )
        """)

        # Variables table - scenario variables and flags
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scenario_variables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                var_name TEXT NOT NULL,
                var_value TEXT,                   -- JSON serialized value
                var_type TEXT DEFAULT 'string',   -- string, number, boolean, object
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES scenario_sessions(id),
                UNIQUE(session_id, var_name)
            )
        """)

        conn.commit()
        conn.close()

    def register_scenario(self, name: str, scenario_type: ScenarioType,
                         title: str, description: str = "",
                         difficulty: int = 1, estimated_minutes: int = 30,
                         xp_reward: int = 100, template_path: str = "") -> Dict:
        """
        Register a new scenario.

        Args:
            name: Unique scenario identifier
            scenario_type: Type of scenario
            title: Display title
            description: Scenario description
            difficulty: 1-5 difficulty rating
            estimated_minutes: Expected completion time
            xp_reward: XP awarded on completion
            template_path: Path to scenario template file

        Returns:
            Dict with scenario details
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR IGNORE INTO scenarios
            (name, scenario_type, title, description, difficulty,
             estimated_minutes, xp_reward, template_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, scenario_type.value, title, description, difficulty,
              estimated_minutes, xp_reward, template_path))

        scenario_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return {
            "scenario_id": scenario_id,
            "name": name,
            "type": scenario_type.value,
            "title": title
        }

    def start_scenario(self, scenario_name: str, initial_state: Dict = None) -> Dict:
        """
        Start a new scenario session.

        Args:
            scenario_name: Name of scenario to start
            initial_state: Optional initial game state

        Returns:
            Dict with session details
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get scenario ID
        cursor.execute("SELECT id FROM scenarios WHERE name = ?", (scenario_name,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return {"error": f"Scenario '{scenario_name}' not found"}

        scenario_id = result[0]

        # Create session
        state_json = json.dumps(initial_state or {})
        cursor.execute("""
            INSERT INTO scenario_sessions
            (scenario_id, current_state, checkpoints)
            VALUES (?, ?, '[]')
        """, (scenario_id, state_json))

        session_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return {
            "session_id": session_id,
            "scenario_id": scenario_id,
            "scenario_name": scenario_name,
            "started": True
        }

    def save_state(self, session_id: int, state: Dict) -> Dict:
        """Save current scenario state"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        state_json = json.dumps(state)
        cursor.execute("""
            UPDATE scenario_sessions
            SET current_state = ?, last_played = ?
            WHERE id = ?
        """, (state_json, datetime.utcnow().isoformat(), session_id))

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return {
            "session_id": session_id,
            "saved": success
        }

    def load_state(self, session_id: int) -> Optional[Dict]:
        """Load scenario state"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT current_state FROM scenario_sessions WHERE id = ?
        """, (session_id,))

        result = cursor.fetchone()
        conn.close()

        if result and result[0]:
            return json.loads(result[0])
        return None

    def create_checkpoint(self, session_id: int, checkpoint_name: str,
                         state: Dict) -> Dict:
        """Create a named checkpoint"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get existing checkpoints
        cursor.execute("SELECT checkpoints FROM scenario_sessions WHERE id = ?",
                      (session_id,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return {"error": "Session not found"}

        checkpoints = json.loads(result[0]) if result[0] else []

        # Add new checkpoint
        checkpoint = {
            "name": checkpoint_name,
            "state": state,
            "timestamp": datetime.utcnow().isoformat()
        }
        checkpoints.append(checkpoint)

        # Save
        cursor.execute("""
            UPDATE scenario_sessions
            SET checkpoints = ?
            WHERE id = ?
        """, (json.dumps(checkpoints), session_id))

        conn.commit()
        conn.close()

        return {
            "checkpoint": checkpoint_name,
            "created": True,
            "total_checkpoints": len(checkpoints)
        }

    def restore_checkpoint(self, session_id: int, checkpoint_name: str) -> Optional[Dict]:
        """Restore state from checkpoint"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT checkpoints FROM scenario_sessions WHERE id = ?",
                      (session_id,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return None

        checkpoints = json.loads(result[0]) if result[0] else []

        # Find checkpoint
        for cp in reversed(checkpoints):  # Search from most recent
            if cp['name'] == checkpoint_name:
                # Restore state
                cursor.execute("""
                    UPDATE scenario_sessions
                    SET current_state = ?
                    WHERE id = ?
                """, (json.dumps(cp['state']), session_id))
                conn.commit()
                conn.close()
                return cp['state']

        conn.close()
        return None

    def set_variable(self, session_id: int, var_name: str, value: Any,
                    var_type: str = "string") -> Dict:
        """Set a scenario variable"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        value_json = json.dumps(value)
        cursor.execute("""
            INSERT OR REPLACE INTO scenario_variables
            (session_id, var_name, var_value, var_type, last_updated)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, var_name, value_json, var_type,
              datetime.now(timezone.utc).isoformat()))

        conn.commit()
        conn.close()

        return {
            "variable": var_name,
            "value": value,
            "type": var_type
        }

    def get_variable(self, session_id: int, var_name: str,
                    default: Any = None) -> Any:
        """Get a scenario variable"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT var_value, var_type FROM scenario_variables
            WHERE session_id = ? AND var_name = ?
        """, (session_id, var_name))

        result = cursor.fetchone()
        conn.close()

        if result:
            return json.loads(result[0])
        return default

    def get_all_variables(self, session_id: int) -> Dict[str, Any]:
        """Get all variables for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT var_name, var_value FROM scenario_variables
            WHERE session_id = ?
        """, (session_id,))

        results = cursor.fetchall()
        conn.close()

        variables = {}
        for var_name, var_value in results:
            variables[var_name] = json.loads(var_value)

        return variables

    def add_quest(self, scenario_id: int, quest_name: str, title: str,
                 description: str = "", objectives: List[str] = None,
                 quest_type: str = "main", rewards: Dict = None,
                 prerequisites: List[str] = None) -> Dict:
        """Add a quest to a scenario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        objectives_json = json.dumps(objectives or [])
        rewards_json = json.dumps(rewards or {})
        prereq_json = json.dumps(prerequisites or [])

        cursor.execute("""
            INSERT INTO quests
            (scenario_id, quest_name, quest_type, title, description,
             objectives, rewards, prerequisites)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (scenario_id, quest_name, quest_type, title, description,
              objectives_json, rewards_json, prereq_json))

        quest_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return {
            "quest_id": quest_id,
            "quest_name": quest_name,
            "title": title
        }

    def start_quest(self, session_id: int, quest_id: int) -> Dict:
        """Start a quest in the current session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get quest objectives count
        cursor.execute("SELECT objectives FROM quests WHERE id = ?", (quest_id,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return {"error": "Quest not found"}

        objectives = json.loads(result[0])
        objectives_completed = [False] * len(objectives)

        cursor.execute("""
            INSERT INTO quest_progress
            (session_id, quest_id, status, objectives_completed, started_at)
            VALUES (?, ?, 'in_progress', ?, ?)
        """, (session_id, quest_id, json.dumps(objectives_completed),
              datetime.utcnow().isoformat()))

        conn.commit()
        conn.close()

        return {
            "quest_id": quest_id,
            "status": "in_progress",
            "objectives_total": len(objectives)
        }

    def update_quest_objective(self, session_id: int, quest_id: int,
                               objective_index: int, completed: bool = True) -> Dict:
        """Update quest objective completion"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT objectives_completed FROM quest_progress
            WHERE session_id = ? AND quest_id = ?
        """, (session_id, quest_id))

        result = cursor.fetchone()
        if not result:
            conn.close()
            return {"error": "Quest progress not found"}

        objectives = json.loads(result[0])
        if objective_index < len(objectives):
            objectives[objective_index] = completed

        # Check if all objectives complete
        all_complete = all(objectives)
        new_status = "completed" if all_complete else "in_progress"

        cursor.execute("""
            UPDATE quest_progress
            SET objectives_completed = ?, status = ?, completed_at = ?
            WHERE session_id = ? AND quest_id = ?
        """, (json.dumps(objectives), new_status,
              datetime.utcnow().isoformat() if all_complete else None,
              session_id, quest_id))

        conn.commit()
        conn.close()

        return {
            "quest_id": quest_id,
            "objective": objective_index,
            "completed": completed,
            "all_complete": all_complete,
            "status": new_status
        }

    def get_quest_progress(self, session_id: int, quest_id: int) -> Optional[Dict]:
        """Get progress for a specific quest"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT qp.status, qp.objectives_completed, q.title, q.objectives
            FROM quest_progress qp
            JOIN quests q ON qp.quest_id = q.id
            WHERE qp.session_id = ? AND qp.quest_id = ?
        """, (session_id, quest_id))

        result = cursor.fetchone()
        conn.close()

        if not result:
            return None

        status, obj_completed, title, objectives = result

        return {
            "quest_id": quest_id,
            "title": title,
            "status": status,
            "objectives": json.loads(objectives),
            "objectives_completed": json.loads(obj_completed),
            "progress_percent": int(sum(json.loads(obj_completed)) /
                                   len(json.loads(obj_completed)) * 100)
        }

    def get_active_quests(self, session_id: int) -> List[Dict]:
        """Get all active quests for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT qp.quest_id, q.title, qp.status, qp.objectives_completed, q.objectives
            FROM quest_progress qp
            JOIN quests q ON qp.quest_id = q.id
            WHERE qp.session_id = ? AND qp.status = 'in_progress'
        """, (session_id,))

        results = cursor.fetchall()
        conn.close()

        quests = []
        for quest_id, title, status, obj_completed, objectives in results:
            obj_list = json.loads(objectives)
            completed_list = json.loads(obj_completed)

            quests.append({
                "quest_id": quest_id,
                "title": title,
                "status": status,
                "objectives": obj_list,
                "completed": completed_list,
                "progress": f"{sum(completed_list)}/{len(obj_list)}"
            })

        return quests

    def list_scenarios(self) -> List[Dict]:
        """List all available scenarios"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, scenario_type, title, description,
                   difficulty, estimated_minutes, xp_reward
            FROM scenarios
            ORDER BY difficulty, name
        """)

        results = cursor.fetchall()
        conn.close()

        scenarios = []
        for row in results:
            scenarios.append({
                "scenario_id": row[0],
                "name": row[1],
                "type": row[2],
                "title": row[3],
                "description": row[4],
                "difficulty": row[5],
                "estimated_minutes": row[6],
                "xp_reward": row[7]
            })

        return scenarios

    def get_session_info(self, session_id: int) -> Optional[Dict]:
        """Get information about a scenario session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT ss.scenario_id, s.name, s.title, ss.started_at,
                   ss.last_played, ss.completed, ss.play_time_minutes
            FROM scenario_sessions ss
            JOIN scenarios s ON ss.scenario_id = s.id
            WHERE ss.id = ?
        """, (session_id,))

        result = cursor.fetchone()
        conn.close()

        if not result:
            return None

        return {
            "session_id": session_id,
            "scenario_id": result[0],
            "scenario_name": result[1],
            "title": result[2],
            "started_at": result[3],
            "last_played": result[4],
            "completed": bool(result[5]),
            "play_time_minutes": result[6]
        }
