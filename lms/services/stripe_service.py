import stripe
from decimal import Decimal
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def _to_cents(amount: Decimal | float | int) -> int:
    # Stripe ждёт сумму в минимальных единицах (cents)
    return int(Decimal(amount) * 100)

def ensure_product(name: str, product_id: str | None = None) -> str:
    """Создать Product или вернуть существующий ID."""
    if product_id:
        return product_id
    product = stripe.Product.create(name=name)
    return product["id"]

def ensure_price(product_id: str, amount: Decimal, currency: str, price_id: str | None = None) -> str:
    """Создать Price под продукт (однократный платеж)."""
    if price_id:
        return price_id
    price = stripe.Price.create(
        product=product_id,
        unit_amount=_to_cents(amount),
        currency=currency,
    )
    return price["id"]

def create_checkout_session(price_id: str, quantity: int = 1) -> dict:
    """Создать Checkout Session и вернуть словарь с id и url."""
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{"price": price_id, "quantity": quantity}],
        success_url=settings.FRONTEND_SUCCESS_URL,
        cancel_url=settings.FRONTEND_CANCEL_URL,
        payment_method_types=["card"],
    )
    return {"id": session["id"], "url": session["url"]}

def retrieve_session(session_id: str) -> dict:
    """Получить данные по сессии (для проверки статуса)."""
    session = stripe.checkout.Session.retrieve(session_id)
    return dict(session)