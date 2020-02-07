const Table = require('cli-table3');
const DateFormatter = require('./DateFormatter');

function create_table($options = {}) {
    $options.chars =  { 'top': '═' , 'top-mid': '╤' , 'top-left': '╔' , 'top-right': '╗'
               , 'bottom': '═' , 'bottom-mid': '╧' , 'bottom-left': '╚' , 'bottom-right': '╝'
               , 'left': '║' , 'left-mid': '╟' , 'mid': '─' , 'mid-mid': '┼'
               , 'right': '║' , 'right-mid': '╢' , 'middle': '│' };

    return new Table($options);
}

function format_amount(amount) {
    var calculatedAmount = Math.abs(amount) / Math.pow(10, 9);
    var formatted = calculatedAmount.toFixed(9) + "ツ";
    if (amount < 0) {
        formatted = "-" + formatted;
    }

    return formatted;
}

function totals(summary) {
    var table = create_table({ head: ['Status', 'Amount']});

    table.push(
        { 'Spendable': [format_amount(summary.spendable)] },
        { 'Total': [format_amount(summary.total)] },
        { 'Immature': [format_amount(summary.immature)] },
        { 'Unconfirmed': [format_amount(summary.unconfirmed)] },
        { 'Locked': [format_amount(summary.locked)] }
    );

    console.log(table.toString());
}

function transactions(txs) {
    var table = create_table({ head: ["ID", "Created Dt/Tm", "Status", "Address", "Amount"] });

    txs.forEach((tx, index) => {
        table.push(
            [ 
                tx.id,
                DateFormatter.format(new Date(tx.creation_date_time * 1000)),
                tx.status,
                tx.address,
                format_amount(tx.amount)
            ]
        );
    });

    console.log(table.toString());
}

module.exports = { totals, transactions }