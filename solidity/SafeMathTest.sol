pragma solidity ^0.4.9;


/**
 * @title SafeMath
 * @dev Math operations with safety checks that throw on error
 */
library SafeMath {
  function mul(uint256 a, uint256 b) internal pure returns (uint256) {
    if (a == 0) {
      return 0;
    }
    uint256 c = a * b;
    assert(c / a == b);
    return c;
  }

  function div(uint256 a, uint256 b) internal pure returns (uint256) {
    // assert(b > 0); // Solidity automatically throws when dividing by 0
    uint256 c = a / b;
    // assert(a == b * c + a % b); // There is no case in which this doesn't hold
    return c;
  }

  function sub(uint256 a, uint256 b) internal pure returns (uint256) {
    assert(b <= a);
    return a - b;
  }

  function add(uint256 a, uint256 b) internal pure returns (uint256) {
    uint256 c = a + b;
    assert(c >= a);
    return c;
  }
}

contract TestSafeMath {
  using SafeMath for uint256;

  function test_mul1(uint256 a) public pure returns (uint256) {
    return a.mul(0x111);
  }

  function test_mul2(uint256 a) public pure returns (uint256) {
    return a.mul(0x222);
  }

  function test_div1(uint256 a) public pure returns (uint256) {
    return a.div(0x333);
  }

  function test_div2(uint256 a) public pure returns (uint256) {
    return a.div(0x444);
  }

  function test_add1(uint256 a) public pure returns (uint256) {
    return a.add(0x555);
  }

  function test_add2(uint256 a) public pure returns (uint256) {
    return a.add(0x666);
  }

  function test_sub1(uint256 a) public pure returns (uint256) {
    return a.sub(0x777);
  }

  function test_sub2(uint256 a) public pure returns (uint256) {
    return a.sub(0x888);
  }
}