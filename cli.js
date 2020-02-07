#!/usr/bin/env node
const commander = require('commander');
const GrinPP = require('./lib/GrinPP.class');
const commands = require('./lib/cli/commands');

async function cli() {
    var program = new commander.Command()
        .version('0.7.5', '-v, --version', 'output the current version')
        .name('GrinPP')
        .description('Grin++ CLI');

    Object.keys(commands.outer).forEach((key) => {
        commands.outer[key].add_command(program);
    });
    
    program.on('--help', function(){
        console.log('')
        console.log('Examples:');
        console.log('  $ GrinPP help');
        console.log('  $ GrinPP create username password');
        console.log('  $ GrinPP restore username password word1 word2...word24');
        console.log('  $ GrinPP open username password');
    });

    await program.parseAsync(process.argv);

    if (global.session_token != null) {
        await new GrinPP(global.session_token).execute();
    }
}

cli();