from sample_integration.uniswap.uniswap_v2.uniswap_v2_helper import UniswapV2Helper

UniswapV2Helper = UniswapV2Helper()

class UniswapV2Pool:

    def __init__(
        self,
        pool
    ):

        # self.pool_address:str
        self.pool_address = pool['pool_address']

        # self.tokens: list[len(tokens)]<str>
        self.tokens = sorted(pool['tokens'])

        # self.source:str
        self.source = pool['source']

        # token0 as defined by Uniswap v2
        self.token0 = self.tokens[0]

        # token1 as defined by Uniswap v2
        self.token1 = self.tokens[1]

        # States to be obtained via RPC calls
        self.reserve0 = None 
        self.reserve1 = None 

    
    def has_complete_data(
        self
    ):
        '''
            Determines if pool has enough data to compute 
            pool quotes off-chain.
        '''

        if not self.reserve0 or not self.reserve1:
            return False
        
        return True
    

    def to_dict(
        self,
        deep = False
    ):
        '''
            transfrms
        '''
        p = dict()
        p['pool_address'] = self.pool_address
        p['source'] = self.source
        p['tokens'] = self.tokens

        if deep:
            p['reserve0'] = self.reserve0
            p['reserve1'] = self.reserve1

        return p
    

    def get_amount_out(
        self,
        sell_token,
        sell_amount
    ):
        '''
            Calculation for amount out of constant-product pools given reserves.

            Source sample:
            https://etherscan.io/address/0x7a250d5630b4cf539739df2c5dacb4c659f2488d#code 
        '''

        if sell_token == self.token0:
            reserve_in = self.reserve0
            reserve_out = self.reserve1
        else:
            reserve_in = self.reserve1
            reserve_out = self.reserve0

        if not (reserve_in > 0 and reserve_out > 0):
            return 0, 0
        
        # multiply amount_in by fee
        amount_in = int(sell_amount)
        amount_in_with_fee = amount_in * 997
        fee_amount = int(amount_in * 0.003)
        numerator = amount_in_with_fee * reserve_out
        denominator = reserve_in * 1000 + amount_in_with_fee
        amount_out = int(numerator/denominator)

        return fee_amount, amount_out

    def get_amount_in(
        self,
        amount_out,
        reserve_in,
        reserve_out
    ):
        '''
            Calculation for amount in of constant-product pool given reserves.

            Source sample:
            https://etherscan.io/address/0x7a250d5630b4cf539739df2c5dacb4c659f2488d
        '''

        if not (reserve_in > 0 and reserve_out > 0):
            return 0, 0

        amount_out = int(amount_out)
        numerator = reserve_in * amount_out * 1000
        denominator = (reserve_out - amount_out) * 997
        amount_in =  (numerator / denominator) + 1
        if amount_in < 0:
            return 0, 0
        fee_amount = int(amount_in * 0.003)
        
        return fee_amount, amount_in


    def process_rpc_data(
        self,
        data
    ):
        '''
            Route RPC response to correct decoding 
            method.
        '''

        if data['attribute'] == 'reserves' and data['result']:
            
            self.process_reserves_call(data['result'])
        
        else:

            raise Exception("### ERROR: Uknown rpc data attribute for Uni v2")
    
    def process_reserves_call(
        self,
        data
    ):
        '''
            Decode reserves call
        '''

        state =  UniswapV2Helper.process_reserves_call(
                                        data = data
                                    )
        
        self.reserve0 = state[0]
        self.reserve1 = state[1]
    
    
    def get_state_calls(
        self
    ):
        '''
            Collects RPC calls for non-static liquidity pool
            states. 
        '''

        queries = list()

        query = UniswapV2Helper.get_reserves_call(pool_address=self.pool_address)
        queries.append(query)

        return queries