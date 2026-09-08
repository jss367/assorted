# Assorted

This is my repo for all the one-off things that I like to build that don't need a repo of their own.

## Investment calculator

The [Robo-Advisor Comparison Calculator](https://jss367.github.io/assorted/investments/) is hosted on GitHub Pages.
The publishing workflow stages only the `investments/` folder, preserving that subdirectory in the published site and leaving the site root available for another page.
Changes to that folder or the workflow on `master` publish automatically; the workflow can also be run manually from the Actions tab.
To publish another site alongside the calculator, extend the same workflow to stage its files too: each Pages deployment replaces the entire published site.
