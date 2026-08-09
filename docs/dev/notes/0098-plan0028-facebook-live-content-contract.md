# Plan 0028 Facebook Live Content Contract

Recorded: 2026-08-08
Plan: `0028`
Roadmap lane: `P12`
Evidence target: retained `session:last30days-facebook`, target
`49A438C7436B310E8375EC630BF55DAD`

## Privacy Boundary

This note preserves structural and aggregate evidence only. It intentionally
omits post bodies, personal messages, cookies, tokens, account identifiers,
raw profile URLs, media URLs, and opaque Facebook IDs. The synthetic regression
uses dummy authors, content, and IDs.

## Live Page Model

The authenticated `OpenAI` recent-post search exposed:

- one `main` search-results region and one feed;
- five visible post-action controls: two author-named organic controls and
  three generic controls belonging to ads;
- organic result cards without a reliable `role=article` boundary, requiring
  the smallest unique action-owner ancestor already used by the adapter;
- ad cards with a reliable closest `role=article` boundary;
- post identity recoverable from a canonical post route or a photo/set route
  that deterministically recovers a canonical post permalink;
- timestamps rendered as position-scrambled single-glyph descendants. Raw DOM
  order is noise; glyphs whose rectangles remain inside the timestamp anchor,
  sorted by rendered position, yield a bounded relative or absolute label;
- ad disclosure rendered by the same glyph mechanism as the human-visible
  label `Ad` rather than a stable plain-text `Sponsored` node.

## Scrapable Post

A Facebook search result is scrapable only when one owning card binds all of:

1. a non-sponsored post action/control and author heading;
2. substantive topic-relevant body text;
3. a canonical post identity, directly or through deterministic media/set
   recovery;
4. a human-visible timestamp label that parses to the requested interval with
   non-low confidence;
5. optional media and bounded engagement metadata owned by the same card.

The following remain non-posts: ads/sponsored cards, navigation/filter chrome,
people/pages/groups/recommendations, comments without their own post identity,
login/checkpoint surfaces, and nested action/media shells.

## Red Evidence

The unchanged live page evaluated through the pre-repair extractor produced:

- candidates: 5;
- accepted: 0;
- candidate kinds: 2 posts, 3 unknown;
- rejection counts: `missing_date=5`, `kind_unknown=3`,
  `missing_permalink=3`, `missing_author=3`, `off_topic=3`.

The exact failure was deterministic:

- timestamp selection chose the first anchor with any `aria-label`, which was
  the author anchor;
- raw `innerText` for the actual timestamp anchor contained scrambled glyph
  noise;
- the date parser did not accept current labels such as compact hour notation
  or `Yesterday at <clock>`;
- generic ad controls were excluded from action-card modeling and the rendered
  `Ad` disclosure was not recognized.

## Candidate Repair Evidence

The same retained page evaluated through the working-tree candidate produced:

- candidates: 5;
- accepted by the unchanged quality guarantees: 2 posts;
- candidate kinds: 2 posts, 3 ads;
- both accepted posts carried a canonical identity, author, in-range date, and
  topic-relevant substantive text;
- all three ads were explicitly rejected with `kind_ad` and `sponsored` among
  their reasons.

This is direct adapter evidence, not installed-runtime or governed-tick proof.
Plan 0028 remains open until an immutable successor is installed and one
preflight-predicted manual tick satisfies the end-to-end acceptance gate.
