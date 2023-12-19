import json
import requests
from os import listdir
from os.path import isfile, join
from itertools import compress
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from sample_integration.uniswap.uniswap_v2.uniswap_v2_helper import UniswapV2Helper
from sample_integration.uniswap.uniswap_v2.uniswap_v2_pool_model import UniswapV2Pool

UniswapV2Helper = UniswapV2Helper()

tests = 'sample_integration/uniswap/uniswap_v2/testing/test_instances/'


def main():

    # Fetch all test instances
    inputs = [f for f in listdir(tests) if isfile(join(tests, f))]

    # Choose test instance
    test_id = "test_1"

    # Read test input instance
    fil = [test_id in i for i in inputs]
    test_input = list(compress(inputs, fil))[0]
    test_input_instance = tests + test_input
    with open(test_input_instance, 'r') as f:
        test = json.load(f)

    # Initialize pool
    pool = UniswapV2Pool(test['pool'])

    # Initialize pool with test states
    pool.reserve0 = test['states']['reserve0']
    pool.reserve1 = test['states']['reserve1']

    # Swap paramters
    sell_token = test['swap']['sell_token']
    sell_amount = test['swap']['sell_amount']

    # Test quoting logic
    fee_amount, amount_out = pool.get_amount_out(sell_token = sell_token, sell_amount = sell_amount)

    if amount_out != test['results']['amount_out']:
        if abs(1 - amount_out/test['results']['amount_out']) > 0.000001:
                print("### ERROR: Off-chain quoter failure.")
                print("Quoter failed to obtain correct amount out given liquidity states at block " + str(test['testing_block_number']) + " for pool " + test['pool']['pool_address'])
                raise Exception("Test Failed")

    if fee_amount != test['results']['fee_amount']:
        if abs(1 - fee_amount/test['results']['fee_amount']) > 0.000001:
                print("### ERROR: Off-chain quoter failure.")
                print("Quoter failed to obtain correct fee out given liquidity states at block " + str(test['testing_block_number']) + " for pool " + test['pool']['pool_address'])
                raise Exception("Test Failed")

    print("### INFO: Quote Testing Coverage: 100%")

if __name__ == "__main__":
    main()