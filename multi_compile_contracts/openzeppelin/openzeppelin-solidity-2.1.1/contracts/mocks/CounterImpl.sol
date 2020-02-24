pragma solidity ^0.5.0;

import "../drafts/Counter.sol";

contract CounterImpl {
    using Counter for Counter.Counter;

    uint256 public theId;

    // use whatever key you want to track your counters
    mapping(string => Counter.Counter) private _counters;

    function doThing(string memory key) public returns (uint256) {
        theId = _counters[key].next();
        return theId;
    }
}
