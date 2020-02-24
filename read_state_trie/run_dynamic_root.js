// reference: https://wanderer.github.io/ethereum/nodejs/code/2014/05/21/using-ethereums-tries-with-node/

var ethereum_path = '/media/sdc1/.ethereum_light/';

var level = require('level');
var rlp = require('rlp');
var Trie = require('merkle-patricia-tree/secure');
var Web3 = require('web3');
var web3 = new Web3();
var net = require('net');

web3 = new Web3(new Web3.providers.IpcProvider(ethereum_path + 'geth.ipc', net));
web3.eth.getBlockNumber().then(function(nr){
    return web3.eth.getBlock(nr);
}).then(function(block){
    var root = block.stateRoot;
    console.log(root);

    var db = level(ethereum_path + 'geth/lightchaindata');
    var trie = new Trie(db, root);

    var stream = trie.createReadStream();

    stream.on('data', function (data){
        var decodedVal = rlp.decode(data.value);
        var codeHash = decodedVal[3].toString('hex');
        if(codeHash != "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470"){
            /*for(var i = 0; i < decodedVal.length; i++){
                console.log(decodedVal[i].toString('hex'));
            }*/
            db.get(new Buffer(codeHash, 'hex'), {
                encoding: 'binary'
            }, function (err, value) {
                console.log(data.key.toString('hex'), value.toString('hex'), "\n");
            });
        }
    });
});
