# Query Orchestration Spec v0

작성일: 2026-04-03
상태: 신규 초안

## 1. 목적

큰 질문 하나가 들어왔을 때, LLM이 필요한 source를 모아 임시 위키를 구성하고, lint와 반복 보강을 거쳐 최종 report를 만드는 흐름을 정의한다.

## 2. 기본 가정

- 질문은 단순 답변으로 끝나지 않을 수 있다.
- 필요한 경우 질문 단위로 임시 위키/작업 묶음을 만든다.
- 최종 산출물은 다시 owl에 파일링한다.

## 3. 기본 흐름

1. 질문 범위를 정의한다.
2. 관련 raw/compiled 문서를 찾는다.
3. 부족한 source가 있으면 웹 검색 또는 추가 ingest로 보완한다.
4. 임시 위키 묶음(summary/index/concept/report draft)을 구성한다.
5. lint/health check로 불일치, 누락, 연결 부족을 점검한다.
6. 필요한 source와 문서를 반복 보강한다.
7. 최종 report / slide / figure를 만든다.
8. 결과를 compiled 또는 outputs에 filing 한다.

## 4. 임시 위키의 구성 요소

- working summary
- working index
- concept draft
- contradiction / gap notes
- final report draft

## 5. lint 항목

- source 없는 주장 존재 여부
- summary는 있는데 관련 concept/index가 없는지
- 충돌하는 진술이 있는지
- 같은 질문에 필요한 누락 source가 있는지
- 최종 결과가 raw/compiled/output을 제대로 참조하는지

## 6. 결과물 계약

- 텍스트 답변만으로 끝내지 않는다.
- 최종 결과는 가능하면 파일로 남긴다.
- markdown report는 `compiled/`에 둔다.
- slide/figure는 `outputs/`에 둔다.
- 결과를 다시 summary/index/concept에서 참조할 수 있게 연결한다.

## 7. 운영 원칙

- 질문은 임시 위키를 호출하는 트리거가 될 수 있다.
- 임시 위키는 영구 자산으로 승격될 수 있다.
- 한 번의 답변보다 재사용 가능한 파일링 결과를 우선한다.
- 이 흐름은 `.decode()` 수준의 단순 검색을 넘어, 질문 단위의 wiki compile loop를 지향한다.
