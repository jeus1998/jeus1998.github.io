---
layout: post
title: "숫자의 개수 - 2577"
date: 2026-11-25 12:00:00 +0900
permalink: /coding-test/posts/boj-2577/
categories: ["코딩 테스트", "백준"]
tags: ["백준", "Bronze II"]
description: "백준 2577번 문제 풀이 (Bronze II)"
coding_test_id: "boj-2577"
---
이 글은 [jeus1998/coding-test](https://github.com/jeus1998/coding-test/tree/main/%EB%B0%B1%EC%A4%80/Bronze/2577.%E2%80%85%EC%88%AB%EC%9E%90%EC%9D%98%E2%80%85%EA%B0%9C%EC%88%98) 저장소의 풀이를 자동으로 가져온 기록입니다. 원본은 [Java 파일](https://github.com/jeus1998/coding-test/blob/main/%EB%B0%B1%EC%A4%80/Bronze/2577.%E2%80%85%EC%88%AB%EC%9E%90%EC%9D%98%E2%80%85%EA%B0%9C%EC%88%98/%EC%88%AB%EC%9E%90%EC%9D%98%E2%80%85%EA%B0%9C%EC%88%98.java)에서 확인할 수 있습니다.

## 문제 설명

# [Bronze II] 숫자의 개수 - 2577 

[문제 링크](https://acmicpc.net/problem/2577) 

### 성능 요약

메모리: 14412 KB, 시간: 96 ms

### 분류

사칙연산, 구현, 수학

### 제출 일자

2026년 11월 25일 13:49:01

### 문제 설명

<p>세 개의 자연수 A, B, C가 주어질 때 A × B × C를 계산한 결과에 0부터 9까지 각각의 숫자가 몇 번씩 쓰였는지를 구하는 프로그램을 작성하시오.</p>

<p>예를 들어 A = 150, B = 266, C = 427 이라면 A × B × C = 150 × 266 × 427 = 17037300 이 되고, 계산한 결과 17037300 에는 0이 3번, 1이 1번, 3이 2번, 7이 2번 쓰였다.</p>

### 입력 

 <p>첫째 줄에 A, 둘째 줄에 B, 셋째 줄에 C가 주어진다. A, B, C는 모두 100보다 크거나 같고, 1,000보다 작은 자연수이다.</p>

### 출력 

 <p>첫째 줄에는 A × B × C의 결과에 0 이 몇 번 쓰였는지 출력한다. 마찬가지로 둘째 줄부터 열 번째 줄까지 A × B × C의 결과에 1부터 9까지의 숫자가 각각 몇 번 쓰였는지 차례로 한 줄에 하나씩 출력한다.</p>



## 풀이 코드

```java
import java.util.*;
import java.io.*;
public class Main {
	public static void main(String[] args) throws IOException {
		var br = new BufferedReader(new InputStreamReader(System.in));
		int A = Integer.parseInt(br.readLine());
		int B = Integer.parseInt(br.readLine());
		int C = Integer.parseInt(br.readLine());
		String result = Integer.toString(A * B * C);
		int [] memo = new int [10];
		for(int i = 0; i < result.length(); i++) {
			memo[result.charAt(i) - '0']++;
		}
		StringBuilder sb = new StringBuilder();
		for(int i = 0; i < 10; i++) {
			sb.append(memo[i]).append("\n");
		}
		System.out.println(sb);
	}
}
```
