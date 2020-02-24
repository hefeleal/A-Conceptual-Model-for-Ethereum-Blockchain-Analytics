pragma solidity ^0.5.0;

import "../Roles.sol";
import "./WhitelisterRole.sol";

/**
 * @title WhitelistedRole
 * @dev Whitelisted accounts have been approved by a Whitelister to perform certain actions (e.g. participate in a
 * crowdsale). This role is special in that the only accounts that can add it are Whitelisters (who can also remove it),
 * and not Whitelisteds themselves.
 */
contract WhitelistedRole is WhitelisterRole {
    using Roles for Roles.Role;

    event WhitelistedAdded(address indexed account);
    event WhitelistedRemoved(address indexed account);

    Roles.Role private _whitelisteds;

    modifier onlyWhitelisted() {
        require(isWhitelisted(msg.sender));
        _;
    }

    function isWhitelisted(address account) public view returns (bool) {
        return _whitelisteds.has(account);
    }

    function addWhitelisted(address account) public onlyWhitelister {
        _addWhitelisted(account);
    }

    function removeWhitelisted(address account) public onlyWhitelister {
        _removeWhitelisted(account);
    }

    function renounceWhitelisted() public {
        _removeWhitelisted(msg.sender);
    }

    function _addWhitelisted(address account) internal {
        _whitelisteds.add(account);
        emit WhitelistedAdded(account);
    }

    function _removeWhitelisted(address account) internal {
        _whitelisteds.remove(account);
        emit WhitelistedRemoved(account);
    }
}
