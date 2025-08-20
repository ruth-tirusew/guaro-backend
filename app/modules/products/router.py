from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.modules.products.schemas import (
    ProductCreate, Product, ProductList, ProductUpdate, GRNRequest,
    CategoryCreate, Category, CategoryList, CategoryUpdate, CategoryDetail,
    ProductDetail, ProductCategoryRequest, ProductSearchRequest, CategorySearchRequest
)
from app.dependencies import ProductServiceDep
from app.utils.middlewares.authorization import require_auth, require_permission, require_role
from app.modules.products.service import ProductService

router = APIRouter(prefix="/product", tags=["Products"])

@router.get("", response_model=ProductList)
def get_all_products(product_service: ProductServiceDep):
    """Get all products"""
    return product_service.get_all_products()

@router.get("/search", response_model=ProductList)
def search_products(
    product_service: ProductServiceDep,
    query: str = Query(..., description="Search query for product name or description"),
    category_id: UUID = Query(None, description="Filter by category ID"),
):
    """Search products by name, description, or category"""
    if category_id:
        return product_service.get_products_by_category(category_id)
    else:
        return product_service.search_products(query)

@router.get("/details")
def get_product_details(id: UUID, product_service: ProductServiceDep):
    """Get detailed product information including categories, warehouses, and raw materials"""
    return product_service.get_product_by_id(id)

@router.get("/{product_id}/categories", response_model=CategoryList)
def get_product_categories(product_id: UUID, product_service: ProductServiceDep):
    """Get all categories for a specific product"""
    return product_service.get_categories_by_product(product_id)

@router.post("", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, product_service: ProductServiceDep):
    """Create a new product"""
    return product_service.create_product(product)

@router.put("", response_model=ProductDetail)
def update_product(product: ProductUpdate, product_service: ProductServiceDep):
    """Update an existing product"""
    return product_service.update_product(product)

@router.put("/receive", response_model=Product)
def receive_product(
    product: GRNRequest, 
    product_service: ProductServiceDep,
    user_info: dict = Depends(require_auth())
):
    """Receive product stock (increase inventory)"""

    return product_service.receive_product(product,user_info.id)

@router.put("/deplete", response_model=Product)
def deplete_product(product: GRNRequest, product_service: ProductServiceDep):
    """Deplete product stock (decrease inventory)"""
    return product_service.deplete_product(product)

@router.post("/{product_id}/categories/{category_id}", status_code=status.HTTP_201_CREATED)
def add_product_to_category(
    product_id: UUID, 
    category_id: UUID, 
    product_service: ProductServiceDep
):
    """Add a product to a category"""
    product_service.add_product_to_category(product_id, category_id)
    return {"message": "Product added to category successfully"}

@router.delete("/{product_id}/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_product_from_category(
    product_id: UUID, 
    category_id: UUID, 
    product_service: ProductServiceDep
):
    """Remove a product from a category"""
    product_service.remove_product_from_category(product_id, category_id)

@router.post("/{product_id}/tax/{tax_id}", status_code=status.HTTP_201_CREATED)
def add_tax_to_product(product_id: UUID, tax_id: UUID, product_service: ProductServiceDep):
    """Associate a tax with a product"""
    product_service.add_tax_to_product(product_id, tax_id)
    return {"message": "Tax added to product successfully"}

@router.delete("/{product_id}/tax/{tax_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_tax_from_product(product_id: UUID, tax_id: UUID, product_service: ProductServiceDep):
    """Remove a tax association from a product"""
    product_service.remove_tax_from_product(product_id, tax_id)
    return {"message": "Tax removed from product successfully"}
    

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(id: UUID, product_service: ProductServiceDep):
    """Delete a product (soft delete)"""
    product_service.delete_product(id)


category_router = APIRouter(prefix="/category", tags=["Categories"])

@category_router.get("", response_model=CategoryList)
def get_all_categories(product_service: ProductServiceDep):
    """Get all categories"""
    return product_service.get_all_categories()

@category_router.get("/search", response_model=CategoryList)
def search_categories(
    product_service: ProductServiceDep,
        query: str = Query(..., description="Search query for category name or description"),

):
    """Search categories by name or description"""
    return product_service.search_categories(query)

@category_router.get("/{category_id}", response_model=CategoryDetail)
def get_category_details(category_id: UUID, product_service: ProductServiceDep):
    """Get detailed category information"""
    return product_service.get_category_by_id(category_id)

@category_router.get("/{category_id}/products", response_model=ProductList)
def get_category_products(category_id: UUID, product_service: ProductServiceDep):
    """Get all products in a specific category"""
    return product_service.get_products_by_category(category_id)

@category_router.post("", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate, product_service: ProductServiceDep):
    """Create a new category"""
    return product_service.create_category(category)

@category_router.put("", response_model=CategoryDetail)
def update_category(category: CategoryUpdate, product_service: ProductServiceDep):
    """Update an existing category"""
    return product_service.update_category(category)

@category_router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: UUID, product_service: ProductServiceDep):
    """Delete a category (soft delete)"""
    product_service.delete_category(category_id)

@category_router.post("/{category_id}/products/{product_id}", status_code=status.HTTP_201_CREATED)
def add_product_to_category_alt(
    category_id: UUID, 
    product_id: UUID, 
    product_service: ProductServiceDep
):
    """Add a product to a category (alternative endpoint)"""
    product_service.add_product_to_category(product_id, category_id)
    return {"message": "Product added to category successfully"}

@category_router.delete("/{category_id}/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_product_from_category_alt(
    category_id: UUID, 
    product_id: UUID, 
    product_service: ProductServiceDep
):
    """Remove a product from a category (alternative endpoint)"""
    product_service.remove_product_from_category(product_id, category_id)