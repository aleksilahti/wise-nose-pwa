"""
class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=True)

    questions = db.relationship("Question", back_populates="topic")


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topic.id", ondelete="SET NULL"))
    question_text = db.Column(db.String(256), nullable=False)
    image_src = db.Column(db.String(256), nullable=True)

    topic = db.relationship("Topic", back_populates="questions")

    quizzes = db.relationship("Quiz", secondary=quiz_questions, back_populates="questions")

    answers = db.relationship("Answer", cascade="all, delete-orphan", back_populates="question")
    comments = db.relationship("Comment", cascade="all, delete-orphan", back_populates="question")


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id", ondelete="CASCADE"))
    answer_text = db.Column(db.String(256), nullable=False)
    explanation_text = db.Column(db.String(256), nullable=True)
    is_correct = db.Column(db.Integer, nullable=False)  # Boolean value 1 or 0

    question = db.relationship("Question", back_populates="answers")


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id", ondelete="CASCADE"), nullable=False)
    comment_text = db.Column(db.String(256), nullable=False)

    user = db.relationship("User", back_populates="comments")
    question = db.relationship("Question", back_populates="comments")

"""
from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), unique=True, nullable=False)
    email = db.Column(db.String(256), nullable=False)
    pw_hash = db.Column(db.String(256), nullable=False)

    sessions = db.relationship("Session", back_populates="user")
    samples = db.relationship("Sample", back_populates="user")

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    created = db.Column(db.DateTime, nullable=False)
    completed = db.Column(db.DateTime, nullable=True)
    result = db.Column(db.String(256), nullable=True)
    number_of_samples = db.Column(db.Integer, nullable=False)

    user = db.relationship("User", back_populates="sessions")
    samples = db.relationship("Sample", back_populates="session")

class Sample(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    added_by = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    is_correct = db.Column(db.Integer, nullable=False)  # Boolean value 1 or 0
    session_id = db.Column(db.Integer, db.ForeignKey("session.id", ondelete="SET NULL"), nullable=True)
    number_in_session = db.Column(db.Integer, nullable=True)
    dog_answer = db.Column(db.String(144), nullable=True)

    session = db.relationship("Session", back_populates="samples")
    user = db.relationship("User", back_populates="samples")
