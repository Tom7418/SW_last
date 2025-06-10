# SW_last 프로젝트
선문대학교 AI소프트웨어 3학년 1학기 SW프로젝트 기초 기말 팀프로젝트  
여기다가 기초 설정같은거 적어 놓읍시다.  

왼쪽 항목 3번째 '소스제어' 탭에서 '변경 내용 동기화'를 누르면 자동 커밋,풀,푸쉬인듯합니다.  
명령어로 하려면 git pull origin main하면 됩니다.  
  
랜섬웨어가 저장되어 있는곳 : https://github.com/ytisf/theZoo/tree/master/malware/Binaries  
api를 통해 악성코드를 받을 수 있는곳 : https://malshare.com/
악성 데이터 수집하는 곳 :  https://bazaar.abuse.ch/browse/

### 주의 이 모든것은 가상환경에서 이루어집니다. 절대 가상환경 외에 실행 X  
가상환경을 생성 깃허브 연결 폴더 경로에 python -m venv .venv  \

## 항상 모든것을 할때(깃명렁어 제외) 가상환경에 들어가야함
생성 후 .\.venv\Scripts\activate 입력하여 활성화  
깃허브 연결 폴더 경로에 pip install -r requirements.txt 실행하여 필요한 패키지 일관 다운로드  
연결폴더\ember 경로에서 pip install . 실행 후 cd.. 한 후  python test_ember.py 실행하여 ember가 제대로 작동하는지 확인  

모델학습 실행 명령어 : python train_model.py  

venv에서 악성코드zip파일을 json으로 변환하려 할 경우
