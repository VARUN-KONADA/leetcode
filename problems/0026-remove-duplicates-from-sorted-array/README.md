<!-- LC-SYNC:AUTO-GENERATED:START — do not edit below, it is overwritten on every sync -->

# 26. Remove Duplicates from Sorted Array

**Difficulty:** Easy  |  **LeetCode:** [remove-duplicates-from-sorted-array](https://leetcode.com/problems/remove-duplicates-from-sorted-array/)
**Topics:** Array, Two Pointers

**Latest submission:** ✅ Accepted in C — see [`solution.c`](solution.c)

## Problem Statement

Given an integer array `nums` sorted in **non-decreasing order**, remove the duplicates **in-place** such that each unique element appears only **once**. The **relative order** of the elements should be kept the **same**.

Consider the number of *unique elements* in `nums` to be `k**​​​​​​​**`​​​​​​​. After removing duplicates, return the number of unique elements `k`.

The first `k` elements of `nums` should contain the unique numbers in **sorted order**. The remaining elements beyond index `k - 1` can be ignored.

**Custom Judge:**

The judge will test your solution with the following code:

```

int[] nums = [...]; // Input array
int[] expectedNums = [...]; // The expected answer with correct length

int k = removeDuplicates(nums); // Calls your implementation

assert k == expectedNums.length;
for (int i = 0; i < k; i++) {
    assert nums[i] == expectedNums[i];
}

```

If all assertions pass, then your solution will be **accepted**.

 

**Example 1:**

```

**Input:** nums = [1,1,2]
**Output:** 2, nums = [1,2,_]
**Explanation:** Your function should return k = 2, with the first two elements of nums being 1 and 2 respectively.
It does not matter what you leave beyond the returned k (hence they are underscores).

```

**Example 2:**

```

**Input:** nums = [0,0,1,1,1,2,2,3,3,4]
**Output:** 5, nums = [0,1,2,3,4,_,_,_,_,_]
**Explanation:** Your function should return k = 5, with the first five elements of nums being 0, 1, 2, 3, and 4 respectively.
It does not matter what you leave beyond the returned k (hence they are underscores).

```

 

**Constraints:**

- `1 <= nums.length <= 3 * 10^4`

- `-100 <= nums[i] <= 100`

- `nums` is sorted in **non-decreasing** order.

## Submission History

| Date | Status | Language | Runtime | Memory | Code |
| --- | --- | --- | --- | --- | --- |
| 2026-08-16 09:08 UTC | ✅ Accepted | C | 0 ms | 12.9 MB | [view](submissions/1786871338_Accepted_2108774775.c) |
| 2026-08-16 09:08 UTC | ✅ Accepted | C | 0 ms | 13 MB | [view](submissions/1786871318_Accepted_2108774481.c) |
| 2026-08-16 09:08 UTC | ✅ Accepted | C | 0 ms | 12.9 MB | [view](submissions/1786871304_Accepted_2108774265.c) |
| 2026-08-16 09:07 UTC | ✅ Accepted | C | 0 ms | 12.8 MB | [view](submissions/1786871222_Accepted_2108773031.c) |
| 2026-08-16 08:17 UTC | ✅ Accepted | C | 3 ms | 12.8 MB | [view](submissions/1786868222_Accepted_2108732138.c) |
| 2026-08-16 08:16 UTC | 🛠️ Compile Error | C | N/A | N/A | [view](submissions/1786868201_Compile-Error_2108731870.c) |
| 2026-08-16 08:10 UTC | 💥 Runtime Error | C | N/A | N/A | [view](submissions/1786867843_Runtime-Error_2108727215.c) |

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
