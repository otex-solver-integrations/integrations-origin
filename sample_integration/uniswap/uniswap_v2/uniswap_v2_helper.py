from eth_abi.packed import encode_abi_packed
import eth_abi
from web3 import Web3

rpc = "<rpc_endpoint>"

class UniswapV2Helper:

    def __init__(
        self
    ):

        self.router_address = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'


    ###                          ###
    ##    DECODING FUNCTIONS      ##
    ###                          ###

    def process_amounts_out_call(
        self,
        data
    ):
        # Decode hex response
        decoded_result = eth_abi.decode_abi(['uint256[]'], bytes.fromhex(data[2:]))

        # Modify step info 
        return decoded_result
    
    def process_reserves_call(
        self,
        data
    ):
        # Decode hex response
        decoded_result = eth_abi.decode_abi(['uint112', 'uint112', 'uint32'], bytes.fromhex(data[2:]))

        # Modify step info 
        return decoded_result


    ###                          ###
    ##    ENCODING FUNCTIONS      ##
    ###                          ###

    def get_reserves_call(
        self,
        pool_address
    ):

        data = self._get_reserves_call()

        params = {
                    "jsonrpc": "2.0", "id": 1, "method": "eth_call", 
                    "params": [
                        {
                            "to": pool_address,
                            "data": data
                        },
                        "latest"
                    ]}

        url = {'url': rpc, 'params': params, 'query_type': 'post', 'request_type': 'fill_data', 'attribute': 'reserves'}

        return url

    def _get_reserves_call(
        self
    ):
        '''
            Low level call encoding to getReserves
        '''

        function_definition = f'getReserves()'
        function_signature = Web3.keccak(text=function_definition).hex()[:10]

        encoded_args = eth_abi.encode_abi([], [])

        data = function_signature + encoded_args.hex()

        return data  


    def get_amounts_out_call(
        self,
        amount_in,
        path
    ):

        data = self._get_amounts_out_call(
                                amount_in = amount_in, 
                                path = path
                            )

        params = {
                    "jsonrpc": "2.0", "id": 1, "method": "eth_call", 
                    "params": [
                        {
                            "to": self.router_address,
                            "data": data
                        },
                        "latest"
                    ]}

        url = {'url': rpc, 'params': params, 'query_type': 'post', 'request_type': 'fill_data', 'attribute': 'maker_amount'}

        return url

    def _get_amounts_out_call(
        self,
        amount_in,
        path
    ):
        '''
            Low level call encoding to getAmountsOut
        '''
        types = ['uint256', 'address[]']

        fields = f'{",".join(types)}'
        function_definition = f'getAmountsOut({fields})'
        function_signature = Web3.keccak(text=function_definition).hex()[:10]

        encoded_args = eth_abi.encode_abi(types, [
            amount_in,
            path
        ])

        data = function_signature + encoded_args.hex()

        return data