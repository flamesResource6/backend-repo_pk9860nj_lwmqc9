"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Example schemas (kept for reference):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# App-specific schemas

class MenuItem(BaseModel):
    """
    Menu items available to order
    Collection name: "menuitem"
    """
    name: str = Field(..., description="Dish name")
    description: Optional[str] = Field(None, description="Short description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Category, e.g., wraps, skewers, fries")
    image: Optional[str] = Field(None, description="Image or video thumbnail URL")
    media: Optional[str] = Field(None, description="Optional video loop URL")
    rating: float = Field(4.8, ge=0, le=5, description="Average rating")
    ratings_count: int = Field(0, ge=0, description="Number of ratings")

class Review(BaseModel):
    """
    Customer reviews for social proof
    Collection name: "review"
    """
    name: str = Field(..., description="Reviewer name")
    avatar: Optional[str] = Field(None, description="Avatar image URL")
    rating: int = Field(..., ge=1, le=5, description="Stars 1-5")
    quote: str = Field(..., description="Short testimonial")
    platform: Optional[str] = Field(None, description="e.g., Google, Yelp")

class OrderItem(BaseModel):
    item_id: Optional[str] = Field(None, description="ID of menu item if applicable")
    name: str
    price: float
    quantity: int = 1
    options: Optional[dict] = None

class Order(BaseModel):
    """
    Orders placed via configurator or menu
    Collection name: "order"
    """
    items: List[OrderItem]
    subtotal: float
    tax: float
    total: float
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    notes: Optional[str] = None
