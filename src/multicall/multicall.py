from eth_abi import decode_single
import web3
import json


# Container for a specific method with specific parameter
class Call():
    def __init__(self, method, params):
        self.method = method
        self.params = params



# A wrapper around a contract instance, exposing the instance and the calls to make
# `calls` is an array of `Call` objects
class CalledContract():
    def __init__(self, w3, address, abi, calls):
        self.instance = w3.eth.contract(address=address, abi=abi)
        self.calls = calls


    def addCall(self, method, params):
        if type(params) is tuple:
            params = list(params)
        elif type(params) is not list:
            params = [params]
        # using append or "+=" here causes call to be added to ALL CalledContract instances. Not sure why. 
        self.calls = self.calls + [Call(method, params)]

    def listCalls(self):
        return list((c.method, c.params) for c in self.calls)



class LocalState:

    def __init__(self, w3Connection, configFile=None):
        # cached state is stored in a single flat dictionary, keyed by keccak(contract + calldata)
        self.state = dict()

        # calledContracts contain the contracts to call and the calldata
        self.calledContracts = dict()

        multicall_address = "0xcA11bde05977b3631167028862bE2a173976CA11"
        multicall_abi = """[{"inputs":[{"components":[{"internalType":"address","name":"target","type":"address"},{"internalType":"bytes","name":"callData","type":"bytes"}],"internalType":"struct Multicall3.Call[]","name":"calls","type":"tuple[]"}],"name":"aggregate","outputs":[{"internalType":"uint256","name":"blockNumber","type":"uint256"},{"internalType":"bytes[]","name":"returnData","type":"bytes[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"components":[{"internalType":"address","name":"target","type":"address"},{"internalType":"bool","name":"allowFailure","type":"bool"},{"internalType":"bytes","name":"callData","type":"bytes"}],"internalType":"struct Multicall3.Call3[]","name":"calls","type":"tuple[]"}],"name":"aggregate3","outputs":[{"components":[{"internalType":"bool","name":"success","type":"bool"},{"internalType":"bytes","name":"returnData","type":"bytes"}],"internalType":"struct Multicall3.Result[]","name":"returnData","type":"tuple[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"components":[{"internalType":"address","name":"target","type":"address"},{"internalType":"bool","name":"allowFailure","type":"bool"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"bytes","name":"callData","type":"bytes"}],"internalType":"struct Multicall3.Call3Value[]","name":"calls","type":"tuple[]"}],"name":"aggregate3Value","outputs":[{"components":[{"internalType":"bool","name":"success","type":"bool"},{"internalType":"bytes","name":"returnData","type":"bytes"}],"internalType":"struct Multicall3.Result[]","name":"returnData","type":"tuple[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"components":[{"internalType":"address","name":"target","type":"address"},{"internalType":"bytes","name":"callData","type":"bytes"}],"internalType":"struct Multicall3.Call[]","name":"calls","type":"tuple[]"}],"name":"blockAndAggregate","outputs":[{"internalType":"uint256","name":"blockNumber","type":"uint256"},{"internalType":"bytes32","name":"blockHash","type":"bytes32"},{"components":[{"internalType":"bool","name":"success","type":"bool"},{"internalType":"bytes","name":"returnData","type":"bytes"}],"internalType":"struct Multicall3.Result[]","name":"returnData","type":"tuple[]"}],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"getBasefee","outputs":[{"internalType":"uint256","name":"basefee","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"blockNumber","type":"uint256"}],"name":"getBlockHash","outputs":[{"internalType":"bytes32","name":"blockHash","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getBlockNumber","outputs":[{"internalType":"uint256","name":"blockNumber","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getChainId","outputs":[{"internalType":"uint256","name":"chainid","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getCurrentBlockCoinbase","outputs":[{"internalType":"address","name":"coinbase","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getCurrentBlockDifficulty","outputs":[{"internalType":"uint256","name":"difficulty","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getCurrentBlockGasLimit","outputs":[{"internalType":"uint256","name":"gaslimit","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getCurrentBlockTimestamp","outputs":[{"internalType":"uint256","name":"timestamp","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"addr","type":"address"}],"name":"getEthBalance","outputs":[{"internalType":"uint256","name":"balance","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getLastBlockHash","outputs":[{"internalType":"bytes32","name":"blockHash","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bool","name":"requireSuccess","type":"bool"},{"components":[{"internalType":"address","name":"target","type":"address"},{"internalType":"bytes","name":"callData","type":"bytes"}],"internalType":"struct Multicall3.Call[]","name":"calls","type":"tuple[]"}],"name":"tryAggregate","outputs":[{"components":[{"internalType":"bool","name":"success","type":"bool"},{"internalType":"bytes","name":"returnData","type":"bytes"}],"internalType":"struct Multicall3.Result[]","name":"returnData","type":"tuple[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"bool","name":"requireSuccess","type":"bool"},{"components":[{"internalType":"address","name":"target","type":"address"},{"internalType":"bytes","name":"callData","type":"bytes"}],"internalType":"struct Multicall3.Call[]","name":"calls","type":"tuple[]"}],"name":"tryBlockAndAggregate","outputs":[{"internalType":"uint256","name":"blockNumber","type":"uint256"},{"internalType":"bytes32","name":"blockHash","type":"bytes32"},{"components":[{"internalType":"bool","name":"success","type":"bool"},{"internalType":"bytes","name":"returnData","type":"bytes"}],"internalType":"struct Multicall3.Result[]","name":"returnData","type":"tuple[]"}],"stateMutability":"payable","type":"function"}]"""
        self.w3 = w3Connection
        self.multicall = self.w3.eth.contract(address=multicall_address, abi=multicall_abi)
        

        # If config file provided, set up the contracts and update the state
        if configFile is not None:
            self.loadConfig(configFile)
            self.update()
            

    def loadConfig(self, configFile):
        with open(configFile) as f:
            config = json.loads(f.read())
            for contract in config:
                for name, contractConfig in contract.items():
                    self.addContract(name, contractConfig['address'], contractConfig['abi_path'])
                    for method, paramsArray in contractConfig['methods'].items():
                        for param in paramsArray:
                            self.contract(name).addCall(method, param)


    def contract(self, name):
        return self.calledContracts[name]

    def listContracts(self):
        return list(self.calledContracts.keys())


    def addContract(self, name, address, abiPath, calls=[]):
        with open(abiPath) as f:
            abi = f.read()
        self.calledContracts[name] = CalledContract(self.w3, address, abi, calls)


    # Set some local state
    def set(self, address, calldata, value):
        key = self.keyState(address, calldata)
        self.state[key] = value
    

    # Read the local state
    def get(self, name, method, params):
        if type(params) is tuple:
            params = list(params)
        elif type(params) is not list:
            params = [params]

        contract = self.contract(name)
        calldata = contract.instance.encodeABI(method, args=params)
        key = self.keyState(contract.instance.address, calldata)
        value = self.state.get(key)

        # Get the output types from the ABI and decode
        outputs = contract.instance.get_function_by_name(method).__dict__['abi']['outputs']
        if len(outputs) == 1:
            decode_pattern = outputs[0]['type']
        else:
            decode_pattern = "(" + ",".join(o['type'] for o in outputs) + ")"
        result = decode_single(decode_pattern, value)
        return result


    # Gather calldata for all calls and send a single request to multicall
    def update(self):
        callArgs = []
        for _, calledContract in self.calledContracts.items():
            for call in calledContract.calls:
                # Encode the calldata
                calldata = calledContract.instance.encodeABI(call.method, args=call.params)
                callArgs.append((calledContract.instance.address, False, calldata))

        results = [r[1] for r in self.multicall.functions.aggregate3(callArgs).call()]

        # Associate calls and results, and set state accordingly
        for c,r in zip(callArgs, results):
            self.set(c[0], c[2], r)


    @staticmethod
    # global state is keyed by contract address and the calldata required to read the state (i.e. call the function)
    def keyState(address, calldata):
        return web3.Web3.sha3(text = address + calldata)
