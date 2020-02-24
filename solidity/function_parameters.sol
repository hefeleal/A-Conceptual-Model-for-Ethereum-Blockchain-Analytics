pragma solidity ^0.4.0;

contract TestFunctionParameters {

    constructor() public {
    }

    function test0() public pure { // hash: 77ff24f4
    }

    function test1(uint u256, int i256) public pure { // hash: c1b9d2e3
    }

    function test2(uint8 u8, int8 i8, uint16 u16, int16 i16, uint248 u248, int248 i248) public pure { // hash: 0714d7b0
    }

    function test3(address addr, uint160 u160) public pure { // hash: fe50c4de
    }

    function test4(bytes1 b1, bytes2 b2, bytes31 b31, bytes32 b32) public pure { // hash: 334d898b
    }

    function test5(string s) public pure { // hash: 03a1c367
    }

    function test6(bool b) public pure { // hash: 201a07b0
    }
}
