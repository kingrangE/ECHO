import streamlit as st
from utils.supabase_function import upload_review, load_review
from utils.functions import navigate_to
from datetime import datetime
import pandas as pd

def show_review():
    # 후기 및 건의사항 확인하기 
    st.title("후기 및 건의사항 확인하기")
    st.subheader("후기와 건의사항을 통해 더 멋지고 쓰기 좋게 만들어보겠습니다!", divider="orange")
    st.markdown("현재는 **삭제 또는 수정**이 불가합니다. 가능하도록 빨리 수정하겠습니다!")

    # 커스텀 CSS 스타일 추가
    st.markdown("""
    <style>
    .review-card {
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 5px solid #FF4B4B;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .review-date {
        font-size: 0.8em;
        margin-bottom: 5px;
    }    
    .review-content {
        font-size: 1em;
        line-height: 1.5;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)


    # 리뷰 작성 섹션
    st.markdown("### 리뷰 작성")
    review = st.text_area(label="review", placeholder="여기에 후기 또는 건의 사항을 입력해주세요!", key="review_input")
    
    col1, col2 = st.columns(2)
    with col1:
        submit = st.button("제출", key="submit", use_container_width=True)
    with col2:
        main = st.button('뒤로 가기', key="main", use_container_width=True)
    
    if submit:
        if review.strip() != "":
            upload_review(st.session_state.user_id, review)
            st.rerun()
        else:
            st.error("정상적인 입력이 아닙니다.")
    
    if main:
        navigate_to("main")
    
    st.divider()
    # 리뷰 표시 섹션
    st.markdown("### 모든 리뷰")
    
    # 리뷰 데이터 가져오기
    responses = load_review()
    
    # 리뷰가 있는 경우에만 표시
    if responses and hasattr(responses, 'data') and len(responses.data) > 0:
        # 최신 리뷰가 위에 오도록 정렬
        reviews = sorted(responses.data, key=lambda x: x.get('created_at', ''), reverse=True)
        # 리뷰 컨테이너 생성
        review_container = st.container()
        
        with review_container:
            for i, review_data in enumerate(reviews):
                # 리뷰 데이터 추출
                content = review_data.get('content', '내용 없음')                
                created_at = review_data.get('created_at', '')
                try:
                    date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    formatted_date = date_obj.strftime('%Y년 %m월 %d일 %H:%M')
                except:
                    formatted_date = created_at
                # HTML로 리뷰 카드 생성
                st.markdown(f"""
                <div class="review-card">
                    <div class="review-date">{formatted_date}</div>
                    <div class="review-content">{content}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("아직 작성된 리뷰가 없습니다. 첫 번째 리뷰를 작성해보세요!")