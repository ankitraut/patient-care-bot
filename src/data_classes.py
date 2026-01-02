from datetime import datetime
from typing import Optional

from livekit.agents import JobContext
from pydantic import BaseModel, Field, ConfigDict
import enum


class SeverityLevel(enum.Enum):
    LOW = "LOW"
    MILD = "MILD"
    SEVERE = "SEVERE"
    NO_PROBLEMS = "NO_PROBLEMS"


class HealthStatus(BaseModel):
    severity: SeverityLevel
    problems: str


class MedicationStatus(BaseModel):
    taking_on_time: bool
    help_needed: bool
    details: str


class AgentTasks(enum.Enum):
    identify = "identify"
    wellbeing = "wellbeing"
    medication_adherence = "medication_adherence"


class AgentSummary(BaseModel):
    identity_verified: bool
    wellbeing: Optional[HealthStatus]
    medication_status: Optional[MedicationStatus]


class UserData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    ctx: Optional[JobContext] = None
    hospital_name: Optional[str] = None
    patient_name: Optional[str] = None
    patient_id: Optional[str] = None
    customer_phone: Optional[str] = None
    consultation_date: Optional[datetime] = None
    discharge_date: Optional[datetime] = None
    doctor_name: Optional[str] = None
    medical_issues: Optional[list[str]] = None
    prescription: Optional[list[str]] = None
    other_instructions: Optional[list[list[str]]] = None
