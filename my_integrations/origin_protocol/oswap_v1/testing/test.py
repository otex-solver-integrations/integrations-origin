import json
import requests
from os import listdir
from os.path import isfile, join
from itertools import compress
import sys
import os.path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
)
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
    )
)

from my_integrations.origin_protocol.oswap_v1.oswap_v1_model import OSwapV1Model

tests = "my_integrations/origin_protocol/oswap_v1/testing/test_instances/"


def main():
    # Fetch all test instances
    inputs = [f for f in listdir(tests) if isfile(join(tests, f))]
    inputs.sort()

    for testfile in inputs:
        test_input_instance = tests + testfile
        print("-> " + testfile.replace(".json", ""))

        with open(test_input_instance, "r") as f:
            test = json.load(f)

        # Initialize pool
        pool = OSwapV1Model(test["pool"])

        # Initialize pool with test states
        pool.traderate0 = test["states"]["traderate0"]
        pool.traderate1 = test["states"]["traderate1"]
        pool.balance0 = test["states"]["balance0"]
        pool.balance1 = test["states"]["balance1"]

        if "sell_token" in test["swap"]:
            # Swap paramters
            sell_token = test["swap"]["sell_token"]
            sell_amount = test["swap"]["sell_amount"]

            # Test quoting logic
            fee_amount, amount_out = pool.get_amount_out(
                sell_token=sell_token, sell_amount=sell_amount
            )
            expected = test["results"]["amount_out"]
            actual = amount_out
        elif "buy_token" in test["swap"]:
            # Swap paramters
            buy_token = test["swap"]["buy_token"]
            buy_amount = test["swap"]["buy_amount"]

            # Test quoting logic
            fee_amount, amount_in = pool.get_amount_in(
                buy_token=buy_token, buy_amount=buy_amount
            )
            expected = test["results"]["amount_in"]
            actual = amount_in
        else:
            raise Exception("Invalid test case.")

        if expected != actual: # Our math is currently exact
                raise Exception("Test %s Failed", testfile)

    print("### INFO: Quote Testing Coverage: 100%")


if __name__ == "__main__":
    main()
