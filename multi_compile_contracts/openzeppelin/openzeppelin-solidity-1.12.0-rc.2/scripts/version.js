#!/usr/bin/env node

// Synchronizes ethpm.json version number with package.json.
// Useful to run as an npm script alogn with `npm version`.

const fs = require('fs');
const cp = require('child_process');

const pkg = require('../package.json');
const ethpm = require('../ethpm.json');

ethpm.version = pkg.version;

fs.writeFileSync('ethpm.json', JSON.stringify(ethpm, null, 2) + '\n');

cp.execSync('git add ethpm.json');
