import os
import time
import logging
import pandas as pd
from concurrent.futures import ProcessPoolExecutor


# ProcessPoolExecutor에서 사용할 함수는 반드시 글로벌로 정의해야 함
def read_excel_file(file_path):
    import pandas as pd
    return pd.read_excel(file_path)


def merge_ncgl(folder_path: str, date: str, milestone: str, progress_queue) -> None:
    start_time = time.time()

    file_names = [
        "StringEnglish.xlsx", "StringTraditionalChinese.xlsx", "StringSimplifiedChinese.xlsx",
        "StringJapanese.xlsx", "StringThai.xlsx", "StringSpanish.xlsx",
        "StringPortuguese.xlsx", "StringRussian.xlsx"
    ]

    dfs = []
    total_steps = len(file_names) + 3  # 파일 읽기 + 병합 + 저장 + 서식 지정
    current_step = 0

    def process_worker(queue):
        nonlocal current_step
        import concurrent.futures

        t0 = time.time()
        with ProcessPoolExecutor() as executor:
            file_paths = [os.path.join(folder_path, f) for f in file_names]
            results = list(executor.map(read_excel_file, file_paths))
            dfs.extend(results)
            for idx, file_name in enumerate(file_names):
                queue.put(f"파일:{file_name}")
                queue.put(f"단계:{idx + 1}/{total_steps}")
                queue.put(f"처리된 파일:{idx + 1}")
                current_step += 1
                current_progress = int(current_step / total_steps * 100)
                
                # 시간 계산 및 전송
                elapsed = int(time.time() - start_time)
                remaining = int((elapsed / current_progress) * (100 - current_progress)) if current_progress > 0 else 0
                queue.put(("time", elapsed, remaining))
                
                queue.put(current_progress)
        t1 = time.time()
        print(f"전체 파일 병렬 읽기 소요 시간: {t1 - t0:.2f}초")

        # 첫 번째 파일에서 기본 열 (Key, Source 등)을 가져옴
        result_df = dfs[0][['Key', 'Source', 'Comment', 'TableName', 'Status']]

        # 각 언어별 Target 열 추가 (concat으로 병합)
        lang_codes = ['EN', 'CT', 'CS', 'JA', 'TH', 'ES', 'PT', 'RU']
        target_dfs = [dfs[i][['Target']].rename(columns={'Target': f'Target_{lang_codes[i]}'}) for i in range(len(dfs))]
        result_df = pd.concat([result_df] + target_dfs, axis=1)

        # 메모리 사용량 최적화: 불필요한 데이터가 남아있지 않은지 확인
        # (필요 없는 컬럼/행이 있다면 이 시점에서 제거)

        # Python의 None 값을 빈 문자열로 대체 (텍스트로 'None'은 그대로 유지)
        for col in result_df.columns:
            if col != 'Comment':
                result_df[col] = result_df[col].apply(lambda x: 'None' if pd.isna(x) else x)

        # NaN, inf, -inf를 모두 빈 문자열로 변환 (xlsxwriter 오류 방지)
        result_df = result_df.replace([float('nan'), float('inf'), float('-inf')], '', regex=False)

        # 열 순서 재정렬
        result_df = result_df[['Key', 'Source', 'Target_EN', 'Target_CT', 'Target_CS',
                            'Target_JA', 'Target_TH', 'Target_ES', 'Target_PT',
                            'Target_RU', 'Comment', 'TableName', 'Status']]

        logging.info(f"Result DataFrame shape: {result_df.shape}")
        print(f"Result DataFrame shape: {result_df.shape}")

        current_step += 1
        queue.put(int(current_step / total_steps * 100))

        # 저장 및 서식 적용 (xlsxwriter)
        t_save_start = time.time()
        output_file = f"{date}_M{milestone}_StringALL.xlsx"
        output_path = os.path.join(folder_path, output_file)
        try:
            import xlsxwriter
            workbook = xlsxwriter.Workbook(output_path)
            worksheet = workbook.add_worksheet('Sheet1')

            # 헤더 스타일 (가운데 정렬)
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'vcenter',
                'align': 'center',
                'fg_color': '#DAE9F8',
                'font_name': '맑은 고딕',
                'font_size': 10,
                'border': 1
            })
            # 데이터 셀 스타일 (왼쪽 정렬 + 텍스트 서식)
            cell_format = workbook.add_format({
                'font_name': '맑은 고딕',
                'font_size': 10,
                'align': 'left',
                'valign': 'vcenter',
                'num_format': '@'  # 텍스트 서식
            })
            for col_num, value in enumerate(result_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 24, cell_format)

            for row_num in range(len(result_df)):
                for col_num in range(len(result_df.columns)):
                    value = result_df.iloc[row_num, col_num]
                    worksheet.write_string(row_num + 1, col_num, str(value), cell_format)

            workbook.close()
            logging.info(f"Successfully saved result to {output_path}")
            print(f"Successfully saved result to {output_path}")
        except Exception as e:
            logging.error(f"Error saving result: {str(e)}")
            queue.put(("error", f"결과 저장 실패: {str(e)}"))
            return
        t_save_end = time.time()
        print(f"엑셀 저장 및 서식 적용 소요 시간: {t_save_end - t_save_start:.2f}초")

        current_step += 1
        
        # 시간 계산 및 전송
        elapsed = int(time.time() - start_time)
        queue.put(("time", elapsed, 0))  # 완료 시 남은 시간 0
        
        queue.put(100)
        
        # 소요 시간 계산
        elapsed_time = time.time() - start_time
        queue.put(f"완료:테이블 병합을 완료했습니다. 소요 시간: {int(elapsed_time)}초")

    # process_worker 실행
    try:
        process_worker(progress_queue)
    except Exception as e:
        progress_queue.put(("error", str(e)))
