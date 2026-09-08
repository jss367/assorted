# Assorted

This is my repo for all the one-off things that I like to build that don't need a repo of their own.

## Calculators

- [Robo-Advisor Comparison Calculator](https://jss367.github.io/assorted/investments/) — compare investment platforms.
- [Rent versus buy calculator](https://jss367.github.io/assorted/rent-versus-buy/) — compare housing costs, investments, and home equity over time. You can also open [the HTML file](rent-versus-buy/index.html) directly in a browser; no installation is required.

The publishing workflow stages both calculators in their own subdirectories on GitHub Pages, leaving the site root available for another page.
Changes to either calculator folder or the workflow on `master` publish automatically; the workflow can also be run manually from the Actions tab.
To publish another site alongside the calculators, extend the same workflow to stage its files too: each Pages deployment replaces the entire published site.
