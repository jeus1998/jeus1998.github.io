---
layout: post
title: "방 번호 - 1475"
date: 2026-11-25 12:00:00 +0900
permalink: /coding-test/posts/boj-1475/
categories: ["코딩 테스트", "백준"]
tags: ["백준", "Silver V"]
description: "백준 1475번 문제 풀이 (Silver V)"
coding_test_id: "boj-1475"
---
이 글은 [jeus1998/coding-test](https://github.com/jeus1998/coding-test/tree/main/%EB%B0%B1%EC%A4%80/Silver/1475.%E2%80%85%EB%B0%A9%E2%80%85%EB%B2%88%ED%98%B8) 저장소의 풀이를 자동으로 가져온 기록입니다. 원본은 [Java 파일](https://github.com/jeus1998/coding-test/blob/main/%EB%B0%B1%EC%A4%80/Silver/1475.%E2%80%85%EB%B0%A9%E2%80%85%EB%B2%88%ED%98%B8/%EB%B0%A9%E2%80%85%EB%B2%88%ED%98%B8.java)에서 확인할 수 있습니다.

## 문제 설명

# [Silver V] 방 번호 - 1475 

[문제 링크](https://acmicpc.net/problem/1475) 

### 성능 요약

메모리: 14940 KB, 시간: 104 ms

### 분류

구현

### 제출 일자

2026년 11월 25일 14:00:47

### 문제 설명

<p>다솜이는 은진이의 옆집에 새로 이사왔다. 다솜이는 자기 방 번호를 예쁜 플라스틱 숫자로 문에 붙이려고 한다.</p>

<p>다솜이의 옆집에서는 플라스틱 숫자를 한 세트로 판다. 한 세트에는 0번부터 9번까지 숫자가 하나씩 들어있다. 다솜이의 방 번호가 주어졌을 때, 필요한 세트의 개수의 최솟값을 출력하시오. (6은 9를 뒤집어서 이용할 수 있고, 9는 6을 뒤집어서 이용할 수 있다.)</p>

### 입력 

 <p>첫째 줄에 다솜이의 방 번호 N이 주어진다. N은 1,000,000보다 작거나 같은 자연수이다.</p>

### 출력 

 <p>첫째 줄에 필요한 세트의 개수를 출력한다.</p>



## 풀이 코드

```java
/**
 * 방 번호 [실버4]
 */
import java.util.*;
import java.io.*;
public class Main {
	public static void main(String[] args) throws IOException {
		var br = new BufferedReader(new InputStreamReader(System.in));
		String input = br.readLine();
		int[] memo = new int[10];
		for(int i = 0; i < input.length(); i++) {
			memo[input.charAt(i) - '0']++;
		}
		int temp = ((memo[6] + memo[9])) / 2 + ((memo[6] + memo[9]) % 2 == 0 ? 0 : 1);
		memo[6] = temp; memo[9] = temp;
		int max = 0;
		for(int i = 0; i < 10; i++) {
			max = Math.max(max, memo[i]);
		}
		System.out.println(max);
	}
}
```
