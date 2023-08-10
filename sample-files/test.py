import asyncio
from fastkafka.testing import Tester
from application import *

async def async_tests():
#     async with Tester(store_product_app).using_inmemory_broker() as tester:
    async with Tester(store_product_app) as tester:
        input_msg = StoreProduct(
            product_name="Mobile Phone",
            currency="HRK",
            price=750.0
        )

        # tester produces message to the store_product topic
        await tester.to_store_product(input_msg)

         # assert that app consumed from the store_product topic and it was called with the accurate argument
        await store_product_app.awaited_mocks.on_store_product.assert_called_with(
            input_msg, timeout=5
        )

        # assert that tester consumed from the change_currency topic and it was called with the accurate argument
        await tester.awaited_mocks.on_change_currency.assert_called_with(
            StoreProduct(
                product_name="Mobile Phone",
                currency="EUR",
                price=100.0
            ), timeout=5
        )
    print("ok")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_tests())
