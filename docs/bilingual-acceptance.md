# 0.10.0 bilingual retrieval acceptance

## Live observations (2026-10-19 UTC)

These are bounded access observations, not guaranteed future availability or model-effectiveness tests. No confidential queries, logins or bypass were used.

| Route | Actual observation | Status and evidence limit |
| --- | --- | --- |
| Google normal browser, `site:reciyi.com "人民当家作主"` | Redirected to /sorry/ abnormal-traffic verification page | captcha; stopped Google automation, no query result evidence |
| Bing normal browser, identical exact site query | Rendered list headed “50 results”, but displayed studentdoctor.net entries unrelated to site or phrase | results_read; relevantResults=0 in displayed list; NOT empty_results or validated evidence, count not used |
| 译之有道 HTTPS homepage | Title 译之有道; public categories and search entry readable | text_read homepage only; operator identity unverified |
| reciyi.com bare host | TLS/connection closed in fetch and browser | fetch_failed; no TLS changes |
| www.reciyi.com homepage and /about/?c=about | Public pages readable; About says “热词译网站和微信小程序由志愿者维护，免费使用。” and “热词译网站是由个人开发的网站。” | text_read; self-description, no claim of official publisher identity |
| www.reciyi.com/search/ | “请登录后使用搜索功能！” | login_required; no login attempted |
| [Reciyi public article](https://www.reciyi.com/2025/12/12201-1.html), also page 2 | Bilingual text and dates readable; note says “注：为确保中英对照准确，“热词译”网站可能对中英文重新分段。” | text_read aggregator; both article pages inspected, no original-source hyperlink found in their link lists |
| [Linguee 法](https://www.linguee.com/chinese-english/translation/%E6%B3%95.html) | Dictionary and “External sources (not reviewed)” visible, with external source labels | text_read aggregator; external originals not verified in this check |

Example generated Google URL (an entry, not proof):

https://www.google.com/search?q=site%3Areciyi.com%20%22%E4%BA%BA%E6%B0%91%E5%BD%93%E5%AE%B6%E4%BD%9C%E4%B8%BB%22

Replace only `www.google.com` with `www.bing.com` for the tested independent fallback. Bing's rendered list did not yield usable evidence; direct public pages did. No HTTP 429 or Retry-After was observed; rate-limit handling is a documented policy, not a live-tested recovery claim. No JS-shell-to-browser recovery was exercised in these checks because Google was opened directly in the browser.

## Actual short bilingual observation

On Reciyi article page 1: “大家好！” ↔ “Greetings to all!” (complete opening sentences within the same aligned paragraph). Article title: “国家主席习近平发表二〇二六年新年贺词”; displayed dates exactly “发布时间：2025年12月31日” and “Published on Dec 31, 2025”. Context: opening greeting in a New Year message. Aggregator: 热词译. Original publisher and original URLs: unverified; paragraph introduction mentions China Media Group/internet transmission, which does not establish the translation publisher. Translation direction: unknown from this page alone. Alignment: the short opening greeting corresponds; applicability: a public-address greeting candidate only, not evidence for 人民当家作主 or a general register recommendation. Target-language verification remains pending. No assistant rewrite is passed off as quotation. This observation was not saved into the user's library.

## Offline acceptance

`python3 -m unittest tools.test_bilingual tools.test_library` covers encoded Chinese/quotes/spaces/reserved characters, fixed hosts, rejection of unsafe input, no secret echo on errors, offline construction, actual temporary Markdown save/readback of a synthetic bilingual pair and exact provenance, immutable practice snapshot, and existing confirmation safeguards. Fixtures use example.org and are not live evidence.

Manual review cases: “找双语译例” routes from tis without requiring an existing English candidate; “回查译法” keeps target-language verification. CAPTCHA stops that source; JS-only permits one normal-browser load; 429 honors Retry-After; login-only search does not prohibit independently public articles. Two copies of one speech count as one original, not corroboration. These are workflow acceptance cases, not measured model performance.

Execution result: metadata validator, EU reference/link validator, update notice and modified-copy/7 migration scenarios, 9 unittest cases (bilingual + library), diagnosis save regression and git diff whitespace check passed. Managed sync applied without conflicts and subsequent --check reported Up to date. The independent usage-evidence SKILL hash was unchanged. No user Obsidian evidence note was created.
