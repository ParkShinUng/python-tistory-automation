import re
import json
import asyncio

from helper import log
from config import Config
from urllib.parse import urljoin
from playwright.async_api import Page, Route
from typing import List, Optional


class ChatGPTSession:
    """하나의 Page(탭) 처리 클래스"""

    def __init__(self, page: Page, cfg: Config, worker_id: int):
        self.page = page
        self.cfg = cfg
        self.worker_id = worker_id
        
        # 캡처 저장소 (세션 전체에서 유지)
        self._captured_responses: List[dict] = []
        self._route_active = False
        self._js_interceptor_ready = False

    # ---------- 공통 동작 ----------

    # ---------- 네트워크 응답 핸들러 ----------
     # ========== 초기화 (페이지 생성 직후 호출) ==========
    async def initialize(self):
        """페이지 초기화 - 반드시 페이지 사용 전에 호출"""
        await self._setup_persistent_route()
        await self._setup_persistent_js_interceptor()
        log(f"[Worker {self.worker_id}] 인터셉터 초기화 완료")
        
    async def _setup_persistent_route(self):
        """상시 활성화 Route 인터셉터"""
        if self._route_active:
            return

        async def handle_route(route: Route):
            response = await route.fetch()
            url = route.request.url

            # 모든 conversation API GET 요청 캡처
            if "backend-api/conversation/" in url and route.request.method == "GET":
                try:
                    body = await response.json()
                    self._captured_responses.append({
                        "url": url,
                        "body": body,
                        "timestamp": asyncio.get_event_loop().time()
                    })
                except:
                    pass

            await route.fulfill(response=response)

        await self.page.route("**/backend-api/conversation/**", handle_route)
        self._route_active = True

    async def _setup_persistent_js_interceptor(self):
        """상시 활성화 JS fetch 후킹"""
        if self._js_interceptor_ready:
            return

        # 페이지 로드될 때마다 자동으로 주입되도록 설정
        await self.page.add_init_script("""
            window.__capturedResponses = window.__capturedResponses || [];
            
            if (!window.__fetchIntercepted) {
                window.__fetchIntercepted = true;
                
                const originalFetch = window.fetch;
                window.fetch = async function(...args) {
                    const response = await originalFetch.apply(this, args);
                    const url = typeof args[0] === 'string' ? args[0] : args[0]?.url || '';
                    
                    if (url.includes('backend-api/conversation/') && !url.includes('/stream')) {
                        try {
                            const clone = response.clone();
                            const body = await clone.json();
                            window.__capturedResponses.push({ 
                                url, 
                                body, 
                                timestamp: Date.now() 
                            });
                        } catch(e) {}
                    }
                    return response;
                };
                
                // XHR도 후킹
                const originalXHROpen = XMLHttpRequest.prototype.open;
                const originalXHRSend = XMLHttpRequest.prototype.send;
                
                XMLHttpRequest.prototype.open = function(method, url, ...rest) {
                    this._url = url;
                    this._method = method;
                    return originalXHROpen.apply(this, [method, url, ...rest]);
                };
                
                XMLHttpRequest.prototype.send = function(...args) {
                    this.addEventListener('load', function() {
                        if (this._url && this._url.includes('backend-api/conversation/') 
                            && !this._url.includes('/stream') && this._method === 'GET') {
                            try {
                                const body = JSON.parse(this.responseText);
                                window.__capturedResponses.push({ 
                                    url: this._url, 
                                    body, 
                                    timestamp: Date.now() 
                                });
                            } catch(e) {}
                        }
                    });
                    return originalXHRSend.apply(this, args);
                };
            }
        """)
        self._js_interceptor_ready = True

    # ========== queries 추출 ==========
    def _extract_queries_from_body(self, data: dict) -> Optional[str]:
        """body에서 queries 추출"""
        try:
            jsonpath_expr = parse("$..queries")
            find_data_list = jsonpath_expr.find(data)

            if not find_data_list:
                return None

            new_queries_data_list = [
                query_str
                for find_data in find_data_list
                for query_str in find_data.value
                if query_str  # 빈 문자열 제외
            ]
            return ', '.join(new_queries_data_list) if new_queries_data_list else None
        except Exception as e:
            log(f"queries 추출 실패: {e}")
            return None

    def _find_queries_in_route_captured(self, session_code: str) -> Optional[str]:
        """Route 캡처에서 queries 검색"""
        for resp in reversed(self._captured_responses):  # 최신 것부터 검색
            if session_code in resp.get("url", ""):
                result = self._extract_queries_from_body(resp.get("body", {}))
                if result:
                    return result
        return None

    async def _find_queries_in_js_captured(self, session_code: str) -> Optional[str]:
        """JS 캡처에서 queries 검색"""
        try:
            responses = await self.page.evaluate("window.__capturedResponses || []")
            for resp in reversed(responses):  # 최신 것부터 검색
                if session_code in resp.get("url", ""):
                    result = self._extract_queries_from_body(resp.get("body", {}))
                    if result:
                        return result
        except Exception as e:
            log(f"JS 캡처 조회 실패: {e}")
        return None

    async def _fetch_directly_via_page(self, session_code: str) -> Optional[str]:
        """페이지 컨텍스트에서 직접 API 호출 (최후의 수단)"""
        try:
            url = urljoin(self.cfg.check_json_url, session_code)
            result = await self.page.evaluate(f"""
                async () => {{
                    try {{
                        const response = await fetch('{url}');
                        const data = await response.json();
                        return data;
                    }} catch(e) {{
                        return null;
                    }}
                }}
            """)
            if result:
                return self._extract_queries_from_body(result)
        except Exception as e:
            log(f"직접 API 호출 실패: {e}")
        return None

    def _clear_captured_for_session(self, session_code: str = None):
        """특정 세션 또는 전체 캡처 초기화"""
        if session_code:
            self._captured_responses = [
                r for r in self._captured_responses
                if session_code not in r.get("url", "")
            ]
        else:
            self._captured_responses.clear()

    async def _clear_js_captured(self):
        """JS 캡처 초기화"""
        try:
            await self.page.evaluate("window.__capturedResponses = [];")
        except:
            pass

    # ========== 4단계 폴백 시스템 ==========
    async def _wait_for_queries_with_fallback(
        self,
        session_code: str,
        timeout: float
    ) -> Optional[str]:
        """
        4단계 폴백으로 100% queries 캡처 시도:
        1단계: Route 캡처 검색 (실시간)
        2단계: JS 캡처 검색 (백업)
        3단계: 페이지 리로드 후 재검색
        4단계: 직접 API 호출 (최후의 수단)
        """
        queries_data: Optional[str] = None
        start_time = asyncio.get_event_loop().time()

        # 1단계 & 2단계: 실시간 캡처 검색 (폴링)
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            # Route 캡처 검색
            queries_data = self._find_queries_in_route_captured(session_code)
            if queries_data:
                log(f"[Worker {self.worker_id}] 1단계 성공: Route 캡처에서 queries 발견")
                return queries_data

            # JS 캡처 검색
            queries_data = await self._find_queries_in_js_captured(session_code)
            if queries_data:
                log(f"[Worker {self.worker_id}] 2단계 성공: JS 캡처에서 queries 발견")
                return queries_data

            await asyncio.sleep(0.3)

        # 3단계: 페이지 리로드 후 재검색
        log(f"[Worker {self.worker_id}] 3단계: 페이지 리로드 시도...")
        for attempt in range(self.cfg.max_reload_try):
            await self.page.reload(wait_until="load")
            await asyncio.sleep(2)

            queries_data = self._find_queries_in_route_captured(session_code)
            if queries_data:
                log(f"[Worker {self.worker_id}] 3단계 성공: 리로드 후 Route 캡처에서 발견 (시도 {attempt + 1})")
                return queries_data

            queries_data = await self._find_queries_in_js_captured(session_code)
            if queries_data:
                log(f"[Worker {self.worker_id}] 3단계 성공: 리로드 후 JS 캡처에서 발견 (시도 {attempt + 1})")
                return queries_data

        # 4단계: 직접 API 호출 (최후의 수단)
        log(f"[Worker {self.worker_id}] 4단계: 직접 API 호출 시도...")
        queries_data = await self._fetch_directly_via_page(session_code)
        if queries_data:
            log(f"[Worker {self.worker_id}] 4단계 성공: 직접 API 호출로 queries 획득")
            return queries_data

        log(f"[Worker {self.worker_id}] 모든 단계 실패: queries를 찾을 수 없음")
        return None

    # ========== 프롬프트 전송 & queries 수집 ==========
    async def send_prompt_and_get_session_and_queries(self, prompt: str) -> Optional[str]:
        """프롬프트 전송 후 queries 수집"""
        
        # 이전 캡처 정리
        self._clear_captured_for_session()
        await self._clear_js_captured()

        try:
            # 프롬프트 전송
            prompt_textarea = await self.page.wait_for_selector(
                "div[id='prompt-textarea']", timeout=10000
            )
            await prompt_textarea.fill(prompt)
            await prompt_textarea.press("Enter")

            # URL 변경 대기 (세션 코드 획득)
            await self.page.wait_for_url("**/c/*", timeout=self.cfg.min_answer_wait * 1000)
            session_code = await self.extract_session_code_from_url(
                await self.page.evaluate("location.href")
            )

            if not session_code:
                log(f"[Worker {self.worker_id}] session_code 추출 실패")
                return None

            log(f"[Worker {self.worker_id}] session_code={session_code}")

            # 4단계 폴백으로 queries 추출
            queries = await self._wait_for_queries_with_fallback(
                session_code, self.cfg.queries_wait_timeout
            )

            log(f"[Worker {self.worker_id}] prompt={prompt[:30]}..., queries_found={queries is not None}")

        except Exception as e:
            log(f"[Worker {self.worker_id}] 프롬프트 처리 중 예외: {e}")
            queries = None

        await self.delete_chat()
        await asyncio.sleep(self.cfg.between_prompts_sleep)

        print(f"result queries : {queries}")
        return queries

    async def reload_and_get_queries(self, session_code: str) -> Optional[str]:
        """리로드 후 queries 수집"""
        self._clear_captured_for_session(session_code)
        await self._clear_js_captured()
        
        await self.page.reload(wait_until="load")
        return await self._wait_for_queries_with_fallback(
            session_code, self.cfg.reload_wait_timeout
        )

    async def delete_chat(self) -> None:
        """채팅 삭제"""
        try:
            await self.page.locator('button[data-testid="conversation-options-button"]').click()
        except Exception as e:
            await self.page.reload(wait_until="load")
            try:
                await self.page.locator('button[data-testid="conversation-options-button"]').click()
            except Exception as e:
                log(f"[Worker {self.worker_id}] 채팅 삭제 실패: {e}")
                return
        await self.page.locator('text=삭제').click()
        await self.page.locator('button[data-testid="delete-conversation-confirm-button"]').click()
        await asyncio.sleep(self.cfg.between_prompts_sleep)

    @staticmethod
    async def extract_session_code_from_url(url: str) -> Optional[str]:
        """URL에서 session_code 추출"""
        m = re.search(r"/c/([0-9a-fA-F\-]+)", url)
        return m.group(1) if m else None
    