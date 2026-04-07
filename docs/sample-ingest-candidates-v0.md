# Sample Ingest Candidates v0

작성일: 2026-04-04
상태: 조사 초안

## 목적

owl의 운영용 샘플 데이터 후보를 정리한다.

## 사용자 제안 기준 후보
- 기존 리서치 오케스트레이션 관련 자료
- Discord 리서치 카테고리 및 하위 리서치 채널
- 카카오톡 대화방
- 긱뉴스 채널 링크

## 처리 원칙
- 먼저 실제 접근 가능한 경로/자료 여부를 확인한다.
- 곧바로 대량 이관하지 않고, source type 별로 1~2건씩 샘플 ingest 한다.
- 민감한 대화 데이터는 raw 보관 범위와 메타 수준을 먼저 정한다.
- 링크 모음은 research source 로, 대화방은 log source 로, 리서치 문서는 article/note/report source 로 본다.

## 예상 source type 매핑
- 리서치 오케스트레이션 문서: report / workflow / research source
- Discord 리서치 채널: chat-log / research-log source
- 카카오톡 대화방: private chat-log source
- 긱뉴스 링크: link-bundle / article-candidate source

## 다음 단계
- 실제 경로 및 접근 가능 자료 확인
- 샘플 ingest 1차 목록 확정
- raw/compiled 생성
