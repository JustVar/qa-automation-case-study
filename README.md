# QA Automation Case Study: Soterix Systems

A test automation framework I built for NexaiQ-Core, the cloud web app of
Soterix Systems, a company selling AI video analytics as a service, while I was
its System Platform QA/QC Manager. It is three connected repos: a browser test
suite, an API test suite, and a shared pytest pipeline that records every run,
explains its failures, reports the results to QA Touch, Slack and email, and
files bugs in Jira. QA Touch is a test management tool: it holds a team's test
cases and records the result of each test run, manual or automated. I built
the framework with AI coding agents, under rules and checks I set up so that
their output had to prove itself.

| | |
|---|---|
| Browser tests | 402 Playwright tests across 13 product areas, each mapped to its test case in QA Touch |
| API tests | 55 functional tests, a sweep of 101 read endpoints, 17 partner-API tests |
| Tests of the tooling itself | 475 in the browser repo, 42 in the API repo, 652 in the shared package |
| Integrations | QA Touch (test management), Jira (defects), Slack and Microsoft 365 email (reports) |
| Scale | About 900 commits across three repos, 31 tagged releases of the shared package |
| Stack | Python, pytest, Playwright, REST API testing (requests), CI/CD with GitHub Actions, QA Touch, Jira, Slack, Microsoft 365, AI coding agents (Claude Code, OpenAI Codex, Microsoft 365 Copilot) |

## The three repos

