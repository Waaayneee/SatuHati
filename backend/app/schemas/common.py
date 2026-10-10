from decimal import Decimal
from typing import Annotated

from pydantic import Field, PlainSerializer

# Money is stored as NUMERIC and sent to the frontend as a JSON number.
Money = Annotated[Decimal, PlainSerializer(float, return_type=float, when_used="json")]
MoneyIn = Annotated[Decimal, Field(max_digits=12, decimal_places=2)]
Rating = Annotated[Decimal, PlainSerializer(float, return_type=float, when_used="json")]
