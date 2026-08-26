<!-- LC-SYNC:AUTO-GENERATED:START — do not edit below, it is overwritten on every sync -->

# 1365. How Many Numbers Are Smaller Than the Current Number

**Difficulty:** Easy  |  **LeetCode:** [how-many-numbers-are-smaller-than-the-current-number](https://leetcode.com/problems/how-many-numbers-are-smaller-than-the-current-number/)
**Topics:** Array, Hash Table, Sorting, Counting Sort

**Latest submission:** ✅ Accepted in C — see [`solution.c`](solution.c)

## Problem Statement

Given the array `nums`, for each `nums[i]` find out how many numbers in the array are smaller than it. That is, for each `nums[i]` you have to count the number of valid `j's` such that `j != i` **and** `nums[j] < nums[i]`.

Return the answer in an array.

 

**Example 1:**

```

**Input:** nums = [8,1,2,2,3]
**Output:** [4,0,1,1,3]
**Explanation:**
For nums[0]=8 there exist four smaller numbers than it (1, 2, 2 and 3).
For nums[1]=1 does not exist any smaller number than it.
For nums[2]=2 there exist one smaller number than it (1).
For nums[3]=2 there exist one smaller number than it (1).
For nums[4]=3 there exist three smaller numbers than it (1, 2 and 2).

```

**Example 2:**

```

**Input:** nums = [6,5,4,8]
**Output:** [2,1,0,3]

```

**Example 3:**

```

**Input:** nums = [7,7,7,7]
**Output:** [0,0,0,0]

```

 

**Constraints:**

- `2 <= nums.length <= 500`

- `0 <= nums[i] <= 100`

## Submission History

| Date | Status | Language | Runtime | Memory | Code |
| --- | --- | --- | --- | --- | --- |
| 2026-08-16 06:28 UTC | ✅ Accepted | C | 9 ms | 12 MB | [view](submissions/1786861731_Accepted_2108632484.c) |
| 2026-08-16 06:28 UTC | ✅ Accepted | C | 21 ms | 11.9 MB | [view](submissions/1786861716_Accepted_2108632245.c) |
| 2026-08-16 06:28 UTC | ✅ Accepted | C | 16 ms | 12 MB | [view](submissions/1786861687_Accepted_2108631700.c) |
| 2026-08-16 06:27 UTC | ✅ Accepted | C | 18 ms | 11.8 MB | [view](submissions/1786861643_Accepted_2108630920.c) |
| 2026-08-16 06:27 UTC | ✅ Accepted | C | 17 ms | 12 MB | [view](submissions/1786861623_Accepted_2108630538.c) |
| 2026-08-16 06:26 UTC | ✅ Accepted | C | 15 ms | 12 MB | [view](submissions/1786861614_Accepted_2108630360.c) |
| 2026-08-16 06:08 UTC | ✅ Accepted | C | 4 ms | 11.9 MB | [view](submissions/1786860486_Accepted_2108610463.c) |
| 2026-08-16 06:07 UTC | 💥 Runtime Error | C | N/A | N/A | [view](submissions/1786860471_Runtime-Error_2108610229.c) |
| 2026-08-16 05:50 UTC | ✅ Accepted | C | 16 ms | 12 MB | [view](submissions/1786859443_Accepted_2108592497.c) |

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
