import tkinter as tk
from tkinter import ttk
import time
import queue
import threading
from typing import Callable, Optional, List, Tuple, Dict, Any

class ProgressWindow:
    """
    진행 상태를 보여주는 모듈화된 윈도우 클래스.
    여러 애플리케이션에서 재사용 가능하도록 설계되었습니다.
    """
    def __init__(
        self, 
        parent: tk.Tk,
        title: str = "처리 중",
        width: int = 500,
        height: int = 300,
        theme_color: str = "#4CAF50",
        font_family: str = "맑은 고딕"
    ):
        """
        진행 창을 초기화합니다.
        
        Args:
            parent: 부모 윈도우
            title: 창 제목
            width: 창 너비
            height: 창 높이
            theme_color: 테마 색상
            font_family: 폰트
        """
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry(f"{width}x{height}")
        self.center_window()
        
        # 창이 닫힐 때 이벤트 처리
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # 테마 설정
        self.theme_color = theme_color
        self.font_family = font_family
        self.window.configure(bg="#f5f5f5")  # 플랫 디자인을 위한 배경색
        
        # 진행 상태 변수
        self.queue = queue.Queue()
        self.start_time = time.time()
        self.is_running = True
        self.progress_value = 0
        self.current_file = ""
        self.current_step = ""
        self.total_steps = 0
        self.processed_files = 0
        self.total_files = 0
        self.cancelled = False
        
        # UI 요소 생성
        self._create_widgets()
    
    def center_window(self):
        """창을 부모 창의 중앙에 배치합니다."""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.parent.winfo_x() + (self.parent.winfo_width() // 2)) - (width // 2)
        y = (self.parent.winfo_y() + (self.parent.winfo_height() // 2)) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_widgets(self):
        """UI 요소를 생성하고 배치합니다."""
        # 진행 단계 표시
        self.step_frame = tk.Frame(self.window, bg="#f5f5f5")
        self.step_frame.pack(fill=tk.X, padx=20, pady=(20, 5))
        
        self.step_label = tk.Label(
            self.step_frame, 
            text="진행 중...", 
            font=(self.font_family, 12, "bold"),
            bg="#f5f5f5",
            fg="#333333"
        )
        self.step_label.pack(side=tk.LEFT)
        
        # 현재 처리 중인 파일 표시 - 수정된 레이아웃
        self.file_frame = tk.Frame(self.window, bg="#f5f5f5")
        self.file_frame.pack(fill=tk.X, padx=20, pady=(5, 5))
        
        # "처리 중:" 라벨 (이제 전체 너비를 차지)
        self.file_prefix_label = tk.Label(
            self.file_frame,
            text="처리 중:",
            font=(self.font_family, 10, "bold"),
            bg="#f5f5f5",
            fg="#555555",
            anchor="w"
        )
        self.file_prefix_label.pack(fill=tk.X, side=tk.TOP, anchor="w")
        
        # 파일명 표시를 위한 컨테이너 프레임 (왼쪽 여백 추가)
        self.file_text_container = tk.Frame(self.file_frame, bg="#f5f5f5")
        self.file_text_container.pack(fill=tk.X, side=tk.TOP, pady=(0, 5))
        
        # 왼쪽 여백을 위한 빈 프레임
        self.left_margin = tk.Frame(
            self.file_text_container, 
            width=20,  # 20픽셀 여백
            bg="#f5f5f5"
        )
        self.left_margin.pack(side=tk.LEFT, fill=tk.Y)
        self.left_margin.pack_propagate(False)  # 크기 고정
        
        # Text 위젯 대신 Label 위젯으로 교체 (파일명이 잘리는 문제 해결)
        self.file_label = tk.Label(
            self.file_text_container,
            text="",
            font=(self.font_family, 10),
            bg="#f0f0f0",  # 배경색을 약간 다르게 하여 구분
            fg="#555555",
            anchor="w",    # 왼쪽 정렬
            justify=tk.LEFT, # 텍스트 왼쪽 정렬
            padx=10,       # 내부 여백
            pady=5,
            wraplength=400 # 자동 줄바꿈
        )
        self.file_label.pack(fill=tk.X, side=tk.LEFT, expand=True)
        
        # 진행 상태 표시 영역
        self.progress_frame = tk.Frame(self.window, bg="#f5f5f5", height=30)
        self.progress_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # 스타일 설정
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor="#e0e0e0",
            background=self.theme_color,
            thickness=20,
            borderwidth=0
        )
        
        # 프로그레스 바
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            orient="horizontal",
            length=460,
            mode="determinate",
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill=tk.X)
        
        # 진행률 표시
        self.info_frame = tk.Frame(self.window, bg="#f5f5f5")
        self.info_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.percent_label = tk.Label(
            self.info_frame, 
            text="0%", 
            font=(self.font_family, 12, "bold"),
            bg="#f5f5f5",
            fg=self.theme_color
        )
        self.percent_label.pack(side=tk.LEFT)
        
        self.time_label = tk.Label(
            self.info_frame, 
            text="남은 시간: 계산 중...", 
            font=(self.font_family, 10),
            bg="#f5f5f5",
            fg="#555555"
        )
        self.time_label.pack(side=tk.RIGHT)
        
        # 파일 수 표시
        self.files_frame = tk.Frame(self.window, bg="#f5f5f5")
        self.files_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.files_label = tk.Label(
            self.files_frame, 
            text="처리된 파일: 0/0", 
            font=(self.font_family, 10),
            bg="#f5f5f5",
            fg="#555555"
        )
        self.files_label.pack(side=tk.LEFT)
        
        # 취소 버튼
        self.button_frame = tk.Frame(self.window, bg="#f5f5f5")
        self.button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.cancel_button = tk.Button(
            self.button_frame,
            text="취소",
            font=(self.font_family, 10),
            bg="#f44336",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.cancel
        )
        self.cancel_button.pack(side=tk.RIGHT)
        
        # 애니메이션 효과를 위한 캔버스
        self.canvas_frame = tk.Frame(self.window, bg="#f5f5f5")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        self.canvas = tk.Canvas(
            self.canvas_frame, 
            width=460, 
            height=30, 
            bg="#f5f5f5",
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 애니메이션 요소 초기화
        self.animation_dot = None
        self._start_animation()
    
    def _start_animation(self):
        """진행 상태 애니메이션을 시작합니다."""
        self.animation_dot = self.canvas.create_oval(10, 10, 20, 20, fill=self.theme_color, outline="")
        self._animate_dot()
    
    def _animate_dot(self):
        """도트 애니메이션을 업데이트합니다."""
        if not self.is_running:
            return
        
        # 캔버스 크기
        width = self.canvas.winfo_width()
        
        # 현재 위치
        x1, y1, x2, y2 = self.canvas.coords(self.animation_dot)
        center_x = (x1 + x2) / 2
        
        # 새 위치 계산 (왕복 애니메이션)
        if center_x < 20:
            direction = 5  # 오른쪽으로 이동
        elif center_x > width - 20:
            direction = -5  # 왼쪽으로 이동
        else:
            # 진행률에 따라 방향 결정
            direction = 5 if (center_x < self.progress_value / 100 * width) else -5
        
        self.canvas.move(self.animation_dot, direction, 0)
        self.window.after(50, self._animate_dot)
    
    def start(self, 
              worker_function: Callable, 
              args: Tuple = (), 
              total_steps: int = 1,
              total_files: int = 0):
        """
        작업 스레드를 시작하고 진행 상태를 모니터링합니다.
        
        Args:
            worker_function: 백그라운드에서 실행할 작업 함수
            args: 작업 함수에 전달할 인자
            total_steps: 전체 단계 수
            total_files: 전체 파일 수
        """
        self.total_steps = total_steps
        self.total_files = total_files
        self.files_label.config(text=f"처리된 파일: 0/{total_files}")
        
        # 작업자 스레드에 큐 추가
        thread_args = (self.queue,) + args
        
        # 작업 스레드 시작
        self.worker_thread = threading.Thread(target=worker_function, args=thread_args)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        
        # 업데이트 시작
        self.window.after(100, self._update_progress)
    
    def _update_progress(self):
        """큐에서 메시지를 받아 진행 상태를 업데이트합니다."""
        if not self.is_running:
            return
            
        try:
            while not self.queue.empty():
                message = self.queue.get_nowait()
                
                if isinstance(message, int):
                    # 진행률 업데이트
                    self.progress_value = message
                    self.progress_bar["value"] = message
                    self.percent_label.config(text=f"{message}%")
                    
                    # 남은 시간 계산 (보다 정확한 알고리즘)
                    elapsed_time = time.time() - self.start_time
                    if message > 0:
                        # 진행률이 0보다 크고 100%가 아닐 때만 계산
                        if message < 100:
                            # 단순 비례식 대신 최근 진행 속도를 고려한 계산
                            remaining_percent = 100 - message
                            rate = elapsed_time / message
                            estimated_remaining = remaining_percent * rate
                            
                            # 급격한 변동 방지를 위한 평활화
                            if hasattr(self, 'last_estimate'):
                                estimated_remaining = (estimated_remaining + self.last_estimate) / 2
                            
                            self.last_estimate = estimated_remaining
                            
                            # 남은 시간 표시
                            if estimated_remaining > 60:
                                mins = int(estimated_remaining // 60)
                                secs = int(estimated_remaining % 60)
                                self.time_label.config(text=f"남은 시간: {mins}분 {secs}초")
                            else:
                                self.time_label.config(text=f"남은 시간: {int(estimated_remaining)}초")
                    
                elif isinstance(message, str):
                    # 작업 완료 또는 일반 메시지
                    if message.startswith("완료:"):
                        self.progress_bar["value"] = 100
                        self.percent_label.config(text="100%")
                        self.step_label.config(text="작업 완료!")
                        self.time_label.config(text=f"소요 시간: {int(time.time() - self.start_time)}초")
                        self.cancel_button.config(text="닫기")
                        return
                    elif message.startswith("파일:"):
                        # 현재 처리 중인 파일 업데이트 - 수정된 부분
                        # message[5:] 대신 더 안전한 방법으로 파일명 추출
                        prefix = "파일:"
                        if message.startswith(prefix):
                            self.current_file = message[len(prefix):]
                        # 디버깅 출력
                        print(f"원본 메시지: '{message}'")
                        print(f"설정할 파일명: '{self.current_file}'")
                        self.file_label.config(text=self.current_file)  # Label 위젯 사용
                    elif message.startswith("단계:"):
                        # 현재 단계 업데이트
                        parts = message[3:].split("/")
                        current = int(parts[0])
                        self.current_step = parts[1]
                        self.step_label.config(text=f"{current}/{self.total_steps}단계: {self.current_step}")
                    elif message.startswith("처리된 파일:"):
                        # 처리된 파일 수 업데이트
                        self.processed_files = int(message.split(":")[1])
                        self.files_label.config(text=f"처리된 파일: {self.processed_files}/{self.total_files}")
                
                elif isinstance(message, tuple) and message[0] == "error":
                    # 오류 처리
                    from tkinter import messagebox
                    messagebox.showerror("오류", message[1], parent=self.window)
                    self.window.destroy()
                    return
            
        except queue.Empty:
            pass
        
        # 계속 업데이트
        self.window.after(100, self._update_progress)
    
    def cancel(self):
        """작업을 취소하거나 완료된 경우 창을 닫습니다."""
        if self.progress_bar["value"] == 100:
            self.window.destroy()
        else:
            from tkinter import messagebox
            if messagebox.askyesno("취소 확인", "진행 중인 작업을 취소하시겠습니까?", parent=self.window):
                self.cancelled = True
                self.is_running = False
                self.queue.put(("error", "사용자에 의해 취소되었습니다."))
    
    def on_close(self):
        """창이 닫힐 때 호출됩니다."""
        self.cancel()
    
    def destroy(self):
        """창을 닫고 리소스를 정리합니다."""
        self.is_running = False
        self.window.destroy()

# 사용 예시
if __name__ == "__main__":
    def example_worker(q):
        """예제 작업 함수"""
        for i in range(101):
            if i == 10:
                q.put("파일:example1.xlsx")
                q.put("단계:1/3")
            elif i == 30:
                q.put("처리된 파일:1")
            elif i == 50:
                q.put("파일:example2.xlsx")
                q.put("단계:2/3")
            elif i == 70:
                q.put("처리된 파일:2")
                q.put("파일:example3.xlsx")
                q.put("단계:3/3")
            elif i == 90:
                q.put("처리된 파일:3")
            
            q.put(i)
            time.sleep(0.1)
        
        q.put("완료:작업이 성공적으로 완료되었습니다.")
    
    root = tk.Tk()
    root.withdraw()  # 메인 창 숨기기
    
    progress = ProgressWindow(root, theme_color="#4CAF50")
    progress.start(example_worker, total_steps=3, total_files=3)
    
    root.mainloop() 