# Changelog

## 2.1.1 (2019-04-01)
 * Version bump to avoid conflict in the npm registry.

## 2.1.0 (2019-04-01)

### New features:
 * Now targeting the 0.5.x line of Solidity compilers. For 0.4.24 support, use version 2.0 of OpenZeppelin.
 * `WhitelistCrowdsale`: a crowdsale where only whitelisted accounts (`WhitelistedRole`) can purchase tokens. Adding or removing accounts from the whitelist is done by whitelist admins (`WhitelistAdminRole`). Similar to the pre-2.0 `WhitelistedCrowdsale`. ([#1525](https://github.com/OpenZeppelin/openzeppelin-solidity/pull/1525), [#1589](https://github.com/OpenZeppelin/openzeppelin-solidity/pull/1589))
 * `RefundablePostDeliveryCrowdsale`: replacement for `RefundableCrowdsale` (deprecated, see below) where tokens are only granted once the crowdsale ends (if it meets its goal). ([#1543](https://github.com/OpenZeppelin/openzeppelin-solidity/pull/1543))
 * `PausableCrowdsale`: allows for pausers (`PauserRole`) to pause token purchases. Other crowdsale operations (e.g. withdrawals and refunds, if applicable) are not affected. ([#832](https://github.com/OpenZeppelin/openzeppelin-solidity/pull/832))
 * `ERC20`: `transferFrom` and `_burnFrom ` now emit `Approval` events, to represent the token's state comprehensively through events. ([#1524](https://github.com/OpenZeppelin/openzeppelin-solidity/pull/1524))
 * `ERC721`: added `_burn(uint256 tokenId)`, replacing the similar deprecated function (see below). ([#1550](https://github.com/OpenZeppelin/openzeppelin-solidity/pull/1550))
 * `ERC721`: added `_tokensOfOwner(address owner)`, allowing to internally retrieve the array of an account's owned tokens. ([#1522](https://github.com/OpenZeppelin/openzeppelin-solidity/pull/1522))
 * Crowdsales: all constructors are now `public`, meaning it is not necessary to extend these contracts in order to deploy them. The exception is `FinalizableCrowdsale`, since it is meaningless unless extended. ([#1564](https://github.com/OpenZeppelin/openzeppelin-solidity/pull/1564))
 * `SignedSafeMath`: added overflow-safe operations for signed integers (`int256`). ([#1559](https://github.com/OpenZeppelin/openzeppelin-solidity/pull/1559), [#1588](https://github.com/OpenZeppelin/openzeppelin-solidity/pull/1588))

### Improvements:
 * The compiler version required by `Array` was behind the rest of the libray so it was updated to `v0.4.24`. ([#1553](https://github.com/OpenZeppelin/openzeppelin-solidity/pull/1553))
 * Now conforming to a 4-space indentation code style. ([1508](https://github.com/OpenZeppelin/openzeppelin-solidity/pull/1508))
 * `ERC20`: more gas efficient due to removed redundant `require`s. ([#1409](https://github.com/OpenZeppelin/openzeppelin-solidity/pull/1409))
 * `ERC721`: fixed a bug that prevented internal data structures from being properly cleaned, missing potential gas refunds. ([#1539](https://github.com/OpenZeppelin/openzeppelin-solidity/pull/1539) and [#1549](https://github.com/OpenZeppelin/openzeppelin-solidity/pull/1549))
 * `ERC721`: general gas savings on `transferFrom`, `_mint` and `_burn`, due to redudant `require`s and `SSTORE`s. ([#1549](https://github.com/OpenZeppelin/openzeppelin-solidity/pull/1549))

### Bugfixes:

### Breaking changes:

### Deprecations:
 * `ERC721._burn(address owner, uint256 tokenId)`: due to the `owner` parameter being unnecessary. ([#1550](https://github.com/OpenZeppelin/openzeppelin-solidity/pull/1550))
 * `RefundableCrowdsale`: due to trading abuse potential on crowdsales that miss their goal. ([#1543](https://github.com/OpenZeppelin/openzeppelin-solidity/pull/1543))
