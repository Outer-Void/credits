# Source header policy (template)

Use only in files **authored by Outer Void** in repositories whose decision is `PROPRIETARY_OUTER_VOID`,
`PUBLIC_SOURCE_PROPRIETARY` or `PRIVATE_PROPRIETARY` (see `projects/<repo>.yaml`).

```
Copyright (c) <YEAR> Outer Void. All rights reserved.
SPDX-License-Identifier: LicenseRef-OuterVoid-Proprietary
Credits and third-party notices: https://github.com/Outer-Void/credits
```

Never:
- add this header to a file that came from, or substantially derives from, a third party (upstream, fork,
  vendored, template-generated, or copied snippet);
- replace or remove an existing copyright/licence header. Add the Outer Void line **below** an upstream header
  only when Outer Void has made material modifications, and mark them (`Modifications copyright (c) ...`);
- apply it to `blhermes-agent` (MIT, Nous Research) or any `UPSTREAM_LICENSE_RETAINED` repository;
- apply it to a repository currently under Apache-2.0/MIT until the owner records a relicensing decision
  (`UNR-008`). Already-published versions keep their licence.

Machine check: an Outer Void header in a file that a lineage record (`provenance/source-lineage.yaml`)
marks as third-party is a defect.
