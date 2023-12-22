import os
import eth_abi.abi as abi
from web3 import Web3

rpc = os.getenv("PROVIDER_URL")


class OSwapV1Helper:
    def __init__(self):
        self.pool_address = "0x85b78aca6deae198fbf201c82daf6ca21942acc6"
        self.steth_address = "0xae7ab96520de3a18e5e111b5eaab095312d7fe84"
        self.weth_address = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
        self.multi_call_address = "0xeefba1e63905ef1d7acba5a8513c70307c1ce441"

    ###                          ###
    ##    DECODING FUNCTIONS      ##
    ###                          ###

    def process_state_call(self, data):
        raw = abi.decode(["uint256", "bytes[]"], bytes.fromhex(data[2:]))[1]
        values = [int(x.hex(), 16) for x in raw]
        return {
            "traderate0": values[0],
            "traderate1": values[1],
            "balance0": values[2],
            "balance1": values[3],
        }

    ###                          ###
    ##    ENCODING FUNCTIONS      ##
    ###                          ###

    def _fn_sig(self, s):
        return Web3.keccak(text=s)[:4].hex()[2:10]

    def _inner_call(self, to, sig, arg_data=b""):
        data = self._fn_sig(sig) + (arg_data.hex() if arg_data else "")
        return [to, bytes.fromhex(data)]

    def get_state_call(self, block="latest"):
        """
        Using the multicall address for efficency, we fetch all data in one shot.

        - Pool traderate0
        - Pool traderate1
        - Pool balance0 from WETH
        - Pool balance1 from STETH
        """

        calls = [
            self._inner_call(self.pool_address, "traderate0()"),
            self._inner_call(self.pool_address, "traderate1()"),
            self._inner_call(
                self.weth_address,
                "balanceOf(address)",
                abi.encode(["address"], [self.pool_address]),
            ),
            self._inner_call(
                self.steth_address,
                "balanceOf(address)",
                abi.encode(["address"], [self.pool_address]),
            ),
        ]

        data = abi.encode(["(address,bytes)[]"], [calls])
        block = block if block == "latest" else hex(block)

        params = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_call",
            "params": [
                {"to": self.multi_call_address, "data": "0x252dba42" + data.hex()},
                block,
            ],
        }
        r = {
            "url": rpc,
            "params": params,
            "query_type": "post",
            "request_type": "fill_data",
            "attribute": "state",
        }
        return r


if __name__ == "__main__":
    """
    Testing for OSwapV1Helper
    """

    helper = OSwapV1Helper()

    def _testEq(actual, expected, name):
        if actual == expected:
            print("PASS", name, actual)
        else:
            print("FAIL", name)
            print("  Expected: " + str(expected))
            print("  Actual: " + str(actual))

    def _request_and_decode(r):
        import requests

        res = requests.post(r["url"], json=r["params"])
        return helper.process_state_call(res.json()["result"])

    def _dump_state(block):
        import json

        print("# Block", block)
        data = _request_and_decode(helper.get_state_call(block=block))
        print(json.dumps(data, indent=2))

    # Tests
    _testEq(helper._fn_sig("traderate0()"), "45059a6b", "fnSig:traderate0")
    _testEq(helper._fn_sig("traderate1()"), "cf1de5d8", "fnSig:traderate1")
    _testEq(
        helper._inner_call(helper.pool_address, "traderate1"),
        ["0x85b78aca6deae198fbf201c82daf6ca21942acc6", b"\xed.\x9f\x94"],
        "innerCall:traderate1",
    )
    _testEq(
        _request_and_decode(helper.get_state_call(block=18834800)),
        {
            "traderate0": 1000312246404290062424705124786067110,
            "traderate1": 999607877634508603977360000000000000,
            "balance0": 19018678471648641311,
            "balance1": 469710326970695283103,
        },
        "getStateCall",
    )

    # Data for testing
    _dump_state(
        18816584
    )  # 0x750d1f339116404f5f65e86c674f85aa0477f9dbb1a7ec4fe50e1c59f5a11bb3
    _dump_state(
        18816531
    )  # 0xdb94f7b64f7672040ed361cc783ed6d9af9b6a3adef453ee85a6ecccb3aa922b
    _dump_state(
        18789716
    )  # 0x69b1b5e0e3fd2dd656d89dc34f490a239651503887a1e69f20c26189e99db1b7
    _dump_state(
        18789712
    )  # 0x496a8d198421a36fd8c2ed1aef3de98285a951c6ca2398e3d6df0ca7bf9732fc
