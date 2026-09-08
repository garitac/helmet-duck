# Helmet Duck marketplace

**One add, every product.** This repository is the Claude Code marketplace for Helmet Duck,
deterministic tools for coding agents, sold at https://helmetduck.com. It holds one file that
matters, `.claude-plugin/marketplace.json`, and it exists so that the line every user types
never changes:

```
/plugin marketplace add garitac/helmet-duck
```

## Products

| Product | Install | Developed at | Version |
| --- | --- | --- | --- |
| Helmet Duck Bushido: gates, a dissent chair and a mirror for Claude Code and Codex, the rules an agent cannot skip | `/plugin install helmet-duck-bushido@helmet-duck` | https://github.com/garitac/helmet-duck-bushido | 0.4.0 |
| Helmet Duck Eyes: sight measured from rendered pixels, for agents that must judge what a page shows | listed when its first version is tagged | https://github.com/garitac/helmet-duck-eyes | in development |

Read a product's `RISKS.md` in its repository before installing it. Installing or using a
product means you accept the risks listed there and the terms at
https://helmetduck.com/terms.html. The site's source is https://github.com/garitac/helmet-duck-website.

## How a product gets listed

A version is tagged in the product's repository. One pull request here changes that
product's entry. The gate, `tools/check.py`, checks that the file parses, that every name is
unique, that every source is one of the owner's repositories, and that the version pinned
here equals the version in that repository's plugin manifest on its `main` branch. The
product's pages on the site change in the website repository. Nothing is installed from
here: a user's Claude Code reads this file and fetches the product from its own repository.

## Support

Issues are off in this repository on purpose. Report a defect in the product's own
repository. Report a vulnerability through the Security tab of
https://github.com/garitac/helmet-duck-website, in English.

## Licence

Copyright (c) 2026 Carlos Garita. All rights reserved. This repository is an index; plugin
tooling may read and copy it to install the products it lists. Each product carries its own
licence in its own repository. See `LICENSE`.
