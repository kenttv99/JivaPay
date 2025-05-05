from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean, Enum, Text, Numeric, Index, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum

# Define the base class for declarative models
Base = declarative_base()

# Placeholder for future models (e.g., User, Order, etc.)
# class User(Base):
#     __tablename__ = 'users'
#     # ... columns ...

class ConfigurationSetting(Base):
    __tablename__ = 'configuration_settings'

    key = Column(String(255), primary_key=True, index=True, comment="Unique key identifying the configuration setting")
    value = Column(Text, nullable=False, comment="Value of the configuration setting (stored as text)")
    description = Column(Text, nullable=True, comment="Description of the setting for administrators")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="Timestamp of creation")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="Timestamp of last update")

    def __repr__(self):
        return f"<ConfigurationSetting(key='{self.key}', value='{self.value[:20]}...')>"

# Add other models below as needed
# ... 