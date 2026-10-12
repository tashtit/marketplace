# One Test Definition, Many Runtimes

When the same checks must run against code in several languages, define each test case once in a
language-neutral form. Give each runtime its own adapter, rather than copying the tests per runtime
[S6].

## When it applies

- The system checks user-written code against expected results, and users may write that code in any
  of several languages [S6].
- An interviewer asks how test cases would actually run, which moves the discussion past drawing
  boxes to implementation [S6].

## Why it matters

Writing a separate set of test cases for every problem in every language would be, in the source's
words, a nightmare to maintain [S6]. The alternative is one set per problem that runs against any
language [S6].

## Method

The source lists three parts [S6]:

- **A standard serialization** for each test case's input and expected output.
- **A test harness per language** that deserializes the input, passes it to the user's code, and
  compares the result with the deserialized expected output.
- **A serialization strategy for each data structure.** The harness of every language must
  deserialize each structure the same way.

*Example:* the source serializes a tree as an array in level order (breadth-first). Each language
supplies its own tree-node class that rebuilds the tree from that array before calling the user's
function [S6]. The helper type has to be present next to the user's code in the execution
environment [S6].

The test cases sit with the problem record, each tagged with the type of its input [S6].

## Failure modes

- **Diverging copies of the same tests** when they are maintained separately for each language
  [S6].

## Not covered by sources

- How to compare outputs whose correct answer is not unique, such as any valid ordering or
  floating-point results.
- How a new data structure or a new language is added, and how harnesses are kept consistent.
- How the harness reports which case failed and why, without exposing hidden test cases.
- How per-test time limits relate to the overall submission timeout.

## Sources

- **[S6]** Hello Interview — Design a Coding Platform Like LeetCode —
  <https://www.hellointerview.com/learn/system-design/problem-breakdowns/leetcode>
