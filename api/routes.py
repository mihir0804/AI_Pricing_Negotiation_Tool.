from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from . import schemas, services, database

router = APIRouter()

@router.post("/recommend_price", response_model=schemas.PriceRecommendation, tags=["Pricing"])
def recommend_price(
    request: schemas.PriceRequest, db: Session = Depends(database.get_db)
):
    """
    Recommends a price for a given product based on the active RL policy
    and user-defined constraints.
    """
    try:
        recommendation = services.get_price_recommendation(db=db, request=request)
        if not recommendation:
            raise HTTPException(status_code=404, detail="Product not found or model cannot make a recommendation.")
        return recommendation
    except services.ModelNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        # In a real app, you'd have more specific error handling
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.post("/what_if", response_model=schemas.WhatIfScenario, tags=["Pricing"])
def what_if_analysis(
    request: schemas.WhatIfRequest, db: Session = Depends(database.get_db)
):
    """
    Runs a what-if analysis to predict KPIs for a given product at a
    hypothetical price.
    """
    try:
        scenario = services.run_what_if_analysis(db=db, request=request)
        if not scenario:
            raise HTTPException(status_code=404, detail="Product not found or analysis failed.")
        return scenario
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@router.get("/products", response_model=List[schemas.Product], tags=["Products"])
def list_products(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    """
    Retrieves a list of all products.
    """
    products = services.get_products(db=db, skip=skip, limit=limit)
    return products


@router.get("/products/{product_id}", response_model=schemas.ProductDetails, tags=["Products"])
def get_product_details(product_id: int, db: Session = Depends(database.get_db)):
    """
    Retrieves detailed information for a single product, including recent
    competitor prices and sentiment.
    """
    product_details = services.get_product_details(db=db, product_id=product_id)
    if not product_details:
        raise HTTPException(status_code=404, detail="Product not found.")
    return product_details

@router.get("/products/{product_id}/kpis", response_model=List[schemas.ProductKpi], tags=["Products"])
def get_product_kpis(product_id: int, db: Session = Depends(database.get_db)):
    """
    Retrieves the latest daily KPIs for a given product.
    """
    kpis = services.get_kpis_for_product(db=db, product_id=product_id)
    return kpis

@router.get("/products/{product_id}/competitor_prices", response_model=List[schemas.CompetitorPrice], tags=["Products"])
def get_product_competitor_prices(product_id: int, db: Session = Depends(database.get_db)):
    """
    Retrieves the latest competitor prices for a given product.
    """
    prices = services.get_competitor_prices_for_product(db=db, product_id=product_id)
    # The service returns a list of Row objects, we need to convert them to dicts
    # so that Pydantic can validate them against the CompetitorPrice schema.
    return [
        {"competitor_name": p.competitor_name, "price": p.price, "observed_at": p.observed_at.isoformat()}
        for p in prices
    ]
