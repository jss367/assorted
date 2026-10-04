const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync(`${__dirname}/index.html`, 'utf8');
const context = vm.createContext({});
vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1], context);
const { DEFAULTS, calculate, mortgagePayment, validate } = context.RentBuy;
const near = (actual, expected, tolerance = .01) => assert.ok(Math.abs(actual - expected) < tolerance, `${actual} should equal ${expected}`);
const simple = {
  ...DEFAULTS, price:120000, down:20, mortgageRate:0, term:10, years:10,
  appreciation:0, propertyTax:0, buyCosts:0, sellCosts:0, maintenance:0,
  homeInsurance:0, hoa:0, mortgageInsurance:0, expenseGrowth:0, taxSavings:0,
  rent:800, rentGrowth:0, investmentReturn:0, rentInsurance:0, depositMonths:0
};

test('standard mortgage agrees with independently tabulated payment and balance', () => {
  // $100,000 at 6% for 30 years: monthly $599.550525; balance after 12 payments $98,771.988294.
  near(mortgagePayment(100000, 6, 30), 599.550525);
  const result = calculate({...simple, price:100000, down:0, mortgageRate:6, term:30, years:1});
  near(result.final.balance, 98771.988294);
});

test('zero-interest mortgage pays only principal and stops at maturity', () => {
  const result = calculate({...simple, years:12});
  near(result.payment, 800);
  near(result.rows[12].balance, 86400);
  near(result.rows[120].balance, 0);
  near(result.rows[144].balance, 0);
  near(result.final.buyerInvestments, 24 * 800);
  near(result.final.rentWealth, 24000);
});

test('all-cash ownership invests monthly savings and appreciates correctly', () => {
  const result = calculate({...simple, down:100, appreciation:5, rent:1000, years:1});
  near(result.payment, 0);
  near(result.final.home, 126000);
  near(result.final.buyerInvestments, 12000);
  near(result.final.buyWealth, 138000);
  near(result.final.rentWealth, 120000);
});

test('upfront costs, sale costs, and refundable deposits are accounted for once', () => {
  const result = calculate({...simple, down:100, rent:1000, depositMonths:2, buyCosts:3, sellCosts:6, years:1});
  near(result.startingCash, 123600);
  near(result.rows[0].rentWealth, 123600);
  near(result.rows[0].buyWealth, 112800);
  near(result.final.rentWealth, 123600);
  near(result.final.buyWealth, 124800);
  near(result.final.difference, 1200);
});

test('renter invests avoided purchase cash and every monthly saving', () => {
  const result = calculate({...simple, rent:0, investmentReturn:12, years:1});
  const monthlyRate = 1.12 ** (1 / 12) - 1;
  const expected = 24000 * 1.12 + 800 * ((1 + monthlyRate) ** 12 - 1) / monthlyRate;
  near(result.final.renterInvestments, expected);
  near(result.final.buyerInvestments, 0);
});

test('equal budgets hold when the renter deposit exceeds buyer upfront cash', () => {
  const result = calculate({...simple, down:0, rent:2000, depositMonths:12, years:1});
  near(result.startingCash, 24000);
  near(result.rows[0].buyerInvestments, 24000);
  near(result.rows[0].renterInvestments, 0);
  near(result.final.buyerInvestments, 24000 + 12 * 1000);
  near(result.final.rentWealth, 24000);
});

test('annual rent and expenses grow on anniversaries, not in the first year', () => {
  const result = calculate({...simple, rent:1000, rentGrowth:10, propertyTax:1, expenseGrowth:10, years:2});
  near(result.rows[12].renterPaid, 12000);
  near(result.rows[24].renterPaid, 25200);
  near(result.rows[12].buyerPaid, 24000 + 12 * 900);
  near(result.rows[24].buyerPaid, 24000 + 12 * 900 + 12 * 910);
});

test('mortgage insurance ends at the modeled original-value threshold', () => {
  const result = calculate({...simple, price:120000, down:10, mortgageInsurance:100, years:2});
  // $900 principal per month. Starting balance is at/below $93,600 from month 17.
  near(result.rows[16].buyerPaid - result.buyerUpfront, 16 * 1000);
  near(result.rows[17].buyerPaid - result.rows[16].buyerPaid, 900);
  near(calculate({...simple, down:100, mortgageInsurance:100}).firstMonth.insurance, 0);
});

test('negative home equity stays visible, and negative returns compound', () => {
  const result = calculate({...simple, down:0, mortgageRate:6, term:30, appreciation:-20, investmentReturn:-20, years:1});
  assert.ok(result.final.buyWealth < 0);
  assert.ok(result.rows.every(row => Number.isFinite(row.difference)));
  const cash = calculate({...simple, down:100, rent:0, investmentReturn:-20, years:1});
  near(cash.final.rentWealth, 96000);
});

test('crossover distinguishes ties, a first monthly lead, and no lead', () => {
  const tie = calculate({...simple, down:100, rent:0});
  near(tie.final.difference, 0);
  assert.equal(tie.firstBuyingLead, null);
  assert.equal(calculate(simple).firstBuyingLead, 1);
  assert.equal(calculate({...simple, rent:0, buyCosts:10, sellCosts:10}).firstBuyingLead, null);
});

test('both sides have identical cumulative budgets when returns are zero', () => {
  const result = calculate({...DEFAULTS, investmentReturn:0, taxSavings:2400});
  for (const row of result.rows) {
    near(row.buyerPaid + row.buyerInvestments, row.renterPaid + row.renterInvestments);
  }
});

test('model rejects missing, nonfinite, out-of-range, and fractional-year inputs', () => {
  for (const change of [{rent:NaN}, {price:Infinity}, {price:0}, {years:0}, {years:1.5}, {term:0}, {down:101}, {investmentReturn:-100}, {rent:undefined}]) {
    assert.ok(validate({...DEFAULTS, ...change}));
    assert.throws(() => calculate({...DEFAULTS, ...change}));
  }
  assert.equal(validate(DEFAULTS), null);
});

test('valid extremes remain finite throughout a forty-year projection', () => {
  for (const changes of [
    {price:100000000, rent:100000, appreciation:20, investmentReturn:25, years:40},
    {price:1, down:100, rent:0, appreciation:-20, investmentReturn:-20, years:40},
    {mortgageRate:25, down:0, term:1, years:40},
    {mortgageRate:.00000001, term:40, years:40}
  ]) {
    const result = calculate({...DEFAULTS, ...changes});
    assert.ok(result.rows.every(row => Object.values(row).every(Number.isFinite)));
    assert.ok(result.final.balance >= 0);
  }
});
