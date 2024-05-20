import heapq


s = "abca" * 250
K = 5
pq = []
for i in range(len(s)):
    for j in range(i, len(s)):
        set_ = s[i:j + 1]
        heapq.heappush(pq, (-ord(set_[0]), set_))


for _ in range(K - 1):
 heapq.heappop(pq)

 print(heapq.heappop(pq)[1])



