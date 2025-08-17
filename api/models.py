from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey,
    Numeric, Text, JSON, Date
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    product_id = Column(Integer, primary_key=True, autoincrement=True)
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    base_price = Column(Numeric(10, 2), nullable=False)
    cost = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    reviews = relationship("Review", back_populates="product")
    competitor_prices = relationship("CompetitorPrice", back_populates="product")
    kpis = relationship("ProductDailyKpi", back_populates="product")

class Competitor(Base):
    __tablename__ = 'competitors'
    competitor_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    website_url = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CompetitorPrice(Base):
    __tablename__ = 'competitor_prices'
    price_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    competitor_id = Column(Integer, ForeignKey('competitors.competitor_id'), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    in_stock = Column(Boolean, default=True)
    observed_at = Column(DateTime(timezone=True), nullable=False)

    product = relationship("Product", back_populates="competitor_prices")
    competitor = relationship("Competitor")

class Review(Base):
    __tablename__ = 'reviews'
    review_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    source = Column(String(50))
    review_text = Column(Text)
    rating = Column(Integer)
    sentiment_label = Column(String(20))
    sentiment_score = Column(Float)
    reviewed_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="reviews")

class ProductDailyKpi(Base):
    __tablename__ = 'product_daily_kpi'
    kpi_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    kpi_date = Column(Date, nullable=False)
    revenue = Column(Numeric(12, 2))
    orders = Column(Integer)
    conversion_rate = Column(Float)
    average_price = Column(Numeric(10, 2))

    product = relationship("Product", back_populates="kpis")

class RLPolicy(Base):
    __tablename__ = 'rl_policies'
    policy_id = Column(Integer, primary_key=True, autoincrement=True)
    policy_name = Column(String(100), unique=True, nullable=False)
    algorithm = Column(String(50))
    hyperparameters = Column(JSON)
    storage_path = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PriceRecommendation(Base):
    __tablename__ = 'price_recommendations'
    recommendation_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    policy_id = Column(Integer, ForeignKey('rl_policies.policy_id'))
    recommended_price = Column(Numeric(10, 2), nullable=False)
    request_constraints = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product")
    policy = relationship("RLPolicy")
