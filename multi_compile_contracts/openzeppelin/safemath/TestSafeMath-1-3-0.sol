pragma solidity ^0.4.11;


/**
 * @title SafeMath
 * @dev Math operations with safety checks that throw on error
 */
library SafeMath {
  function mul(uint256 a, uint256 b) internal constant returns (uint256) {
    uint256 c = a * b;
    assert(a == 0 || c / a == b);
    return c;
  }

  function div(uint256 a, uint256 b) internal constant returns (uint256) {
    // assert(b > 0); // Solidity automatically throws when dividing by 0
    uint256 c = a / b;
    // assert(a == b * c + a % b); // There is no case in which this doesn't hold
    return c;
  }

  function sub(uint256 a, uint256 b) internal constant returns (uint256) {
    assert(b <= a);
    return a - b;
  }

  function add(uint256 a, uint256 b) internal constant returns (uint256) {
    uint256 c = a + b;
    assert(c >= a);
    return c;
  }
}

contract TestSafeMath {
  using SafeMath for uint256;

  function test_mul(uint256 a) public constant returns (uint256) {
    return a.mul(0x1111);
  }

  function test_div(uint256 a) public constant returns (uint256) {
    return a.div(0x2222);
  }

  function test_add(uint256 a) public constant returns (uint256) {
    return a.add(0x3333);
  }

  function test_sub(uint256 a) public constant returns (uint256) {
    return a.sub(0x4444);
  }
}
