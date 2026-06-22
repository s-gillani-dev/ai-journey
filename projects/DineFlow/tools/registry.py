# # DineFlow/tools/registry.py
# from state_machine.types import MenuItemSnapshot


# def get_menu_items() -> list[MenuItemSnapshot]:
#     """
#     POC-only static menu.
#     Replace with DB or Search later.
#     """
#     return [
#         MenuItemSnapshot(
#             sku="PZ-FANCY",
#             name="Fancy Truffle Pizza",
#             in_stock=True,
#             is_alcohol=False,
#             complexity_score=5,  # 🚨 This is > 3, so it will trigger the block
#             price=24.99,
#         ),
#         MenuItemSnapshot(
#             sku="PZ-PEP",
#             name="Pepperoni Pizza",
#             in_stock=True,
#             is_alcohol=False,
#             complexity_score=2,
#             price=12.99,
#         ),
#         MenuItemSnapshot(
#             sku="PZ-MARG",
#             name="Margherita Pizza",
#             in_stock=True,
#             is_alcohol=False,
#             complexity_score=2,
#             price=11.49,
#         ),
#         MenuItemSnapshot(
#             sku="BEER-001",
#             name="Craft Beer",
#             in_stock=True,
#             is_alcohol=True,
#             complexity_score=1,
#             price=6.50,
#         ),
#         MenuItemSnapshot(
#             sku="BEER-002", 
#             name="Heineken Beer", # Use the specific name!
#             price=6.0, 
#             is_alcohol=True, 
#             in_stock=True, 
#             complexity_score=1
#         ),
#     ]




# DineFlow/tools/registry.py
from state_machine.types import MenuItemSnapshot


def get_menu_items() -> list[MenuItemSnapshot]:
    """
    POC-only static menu.
    Replace with DB or Search later.

    Data Completeness Contract:
    - Every item MUST have a `description` that truthfully describes its
      flavor profile, texture, and notable attributes in natural language.
    - Every item MUST have `tags` covering dietary, flavor, and category
      attributes that users might search for.

    Why both fields?
    - `description` → feeds the LLM prompt so it can reason in natural language
      ("Is the Pepperoni Pizza spicy?" → LLM reads "spicy pepperoni" and answers yes)
    - `tags` → feeds BM25/vector search so retrieval finds the right items
      before the LLM even runs ("anything spicy" → BM25 matches tag "spicy")

    Without these fields, the MenuExpert receives an empty {{MENU_CONTEXT}}
    and correctly falls back to "I don't have that information" — which is
    not a bug in the agent, it's a gap in the data.
    """
    return [
        MenuItemSnapshot(
            sku="PZ-FANCY",
            name="Fancy Truffle Pizza",
            price=24.99,
            in_stock=True,
            is_alcohol=False,
            complexity_score=5,  # 🚨 > 3: triggers kitchen throttle when load >= 85%
            description=(
                "A luxurious white pizza finished with black truffle oil, "
                "wild mushrooms, fresh thyme, and a drizzle of aged balsamic. "
                "Rich, earthy, and deeply savory. Not spicy."
            ),
            tags=["vegetarian", "luxury", "truffle", "mushroom", "earthy", "rich", "non-spicy"],
        ),
        MenuItemSnapshot(
            sku="PZ-PEP",
            name="Pepperoni Pizza",
            price=12.99,
            in_stock=True,
            is_alcohol=False,
            complexity_score=2,
            description=(
                "Classic pizza loaded with spicy pepperoni slices, "
                "stretchy mozzarella, and a tangy tomato base. "
                "A crowd favourite with a satisfying kick of heat."
            ),
            tags=["spicy", "hot", "classic", "pork", "meat", "pepperoni", "popular"],
        ),
        MenuItemSnapshot(
            sku="PZ-MARG",
            name="Margherita Pizza",
            price=11.49,
            in_stock=True,
            is_alcohol=False,
            complexity_score=2,
            description=(
                "Simple and fresh: San Marzano tomato sauce, torn basil, "
                "and creamy fresh mozzarella on a hand-stretched base. "
                "Light, mild, and vegetarian."
            ),
            tags=["vegetarian", "vegan-option", "mild", "classic", "light", "fresh", "non-spicy"],
        ),
        MenuItemSnapshot(
            sku="BEER-001",
            name="Craft Beer",
            price=6.50,
            in_stock=True,
            is_alcohol=True,
            complexity_score=1,
            description=(
                "A locally brewed IPA with bright citrus notes, "
                "a floral hop aroma, and a crisp, dry finish. "
                "Pairs well with spicy or rich dishes."
            ),
            tags=["alcohol", "beer", "ipa", "cold", "craft", "citrus", "hoppy"],
        ),
        MenuItemSnapshot(
            sku="BEER-002",
            name="Heineken Beer",
            price=6.0,
            in_stock=True,
            is_alcohol=True,
            complexity_score=1,
            description=(
                "A world-famous Dutch lager — clean, crisp, and refreshing "
                "with a mild bitterness and light malt sweetness. "
                "A reliable classic served ice cold."
            ),
            tags=["alcohol", "beer", "lager", "cold", "mild", "classic", "refreshing"],
        ),
    ]