from sqlalchemy import Column, String, DateTime, ForeignKey, Date, func, Text, Integer, Numeric, Boolean
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class Board(Base):
    __tablename__ = "boards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="boards")
    columns = relationship("BoardColumn", back_populates="board", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Board(id={self.id}, name={self.name})>"


class BoardColumn(Base):
    __tablename__ = "board_columns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    board_id = Column(UUID(as_uuid=True), ForeignKey("boards.id"), nullable=False)
    name = Column(String, nullable=False)
    wip_limit = Column(Integer)
    position = Column(Integer, default=0)
    
    # Relationships
    board = relationship("Board", back_populates="columns")

    def __repr__(self):
        return f"<BoardColumn(id={self.id}, name={self.name})>"


class Sprint(Base):
    __tablename__ = "sprints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    state = Column(String, nullable=False, default="planned")  # planned/active/closed
    goal = Column(Text)
    
    # Relationships
    project = relationship("Project", back_populates="sprints")
    tasks = relationship("Task", back_populates="sprint")

    def __repr__(self):
        return f"<Sprint(id={self.id}, name={self.name}, state={self.state})>"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))
    sprint_id = Column(UUID(as_uuid=True), ForeignKey("sprints.id"))
    key = Column(String, nullable=False)  # e.g., MKT-101
    title = Column(String, nullable=False)
    description_md = Column(Text)
    type = Column(String, nullable=False, default="task")  # task/bug/epic/subtask
    status = Column(String, nullable=False)
    priority = Column(String, nullable=False, default="medium")
    assignee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reporter_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    story_points = Column(Numeric(5, 2))
    due_date = Column(Date)
    version = Column(Integer, nullable=False, default=1)  # OCC
    search_vector = Column(TSVECTOR)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="tasks")
    project = relationship("Project", back_populates="tasks")
    parent_task = relationship("Task", remote_side=[id], back_populates="subtasks")
    subtasks = relationship("Task", back_populates="parent_task", cascade="all, delete-orphan")
    sprint = relationship("Sprint", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_tasks")
    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="reported_tasks")
    
    # Task relationships
    outgoing_links = relationship("TaskLink", foreign_keys="TaskLink.from_task_id", back_populates="from_task", cascade="all, delete-orphan")
    incoming_links = relationship("TaskLink", foreign_keys="TaskLink.to_task_id", back_populates="to_task", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="task", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="task", cascade="all, delete-orphan")
    task_labels = relationship("TaskLabel", back_populates="task", cascade="all, delete-orphan")
    custom_field_values = relationship("TaskCustomField", back_populates="task", cascade="all, delete-orphan")
    history = relationship("TaskHistory", back_populates="task", cascade="all, delete-orphan")
    watchers = relationship("TaskWatcher", back_populates="task", cascade="all, delete-orphan")
    time_entries = relationship("TimeEntry", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Task(id={self.id}, key={self.key}, title={self.title})>"


class TaskLink(Base):
    __tablename__ = "task_links"

    from_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), primary_key=True)
    to_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), primary_key=True)
    link_type = Column(String, nullable=False, primary_key=True)  # blocks/is_blocked_by/relates
    
    # Relationships
    from_task = relationship("Task", foreign_keys=[from_task_id], back_populates="outgoing_links")
    to_task = relationship("Task", foreign_keys=[to_task_id], back_populates="incoming_links")

    def __repr__(self):
        return f"<TaskLink(from={self.from_task_id}, to={self.to_task_id}, type={self.link_type})>"


class Comment(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    author_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    body_md = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True))
    
    # Relationships
    task = relationship("Task", back_populates="comments")
    author = relationship("User", back_populates="comments")

    def __repr__(self):
        return f"<Comment(id={self.id}, task_id={self.task_id})>"


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    uploader_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    object_key = Column(String, nullable=False)  # S3 key
    original_filename = Column(String, nullable=False)
    mime_type = Column(String)
    size_bytes = Column(Integer)
    av_status = Column(String, default="pending")  # pending/clean/quarantined
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    task = relationship("Task", back_populates="attachments")
    project = relationship("Project")
    uploader = relationship("User", back_populates="attachments")

    def __repr__(self):
        return f"<Attachment(id={self.id}, filename={self.original_filename})>"


class Label(Base):
    __tablename__ = "labels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    name = Column(String, nullable=False)
    color_hex = Column(String)
    
    # Relationships
    task_labels = relationship("TaskLabel", back_populates="label", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Label(id={self.id}, name={self.name})>"


class TaskLabel(Base):
    __tablename__ = "task_labels"

    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), primary_key=True)
    label_id = Column(UUID(as_uuid=True), ForeignKey("labels.id"), primary_key=True)
    
    # Relationships
    task = relationship("Task", back_populates="task_labels")
    label = relationship("Label", back_populates="task_labels")


class CustomField(Base):
    __tablename__ = "custom_fields"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # text/number/select/user/date
    config_json = Column(Text)
    
    # Relationships
    task_values = relationship("TaskCustomField", back_populates="field", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CustomField(id={self.id}, name={self.name}, type={self.type})>"


class TaskCustomField(Base):
    __tablename__ = "task_custom_fields"

    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), primary_key=True)
    field_id = Column(UUID(as_uuid=True), ForeignKey("custom_fields.id"), primary_key=True)
    value_json = Column(Text)
    
    # Relationships
    task = relationship("Task", back_populates="custom_field_values")
    field = relationship("CustomField", back_populates="task_values")


class TaskHistory(Base):
    __tablename__ = "task_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    actor_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    changes = Column(Text)  # JSONB equivalent
    
    # Relationships
    task = relationship("Task", back_populates="history")
    actor = relationship("User")

    def __repr__(self):
        return f"<TaskHistory(id={self.id}, task_id={self.task_id})>"


class TaskWatcher(Base):
    __tablename__ = "task_watchers"

    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    task = relationship("Task", back_populates="watchers")
    user = relationship("User")

    def __repr__(self):
        return f"<TaskWatcher(task_id={self.task_id}, user_id={self.user_id})>"