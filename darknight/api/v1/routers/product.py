from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from darknight.db import Session, crud, get_db
from darknight.models.admin import Admin
from darknight.models.product import ProductCreate, ProductModify, ProductResponse

router = APIRouter(tags=["Product"])

_CONFLICT_DETAIL = "Product slug already exists"


def _product_or_404(db: Session, product_id: int):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/products", response_model=list[ProductResponse])
def list_products(db: Session = Depends(get_db), _: Admin = Depends(Admin.get_current)):
    return crud.list_products(db)


@router.post("/product", response_model=ProductResponse)
def add_product(
    body: ProductCreate,
    db: Session = Depends(get_db),
    _: Admin = Depends(Admin.check_sudo_admin),
):
    try:
        return crud.create_product(db, body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=_CONFLICT_DETAIL)


@router.get("/product/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(Admin.get_current),
):
    return _product_or_404(db, product_id)


@router.put("/product/{product_id}", response_model=ProductResponse)
def modify_product(
    product_id: int,
    body: ProductModify,
    db: Session = Depends(get_db),
    _: Admin = Depends(Admin.check_sudo_admin),
):
    product = _product_or_404(db, product_id)
    try:
        return crud.update_product(db, product, body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=_CONFLICT_DETAIL)


@router.delete("/product/{product_id}")
def remove_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(Admin.check_sudo_admin),
):
    product = _product_or_404(db, product_id)
    if crud.has_pending_orders_for_product(db, product.slug):
        raise HTTPException(status_code=409, detail="Product has pending orders")
    crud.remove_product(db, product)
    return {}
