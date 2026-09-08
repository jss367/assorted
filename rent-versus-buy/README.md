# Rent versus buy calculator

Open [index.html](index.html) directly in a browser. The calculator is a standalone HTML file with no dependencies, network requests, or build step.

Enter a home price, comparable rent, expected length of stay, and financing assumptions. Expand the cost sections to adjust purchase and sale costs, maintenance, insurance, tax estimates, and a refundable rental deposit. Results update immediately, including a wealth chart, a sensitivity table, and an annual breakdown that can be downloaded as CSV with the input assumptions.

The model compares equal starting cash and equal monthly budgets. Each option invests its unused upfront cash and any monthly housing savings. Buying wealth includes home value less the remaining mortgage and selling costs, plus investments. Renting wealth includes investments and the returned deposit. The page documents growth timing, simplified mortgage insurance, and excluded costs. Defaults are illustrative; tax benefits require a user-supplied estimate.

Run the financial model tests with Node.js 18 or later:

```sh
node --test rent-versus-buy/calculator.test.cjs
```

The tests execute the same embedded model used in the browser and cover amortization, opportunity cost, equal budgets, deposits, growth, mortgage insurance, and edge cases.
