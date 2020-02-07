const { exec } = require('pkg');
const jetpack = require('fs-jetpack');
const os = require('os');

const platform = os.platform();
const package = jetpack.cwd('.').read('package.json', 'json');
const distFolder = 'dist/';
const distName = (package.productName).replace(/\s/g, '');
let distExtension = '.exe';

console.log('Packaging release executable for ' + platform);

if (platform === 'win32') {
    //windows
    //TODO: remove --public option for production, this is so we can get proper stack trace line #, also depends on import 'source-map-support/register'
    exec([ 'package.json', '--target', 'host', '--output', distFolder + distName + distExtension ]).then(() => {
        console.log('Packaging done!');
    }).catch((err) => {
        console.log('Packaging Error!');
        console.log(err);
    });
} else {
    //unix
    distExtension = '';
    distName.toLowerCase();
    exec([ 'package.json', '--target', 'host', '--output', distFolder + distName + distExtension ]).then(() => {
        console.log('Packaging done!');
    }).catch((err) => {
        console.log('Packaging Error!');
        console.log(err);
    });
}
