const outer = {};
outer.CreateWallet = require('./CreateWallet');
outer.RestoreWallet = require('./RestoreWallet');
outer.OpenWallet = require('./OpenWallet');

const inner = {};
inner.Summary = require('./Summary');
inner.Send = require('./Send');
inner.Receive = require('./Receive');
inner.Finalize = require('./Finalize');
inner.Clear = require('./Clear');
inner.Exit = require('./Exit');

exports.outer = outer;
exports.inner = inner;