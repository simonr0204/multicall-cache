import multicall.multicall as mc
import web3
import time

def main():
    w3 = web3.Web3(web3.Web3.IPCProvider(request_kwargs={'timeout': 300}))
    
    # Create new local state and add a contract and some methods to call
    state = mc.LocalState(w3)
    state.addContract("dai", "0x6B175474E89094C44Da98b954EedeAC495271d0F", "abi/daiABI.json")
    state.contract("dai").addCall('balanceOf', "0xA478c2975Ab1Ea89e8196811F51A7B7Ade33eB11")
    state.contract("dai").addCall('balanceOf', "0xB20bd5D04BE54f870D5C0d3cA85d82b34B836405")
    state.contract("dai").addCall('balanceOf', "0xAE461cA67B15dc8dc81CE7615e0320dA1A9aB8D5")

    # Fetch all the data in one call, once per block
    block = 0
    while True:
        newBlock = w3.eth.blockNumber
        if newBlock != block:
            print(f'\nNew block @{newBlock}, getting state:')
            state.update()
            print("WETH/DAI ", state.get("dai", 'balanceOf', "0xA478c2975Ab1Ea89e8196811F51A7B7Ade33eB11") / 1e18)
            print("USDT/DAI ",state.get("dai", 'balanceOf', "0xB20bd5D04BE54f870D5C0d3cA85d82b34B836405") / 1e18)
            print("USDC/DAI ",state.get("dai", 'balanceOf', "0xAE461cA67B15dc8dc81CE7615e0320dA1A9aB8D5") / 1e18)
            block = newBlock
        time.sleep(1)


if __name__ == "__main__":
    main()
