from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from src.dependencies import get_db, get_product_cache_service
from src.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from src.services.cache_service import ProductCacheService
from src.services.product_repository import (
    create_product,
    delete_product,
    get_product_by_id,
    update_product,
)

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product_endpoint(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    cache_service: ProductCacheService = Depends(get_product_cache_service),
):
    product = create_product(db, payload)
    response = ProductResponse.model_validate(product)
    cache_service.invalidate_product_cache(response.id)
    return response


@router.get("/{product_id}", response_model=ProductResponse)
def get_product_endpoint(
    product_id: str,
    db: Session = Depends(get_db),
    cache_service: ProductCacheService = Depends(get_product_cache_service),
):
    cached_product = cache_service.get_product_from_cache(product_id)
    if cached_product is not None:
        return cached_product

    product = get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    response = ProductResponse.model_validate(product)
    cache_service.set_product_in_cache(response)
    return response


@router.put("/{product_id}", response_model=ProductResponse)
def update_product_endpoint(
    product_id: str,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    cache_service: ProductCacheService = Depends(get_product_cache_service),
):
    if not payload.model_dump(exclude_unset=True):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one field is required")

    product = get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    updated_product = update_product(db, product, payload)
    cache_service.invalidate_product_cache(product_id)
    return ProductResponse.model_validate(updated_product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_endpoint(
    product_id: str,
    db: Session = Depends(get_db),
    cache_service: ProductCacheService = Depends(get_product_cache_service),
):
    product = get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    delete_product(db, product)
    cache_service.invalidate_product_cache(product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
