#!/usr/bin/env python3
"""
HAES Demo - Hybrid AI Evolution System 데모

OpenAI GPT-5-mini/GPT-5.1 연동 테스트
"""

import asyncio
import os
from pathlib import Path

# 환경 변수 로드
from dotenv import load_dotenv
load_dotenv()

from haes import HybridAISystem, Config
from haes.llm import OpenAIClient


async def main():
    """메인 데모 함수"""
    print("=" * 60)
    print("🚀 HAES - Hybrid AI Evolution System Demo")
    print("=" * 60)
    
    # 1. OpenAI 클라이언트 초기화
    print("\n[1] OpenAI 클라이언트 초기화...")
    try:
        llm_client = OpenAIClient(
            routing_model=os.getenv("ROUTING_MODEL", "gpt-5-mini"),
            main_model=os.getenv("MAIN_MODEL", "gpt-5.1"),
        )
        print(f"   ✅ 라우팅 모델: {llm_client.routing_model}")
        print(f"   ✅ 메인 모델: {llm_client.main_model}")
    except Exception as e:
        print(f"   ❌ 오류: {e}")
        print("   Mock 모드로 실행...")
        llm_client = None
    
    # 2. 시스템 설정
    print("\n[2] 시스템 설정...")
    
    # 샘플 데이터 경로 사용
    project_root = Path(__file__).parent
    config = Config(
        skills_path=project_root / "tests" / "fixtures" / "sample_skills",
        agents_path=project_root / "tests" / "fixtures" / "sample_agents",
        persist_dir=project_root / "demo_vectordb",
    )
    
    # 3. 시스템 초기화
    print("\n[3] HybridAISystem 초기화...")
    system = HybridAISystem(config=config, llm_client=llm_client)
    stats = system.initialize()
    print(f"   ✅ SKILL 인덱싱: {stats['skills_indexed']}개")
    print(f"   ✅ 에이전트 로드: {stats['agents_loaded']}개")
    
    # 4. API 연결 테스트 (LLM 클라이언트 있는 경우)
    if llm_client:
        print("\n[4] OpenAI API 연결 테스트...")
        success = await llm_client.test_connection()
        if success:
            print("   ✅ API 연결 성공!")
        else:
            print("   ❌ API 연결 실패")
    
    # 5. 샘플 쿼리 테스트
    print("\n[5] 샘플 쿼리 테스트...")
    print("-" * 50)
    
    queries = [
        "LoRA가 뭐야?",
        "파인튜닝 방법 알려줘",
        "RAG 시스템 구현해줘",
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n📝 쿼리 {i}: {query}")
        
        result = await system.chat(query)
        
        print(f"   모드: {result.mode}")
        print(f"   사용된 SKILL: {result.skills_used}")
        print(f"   실행 시간: {result.execution_time:.2f}s")
        print(f"   응답 미리보기: {result.response[:100]}...")
        
        # 피드백 (랜덤)
        import random
        score = random.choice([4, 5])
        system.feedback(score=score, comment="테스트 피드백")
        print(f"   피드백: {score}점")
    
    # 6. 시스템 통계
    print("\n[6] 시스템 통계")
    print("-" * 50)
    stats = system.get_stats()
    print(f"   피드백 총계: {stats['feedback']['total']}")
    print(f"   Evolution 패턴: {stats['evolution']['learned_patterns_count']}개")
    print(f"   대화 히스토리: {stats['history_length']}개")
    
    print("\n" + "=" * 60)
    print("🎉 데모 완료!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
