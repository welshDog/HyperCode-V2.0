import time
from typing import Dict, Any

class PulseAgent:
    """
    PULSE: The Cognitive Energy Governor
    Responsibility: Monitoring user energy levels and flow state.
    """
    def __init__(self):
        self.name = "PULSE"
        self.role = "Energy Governor"
        self.energy_level = 100 # 0-100
        self.flow_state = False
        self.last_activity = time.time()
        self.keystroke_history = [] # Timestamp of last 100 keystrokes

    async def monitor_activity(self, activity_type: str, data: Any):
        """
        Ingests user activity data (keystrokes, navigation, pauses) to update energy model.
        """
        current_time = time.time()
        pause_duration = current_time - self.last_activity
        self.last_activity = current_time

        # Simple Heuristic Model for Prototype
        if activity_type == "keystroke":
            self.keystroke_history.append(current_time)
            if len(self.keystroke_history) > 20:
                # Calculate typing speed (approx)
                duration = self.keystroke_history[-1] - self.keystroke_history[0]
                wpm_proxy = (20 / duration) * 60
                
                if wpm_proxy > 80:
                    self.flow_state = True
                    print(f"[{self.name}] 🌊 FLOW STATE DETECTED (High WPM)")
                else:
                    self.flow_state = False
                
                self.keystroke_history.pop(0)

        elif activity_type == "pause":
            if pause_duration > 60: # 1 minute pause
                self.energy_level -= 5
                print(f"[{self.name}] 🔋 Energy dip detected (Long Pause). Level: {self.energy_level}%")

    async def get_energy_report(self) -> Dict[str, Any]:
        return {
            "energy_level": self.energy_level,
            "is_flow_state": self.flow_state,
            "recommendation": "Take a break" if self.energy_level < 40 else "Keep pushing"
        }
