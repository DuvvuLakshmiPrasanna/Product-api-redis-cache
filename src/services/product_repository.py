import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.product import Product
from src.schemas.product import ProductCreate, ProductUpdate


def create_product(db: Session, payload: ProductCreate) -> Product:
    product = Product(
        id=str(uuid.uuid4()),
        name=payload.name,
        description=payload.description,
        price=payload.price,
        stock_quantity=payload.stock_quantity,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_product_by_id(db: Session, product_id: str) -> Product | None:
    return db.get(Product, product_id)


def update_product(db: Session, product: Product, payload: ProductUpdate) -> Product:
    update_values = payload.model_dump(exclude_unset=True)
    for field_name, value in update_values.items():
        setattr(product, field_name, value)

    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: Product) -> None:
    db.delete(product)
    db.commit()


def count_products(db: Session) -> int:
    return len(db.execute(select(Product.id)).all())


def seed_products(db: Session) -> None:
    if count_products(db) > 0:
        return

    sample_products = [
        Product(
            id=str(uuid.uuid4()),
            name="Wireless Mouse",
            description="Ergonomic 2.4GHz wireless mouse",
            price=24.99,
            stock_quantity=120,
        ),
        Product(
            id=str(uuid.uuid4()),
            name="Mechanical Keyboard",
            description="RGB backlit mechanical keyboard",
            price=79.50,
            stock_quantity=75,
        ),
        Product(
            id=str(uuid.uuid4()),
            name="USB-C Hub",
            description="7-in-1 USB-C hub for laptops",
            price=39.00,
            stock_quantity=200,
        ),
    ]

    db.add_all(sample_products)
    db.commit()
