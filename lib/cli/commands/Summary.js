const WalletAPI = require('../../api/WalletAPI');
const Tables = require('../Tables');
const Wallet = require('../Wallet');

var help = false;
var command = null;
class Summary {
    static add_command(program) {
        command = program.command('summary')
            .description('Wallet summary')
            .option('-c, --canceled', 'include canceled txs')
            .action(this.run)
            .allowUnknownOption(true);
        command._exit = () => {};
        command.on('--help', () => { help = true; })
    }
    
    static get_status(txn, lastConfirmedHeight) {
        const status = txn.type;
        if (status == "Sent" || status == "Received") {
            if ((txn.confirmed_height + 9) > lastConfirmedHeight) {
                return status + " (" + (lastConfirmedHeight - txn.confirmed_height + 1) + " Confirmations)";
            }

            return status;
        } else if (status == "Sending (Finalized)") {
            return "Sending (Unconfirmed)";
        } else {
            return status;
        }
    }

    static async run(command_obj) {
        if (help) {
            help = false;
            return;
        }

        Wallet.display_info();

        const headers = {
            session_token: global.session_token
        };

        const response = await WalletAPI.GET('retrieve_summary_info', headers, {});
        if (response != null && response.status_code == 200) {
            const summary = response.body;
            Tables.totals({
                spendable: summary.amount_currently_spendable,
                total: summary.total,
                immature: summary.amount_immature,
                unconfirmed: summary.amount_awaiting_confirmation,
                locked: summary.amount_locked
            });

            const txs = [];
            response.body.transactions.forEach((tx, index) => {
                const status = Summary.get_status(tx, response.body.last_confirmed_height);
                if (command_obj.canceled || status != 'Canceled') {
                    txs.push({
                        id: tx.id,
                        amount: tx.amount_credited - tx.amount_debited,
                        address: tx.address,
                        status: status,
                        creation_date_time: tx.creation_date_time
                    });
                }
            });

            Tables.transactions(txs);
        } else {
            console.error("Failed to retrieve wallet summary!\n");
            console.error(`Status: ${response.status_code}`);
            console.error(`Error: ${response.body}`);
        }
    }
}

module.exports = Summary;