| Repo | What it is | Start with |
|---|---|---|
| [Soterix-WebApp-QA](https://github.com/JustVar/Soterix-WebApp-QA) | Browser tests of the web app. A test does what a user does in Chrome, and a report page says what failed and why. | [the stream guard](https://github.com/JustVar/Soterix-WebApp-QA/blob/main/tests/shared/helpers/stream_health.py), [the convention checker](https://github.com/JustVar/Soterix-WebApp-QA/blob/main/tools/convention_check.py) |
| [Soterix-API-QA](https://github.com/JustVar/Soterix-API-QA) | API tests of the internal and partner APIs, with no browser. | [the login triage](https://github.com/JustVar/Soterix-API-QA/blob/main/api_clients/auth_helper.py), [the endpoint inventory](https://github.com/JustVar/Soterix-API-QA/blob/main/docs/INTERNAL_API_INVENTORY.md) |
| [SOTERIX-QA-SHARED](https://github.com/JustVar/SOTERIX-QA-SHARED) | The pipeline both suites install: run records, report pages, the QA Touch upload, the CI gates. | [the verified upload](https://github.com/JustVar/SOTERIX-QA-SHARED/blob/main/src/soterix_qa_shared/qatouch/upload.py), [the run report page](https://github.com/JustVar/SOTERIX-QA-SHARED/blob/main/src/soterix_qa_shared/reporting/run_page.py) |

## How it fits together

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="diagram/architecture-dark.svg">
  <img src="diagram/architecture-light.svg" width="900" alt="Scheduled runs on a Linux lab server and a Windows runner feed the browser suite. Both test suites run through the shared pytest pipeline, which produces reports (run archive, Slack, email), test management results (QA Touch, a Jira bug filer) and run records.">
</picture>

A nightly on a Linux lab server ran the browser suite against two test
tenants, and a Windows machine ran the live-video tests, which need a browser
that can decode H.265 video. Each run posted a summary to Slack, and the
pipeline can email a run's report to a distribution list through Microsoft 365.
Any run, scheduled or started by hand, uploads its results to QA Touch when
the upload switch is on (`--qatouch-upload` with a QA Touch run key), and every
result is read back and checked.

Both suites install the shared pipeline as a package kept inside each repo, so
a new engineer needs access to one repo and nothing else. The pipeline hands
each finished run to a list of destinations, and adding one, such as a JUnit
file or a dashboard feed, means adding a small class, not changing the core.

A Jira bug filer scores each failure on its history and on the health of the
test environment, queues the bug for a QA engineer to approve, and then files
it with every required field of the Jira project filled in.

## Engineering highlights

1. **Results that are checked, not trusted.** QA Touch's API answers "success"
   for results it throws away. The uploader reads every result back and
   compares it, and a result it cannot confirm is queued for retry, never
   counted as a pass.
   [upload.py](https://github.com/JustVar/SOTERIX-QA-SHARED/blob/main/src/soterix_qa_shared/qatouch/upload.py)
2. **A report that names causes, not just failures.** The run page opens with
   a one-sentence verdict, groups failures that share one error, labels known
   app defects apart from new ones, and gives each failure its screenshot,
   video and trace.
   [run_page.py](https://github.com/JustVar/SOTERIX-QA-SHARED/blob/main/src/soterix_qa_shared/reporting/run_page.py)
3. **Measuring the environment before blaming the test.** The live-video
   tests need H.265, which Chrome on Linux cannot decode. Before any of them
   runs, the stream guard opens the video stream, counts frames, reads the
   codec and asks this browser whether it can play it. It measures twice
   before skipping, and it refuses headless Chrome on Windows, which claims
   the codec and never decodes a frame.
   [stream_health.py](https://github.com/JustVar/Soterix-WebApp-QA/blob/main/tests/shared/helpers/stream_health.py)
4. **Failing in one line instead of one minute.** Before any browser opens, a
   preflight signs in through the API and prints one line naming the cause of
   a problem: server down, wrong password, or wrong site.
   [preflight.py](https://github.com/JustVar/Soterix-WebApp-QA/blob/main/tests/shared/helpers/preflight.py)
5. **House rules a machine enforces.** A convention checker reads the code on
   every commit and blocks the patterns that caused real defects. Each message
   names the defect behind the rule.
   [convention_check.py](https://github.com/JustVar/Soterix-WebApp-QA/blob/main/tools/convention_check.py)
6. **Test cases that come from the tests.** Each test carries its steps and
   expected result. A tool turns them into QA Touch cases, and an audit scores
   every test against its case and flags weak matches. All 402 browser tests
   are mapped.
   [qatouch_cases_from_tests.py](https://github.com/JustVar/Soterix-WebApp-QA/blob/main/tools/qatouch_cases_from_tests.py),
   [qatouch_mapping_audit.py](https://github.com/JustVar/Soterix-WebApp-QA/blob/main/tools/qatouch_mapping_audit.py)
7. **Credentials that cannot leak into evidence.** Every password is a type
   that prints `***`, and a scan checks the evidence of each run for leaked
   values, including escaped forms. Both were added after a password reached a
   shared test log.
   [secret.py](https://github.com/JustVar/Soterix-WebApp-QA/blob/main/config/secret.py),
   [evidence_scan.py](https://github.com/JustVar/Soterix-WebApp-QA/blob/main/tools/evidence_scan.py)
8. **API failures that explain themselves.** A failed login says whether the
   account is unknown, the password is stale or the server is unreachable. A
   failed test carries its HTTP requests and responses with secrets masked.
   Every endpoint the sweep skips records where and when the failure was
   measured.
   [auth_helper.py](https://github.com/JustVar/Soterix-API-QA/blob/main/api_clients/auth_helper.py),
   [endpoints.py](https://github.com/JustVar/Soterix-API-QA/blob/main/tests/internal_api/data/endpoints.py)
9. **Releases that cannot drift.** CI installs the built package and imports
   it, refuses a release tag that differs from the package version, and pins
   every action to a commit. Each test repo has a test that fails when the
   version it runs differs from the version it declares.
   [ci.yml](https://github.com/JustVar/SOTERIX-QA-SHARED/blob/main/.github/workflows/ci.yml)

### Why a custom pipeline

Three reasons. The company preferred in-house tools to paid third-party
services. Building it ourselves meant it fit the team's actual needs, such as
checking every QA Touch result and testing live H.265 video. And because it was
built with AI coding agents, building it in-house let me vet the agents' work
step by step, under the same rules and checks as the tests themselves.

## What the testing found

- An API call that answered `Successfully deleted!` and deleted nothing,
  confirmed in the UI.
  ([API_SURFACES.md](https://github.com/JustVar/Soterix-API-QA/blob/main/docs/API_SURFACES.md))
- The vendor's OpenAPI spec was missing at least 14 production endpoints, and
  it gives every endpoint the suites call a generic wrapper as its response,
  so it cannot describe what an endpoint returns. The suites document the 83
  internal endpoints they use from the live system instead, each with the
  date it was last confirmed.
- The first live run of the endpoint sweep failed 30 of 101 endpoints. The
  cause was in the test code (a channel looked up on the wrong site), not the
  product. After the fix the whole internal API suite ran 120 passed and 0
  failed, with 47 skipped for documented reasons.
- A known-defects list labels the failures caused by app defects already
  reported (when in use, it held 16 tests across 6 defects), so the run page separates them from
  new failures and a reader finds the new ones in minutes.

## How I work with AI coding agents

I built this with AI coding agents (Claude Code, OpenAI Codex and Microsoft 365
Copilot), and I was the human in the loop throughout. I set the plan and the
scope, reviewed and fact-checked what the agents produced, researched where
their answer was not enough, and wrote the documentation from the verified
result. The practices that kept their output honest:

- **Written rules.** Every repo has an
  [AGENTS.md](https://github.com/JustVar/Soterix-WebApp-QA/blob/main/AGENTS.md):
  what to read first, and hard rules such as "read a file fully before you
  edit it" and "propose a large rewrite instead of applying it".
- **Rules a machine enforces.** A rule that depends on memory fails, so the
  important ones are also
  [pre-commit checks](https://github.com/JustVar/Soterix-WebApp-QA/blob/main/tools/hooks/pre-commit)
  and CI steps: no credential in a staged line, the conventions hold, the test
  count did not fall, lint is clean, the offline suites pass.
- **Measure, do not assert.** A number in a doc or a commit has to come from a
  command that was run. A check has to be shown failing when it should before
  it is trusted, and a test is believed once a deliberate bug makes it fail.
- **Adversarial review.** I had the pipeline audited across seven dimensions
  (concurrency, multiple environments, network, partial outage, data
  integrity, security, performance): 32 raw findings, 30 confirmed, each
  given a resolution. The most serious, a trace file that could expose session
  cookies in the evidence archive, was fixed.
- **A writing standard.** Docs, comments and commit messages follow a short
  style guide with a mechanical check, so the prose stays plain and consistent
  whoever or whatever wrote it.

## What this makes possible

What is built supports these next steps directly:

- **A manual regression that shrinks as automation grows.** Because every
  browser test is mapped to its QA Touch case, each release can run as two
  runs: one the pipeline fills, and one for the manual team that holds only
  the cases no test covers yet.
- **Faster, steadier coverage of backend behaviour.** An API test runs in about
  a second, against about 13 seconds for a browser test, so checks of server
  behaviour can move to the API suite and keep the browser suite for what a
  user sees.
- **New products on the same pipeline.** A new suite, such as the partner
  admin tool or the mobile app, installs the shared package and gets the run
  records, report pages, QA Touch upload and CI gates through a thin setup
  layer, with no new pipeline code.
- **Defects filed from failures, with a person in the loop.** The Jira bug
  filer turns a confirmed failure into a complete bug report once a QA
  engineer approves it.
- **A team that can run it without its author.** A new engineer needs read
  access to one repo, the offline suites run on any machine, and every rule
  is written down with the reason behind it.

## Running the code

Soterix has since closed and its QA server is gone, so the browser and API
suites have nothing to run against. Each repo's offline suites still run on
any machine, and each README's first section says how. CI ran on the
company's copies of these repos and is switched off here. The full scheduled
setup (the nightly, the published run archive, the Slack posts and the
Windows runner) is preserved under a git tag in each repo, and each repo's
ARCHIVE.md lists it.

## Contact

Justin Varughese, [LinkedIn](https://www.linkedin.com/in/justin-var/)
