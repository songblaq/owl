# Session Transcript Source Spec v0

작성일: 2026-04-04
상태: 초안

## 1. 목적

OpenClaw 세션 transcript를 owl source로 흡수할 때의 기본 규칙을 정의한다.

## 2. 기본 원칙
- transcript 전체를 무조건 복제하지 않는다.
- 운영 패턴, 반복 규칙, 중요한 결정이 드러난 세션을 우선한다.
- raw에는 세션 맥락 요약을 남기고, compiled에서는 패턴 해석을 남긴다.
- 민감한 개인 대화는 범위와 보존 수준을 별도로 판단한다.

## 3. 우선 ingest 대상
- heartbeat 세션
- 운영 정책/구조 결정 세션
- 연구/오케스트레이션 세션
- 문서 생성 세션

## 4. 기대 효과
세션 transcript를 단순 로그가 아니라 운영 지식 source 로 재편해 owl이 OpenClaw의 장기 브레인 역할을 하게 한다.
