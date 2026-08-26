<!-- LC-SYNC:AUTO-GENERATED:START — do not edit below, it is overwritten on every sync -->

# 27. Remove Element

**Difficulty:** Easy  |  **LeetCode:** [remove-element](https://leetcode.com/problems/remove-element/)
**Topics:** Array, Two Pointers

**Latest submission:** ✅ Accepted in C — see [`solution.c`](solution.c)

## Problem Statement

Given an integer array `nums` and an integer `val`, remove all occurrences of `val` in `nums` **in-place**. The order of the elements may be changed. Then return *the number of elements in *`nums`* which are not equal to *`val`.

Consider the number of elements in `nums` which are not equal to `val` be `k`, to get accepted, you need to do the following things:

- Change the array `nums` such that the first `k` elements of `nums` contain the elements which are not equal to `val`. The remaining elements of `nums` are not important as well as the size of `nums`.

- Return `k`.

**Custom Judge:**

The judge will test your solution with the following code:

```

int[] nums = [...]; // Input array
int val = ...; // Value to remove
int[] expectedNums = [...]; // The expected answer with correct length.
                            // It is sorted with no values equaling val.

int k = removeElement(nums, val); // Calls your implementation

assert k == expectedNums.length;
sort(nums, 0, k); // Sort the first k elements of nums
for (int i = 0; i < actualLength; i++) {
    assert nums[i] == expectedNums[i];
}

```

If all assertions pass, then your solution will be **accepted**.

 

**Example 1:**

```

**Input:** nums = [3,2,2,3], val = 3
**Output:** 2, nums = [2,2,_,_]
**Explanation:** Your function should return k = 2, with the first two elements of nums being 2.
It does not matter what you leave beyond the returned k (hence they are underscores).

```

**Example 2:**

```

**Input:** nums = [0,1,2,2,3,0,4,2], val = 2
**Output:** 5, nums = [0,1,4,0,3,_,_,_]
**Explanation:** Your function should return k = 5, with the first five elements of nums containing 0, 0, 1, 3, and 4.
Note that the five elements can be returned in any order.
It does not matter what you leave beyond the returned k (hence they are underscores).

```

 

**Constraints:**

- `0 <= nums.length <= 100`

- `0 <= nums[i] <= 50`

- `0 <= val <= 100`

## Submission History

| Date | Status | Language | Runtime | Memory | Code |
| --- | --- | --- | --- | --- | --- |
| 2026-08-17 17:00 UTC | ✅ Accepted | C | 0 ms | 10.3 MB | [view](submissions/1786986001_Accepted_2110425260.c) |
| 2026-08-17 16:59 UTC | ✅ Accepted | C | 0 ms | 10.5 MB | [view](submissions/1786985977_Accepted_2110424675.c) |
| 2026-08-17 16:59 UTC | ✅ Accepted | C | 0 ms | 10.4 MB | [view](submissions/1786985956_Accepted_2110424169.c) |
| 2026-08-17 16:59 UTC | 🛠️ Compile Error | C | N/A | N/A | — |
| 2026-08-17 16:58 UTC | ✅ Accepted | C | 0 ms | 10.5 MB | [view](submissions/1786985937_Accepted_2110423668.c) |
| 2026-08-17 16:58 UTC | ✅ Accepted | C | 0 ms | 10.4 MB | [view](submissions/1786985928_Accepted_2110423434.c) |
| 2026-08-17 16:55 UTC | ✅ Accepted | C | 0 ms | 10.4 MB | [view](submissions/1786985753_Accepted_2110418950.c) |
| 2026-08-17 16:55 UTC | 🛠️ Compile Error | C | N/A | N/A | [view](submissions/1786985726_Compile-Error_2110418302.c) |
| 2026-08-17 16:54 UTC | ✅ Accepted | C | 0 ms | 10.5 MB | [view](submissions/1786985696_Accepted_2110417531.c) |
| 2026-08-17 16:53 UTC | ✅ Accepted | C | 0 ms | 10.5 MB | [view](submissions/1786985632_Accepted_2110415995.c) |
| 2026-08-17 16:53 UTC | ✅ Accepted | C | 0 ms | 10.3 MB | [view](submissions/1786985585_Accepted_2110414846.c) |

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
