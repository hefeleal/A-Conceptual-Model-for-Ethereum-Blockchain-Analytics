var solc = require("solc")
var path = require("path")
var fs = require('fs')

process.setMaxListeners(0)

if(!fs.existsSync(path.join(__dirname, "solc-bin"))){
    console.log("solc-bin doesn't exist. Please execute `git clone https://github.com/ethereum/solc-bin.git`")
    process.exit(1)
}
if(process.argv.length < 3){
    console.log("Please specify the file to compile")
    process.exit(1)
}
if(process.argv.length < 4){
    console.log("Please specify the output directory")
    process.exit(1)
}
solidity_filename = process.argv[2]
out_dir = process.argv[3]
try{
    fs.mkdirSync(out_dir)
} catch(err){
    if(err.code !== 'EEXIST') throw err
}

source_code = fs.readFileSync(solidity_filename, { encoding: 'utf8'} )
code_version = source_code.match("\\^(.*?);")[1]

var solc_list = require(path.join(__dirname, "solc-bin/bin/list.json"))
for(var solc_version in solc_list.releases){
    if(is_compatible_version(code_version, solc_version)){
        compile_file_with(out_dir, solc, solc_version, solc_list, source_code, false)
        compile_file_with(out_dir, solc, solc_version, solc_list, source_code, true)
    }
}

function compile_file_with(out_dir, solc, solc_version, solc_list, source_code, optimized){
    contract_name = "mycontract.sol"
    var input = {
        language: 'Solidity',
        sources: {
            [contract_name]: {
                content: source_code
            }
        },
        settings: {
            optimizer: {
              enabled: optimized,
              runs: 200
            },
            outputSelection: {
                '*': {
                    '*': [ '*' ]
                }
            }
        }
    }
    var solc = solc.setupMethods(require(path.join(__dirname, "solc-bin/bin/", solc_list.releases[solc_version])))
    var output = JSON.parse(solc.compile(JSON.stringify(input)))
    var contract_object = output.contracts[contract_name]
    if(typeof contract_object === 'undefined'){ // needed for compiler version <= 0.4.8
        contract_object = output.contracts[""]
    }

    // when using a library, the contract_object contains two elements: the library and the actual contract
    // we are only interested in the actual contract, which is the last element here
    var last_contract = Object.keys(contract_object)[Object.keys(contract_object).length - 1]
    var runtime_bytecode = contract_object[last_contract].evm.deployedBytecode.object
    fs.writeFileSync(path.join(out_dir, solc_version + (optimized ? "-1" : "-0")), runtime_bytecode);
    // console.log(solc_version, optimized ? "optimized" : "not optimized")
    // console.log(runtime_bytecode + "\n")
}

function is_compatible_version(test_lower, test_higher){
    test_lower_split = test_lower.split(".").map(function(x){ return parseInt(x); })
    test_higher_split = test_higher.split(".").map(function(x){ return parseInt(x); })
    if(test_lower_split[0] != test_higher_split[0] || test_lower_split[1] != test_higher_split[1]
        || test_lower_split[2] > test_higher_split[2]){
        return false
    }
    return true
}
