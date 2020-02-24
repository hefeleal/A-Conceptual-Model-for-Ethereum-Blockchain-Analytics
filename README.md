# A Conceptual Model for Ethereum Blockchain Analytics

This repository contains all code that I wrote for my Master's thesis.

## Abstract
In this thesis, we develop a comprehensive formal model representing the Ethereum platform in the form of UML class diagrams. Splitting the system into the four parts "Source", "EVM", "Storage", and "Ledger" helps us to bring a clear structure into this complex environment. These four parts aim to give a deep understanding of the contract-programming language Solidity, the underlying Ethereum Virtual Machine, how each node in the network stores account and state information, and the contents of the blockchain itself.

Afterwards, we apply our knowledge about the system and explore what data can be extracted from the Ethereum platform, and how this can be done efficiently. In the relational database that we build up, we store bytecodes and additional information of all user- and contract-created smart contracts from the first 6,900,000 blocks.

With this data, we perform different analyses to gain more insights into the system. The researched anomalies include front-running, self-destructing constructors, and transactions to accounts that only become contracts after the transaction has been executed. Additionally, we cluster smart contracts based on different criteria, like who created them and whether they implement ERC token standards. Consulting metadata information, like references of hard-coded addresses in the bytecode of contracts, the usage of certain function signature hashes, and the balances of contracts that a contract created, further refines our system understanding.

![Graph of user-created ERC20 and ERC721 tokens over time](https://raw.githubusercontent.com/hefeleal/A-Conceptual-Model-for-Ethereum-Blockchain-Analytics/master/thesis/screenshots/erc_tokens.png)

The main contribution of this work is the estimation of compiler and Solidity library versions of arbitrary smart contracts. With two heuristics based on the contract creation date and the bytecode header, we set a range of minimum and maximum compiler versions for every contract code. We discover usage of the most popular Solidity library "SafeMath" by compiling every version of the library with every compatible compiler version, extracting its internal functions, and comparing the resulting bytecodes with all contract codes deployed on the blockchain. That also helps us improve the compiler version estimation.

![Image of most used prefixes of smart contract bytecodes](https://raw.githubusercontent.com/hefeleal/A-Conceptual-Model-for-Ethereum-Blockchain-Analytics/master/thesis/screenshots/prefixes.png)

We evaluate our version estimations with verified contracts from the block explorer website Etherscan. For our compiler version estimation, the range we set is correct for 99% of the evaluated contract codes. The median size of the estimated compiler version range is 3. For SafeMath usage detection, we have a success rate of 82% with a median distance of 4. Despite considering 31 SafeMath versions, the highest library distance our approach sets for a contract code is only 14.

## Overview of this repository
The `diagrams` folder contains the raw UML class diagrams for the conceptual model. They were created with [PlantUML](https://plantuml.com/).

In the `database_model` folder, there is the SQL code to create the database which stores all data. This repository does not contain code to fill the `eth.functions` and `eth.verifiedContracts` tables because these tables were generated as part of other works at the chair.

The folder `contract_analysis` contains all Python scripts that were used for the analyses. Running a script with the `-h` option displays a usage description. The script `eth_util.py` contains utility functions that are used by other scripts.

`multi_compile_contracts` is a NodeJS project that can be used to compile a smart contract with multiple compiler versions at once. There is also a Shell script that compiles test contracts for each SafeMath library version with all compatible compiler versions. The test contracts, as well as the compiled binaries, are in the `multi_compile_contracts/openzeppelin/safemath` folder. To get historic Solidity compiler versions, [solc-bin](https://github.com/ethereum/solc-bin/) is used.

The NodeJS project in the `read_state_trie` folder was an experiment to read Ethereum's state trie directly. Unfortunately, it did not really work out as hoped.

All code in the `solidity` folder was used while experimenting with Solidity and the compiler. There is some source code, some compiled binaries and EVM bytecode opcodes.

The raw text outputs of many of the analysis scripts can be found in the `results` folder.

Finally, the `thesis` folder contains the Master's thesis in PDF format.

## Further reading

We submitted a research paper about library usage detection in Ethereum smart contracts to the CoopIS 2019 conference. It was published in [On the Move to Meaningful Internet Systems: OTM 2019 Conferences](https://link.springer.com/book/10.1007/978-3-030-33246-4) (pages 310 - 317) and it can be download [here](https://link.springer.com/chapter/10.1007/978-3-030-33246-4_20) (`DOI 10.1007/978-3-030-33246-4_20`). In the paper, we describe and evaluate a five-step approach to detect whether a smart contract uses the SafeMath library.

![Approach to detect library usage](https://raw.githubusercontent.com/hefeleal/A-Conceptual-Model-for-Ethereum-Blockchain-Analytics/master/thesis/screenshots/library_usage_detection_approach.png)

## Acknowledgements
I would like to thank my advisor [Uli Gallersdörfer](https://github.com/UliGall) and my supervisor [Prof. Dr. Florian Matthes](https://wwwmatthes.in.tum.de/pages/88bkmvw6y7gx/Prof.-Dr.-Florian-Matthes) for their extensive support.
