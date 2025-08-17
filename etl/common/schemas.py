from pydantic import BaseModel, Field
from datetime import datetime

class CompetitorPriceRecord(BaseModel):
    """
    Schema for a single scraped competitor price point.
    """
    sku: str = Field(..., description="Product SKU")
    competitor_name: str = Field(..., description="Name of the competitor")
    price: float = Field(..., gt=0, description="Observed price")
    in_stock: bool = Field(True, description="Whether the product is in stock")
    observed_at: datetime = Field(default_factory=datetime.utcnow)

class ReviewRecord(BaseModel):
    """
    Schema for a product review.
    """
    product_id: int
    source: str
    review_text: str
    rating: int = Field(..., ge=1, le=5)
    reviewed_at: datetime
