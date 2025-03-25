import os
import logging
from app import create_app
from app.utils.sms import send_verification_code

# 設置日誌記錄
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_sms():
    try:
        # 明確禁用所有代理
        os.environ['HTTP_PROXY'] = ''
        os.environ['HTTPS_PROXY'] = ''
        os.environ['NO_PROXY'] = '*'
        
        # 創建應用程式實例
        app = create_app()
        
        # 在應用程式上下文中執行
        with app.app_context():
            # 測試發送簡訊
            phone_number = '0912345678'
            code = '123456'
            
            logger.info(f'開始測試簡訊發送到 {phone_number}')
            result = send_verification_code(phone_number, code)
            
            if result:
                logger.info('簡訊發送成功！')
            else:
                logger.error('簡訊發送失敗！')
                
    except Exception as e:
        logger.error(f'測試過程中發生錯誤: {str(e)}', exc_info=True)

if __name__ == '__main__':
    test_sms()