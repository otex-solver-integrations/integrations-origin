from typing import Tuple

from my_integrations.origin_protocol.oswap_v1.oswap_v1_helper import OSwapV1Helper


class OSwapV1Model:
    def __init__(self, pool: dict):
        self.pool_address = pool["pool_address"]
        self.tokens = pool["tokens"]

        self.token0 = self.tokens[0]
        self.token1 = self.tokens[1]

        self.traderate0 = 0
        self.traderate1 = 0
        self.balance0 = 0
        self.balance1 = 0

    def to_dict(
        self, 
        deep=False
    ) -> dict:
        data = {
            "pool_address": self.pool_address,
            "tokens": self.tokens,
            "token0": self.token0,
            "token1": self.token1,
        }
        if deep:
            data["traderate0"] = self.traderate0
            data["traderate1"] = self.traderate1
            data["balance0"] = self.balance0
            data["balance1"] = self.balance1
        return data

    def has_complete_data(self) -> bool:
        return self.traderate0 > 0 and self.traderate1 > 0

    def get_amount_out(
        self, 
        sell_token: str, 
        sell_amount: int
    ) -> Tuple[int, int]:
        
        inToken = sell_token
        amountIn = sell_amount
        price = 0
        if inToken == self.tokens[0]:
            price = self.traderate0
        elif inToken == self.tokens[1]:
            price = self.traderate1
        else:
            return 0, 0
        amountOut = int(amountIn) * int(price) // 10**36
        if inToken == self.tokens[0] and amountOut > self.balance1:
            return 0, 0
        elif inToken == self.tokens[1] and amountOut > self.balance0:
            return 0, 0
        return 0, amountOut

    def get_amount_in(
        self, 
        buy_token:str, 
        buy_amount:int
    ) -> Tuple[int,int]:
        
        outToken = buy_token
        amountOut = buy_amount
        price = 0
        if outToken == self.tokens[1]:
            price = self.traderate0
        elif outToken == self.tokens[0]:
            price = self.traderate1
        else:
            return 0, 0
        amountIn = int(amountOut) * 10**36 // int(price) + 1
        if outToken == self.tokens[0] and amountOut > self.balance0:
            return 0, 0
        elif outToken == self.tokens[1] and amountOut > self.balance1:
            return 0, 0
        return 0, amountIn

    def get_state_calls(self) -> list:
        return [OSwapV1Helper.get_state_call()]

    def process_rpc_data(
        self, 
        data: dict
    ):
        '''
            data -> {'result':str, 'attribute': str}
        '''
        if data['attribute'] == 'states' and data['result']:

            results = OSwapV1Helper.get_state_call(data['result'])
            self.traderate0 = results.traderate0
            self.traderate1 = results.traderate1
            self.balance0 = results.balance0
            self.balance1 = results.balance1

        else:

            raise Exception("### ERROR: Uknown rpc data attribute for OSwapV1")
