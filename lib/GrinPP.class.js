const commander = require('commander');

const commands = require('./cli/commands');
const readline = require('readline');

class GrinPP {
    constructor($token) {
        this.token = $token;
        this.program = new commander.Command()
            .usage('<command> [options]');
        Object.keys(commands.inner).forEach((key) => {
            commands.inner[key].add_command(this.program);
        });
    }

    async execute() {
        this.program._exit = () => {};

        const args = (await this._waitForInput()).split(' ');
        args.unshift('1', '');

        try {
            await this.program.parseAsync(args);
        } catch (e) {
            console.error("Error:");
            console.error(e);
        }

        await this.execute();
    }

    _waitForInput() {
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout,
        });

        return new Promise(resolve => rl.question('> ', ans => {
            rl.close();
            resolve(ans);
        }));
    }
}

module.exports = GrinPP;