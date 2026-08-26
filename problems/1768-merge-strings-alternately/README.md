<!-- LC-SYNC:AUTO-GENERATED:START — do not edit below, it is overwritten on every sync -->

# 1768. Merge Strings Alternately

**Difficulty:** Easy  |  **LeetCode:** [merge-strings-alternately](https://leetcode.com/problems/merge-strings-alternately/)
**Topics:** Two Pointers, String

**Latest submission:** ✅ Accepted in C — see [`solution.c`](solution.c)

## Problem Statement

You are given two strings `word1` and `word2`. Merge the strings by adding letters in alternating order, starting with `word1`. If a string is longer than the other, append the additional letters onto the end of the merged string.


Return *the merged string.*


 

**Example 1:**


```

**Input:** word1 = "abc", word2 = "pqr"
**Output:** "apbqcr"
**Explanation:** The merged string will be merged as so:
word1:  a   b   c
word2:    p   q   r
merged: a p b q c r

```




**Example 2:**


```

**Input:** word1 = "ab", word2 = "pqrs"
**Output:** "apbqrs"
**Explanation:** Notice that as word2 is longer, "rs" is appended to the end.
word1:  a   b 
word2:    p   q   r   s
merged: a p b q   r   s

```




**Example 3:**


```

**Input:** word1 = "abcd", word2 = "pq"
**Output:** "apbqcd"
**Explanation:** Notice that as word1 is longer, "cd" is appended to the end.
word1:  a   b   c   d
word2:    p   q 
merged: a p b q c   d

```




 

**Constraints:**



- `1 <= word1.length, word2.length <= 100`

- `word1` and `word2` consist of lowercase English letters.

## Submission History

| Date | Status | Language | Runtime | Memory | Code |
| --- | --- | --- | --- | --- | --- |
| 2026-08-18 15:26 UTC | ✅ Accepted | C | 0 ms | 8.6 MB | [view](submissions/1787066795_Accepted_2111606754.c) |

<!-- LC-SYNC:AUTO-GENERATED:END -->

<!-- LC-SYNC:PERSONAL:START — write freely below, this section is never touched by sync -->

### My Approach

_How I personally solved it — write this yourself._

### Complexity

- Time complexity:
- Space complexity:

### My Notes

_Mistakes made, edge cases missed, anything worth remembering._

### What I Learned

_Anything useful for next time._

<!-- LC-SYNC:PERSONAL:END -->
