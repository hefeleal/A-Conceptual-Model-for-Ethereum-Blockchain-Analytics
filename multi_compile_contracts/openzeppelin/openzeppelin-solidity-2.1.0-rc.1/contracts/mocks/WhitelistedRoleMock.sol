pragma solidity ^0.4.24;

import "../access/roles/WhitelistedRole.sol";

contract WhitelistedRoleMock is WhitelistedRole {
    function onlyWhitelistedMock() public view onlyWhitelisted {
    }
}
