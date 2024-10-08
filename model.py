import typing
from typing import ForwardRef, cast
from enum import Enum

import functools
import databases
import pydantic
from datetime import datetime, timedelta
import ormar
import sqlalchemy

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

database = databases.Database(
    os.environ["LOCAL_DB_URL"],
    timeout=10,  # seconds
)
metadata = sqlalchemy.MetaData()

# Create a base OrmarConfig
base_ormar_config = ormar.OrmarConfig(
    metadata=metadata,
    database=database,
)


class DefaultModel(ormar.Model):
    ormar_config = base_ormar_config.copy(abstract=True)

    id: int = ormar.Integer(primary_key=True)
    created_at: datetime = ormar.DateTime(nullable=False, default=datetime.utcnow)
    updated_at: datetime = ormar.DateTime(nullable=False, default=datetime.utcnow)
    model_config = dict(protected_namespaces=())

    async def update(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return await super().update(*args, **kwargs)

# deprecated
class Challenge(DefaultModel):
    ormar_config = base_ormar_config.copy(tablename="challenge_environments")

    name: str = ormar.String(nullable=False, unique=True, max_length=1_000_000)
    image_name: str = ormar.String(nullable=False, max_length=1_000_000)
    golden_output: str = ormar.String(nullable=False, max_length=1_000_000)


class RunTerminalInteropProtocol(str, Enum):
    CLOSING_ANGLE_BRACKET = "CLOSING_ANGLE_BRACKET"
    MARKDOWN_CODE_BLOCKS = "MARKDOWN_CODE_BLOCKS"
    JSON_BASIC = "JSON_BASIC"
    XML_TAGS = "XML_TAGS"


class TaskConfigSnapshot(DefaultModel):
    ormar_config = base_ormar_config.copy(
        tablename="task_config_snapshots",
        constraints=[ormar.UniqueColumns("name", "toml_content")],
    )

    name: str = ormar.String(nullable=False, max_length=1_000_000)
    # must be normalized
    toml_content: str = ormar.String(nullable=False, max_length=1_000_000)
    is_most_recent: bool = ormar.Boolean(nullable=True)


class ElicitationSnapshot(DefaultModel):
    ormar_config = base_ormar_config.copy(
        tablename="elicitation_snapshots",
        constraints=[ormar.UniqueColumns("toml_content")],
    )

    # must be normalized
    toml_content: str = ormar.String(nullable=False, max_length=1_000_000)
    is_most_recent: bool = ormar.Boolean(nullable=True)


class EvalRun(DefaultModel):
    ormar_config = base_ormar_config.copy(tablename="eval_runs_v2")

    # oneof
    # deprecated
    challenge: Challenge = ormar.ForeignKey(
        Challenge,
        nullable=True,
        related_name="runs",
        ondelete=ormar.ReferentialAction.CASCADE,
    )
    task_config_snapshot: TaskConfigSnapshot = ormar.ForeignKey(
        TaskConfigSnapshot,
        nullable=True,
        related_name="runs",
        ondelete=ormar.ReferentialAction.CASCADE,
    )
    elicitation_snapshot: ElicitationSnapshot = ormar.ForeignKey(
        ElicitationSnapshot,
        nullable=True,
        related_name="runs",
        ondelete=ormar.ReferentialAction.CASCADE,
    )

    model: str = ormar.String(nullable=False, max_length=1_000_000)

    # model params
    # deprecated
    model_seed: int = ormar.Integer(nullable=True)
    # deprecated
    model_context_length: int = ormar.Integer(nullable=True)
    # deprecated
    model_force_json: bool = ormar.Boolean(nullable=True)

    # run params
    # deprecated
    run_max_turn_number: int = ormar.Integer(nullable=True)
    # deprecated
    run_prefilled_messages = ormar.JSON(nullable=True)
    # deprecated
    run_terminal_interop_protocol: RunTerminalInteropProtocol = ormar.Enum(
        nullable=True, enum_class=RunTerminalInteropProtocol
    )

    class RunStatus(str, Enum):
        # unfinished, result not available
        RUNNING = "RUNNING"
        # found the flag within the alloted turns
        SUCCESS = "SUCCESS"
        # ran out of time or broke the env
        FAILURE = "FAILURE"
        # system error, shouldn't count
        ERROR = "ERROR"
        # e.g. o1 refusal
        REFUSED = "REFUSED"

    status: RunStatus = ormar.Enum(enum_class=RunStatus, nullable=False)
    exception_stacktrace: str = ormar.String(nullable=True, max_length=1_000_000)


class ChatMessage(DefaultModel):
    ormar_config = base_ormar_config.copy(tablename="chat_messages_v2")

    run: EvalRun = ormar.ForeignKey(
        EvalRun,
        nullable=False,
        related_name="messages",
        ondelete=ormar.ReferentialAction.CASCADE,
        index=True,
    )
    ordinal: int = ormar.Integer(nullable=False)
    role: str = ormar.String(nullable=False, max_length=1_000_000)
    content: str = ormar.String(nullable=False, max_length=1_000_000)
    is_prefilled: bool = ormar.Boolean(nullable=False)
    underlying_communication: str = ormar.String(nullable=True, max_length=1_000_000)
