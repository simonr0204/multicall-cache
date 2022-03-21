import multicall.multicall as mc
import web3


def main():
    w3 = web3.Web3(web3.Web3.IPCProvider(request_kwargs={'timeout': 300}))

    # Initiate the state from config file
    state = mc.LocalState(w3, configFile="config.json")

    # Get some values from the state
    print(state.get("dai", 'balanceOf', "0xF89e33835E0Eb0e09666030695B674cDEF466e53") / 1e18)
    print(state.get("dai", 'balanceOf', "0x008Ca3a9C52e0F0d9Ee94d310D20d67399d44f6C") / 1e18)
    print(state.get("dai", 'allowance', ("0xF89e33835E0Eb0e09666030695B674cDEF466e53", "0x9759A6Ac90977b93B58547b4A71c78317f391A28")) / 1e18)
    pos, tab, lot, usr, tic, top = state.get("clipper", 'sales', 3)
    print(pos, tab, usr)

    # Add a new call to an existing contract
    state.contract("dai").addCall('allowance', ("0x008Ca3a9C52e0F0d9Ee94d310D20d67399d44f6C", "0x9759A6Ac90977b93B58547b4A71c78317f391A28"))

    # Add a new contract and add a call to it
    state.addContract("weth", "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "abi/daiABI.json")
    state.contract("weth").addCall('balanceOf', "0x008Ca3a9C52e0F0d9Ee94d310D20d67399d44f6C")
    
    
    state.update()
    print(state.get("dai", 'allowance', ("0x008Ca3a9C52e0F0d9Ee94d310D20d67399d44f6C", "0x9759A6Ac90977b93B58547b4A71c78317f391A28")) / 1e18)
    print(state.get("weth", 'balanceOf', "0x008Ca3a9C52e0F0d9Ee94d310D20d67399d44f6C") / 1e18)

    # Inspect all current state
    for c in state.listContracts():
        print(c)
        print(state.contract(c).listCalls())


if __name__ == "__main__":
    main()
