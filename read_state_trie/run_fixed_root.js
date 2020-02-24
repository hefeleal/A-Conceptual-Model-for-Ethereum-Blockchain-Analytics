// reference: https://wanderer.github.io/ethereum/nodejs/code/2014/05/21/using-ethereums-tries-with-node/

var level = require('level');
var rlp = require('rlp');
var Trie = require('merkle-patricia-tree/secure');

var db = level('/media/sdc1/.ethereum2/geth/chaindata');

var root = '0x2c6e6ec4c764741b35e2a966f5b78d4d7250e193b9fff72bfe7a34a0c1a9bf02'; // block 2679230
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
