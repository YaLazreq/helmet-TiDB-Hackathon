# class Task(Base):
#     __tablename__ = "tasks"

#     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
#     title: Mapped[str] = mapped_column(String(100), nullable=False)
#     description: Mapped[Optional[str]] = mapped_column(String(255))
#     status: Mapped[str] = mapped_column(String(20), default="pending")
#     created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
#     )

#     user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
#     user: Mapped["User"] = relationship("User", back_populates="tasks")

#     def __repr__(self) -> str:
#         return f"<Task(id={self.id}, title={self.title}, status={self.status})>"
