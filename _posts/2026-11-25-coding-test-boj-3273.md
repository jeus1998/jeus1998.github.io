---
layout: post
title: "두 수의 합 - 3273"
date: 2026-11-25 12:00:00 +0900
permalink: /coding-test/posts/boj-3273/
categories: ["코딩 테스트", "백준"]
tags: ["백준", "Silver III"]
description: "백준 3273번 문제 풀이 (Silver III)"
coding_test_id: "boj-3273"
---
이 글은 [jeus1998/coding-test](https://github.com/jeus1998/coding-test/tree/main/%EB%B0%B1%EC%A4%80/Silver/3273.%E2%80%85%EB%91%90%E2%80%85%EC%88%98%EC%9D%98%E2%80%85%ED%95%A9) 저장소의 풀이를 자동으로 가져온 기록입니다. 원본은 [Java 파일](https://github.com/jeus1998/coding-test/blob/main/%EB%B0%B1%EC%A4%80/Silver/3273.%E2%80%85%EB%91%90%E2%80%85%EC%88%98%EC%9D%98%E2%80%85%ED%95%A9/%EB%91%90%E2%80%85%EC%88%98%EC%9D%98%E2%80%85%ED%95%A9.java)에서 확인할 수 있습니다.

## 문제

### 문제 설명

<p>n개의 서로 다른 양의 정수 a<sub>1</sub>, a<sub>2</sub>, ..., a<sub>n</sub>으로 이루어진 수열이 있다. a<sub>i</sub>의 값은 1보다 크거나 같고, 1000000보다 작거나 같은 자연수이다. 자연수 x가 주어졌을 때, a<sub>i</sub> + a<sub>j</sub> = x (1 ≤ i < j ≤ n)을 만족하는 (a<sub>i</sub>, a<sub>j</sub>)쌍의 수를 구하는 프로그램을 작성하시오.</p>

### 입력 

 <p>첫째 줄에 수열의 크기 n이 주어진다. 다음 줄에는 수열에 포함되는 수가 주어진다. 셋째 줄에는 x가 주어진다. (1 ≤ n ≤ 100000, 1 ≤ x ≤ 2000000)</p>

### 출력 

 <p>문제의 조건을 만족하는 쌍의 개수를 출력한다.</p>

## 풀이 코드

```java
import java.io.*;
import java.util.*;
public class Main {
	static final int INF = 1000001;
	public static void main(String[] args) throws  IOException {
		var br = new BufferedReader(new InputStreamReader(System.in));
		var n = Integer.parseInt(br.readLine());
		var elements = new boolean[INF];
		var record = new int [n];
		var inputTokens = new StringTokenizer(br.readLine());
		for (int i = 0; i < n; i++) {
			var cur = Integer.parseInt(inputTokens.nextToken());
			elements[cur] = true;
			record[i] = cur;
		}
		var x = Integer.parseInt(br.readLine());
		var answer = 0;
		for(int i = 0; i < n; i++) {
			if(x - record[i] <= 0 || x - record[i] >= INF) continue;
			if(elements[x - record[i]]) answer++;
		}
		System.out.println(answer / 2);
	}
}
```
