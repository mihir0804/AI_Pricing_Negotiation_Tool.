from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

# ======== Request Schemas ========

class PriceRequest(BaseModel):
    product_id: int = Field(..., example=101, description="The unique identifier for the product.")
    constraints: Optional[Dict[str, Any]] = Field(None, example={"min_margin": 0.15}, description="Constraints for the pricing model.")

class WhatIfRequest(BaseModel):
    product_id: int = Field(..., example=101)
    price: float = Field(..., gt=0, example=299.99, description="The hypothetical price to evaluate.")

# ======== Response Schemas ========

class PriceRecommendation(BaseModel):
    product_id: int = Field(..., example=101)
    recommended_price: float = Field(..., example=249.99)
    policy_id: int = Field(..., example=1)
    confidence_score: Optional[float] = Field(None, example=0.95)

class WhatIfPrediction(BaseModel):
    orders: float = Field(..., example=50)
    revenue: float = Field(..., example=14999.50)
    profit_margin: float = Field(..., example=0.18)
    customer_sentiment_impact: float = Field(..., example=-0.02, description="Predicted change in sentiment score.")

class WhatIfScenario(BaseModel):
    request: WhatIfRequest
    prediction: WhatIfPrediction

# ======== Data Schemas for Dashboard/Internal Use ========

class Product(BaseModel):
    product_id: int
    sku: str
    name: str
    category: str
    base_price: float
    cost: float

    class Config:
        from_attributes = True # orm_mode = True for pydantic v1

class CompetitorPrice(BaseModel):
    competitor_name: str
    price: float
    observed_at: str

    class Config:
        from_attributes = True

class ProductDetails(Product):
    competitor_prices: List[CompetitorPrice] = []
    sentiment_score_30d: Optional[float] = None
    avg_orders_14d: Optional[float] = None

class ProductKpi(BaseModel):
    kpi_date: "date"
    revenue: float
    orders: int
    conversion_rate: Optional[float] = None
    average_price: Optional[float] = None

    class Config:
        from_attributes = True
